import logging
from django.conf import settings
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from bridgedash.apps.users.models import User

logger = logging.getLogger(__name__)

class NotificationUtils:
    """Utility class for handling notifications across the application"""
    
    @staticmethod
    def create_notification(user, notification_type, title, message, related_url=None):
        """
        Create a new notification for a user
        """
        try:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_url=related_url
            )
            
            # Send real-time notification via WebSocket
            NotificationUtils.send_realtime_notification(user, notification)
            
            return notification
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def send_realtime_notification(user, notification):
        """
        Send real-time notification via WebSocket
        """
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    "type": "send_notification",
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "related_url": notification.related_url or ""
                }
            )
        except Exception as e:
            logger.error(f"Error sending real-time notification: {e}")
    
    @staticmethod
    def notify_delivery_request(delivery):
        """
        Notify all online drivers about a new delivery request
        """
        try:
            online_drivers = User.objects.filter(
                role='driver',
                driver__is_online=True,
                status='active'
            )
            
            for driver in online_drivers:
                NotificationUtils.create_notification(
                    user=driver,
                    notification_type='delivery_request',
                    title='New Delivery Request',
                    message=f'New delivery from {delivery.customer.user.username} - ${delivery.total_price}',
                    related_url=f'/deliveries/driver/'
                )
            
            return True
        except Exception as e:
            logger.error(f"Error notifying drivers: {e}")
            return False
    
    @staticmethod
    def notify_delivery_accepted(delivery):
        """
        Notify customer that their delivery was accepted
        """
        try:
            NotificationUtils.create_notification(
                user=delivery.customer.user,
                notification_type='delivery_accepted',
                title='Delivery Accepted!',
                message=f'Driver {delivery.driver.user.username} has accepted your delivery',
                related_url=f'/deliveries/customer/active/{delivery.id}/'
            )
            return True
        except Exception as e:
            logger.error(f"Error notifying delivery acceptance: {e}")
            return False
    
    @staticmethod
    def notify_delivery_status_update(delivery, old_status, new_status):
        """
        Notify about delivery status changes
        """
        try:
            status_messages = {
                'picked_up': 'Driver has picked up your item',
                'in_transit': 'Driver is on the way with your delivery',
                'delivered': 'Delivery completed successfully'
            }
            
            message = status_messages.get(new_status, f'Delivery status updated to {new_status}')
            
            # Notify customer
            NotificationUtils.create_notification(
                user=delivery.customer.user,
                notification_type=f'delivery_{new_status}',
                title=f'Delivery {new_status.replace("_", " ").title()}',
                message=message,
                related_url=f'/deliveries/customer/active/{delivery.id}/'
            )
            
            return True
        except Exception as e:
            logger.error(f"Error notifying status update: {e}")
            return False
    
    @staticmethod
    def notify_delivery_cancelled(delivery, cancelled_by, reason):
        """
        Notify about delivery cancellation
        """
        try:
            if cancelled_by.role == 'customer':
                # Notify driver
                if delivery.driver:
                    NotificationUtils.create_notification(
                        user=delivery.driver.user,
                        notification_type='delivery_cancelled',
                        title='Delivery Cancelled',
                        message=f'Delivery #{delivery.id} was cancelled by customer. Reason: {reason}',
                        related_url=f'/deliveries/driver/'
                    )
            else:
                # Notify customer
                NotificationUtils.create_notification(
                    user=delivery.customer.user,
                    notification_type='delivery_cancelled',
                    title='Delivery Cancelled',
                    message=f'Delivery #{delivery.id} was cancelled by driver. Reason: {reason}',
                    related_url=f'/deliveries/customer/'
                )
            
            return True
        except Exception as e:
            logger.error(f"Error notifying cancellation: {e}")
            return False
    
    @staticmethod
    def notify_new_chat_message(chat_message):
        """
        Notify about new chat messages
        """
        try:
            delivery = chat_message.room.delivery
            sender = chat_message.sender
            
            # Determine who to notify (the other user in the chat)
            if sender == delivery.customer.user:
                notify_user = delivery.driver.user if delivery.driver else None
            else:
                notify_user = delivery.customer.user
            
            if notify_user and notify_user != sender:
                NotificationUtils.create_notification(
                    user=notify_user,
                    notification_type='message',
                    title='New Message',
                    message=f'New message in delivery #{delivery.id}: {chat_message.content[:50]}...',
                    related_url=f'/chat/room/{chat_message.room.id}/'
                )
            
            return True
        except Exception as e:
            logger.error(f"Error notifying chat message: {e}")
            return False
    
    @staticmethod
    def get_unread_count(user):
        """
        Get count of unread notifications for a user
        """
        try:
            return Notification.objects.filter(user=user, is_read=False).count()
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0
    
    @staticmethod
    def mark_all_read(user):
        """
        Mark all notifications as read for a user
        """
        try:
            updated = Notification.objects.filter(user=user, is_read=False).update(is_read=True)
            return updated
        except Exception as e:
            logger.error(f"Error marking notifications as read: {e}")
            return 0
    
    @staticmethod
    def cleanup_old_notifications(days=30):
        """
        Clean up notifications older than specified days
        """
        try:
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            deleted_count, _ = Notification.objects.filter(
                created_at__lt=cutoff_date
            ).delete()
            
            logger.info(f"Cleaned up {deleted_count} old notifications")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {e}")
            return 0

# Global utility instance
notification_utils = NotificationUtils()