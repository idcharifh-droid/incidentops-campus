from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category
from accounts.decorators import admin_required


@login_required
@admin_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/list.html', {'categories': categories})


@login_required
@admin_required
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        icon = request.POST.get('icon', 'bi-tag')
        color = request.POST.get('color', 'primary')
        if name:
            Category.objects.create(name=name, description=description, icon=icon, color=color)
            messages.success(request, 'Catégorie créée.')
            return redirect('categories:list')
    return render(request, 'categories/form.html', {'title': 'Nouvelle catégorie'})


@login_required
@admin_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name', category.name)
        category.description = request.POST.get('description', '')
        category.icon = request.POST.get('icon', 'bi-tag')
        category.color = request.POST.get('color', 'primary')
        category.save()
        messages.success(request, 'Catégorie mise à jour.')
        return redirect('categories:list')
    return render(request, 'categories/form.html', {'category': category, 'title': 'Modifier la catégorie'})


@login_required
@admin_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Catégorie supprimée.')
    return redirect('categories:list')
