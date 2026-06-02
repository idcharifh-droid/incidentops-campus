from django.db import models
from django.contrib.auth.models import User
from categories.models import Category
from technicians.models import Technician
import os


class Priority(models.TextChoices):
    LOW = 'low', 'Faible'
    MEDIUM = 'medium', 'Moyenne'
    HIGH = 'high', 'Élevée'
    CRITICAL = 'critical', 'Critique'


class Status(models.TextChoices):
    OPEN = 'open', 'Ouvert'
    PENDING_ASSIGNMENT = 'pending_assignment', 'En attente d\'affectation'
    ASSIGNED = 'assigned', 'Affecté'
    IN_PROGRESS = 'in_progress', 'En cours de traitement'
    PENDING_INFO = 'pending_info', 'En attente d\'information'
    RESOLVED = 'resolved', 'Résolu'
    CLOSED = 'closed', 'Fermé'
    CANCELLED = 'cancelled', 'Annulé'


def attachment_upload_path(instance, filename):
    return f'tickets/{instance.ticket.id}/{filename}'


class Ticket(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='tickets',
        verbose_name='Catégorie'
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM,
        verbose_name='Priorité'
    )
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.OPEN,
        verbose_name='Statut'
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tickets_created',
        verbose_name='Créé par'
    )
    assigned_to = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tickets', verbose_name='Affecté à'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Dernière modification')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='Date de résolution')
    ai_suggested_category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ai_suggested_tickets', verbose_name='Catégorie suggérée par IA'
    )
    ai_suggested_priority = models.CharField(
        max_length=20, choices=Priority.choices, blank=True,
        verbose_name='Priorité suggérée par IA'
    )

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title}"

    def is_open(self):
        return self.status not in [Status.RESOLVED, Status.CLOSED, Status.CANCELLED]

    def get_priority_badge(self):
        badges = {
            'low': 'success',
            'medium': 'warning',
            'high': 'orange',
            'critical': 'danger',
        }
        return badges.get(self.priority, 'secondary')

    def get_status_badge(self):
        badges = {
            'open': 'primary',
            'pending_assignment': 'warning',
            'assigned': 'info',
            'in_progress': 'primary',
            'pending_info': 'warning',
            'resolved': 'success',
            'closed': 'secondary',
            'cancelled': 'dark',
        }
        return badges.get(self.status, 'secondary')

    def resolution_time(self):
        if self.resolved_at:
            delta = self.resolved_at - self.created_at
            hours = delta.total_seconds() / 3600
            return round(hours, 1)
        return None


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(verbose_name='Contenu')
    is_internal = models.BooleanField(default=False, verbose_name='Note interne (technicien)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['created_at']

    def __str__(self):
        return f"Commentaire de {self.author.username} sur #{self.ticket.id}"


def validate_file_extension(value):
    from django.core.exceptions import ValidationError
    from django.conf import settings
    ext = os.path.splitext(value.name)[1].lower()
    allowed = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS',
                      ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.docx'])
    if ext not in allowed:
        raise ValidationError(f'Extension non autorisée. Extensions permises : {", ".join(allowed)}')


class Attachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=attachment_upload_path, validators=[validate_file_extension])
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pièce jointe'
        verbose_name_plural = 'Pièces jointes'

    def __str__(self):
        return self.original_name

    def save(self, *args, **kwargs):
        if not self.original_name:
            self.original_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)


class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    field_changed = models.CharField(max_length=50)
    old_value = models.CharField(max_length=200, blank=True)
    new_value = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historique'
        verbose_name_plural = 'Historiques'
        ordering = ['-timestamp']

    def __str__(self):
        return f"#{self.ticket.id}: {self.field_changed} → {self.new_value}"
