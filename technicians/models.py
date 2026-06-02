from django.db import models
from django.contrib.auth.models import User
from categories.models import Category


class Technician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician_profile')
    specializations = models.ManyToManyField(Category, blank=True, verbose_name='Spécialisations')
    is_available = models.BooleanField(default=True, verbose_name='Disponible')
    max_tickets = models.IntegerField(default=10, verbose_name='Tickets max simultanés')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Technicien'
        verbose_name_plural = 'Techniciens'

    def __str__(self):
        return f"Technicien: {self.user.get_full_name() or self.user.username}"

    def active_ticket_count(self):
        return self.assigned_tickets.exclude(status__in=['resolved', 'closed', 'cancelled']).count()

    def is_overloaded(self):
        return self.active_ticket_count() >= self.max_tickets
