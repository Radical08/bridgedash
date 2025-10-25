from django.urls import re_path
from bridgedash.apps.chat import consumers as chat_consumers
from bridgedash.apps.deliveries import consumers as delivery_consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', chat_consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/delivery/(?P<delivery_id>\w+)/$', delivery_consumers.DeliveryConsumer.as_asgi()),
    re_path(r'ws/notifications/$', delivery_consumers.NotificationConsumer.as_asgi()),
]