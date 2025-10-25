from django.db import models
from django.utils import timezone
from bridgedash.apps.users.models import User, Customer, Driver

class Delivery(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Acceptance'),
        ('accepted', 'Accepted by Driver'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    CANCELLATION_REASONS = (
        ('customer_not_available', 'Customer Not Available'),
        ('wrong_address', 'Wrong Address'),
        ('item_not_found', 'Item Not Found'),
        ('driver_unavailable', 'Driver Unavailable'),
        ('other', 'Other'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Delivery details
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    item_description = models.TextField()
    
    # Location coordinates
    pickup_lat = models.FloatField(default=-22.2167)
    pickup_lng = models.FloatField(default=30.0000)
    delivery_lat = models.FloatField(default=-22.2167)
    delivery_lng = models.FloatField(default=30.0000)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    accepted_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Pricing
    base_fare = models.DecimalField(max_digits=8, decimal_places=2, default=5.00)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    per_km_rate = models.DecimalField(max_digits=6, decimal_places=2, default=2.00)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Cancellation
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_deliveries')
    cancellation_reason = models.CharField(max_length=50, choices=CANCELLATION_REASONS, null=True, blank=True)
    cancellation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    def calculate_price(self):
        from django.conf import settings
        self.total_price = self.base_fare + (self.distance_km * self.per_km_rate)
        self.commission_amount = self.total_price * settings.BRIDGEDASH_COMMISSION_RATE
        self.save()
    
    def __str__(self):
        return f"Delivery #{self.id} - {self.customer.user.username}"

class DeliveryTracking(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
    driver_lat = models.FloatField()
    driver_lng = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']