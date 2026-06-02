from .models import Notification


def unread_notifications(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(recipient=request.user, is_read=False)
        return {
            'unread_notifications': unread[:5],
            'unread_count': unread.count(),
        }
    return {'unread_notifications': [], 'unread_count': 0}
