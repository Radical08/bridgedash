from django.urls import path
from . import views

urlpatterns = [
    # Customer URLs
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/new/', views.new_delivery, name='new_delivery'),
    path('customer/active/<int:delivery_id>/', views.active_delivery, name='active_delivery'),
    path('customer/cancel/<int:delivery_id>/', views.cancel_delivery, name='cancel_delivery'),
    path('customer/history/', views.order_history, name='order_history'),
    path('customer/status/<int:delivery_id>/', views.get_delivery_status, name='get_delivery_status'),
    
    # Driver URLs
    path('driver/', views.driver_dashboard, name='driver_dashboard'),
    path('driver/online-toggle/', views.driver_online_toggle, name='driver_online_toggle'),
    path('driver/accept-delivery/<int:delivery_id>/', views.accept_delivery, name='accept_delivery'),
    path('driver/update-status/<int:delivery_id>/', views.update_delivery_status, name='update_delivery_status'),
    path('driver/update-location/', views.update_driver_location, name='update_driver_location'),
    path('driver/earnings/', views.driver_earnings, name='driver_earnings'),
]