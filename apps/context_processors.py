
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

from .constants import GO_DIGITAL_TITLE, GO_DIGITAL_SUBTITLE,Hello_TITLE,Hello_SUBTITLE,Aicha,COM_AICHA,Edit,Delete,Search,Login,Add_Order,Add_New_Order,The_list_of_all_products,Products
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
        "Login":Login,
        "Add Order":Add_Order,
        "Add a New Order":Add_New_Order,
        "The list of all products":The_list_of_all_products,
        "Products":Products,
    }
