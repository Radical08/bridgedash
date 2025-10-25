from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'customer':
        return redirect('customer_dashboard')
    elif user.role == 'driver':
        return redirect('driver_dashboard')
    elif user.role == 'admin':
        return redirect('admin_dashboard')
    else:
        messages.error(request, 'Unknown user role. Please contact support.')
        return redirect('logout')

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, "Access denied. Admin area only.")
        return redirect('dashboard')
    
    from bridgedash.apps.users.models import Customer, Driver
    from bridgedash.apps.deliveries.models import Delivery
    from django.db.models import Sum
    
    # Statistics
    total_customers = Customer.objects.count()
    total_drivers = Driver.objects.count()
    total_deliveries = Delivery.objects.count()
    pending_deliveries = Delivery.objects.filter(status='pending').count()
    
    # Recent activity
    recent_deliveries = Delivery.objects.select_related('customer__user', 'driver__user').order_by('-created_at')[:10]
    pending_approvals = request.user.__class__.objects.filter(status='pending').count()
    
    # Earnings
    total_earnings = Delivery.objects.aggregate(total=Sum('total_price'))['total'] or 0
    total_commission = Delivery.objects.aggregate(total=Sum('commission_amount'))['total'] or 0
    
    context = {
        'total_customers': total_customers,
        'total_drivers': total_drivers,
        'total_deliveries': total_deliveries,
        'pending_deliveries': pending_deliveries,
        'pending_approvals': pending_approvals,
        'total_earnings': total_earnings,
        'total_commission': total_commission,
        'recent_deliveries': recent_deliveries,
        'BRIDGEDASH_COMMISSION_RATE': 15,
        'BRIDGEDASH_BASE_FARE': 5.00,
        'BRIDGEDASH_PER_KM_RATE': 2.00,
    }
    return render(request, 'admin/dashboard.html', context)