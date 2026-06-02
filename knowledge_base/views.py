from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import KnowledgeArticle
from accounts.decorators import admin_or_technician_required


def article_list(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    articles = KnowledgeArticle.objects.filter(is_published=True)
    if search:
        articles = articles.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )
    if category:
        articles = articles.filter(category_id=category)
    from categories.models import Category
    return render(request, 'knowledge_base/list.html', {
        'articles': articles,
        'search': search,
        'categories': Category.objects.filter(is_active=True),
    })


def article_detail(request, pk):
    article = get_object_or_404(KnowledgeArticle, pk=pk, is_published=True)
    article.views_count += 1
    article.save()
    return render(request, 'knowledge_base/detail.html', {'article': article})


@login_required
@admin_or_technician_required
def article_create(request):
    from categories.models import Category
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        cat_id = request.POST.get('category')
        if title and content:
            cat = Category.objects.get(pk=cat_id) if cat_id else None
            KnowledgeArticle.objects.create(
                title=title, content=content, category=cat, author=request.user
            )
            return redirect('knowledge_base:list')
    return render(request, 'knowledge_base/form.html', {
        'categories': Category.objects.filter(is_active=True),
        'title': 'Nouvel article',
    })


@login_required
@admin_or_technician_required
def article_edit(request, pk):
    article = get_object_or_404(KnowledgeArticle, pk=pk)
    from categories.models import Category
    if request.method == 'POST':
        article.title = request.POST.get('title', article.title)
        article.content = request.POST.get('content', article.content)
        cat_id = request.POST.get('category')
        article.category = Category.objects.get(pk=cat_id) if cat_id else None
        article.save()
        return redirect('knowledge_base:detail', pk=article.pk)
    return render(request, 'knowledge_base/form.html', {
        'article': article,
        'categories': Category.objects.filter(is_active=True),
        'title': 'Modifier l\'article',
    })
