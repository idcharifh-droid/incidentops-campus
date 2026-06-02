from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Ticket, Comment, Attachment, TicketHistory, Status, Priority
from .forms import TicketCreateForm, TicketEditForm, CommentForm, AttachmentForm
from accounts.decorators import admin_required, admin_or_technician_required
from technicians.models import Technician
from notifications.utils import send_ticket_notification


@login_required
def ticket_list(request):
    profile = request.user.profile
    tickets = Ticket.objects.select_related('category', 'created_by', 'assigned_to__user')

    if profile.is_user():
        tickets = tickets.filter(created_by=request.user)
    elif profile.is_technician():
        try:
            tech = request.user.technician_profile
            tickets = tickets.filter(
                Q(assigned_to=tech) | Q(status=Status.PENDING_ASSIGNMENT)
            )
        except Exception:
            tickets = tickets.none()

    # Filters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')

    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if category_filter:
        tickets = tickets.filter(category_id=category_filter)
    if search:
        tickets = tickets.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    from categories.models import Category
    return render(request, 'tickets/list.html', {
        'tickets': tickets,
        'statuses': Status.choices,
        'priorities': Priority.choices,
        'categories': Category.objects.filter(is_active=True),
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'search': search,
    })


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    profile = request.user.profile

    # Access control
    if profile.is_user() and ticket.created_by != request.user:
        messages.error(request, 'Accès refusé.')
        return redirect('tickets:list')
    if profile.is_technician():
        try:
            tech = request.user.technician_profile
            if ticket.assigned_to and ticket.assigned_to != tech and ticket.status != Status.PENDING_ASSIGNMENT:
                messages.error(request, 'Accès refusé.')
                return redirect('tickets:list')
        except Exception:
            pass

    comment_form = CommentForm()
    attachment_form = AttachmentForm()

    return render(request, 'tickets/detail.html', {
        'ticket': ticket,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'history': ticket.history.all(),
        'comments': ticket.comments.all(),
        'attachments': ticket.attachments.all(),
        'technicians': Technician.objects.filter(is_available=True) if profile.is_admin() else None,
        'statuses': Status.choices,
        'priorities': Priority.choices,
    })


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.status = Status.OPEN

            # AI classification
            from ai_classifier.classifier import classify_incident
            result = classify_incident(ticket.title, ticket.description)
            if result:
                from categories.models import Category
                try:
                    suggested_cat = Category.objects.get(name__iexact=result.get('category', ''))
                    ticket.ai_suggested_category = suggested_cat
                    if not ticket.category:
                        ticket.category = suggested_cat
                except Category.DoesNotExist:
                    pass
                ticket.ai_suggested_priority = result.get('priority', '')
                if not ticket.priority or ticket.priority == Priority.MEDIUM:
                    ticket.priority = result.get('priority', Priority.MEDIUM)

            ticket.save()

            # Auto-assign
            _auto_assign(ticket)

            # File attachment
            if request.FILES.get('attachment'):
                f = request.FILES['attachment']
                Attachment.objects.create(
                    ticket=ticket, uploaded_by=request.user,
                    file=f, original_name=f.name
                )

            TicketHistory.objects.create(
                ticket=ticket, changed_by=request.user,
                field_changed='création', old_value='', new_value='Ticket créé'
            )
            send_ticket_notification(ticket, 'created')
            messages.success(request, f'Ticket #{ticket.id} créé avec succès.')
            return redirect('tickets:detail', pk=ticket.pk)
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/create.html', {'form': form})


def _auto_assign(ticket):
    """Auto-assign ticket to technician based on specialization and load."""
    if not ticket.category:
        return
    technicians = Technician.objects.filter(
        is_available=True,
        specializations=ticket.category
    ).order_by('assigned_tickets__id')

    for tech in technicians:
        if not tech.is_overloaded():
            ticket.assigned_to = tech
            ticket.status = Status.ASSIGNED
            ticket.save()
            TicketHistory.objects.create(
                ticket=ticket, changed_by=ticket.created_by,
                field_changed='affectation', old_value='',
                new_value=f'Auto-affecté à {tech.user.username}'
            )
            send_ticket_notification(ticket, 'assigned')
            break
    else:
        ticket.status = Status.PENDING_ASSIGNMENT
        ticket.save()


@login_required
def add_comment(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    profile = request.user.profile

    if profile.is_user() and ticket.created_by != request.user:
        messages.error(request, 'Accès refusé.')
        return redirect('tickets:list')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            # Only technicians/admins can post internal notes
            if not (profile.is_technician() or profile.is_admin()):
                comment.is_internal = False
            comment.save()
            send_ticket_notification(ticket, 'commented')
            messages.success(request, 'Commentaire ajouté.')
    return redirect('tickets:detail', pk=pk)


@login_required
@admin_or_technician_required
def update_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        old_status = ticket.get_status_display()
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Status.choices):
            ticket.status = new_status
            if new_status == Status.RESOLVED:
                ticket.resolved_at = timezone.now()
            ticket.save()
            TicketHistory.objects.create(
                ticket=ticket, changed_by=request.user,
                field_changed='statut', old_value=old_status,
                new_value=ticket.get_status_display()
            )
            send_ticket_notification(ticket, 'status_changed')
            messages.success(request, 'Statut mis à jour.')
    return redirect('tickets:detail', pk=pk)


@login_required
@admin_required
def assign_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        tech_id = request.POST.get('technician')
        old_assignee = str(ticket.assigned_to) if ticket.assigned_to else 'Non affecté'
        if tech_id:
            tech = get_object_or_404(Technician, pk=tech_id)
            ticket.assigned_to = tech
            ticket.status = Status.ASSIGNED
        else:
            ticket.assigned_to = None
            ticket.status = Status.PENDING_ASSIGNMENT
        ticket.save()
        TicketHistory.objects.create(
            ticket=ticket, changed_by=request.user,
            field_changed='affectation', old_value=old_assignee,
            new_value=str(ticket.assigned_to) if ticket.assigned_to else 'Non affecté'
        )
        send_ticket_notification(ticket, 'assigned')
        messages.success(request, 'Ticket affecté.')
    return redirect('tickets:detail', pk=pk)


@login_required
def close_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.created_by != request.user and not request.user.profile.is_admin():
        messages.error(request, 'Accès refusé.')
        return redirect('tickets:list')
    if request.method == 'POST' and ticket.status == Status.RESOLVED:
        ticket.status = Status.CLOSED
        ticket.save()
        TicketHistory.objects.create(
            ticket=ticket, changed_by=request.user,
            field_changed='statut', old_value='Résolu', new_value='Fermé'
        )
        messages.success(request, 'Ticket fermé.')
    return redirect('tickets:detail', pk=pk)
