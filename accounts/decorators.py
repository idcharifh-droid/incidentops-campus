from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.is_admin():
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Accès refusé. Réservé aux administrateurs.')
        return redirect('dashboard:index')
    return wrapper


def technician_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and (
            request.user.profile.is_technician() or request.user.profile.is_admin()
        ):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Accès refusé. Réservé aux techniciens.')
        return redirect('dashboard:index')
    return wrapper


def admin_or_technician_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and (
            request.user.profile.is_admin() or request.user.profile.is_technician()
        ):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Accès refusé.')
        return redirect('dashboard:index')
    return wrapper
