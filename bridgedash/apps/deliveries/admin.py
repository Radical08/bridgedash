from django.contrib import admin
from django.utils.html import format_html
from .models import Delivery, DeliveryTracking

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'driver', 'status', 'total_price', 'created_at', 'delivery_status']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__user__username', 'driver__user__username', 'item_description']
    readonly_fields = ['created_at', 'accepted_at', 'picked_up_at', 'delivered_at']
    
    def delivery_status(self, obj):
        status_colors = {
            'pending': 'orange',
            'accepted': 'blue',
            'picked_up': 'purple',
            'in_transit': 'green',
            'delivered': 'green',
            'cancelled': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    delivery_status.short_description = 'Status'

@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ['delivery', 'driver_lat', 'driver_lng', 'timestamp']
    list_filter = ['timestamp']
    readonly_fields = ['timestamp']