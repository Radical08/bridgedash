import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, ChatMessage
from bridgedash.apps.deliveries.models import Delivery
from bridgedash.apps.notifications.models import Notification

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send last 50 messages to the new connection
        messages = await self.get_room_messages()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': messages
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = text_data_json['message']
            sender = self.scope['user']
            
            # Save message to database
            saved_message = await self.save_message(message, sender)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender.username,
                    'sender_id': sender.id,
                    'timestamp': saved_message['timestamp'],
                    'message_id': saved_message['id']
                }
            )
            
            # Send notification to the other user
            await self.send_notification(sender, message)

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))

    async def chat_history(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': event['messages']
        }))

    @database_sync_to_async
    def get_room_messages(self):
        try:
            room = ChatRoom.objects.get(id=self.room_name)
            messages = ChatMessage.objects.filter(room=room).select_related('sender').order_by('timestamp')[:50]
            
            return [
                {
                    'id': msg.id,
                    'message': msg.content,
                    'sender': msg.sender.username,
                    'sender_id': msg.sender.id,
                    'timestamp': msg.timestamp.isoformat(),
                    'message_type': msg.message_type
                }
                for msg in messages
            ]
        except ChatRoom.DoesNotExist:
            return []

    @database_sync_to_async
    def save_message(self, message, sender):
        try:
            room = ChatRoom.objects.get(id=self.room_name)
            chat_message = ChatMessage.objects.create(
                room=room,
                sender=sender,
                content=message,
                message_type='text'
            )
            
            # Mark as read for the sender immediately
            chat_message.is_read = True
            chat_message.save()
            
            return {
                'id': chat_message.id,
                'timestamp': chat_message.timestamp.isoformat()
            }
        except ChatRoom.DoesNotExist:
            return {'id': None, 'timestamp': timezone.now().isoformat()}

    @database_sync_to_async
    def send_notification(self, sender, message):
        try:
            room = ChatRoom.objects.get(id=self.room_name)
            delivery = room.delivery
            
            # Determine who to notify (the other user in the chat)
            if sender == delivery.customer.user:
                # Notify driver
                notify_user = delivery.driver.user if delivery.driver else None
            else:
                # Notify customer
                notify_user = delivery.customer.user
            
            if notify_user and notify_user != sender:
                Notification.objects.create(
                    user=notify_user,
                    notification_type='message',
                    title='New Message',
                    message=f'New message in delivery #{delivery.id}: {message[:50]}...',
                    related_url=f'/deliveries/customer/active/{delivery.id}/'
                )
        except ChatRoom.DoesNotExist:
            pass