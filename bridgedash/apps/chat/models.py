from django.db import models
from django.utils import timezone
from bridgedash.apps.deliveries.models import Delivery
from bridgedash.apps.users.models import User

class ChatRoom(models.Model):
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Chat for Delivery #{self.delivery.id}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text Message'),
        ('system', 'System Message'),
        ('price', 'Price Quote'),
        ('status', 'Status Update'),
    )
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"