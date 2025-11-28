
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

from .constants import GO_DIGITAL_TITLE, GO_DIGITAL_SUBTITLE,Hello_TITLE,Hello_SUBTITLE,Aicha,COM_AICHA,Edit,Delete,Search

def ui_constants(request):
    return {
        "GO_DIGITAL_TITLE": GO_DIGITAL_TITLE,
        "GO_DIGITAL_SUBTITLE": GO_DIGITAL_SUBTITLE,
        "Hello_TITLE": Hello_TITLE,
        "Hello_SUBTITLE": Hello_SUBTITLE,
        "Aicha":Aicha,
        "COM_AICHA":COM_AICHA,
        "Edit":Edit,
        "Delete":Delete,
        "Search":Search,
    }
