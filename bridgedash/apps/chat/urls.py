from django.urls import path
from . import views

urlpatterns = [
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('api/messages/<int:room_id>/', views.get_chat_messages, name='get_chat_messages'),
    path('api/send-message/<int:room_id>/', views.send_message, name='send_message'),
    path('api/mark-read/<int:room_id>/', views.mark_messages_read, name='mark_messages_read'),
]