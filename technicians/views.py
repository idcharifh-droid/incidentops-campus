from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Technician
from accounts.models import UserProfile, Role
from accounts.decorators import admin_required


@login_required
@admin_required
def technician_list(request):
    technicians = Technician.objects.select_related('user__profile').prefetch_related('specializations')
    return render(request, 'technicians/list.html', {'technicians': technicians})


@login_required
@admin_required
def technician_create(request):
    # Show users with technician role who don't have a Technician record yet
    existing_tech_user_ids = Technician.objects.values_list('user_id', flat=True)
    available_users = User.objects.filter(
        profile__role=Role.TECHNICIAN
    ).exclude(id__in=existing_tech_user_ids)

    if request.method == 'POST':
        user_id = request.POST.get('user')
        user = get_object_or_404(User, pk=user_id)
        tech, created = Technician.objects.get_or_create(user=user)
        if created:
            messages.success(request, f'Technicien {user.username} créé.')
        return redirect('technicians:list')
    return render(request, 'technicians/form.html', {'available_users': available_users})


@login_required
@admin_required
def technician_edit(request, pk):
    technician = get_object_or_404(Technician, pk=pk)
    from categories.models import Category
    all_categories = Category.objects.filter(is_active=True)
    if request.method == 'POST':
        technician.is_available = request.POST.get('is_available') == 'on'
        technician.max_tickets = int(request.POST.get('max_tickets', 10))
        spec_ids = request.POST.getlist('specializations')
        technician.specializations.set(spec_ids)
        technician.save()
        messages.success(request, 'Technicien mis à jour.')
        return redirect('technicians:list')
    return render(request, 'technicians/edit.html', {
        'technician': technician, 'all_categories': all_categories
    })
