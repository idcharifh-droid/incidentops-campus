from .models import Notification


def send_ticket_notification(ticket, event_type):
    """Create in-app notifications for relevant users."""
    recipients = set()

    if event_type == 'created':
        # Notify admins
        from django.contrib.auth.models import User
        admins = User.objects.filter(profile__role='admin')
        for admin in admins:
            recipients.add((admin, 'ticket_created',
                           f'Nouveau ticket #{ticket.id}',
                           f'{ticket.created_by.get_full_name() or ticket.created_by.username} a créé : {ticket.title}'))

    elif event_type == 'assigned':
        if ticket.assigned_to:
            recipients.add((ticket.assigned_to.user, 'ticket_assigned',
                           f'Ticket #{ticket.id} vous a été affecté',
                           f'Nouveau ticket à traiter : {ticket.title}'))
        # Notify creator
        recipients.add((ticket.created_by, 'ticket_assigned',
                       f'Ticket #{ticket.id} affecté à un technicien',
                       f'Votre ticket "{ticket.title}" est en cours de traitement.'))

    elif event_type == 'status_changed':
        recipients.add((ticket.created_by, 'status_changed',
                       f'Ticket #{ticket.id} mis à jour',
                       f'Statut : {ticket.get_status_display()}'))

    elif event_type == 'commented':
        recipients.add((ticket.created_by, 'comment_added',
                       f'Nouveau commentaire sur #{ticket.id}',
                       f'Un commentaire a été ajouté à votre ticket "{ticket.title}"'))
        if ticket.assigned_to:
            recipients.add((ticket.assigned_to.user, 'comment_added',
                           f'Nouveau commentaire sur #{ticket.id}',
                           f'Commentaire sur : {ticket.title}'))

    for recipient, ntype, title, message in recipients:
        Notification.objects.create(
            recipient=recipient,
            notification_type=ntype,
            title=title,
            message=message,
            ticket_id=ticket.id
        )
