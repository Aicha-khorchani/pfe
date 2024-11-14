from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from .models import Stock  
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Stock)
def stock_quantity_notification(sender, instance, **kwargs):
    if instance.quantity_available < 10:
        # Filter only users with type 'customuser' or 'admin'
        users_to_notify = User.objects.filter(user_type__in=['customuser', 'admin'])
        
        # Create a notification for each user
        for user in users_to_notify:
            Notification.objects.create(
                user=user,
                message=f"Stock low for {instance.item.product_name} - {instance.item_variant.variant_name}. Only {instance.quantity_available} left."
            )
