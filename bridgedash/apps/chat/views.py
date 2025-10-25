from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json

from .models import ChatRoom, ChatMessage
from bridgedash.apps.deliveries.models import Delivery

@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    delivery = chat_room.delivery
    
    # Check if user has permission to access this chat
    if request.user not in [delivery.customer.user, delivery.driver.user] and request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    messages = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')[:100]
    
    context = {
        'room': chat_room,
        'delivery': delivery,
        'messages': messages,
        'ws_url': f"ws://{request.get_host()}/ws/chat/{room_id}/"
    }
    return render(request, 'chat/room.html', context)

@login_required
@require_http_methods(["GET"])
def get_chat_messages(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    delivery = chat_room.delivery
    
    # Check permissions
    if request.user not in [delivery.customer.user, delivery.driver.user] and request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    messages = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender': {
                'id': msg.sender.id,
                'username': msg.sender.username,
                'role': msg.sender.role
            },
            'message_type': msg.message_type,
            'timestamp': msg.timestamp.isoformat(),
            'is_read': msg.is_read
        })
    
    return JsonResponse({'messages': messages_data})

@login_required
@require_http_methods(["POST"])
def send_message(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    delivery = chat_room.delivery
    
    # Check permissions
    if request.user not in [delivery.customer.user, delivery.driver.user]:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Create message
        message = ChatMessage.objects.create(
            room=chat_room,
            sender=request.user,
            content=message_content,
            message_type='text'
        )
        
        # Mark as read for sender
        message.is_read = True
        message.save()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'role': request.user.role
                },
                'timestamp': message.timestamp.isoformat(),
                'message_type': message.message_type
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Failed to send message'}, status=500)

@login_required
@require_http_methods(["POST"])
def mark_messages_read(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    delivery = chat_room.delivery
    
    # Check permissions
    if request.user not in [delivery.customer.user, delivery.driver.user]:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Mark all unread messages from other users as read
    updated = ChatMessage.objects.filter(
        room=chat_room,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)
    
    return JsonResponse({'success': True, 'updated_count': updated})