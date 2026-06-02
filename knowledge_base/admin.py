from django.contrib import admin
from .models import KnowledgeArticle

@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'views_count', 'is_published']
    list_editable = ['is_published']
