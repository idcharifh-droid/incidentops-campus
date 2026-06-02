from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, AdminUserCreateForm
from .models import UserProfile, Role
from .decorators import admin_required


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} ! Votre compte a été créé.')
            return redirect('dashboard:index')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenue, {user.first_name or user.username} !')
            return redirect(request.GET.get('next', 'dashboard:index'))
        else:
            messages.error(request, 'Identifiants incorrects.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('home')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
@admin_required
def user_list_view(request):
    search = request.GET.get('search', '')
    role = request.GET.get('role', '')
    users = User.objects.select_related('profile').all()
    if search:
        users = users.filter(
            Q(username__icontains=search) | Q(email__icontains=search) |
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )
    if role:
        users = users.filter(profile__role=role)
    return render(request, 'accounts/user_list.html', {
        'users': users, 'search': search, 'role': role, 'roles': Role.choices
    })


@login_required
@admin_required
def user_create_view(request):
    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Utilisateur {user.username} créé avec succès.')
            return redirect('accounts:user_list')
    else:
        form = AdminUserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Créer un utilisateur'})


@login_required
@admin_required
def user_edit_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=user)
        role = request.POST.get('role')
        if form.is_valid():
            profile.role = role
            form.save()
            messages.success(request, 'Utilisateur mis à jour.')
            return redirect('accounts:user_list')
    else:
        form = ProfileUpdateForm(instance=profile, user=user)
    return render(request, 'accounts/user_edit.html', {
        'form': form, 'target_user': user, 'roles': Role.choices
    })


@login_required
@admin_required
def user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        status = 'activé' if user.is_active else 'désactivé'
        messages.success(request, f'Compte {user.username} {status}.')
    return redirect('accounts:user_list')
