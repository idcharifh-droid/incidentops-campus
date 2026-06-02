import csv
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count
from tickets.models import Ticket, Status, Priority
from accounts.decorators import admin_required


@login_required
@admin_required
def reports_index(request):
    by_category = (
        Ticket.objects.values('category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    by_priority = (
        Ticket.objects.values('priority')
        .annotate(count=Count('id'))
    )
    by_status = (
        Ticket.objects.values('status')
        .annotate(count=Count('id'))
    )
    return render(request, 'reports/index.html', {
        'by_category': list(by_category),
        'by_priority': list(by_priority),
        'by_status': list(by_status),
        'total': Ticket.objects.count(),
    })


@login_required
@admin_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="incidents_export.csv"'
    response.write('\ufeff')  # BOM for Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'ID', 'Titre', 'Catégorie', 'Priorité', 'Statut',
        'Créé par', 'Affecté à', 'Date création', 'Date résolution', 'Durée (h)'
    ])

    for t in Ticket.objects.select_related('category', 'created_by', 'assigned_to__user').all():
        writer.writerow([
            t.id,
            t.title,
            t.category.name if t.category else 'N/A',
            t.get_priority_display(),
            t.get_status_display(),
            t.created_by.get_full_name() or t.created_by.username,
            t.assigned_to.user.get_full_name() if t.assigned_to else 'Non affecté',
            t.created_at.strftime('%d/%m/%Y %H:%M'),
            t.resolved_at.strftime('%d/%m/%Y %H:%M') if t.resolved_at else '',
            t.resolution_time() or '',
        ])

    return response


@login_required
@admin_required
def export_json(request):
    tickets = []
    for t in Ticket.objects.select_related('category', 'created_by', 'assigned_to__user').all():
        tickets.append({
            'id': t.id,
            'title': t.title,
            'category': t.category.name if t.category else None,
            'priority': t.priority,
            'status': t.status,
            'created_by': t.created_by.username,
            'assigned_to': t.assigned_to.user.username if t.assigned_to else None,
            'created_at': t.created_at.isoformat(),
            'resolved_at': t.resolved_at.isoformat() if t.resolved_at else None,
        })
    response = HttpResponse(
        json.dumps({'tickets': tickets, 'total': len(tickets)}, ensure_ascii=False, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename="incidents_export.json"'
    return response
