from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    TYPES = [
        ('ticket_created', 'Ticket créé'),
        ('ticket_assigned', 'Ticket affecté'),
        ('status_changed', 'Statut changé'),
        ('ticket_resolved', 'Ticket résolu'),
        ('comment_added', 'Commentaire ajouté'),
        ('info_requested', 'Information demandée'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    ticket_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification pour {self.recipient.username}: {self.title}"
