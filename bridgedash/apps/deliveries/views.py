from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import logging

from .models import Delivery, DeliveryTracking
from .forms import DeliveryRequestForm, DeliveryCancelForm
from bridgedash.apps.chat.models import ChatRoom, ChatMessage
from bridgedash.apps.notifications.models import Notification
from bridgedash.apps.users.models import Driver
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)
geolocator = Nominatim(user_agent="bridgedash")

@login_required
def customer_dashboard(request):
    if request.user.role != 'customer':
        messages.error(request, "Access denied. Customer area only.")
        return redirect('dashboard')
    
    customer = request.user.customer
    active_delivery = Delivery.objects.filter(
        customer=customer, 
        status__in=['pending', 'accepted', 'picked_up', 'in_transit']
    ).first()
    
    recent_deliveries = Delivery.objects.filter(customer=customer).order_by('-created_at')[:10]
    
    context = {
        'active_delivery': active_delivery,
        'recent_deliveries': recent_deliveries,
    }
    return render(request, 'customer/dashboard.html', context)

@login_required
def new_delivery(request):
    if request.user.role != 'customer':
        messages.error(request, "Access denied. Customer area only.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DeliveryRequestForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create delivery
                    delivery = form.save(commit=False)
                    delivery.customer = request.user.customer
                    
                    # Calculate coordinates (simplified - in production use proper geocoding)
                    delivery.pickup_lat = -22.2167  # Beitbridge coordinates
                    delivery.pickup_lng = 30.0000
                    delivery.delivery_lat = -22.2167
                    delivery.delivery_lng = 30.0000
                    
                    # Calculate distance (simplified)
                    delivery.distance_km = 5.0  # Default distance
                    
                    # Calculate price
                    delivery.calculate_price()
                    delivery.save()
                    
                    # Create chat room
                    chat_room = ChatRoom.objects.create(delivery=delivery)
                    
                    # Add system message
                    ChatMessage.objects.create(
                        room=chat_room,
                        sender=request.user,
                        message_type='system',
                        content=f"Delivery request created. Waiting for driver acceptance..."
                    )
                    
                    # Notify online drivers
                    online_drivers = Driver.objects.filter(is_online=True, user__status='active')
                    
                    for driver in online_drivers:
                        Notification.objects.create(
                            user=driver.user,
                            notification_type='delivery_request',
                            title='New Delivery Request',
                            message=f'New delivery from {delivery.customer.user.username}',
                            related_url=f'/deliveries/driver/'
                        )
                    
                    messages.success(request, '🚀 Delivery request created! Drivers are being notified.')
                    return redirect('customer_dashboard')
                    
            except Exception as e:
                logger.error(f"Error creating delivery: {e}")
                messages.error(request, 'Error creating delivery request. Please try again.')
    else:
        form = DeliveryRequestForm()
    
    return render(request, 'customer/new_delivery.html', {'form': form})

@login_required
def active_delivery(request, delivery_id):
    if request.user.role != 'customer':
        messages.error(request, "Access denied. Customer area only.")
        return redirect('dashboard')
    
    delivery = get_object_or_404(Delivery, id=delivery_id, customer=request.user.customer)
    chat_room = ChatRoom.objects.get(delivery=delivery)
    messages_list = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')
    
    # Get latest tracking info
    latest_tracking = DeliveryTracking.objects.filter(delivery=delivery).order_by('-timestamp').first()
    
    context = {
        'delivery': delivery,
        'chat_room': chat_room,
        'messages': messages_list,
        'latest_tracking': latest_tracking,
    }
    return render(request, 'customer/active_delivery.html', context)

@login_required
def cancel_delivery(request, delivery_id):
    if request.user.role != 'customer':
        messages.error(request, "Access denied. Customer area only.")
        return redirect('dashboard')
    
    delivery = get_object_or_404(Delivery, id=delivery_id, customer=request.user.customer)
    
    # Check if delivery can be cancelled
    if delivery.status not in ['pending', 'accepted']:
        messages.error(request, "This delivery cannot be cancelled at this stage.")
        return redirect('active_delivery', delivery_id=delivery_id)
    
    if request.method == 'POST':
        form = DeliveryCancelForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Update delivery status
                    delivery.status = 'cancelled'
                    delivery.cancelled_by = request.user
                    delivery.cancellation_reason = form.cleaned_data['reason']
                    
                    # Apply cancellation fee if driver already accepted
                    if delivery.status == 'accepted':
                        delivery.cancellation_fee = delivery.total_price * 0.5  # 50% fee
                    
                    delivery.save()
                    
                    # Add system message
                    chat_room = ChatRoom.objects.get(delivery=delivery)
                    ChatMessage.objects.create(
                        room=chat_room,
                        sender=request.user,
                        message_type='system',
                        content=f"Delivery cancelled. Reason: {form.cleaned_data['reason']}"
                    )
                    
                    # Notify driver if assigned
                    if delivery.driver:
                        Notification.objects.create(
                            user=delivery.driver.user,
                            notification_type='delivery_cancelled',
                            title='Delivery Cancelled',
                            message=f'Delivery #{delivery.id} was cancelled by customer',
                            related_url=f'/deliveries/driver/'
                        )
                    
                    cancel_msg = "Delivery cancelled successfully."
                    if delivery.cancellation_fee > 0:
                        cancel_msg += f" Cancellation fee: ${delivery.cancellation_fee}"
                    
                    messages.success(request, cancel_msg)
                    return redirect('customer_dashboard')
                    
            except Exception as e:
                logger.error(f"Error cancelling delivery: {e}")
                messages.error(request, 'Error cancelling delivery. Please try again.')
    else:
        form = DeliveryCancelForm()
    
    context = {
        'delivery': delivery,
        'form': form,
    }
    return render(request, 'customer/cancel_delivery.html', context)

@login_required
def order_history(request):
    if request.user.role != 'customer':
        messages.error(request, "Access denied. Customer area only.")
        return redirect('dashboard')
    
    deliveries = Delivery.objects.filter(customer=request.user.customer).order_by('-created_at')
    
    context = {
        'deliveries': deliveries,
    }
    return render(request, 'customer/order_history.html', context)

@login_required
def get_delivery_status(request, delivery_id):
    """API endpoint for real-time delivery status updates"""
    if request.user.role != 'customer':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    delivery = get_object_or_404(Delivery, id=delivery_id, customer=request.user.customer)
    latest_tracking = DeliveryTracking.objects.filter(delivery=delivery).order_by('-timestamp').first()
    
    data = {
        'status': delivery.status,
        'status_display': delivery.get_status_display(),
        'driver_name': delivery.driver.user.username if delivery.driver else None,
        'driver_phone': delivery.driver.user.phone if delivery.driver else None,
        'current_location': {
            'lat': latest_tracking.driver_lat if latest_tracking else delivery.pickup_lat,
            'lng': latest_tracking.driver_lng if latest_tracking else delivery.pickup_lng,
        } if latest_tracking or delivery.pickup_lat else None,
        'total_price': str(delivery.total_price),
    }
    
    return JsonResponse(data)

@login_required
def driver_dashboard(request):
    if request.user.role != 'driver':
        messages.error(request, "Access denied. Driver area only.")
        return redirect('dashboard')
    
    driver = request.user.driver
    active_delivery = Delivery.objects.filter(
        driver=driver,
        status__in=['accepted', 'picked_up', 'in_transit']
    ).first()
    
    # Get available deliveries (pending ones)
    available_deliveries = Delivery.objects.filter(
        status='pending'
    ).order_by('-created_at')[:10]
    
    recent_deliveries = Delivery.objects.filter(driver=driver).order_by('-created_at')[:10]
    
    # Calculate today's earnings
    today = timezone.now().date()
    from django.db.models import Sum
    today_earnings = Delivery.objects.filter(
        driver=driver,
        status='delivered',
        delivered_at__date=today
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    context = {
        'driver': driver,
        'active_delivery': active_delivery,
        'available_deliveries': available_deliveries,
        'recent_deliveries': recent_deliveries,
        'today_earnings': today_earnings,
    }
    return render(request, 'driver/dashboard.html', context)

@login_required
def driver_online_toggle(request):
    if request.user.role != 'driver':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    driver = request.user.driver
    driver.is_online = not driver.is_online
    driver.save()
    
    # Notify customers about driver status change
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "drivers_updates",
        {
            "type": "driver.status_update",
            "driver_id": driver.user.id,
            "is_online": driver.is_online,
            "username": driver.user.username,
        }
    )
    
    return JsonResponse({
        'is_online': driver.is_online,
        'message': f'You are now {"online" if driver.is_online else "offline"}'
    })

@login_required
def accept_delivery(request, delivery_id):
    if request.user.role != 'driver':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    driver = request.user.driver
    
    if not driver.is_online:
        return JsonResponse({'error': 'You must be online to accept deliveries'}, status=400)
    
    try:
        with transaction.atomic():
            delivery = Delivery.objects.select_for_update().get(
                id=delivery_id, 
                status='pending'
            )
            
            # Accept the delivery
            delivery.driver = driver
            delivery.status = 'accepted'
            delivery.accepted_at = timezone.now()
            delivery.save()
            
            # Create chat room if not exists
            chat_room, created = ChatRoom.objects.get_or_create(delivery=delivery)
            
            # Add system message
            ChatMessage.objects.create(
                room=chat_room,
                sender=request.user,
                message_type='system',
                content=f"Driver {driver.user.username} has accepted your delivery! They will contact you shortly."
            )
            
            # Create initial tracking point
            DeliveryTracking.objects.create(
                delivery=delivery,
                driver_lat=driver.current_lat or -22.2167,
                driver_lng=driver.current_lng or 30.0000
            )
            
            # Notify customer
            Notification.objects.create(
                user=delivery.customer.user,
                notification_type='delivery_accepted',
                title='Delivery Accepted!',
                message=f'Driver {driver.user.username} has accepted your delivery',
                related_url=f'/deliveries/customer/active/{delivery.id}/'
            )
            
            # Broadcast to other drivers that delivery is taken
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "drivers_updates",
                {
                    "type": "delivery.accepted",
                    "delivery_id": delivery.id,
                    "driver_id": driver.user.id,
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Delivery accepted successfully!',
                'delivery_id': delivery.id
            })
            
    except Delivery.DoesNotExist:
        return JsonResponse({'error': 'Delivery not available or already taken'}, status=400)
    except Exception as e:
        logger.error(f"Error accepting delivery: {e}")
        return JsonResponse({'error': 'Error accepting delivery'}, status=500)

@login_required
def update_delivery_status(request, delivery_id):
    if request.user.role != 'driver':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    driver = request.user.driver
    delivery = get_object_or_404(Delivery, id=delivery_id, driver=driver)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        current_lat = request.POST.get('lat')
        current_lng = request.POST.get('lng')
        
        if new_status not in ['picked_up', 'in_transit', 'delivered']:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        try:
            with transaction.atomic():
                old_status = delivery.status
                delivery.status = new_status
                
                # Update timestamps
                if new_status == 'picked_up' and not delivery.picked_up_at:
                    delivery.picked_up_at = timezone.now()
                elif new_status == 'delivered' and not delivery.delivered_at:
                    delivery.delivered_at = timezone.now()
                    
                    # Update driver earnings
                    driver.total_earnings += delivery.total_price
                    driver.commission_owed += delivery.commission_amount
                    driver.save()
                
                delivery.save()
                
                # Update driver location if provided
                if current_lat and current_lng:
                    driver.current_lat = float(current_lat)
                    driver.current_lng = float(current_lng)
                    driver.save()
                    
                    # Create tracking point
                    DeliveryTracking.objects.create(
                        delivery=delivery,
                        driver_lat=driver.current_lat,
                        driver_lng=driver.current_lng
                    )
                
                # Add system message
                chat_room = ChatRoom.objects.get(delivery=delivery)
                status_messages = {
                    'picked_up': f"Driver has picked up your item and is on the way!",
                    'in_transit': f"Driver is in transit with your delivery",
                    'delivered': f"Delivery completed! Payment of ${delivery.total_price} received."
                }
                
                ChatMessage.objects.create(
                    room=chat_room,
                    sender=request.user,
                    message_type='system',
                    content=status_messages.get(new_status, f"Status updated to {new_status}")
                )
                
                # Notify customer
                notification_types = {
                    'picked_up': 'delivery_picked_up',
                    'in_transit': 'system',
                    'delivered': 'delivery_delivered'
                }
                
                Notification.objects.create(
                    user=delivery.customer.user,
                    notification_type=notification_types.get(new_status, 'system'),
                    title=f'Delivery {new_status.replace("_", " ").title()}',
                    message=status_messages.get(new_status, f'Delivery status updated'),
                    related_url=f'/deliveries/customer/active/{delivery.id}/'
                )
                
                # Broadcast status update
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"delivery_{delivery.id}",
                    {
                        "type": "delivery.status_update",
                        "delivery_id": delivery.id,
                        "status": new_status,
                        "status_display": delivery.get_status_display(),
                    }
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Status updated to {new_status}',
                    'new_status': new_status
                })
                
        except Exception as e:
            logger.error(f"Error updating delivery status: {e}")
            return JsonResponse({'error': 'Error updating status'}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def update_driver_location(request):
    if request.user.role != 'driver':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    driver = request.user.driver
    
    if request.method == 'POST':
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        
        if not lat or not lng:
            return JsonResponse({'error': 'Latitude and longitude required'}, status=400)
        
        try:
            driver.current_lat = float(lat)
            driver.current_lng = float(lng)
            driver.save()
            
            # Update active delivery tracking if exists
            active_delivery = Delivery.objects.filter(
                driver=driver,
                status__in=['accepted', 'picked_up', 'in_transit']
            ).first()
            
            if active_delivery:
                DeliveryTracking.objects.create(
                    delivery=active_delivery,
                    driver_lat=driver.current_lat,
                    driver_lng=driver.current_lng
                )
                
                # Broadcast location update to customer
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"delivery_{active_delivery.id}",
                    {
                        "type": "driver.location_update",
                        "delivery_id": active_delivery.id,
                        "lat": driver.current_lat,
                        "lng": driver.current_lng,
                        "timestamp": timezone.now().isoformat()
                    }
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Location updated'
            })
            
        except ValueError:
            return JsonResponse({'error': 'Invalid coordinates'}, status=400)
        except Exception as e:
            logger.error(f"Error updating location: {e}")
            return JsonResponse({'error': 'Error updating location'}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def driver_earnings(request):
    if request.user.role != 'driver':
        messages.error(request, "Access denied. Driver area only.")
        return redirect('dashboard')
    
    driver = request.user.driver
    
    # Calculate various earnings metrics
    today = timezone.now().date()
    week_ago = today - timezone.timedelta(days=7)
    month_ago = today - timezone.timedelta(days=30)
    
    from django.db.models import Sum
    today_earnings = Delivery.objects.filter(
        driver=driver,
        status='delivered',
        delivered_at__date=today
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    week_earnings = Delivery.objects.filter(
        driver=driver,
        status='delivered',
        delivered_at__date__gte=week_ago
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    month_earnings = Delivery.objects.filter(
        driver=driver,
        status='delivered',
        delivered_at__date__gte=month_ago
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Recent completed deliveries
    recent_deliveries = Delivery.objects.filter(
        driver=driver,
        status='delivered'
    ).order_by('-delivered_at')[:20]
    
    from django.conf import settings
    context = {
        'driver': driver,
        'today_earnings': today_earnings,
        'week_earnings': week_earnings,
        'month_earnings': month_earnings,
        'recent_deliveries': recent_deliveries,
        'commission_rate': settings.BRIDGEDASH_COMMISSION_RATE * 100,
    }
    return render(request, 'driver/earnings.html', context)