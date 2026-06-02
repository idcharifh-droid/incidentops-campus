from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket, Status, Priority


@login_required
def dashboard_index(request):
    profile = request.user.profile
    if profile.is_admin():
        return admin_dashboard(request)
    elif profile.is_technician():
        return technician_dashboard(request)
    else:
        return user_dashboard(request)


@login_required
def user_dashboard(request):
    user = request.user
    tickets = Ticket.objects.filter(created_by=user)
    ctx = {
        'total': tickets.count(),
        'open': tickets.filter(status=Status.OPEN).count(),
        'in_progress': tickets.filter(status__in=[Status.ASSIGNED, Status.IN_PROGRESS]).count(),
        'resolved': tickets.filter(status=Status.RESOLVED).count(),
        'closed': tickets.filter(status=Status.CLOSED).count(),
        'recent_tickets': tickets.order_by('-created_at')[:5],
        'critical': tickets.filter(priority=Priority.CRITICAL, status__in=[
            Status.OPEN, Status.ASSIGNED, Status.IN_PROGRESS
        ]).count(),
    }
    return render(request, 'dashboard/user.html', ctx)


@login_required
def technician_dashboard(request):
    try:
        tech = request.user.technician_profile
    except Exception:
        return user_dashboard(request)

    my_tickets = Ticket.objects.filter(assigned_to=tech)
    unassigned = Ticket.objects.filter(status=Status.PENDING_ASSIGNMENT)

    resolved = my_tickets.filter(status=Status.RESOLVED, resolved_at__isnull=False)
    avg_hours = None
    if resolved.exists():
        total_hours = sum(
            (t.resolved_at - t.created_at).total_seconds() / 3600
            for t in resolved if t.resolved_at
        )
        avg_hours = round(total_hours / resolved.count(), 1)

    ctx = {
        'my_tickets': my_tickets.exclude(status__in=[Status.CLOSED, Status.CANCELLED]).count(),
        'pending': my_tickets.filter(status__in=[Status.ASSIGNED, Status.PENDING_ASSIGNMENT]).count(),
        'critical': my_tickets.filter(priority=Priority.CRITICAL).exclude(
            status__in=[Status.RESOLVED, Status.CLOSED]
        ).count(),
        'resolved_count': my_tickets.filter(status=Status.RESOLVED).count(),
        'avg_resolution_hours': avg_hours,
        'unassigned_count': unassigned.count(),
        'recent_tickets': my_tickets.order_by('-created_at')[:5],
        'unassigned_tickets': unassigned.order_by('-created_at')[:5],
        'technician': tech,
    }
    return render(request, 'dashboard/technician.html', ctx)


@login_required
def admin_dashboard(request):
    all_tickets = Ticket.objects.all()
    last_30 = timezone.now() - timedelta(days=30)

    # By category
    by_category = (
        Ticket.objects.values('category__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )

    # By priority
    by_priority = (
        Ticket.objects.values('priority')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # By status
    by_status = (
        Ticket.objects.values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Top technicians
    from technicians.models import Technician
    technicians = Technician.objects.annotate(
        ticket_count=Count('assigned_tickets')
    ).order_by('-ticket_count')[:5]

    # Average resolution time
    resolved = all_tickets.filter(status=Status.RESOLVED, resolved_at__isnull=False)
    avg_hours = None
    if resolved.exists():
        total_hours = sum(
            (t.resolved_at - t.created_at).total_seconds() / 3600
            for t in resolved if t.resolved_at
        )
        avg_hours = round(total_hours / resolved.count(), 1)

    ctx = {
        'total': all_tickets.count(),
        'open': all_tickets.filter(status=Status.OPEN).count(),
        'in_progress': all_tickets.filter(status=Status.IN_PROGRESS).count(),
        'resolved': all_tickets.filter(status=Status.RESOLVED).count(),
        'critical': all_tickets.filter(
            priority=Priority.CRITICAL
        ).exclude(status__in=[Status.RESOLVED, Status.CLOSED]).count(),
        'pending_assignment': all_tickets.filter(status=Status.PENDING_ASSIGNMENT).count(),
        'recent_tickets': all_tickets.order_by('-created_at')[:8],
        'by_category': list(by_category),
        'by_priority': list(by_priority),
        'by_status': list(by_status),
        'top_technicians': technicians,
        'avg_resolution_hours': avg_hours,
        'tickets_last_30': all_tickets.filter(created_at__gte=last_30).count(),
    }
    return render(request, 'dashboard/admin.html', ctx)
