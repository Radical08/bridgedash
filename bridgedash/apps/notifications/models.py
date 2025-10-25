from django.db import models
from django.utils import timezone
from bridgedash.apps.users.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('delivery_request', 'New Delivery Request'),
        ('delivery_accepted', 'Delivery Accepted'),
        ('delivery_picked_up', 'Item Picked Up'),
        ('delivery_delivered', 'Item Delivered'),
        ('delivery_cancelled', 'Delivery Cancelled'),
        ('message', 'New Message'),
        ('system', 'System Notification'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    related_url = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"