from django.contrib import admin
from .models import Technician

@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_available', 'max_tickets']
    list_editable = ['is_available']
    filter_horizontal = ['specializations']
