
from .models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        unread_count = unread_notifications.count()
        return {
            'unread_notifications': unread_notifications,
            'unread_count': unread_count,
        }
    return {}
