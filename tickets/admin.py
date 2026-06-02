from django.contrib import admin
from .models import Ticket, Comment, Attachment, TicketHistory


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'priority', 'status', 'created_by', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'category']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal']


admin.site.register(Attachment)
admin.site.register(TicketHistory)
