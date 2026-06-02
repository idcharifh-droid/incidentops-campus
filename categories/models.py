from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nom')
    description = models.TextField(blank=True, verbose_name='Description')
    icon = models.CharField(max_length=50, default='bi-tag', verbose_name='Icône Bootstrap')
    color = models.CharField(max_length=20, default='primary', verbose_name='Couleur')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def get_default_categories(cls):
        return [
            ('Réseau', 'bi-wifi', 'primary'),
            ('Matériel', 'bi-pc-display', 'secondary'),
            ('Logiciel', 'bi-code-square', 'info'),
            ('Compte utilisateur', 'bi-person-lock', 'warning'),
            ('Sécurité', 'bi-shield-exclamation', 'danger'),
            ('Plateforme pédagogique', 'bi-mortarboard', 'success'),
            ('Serveur', 'bi-server', 'dark'),
            ('Imprimante', 'bi-printer', 'secondary'),
            ('Vidéoprojecteur', 'bi-projector', 'info'),
            ('Autre', 'bi-question-circle', 'secondary'),
        ]
