from django.db import models
from django.contrib.auth.models import User
from categories.models import Category


class KnowledgeArticle(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titre')
    content = models.TextField(verbose_name='Contenu / Solution')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='articles', verbose_name='Catégorie'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Auteur')
    views_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True, verbose_name='Publié')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Article de base de connaissances'
        verbose_name_plural = 'Articles de base de connaissances'
        ordering = ['-views_count', '-created_at']

    def __str__(self):
        return self.title
