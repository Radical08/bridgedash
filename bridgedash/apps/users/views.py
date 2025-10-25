from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import CustomerSignupForm, DriverSignupForm, UserUpdateForm, CustomerUpdateForm, DriverUpdateForm
from .models import User, Customer, Driver

def signup(request):
    return render(request, 'registration/signup.html')

def customer_signup(request):
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.status = 'pending'
            user.save()
            
            # Create customer profile
            customer = Customer.objects.create(
                user=user,
                address=form.cleaned_data['address']
            )
            
            messages.success(request, 'Your account has been created! Please wait for admin approval. You will be able to login within 24 hours.')
            return redirect('login')
    else:
        form = CustomerSignupForm()
    
    return render(request, 'registration/customer_signup.html', {'form': form})

def driver_signup(request):
    if request.method == 'POST':
        form = DriverSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.status = 'pending'
            user.save()
            
            # Create driver profile
            driver = Driver.objects.create(
                user=user,
                bike_registration=form.cleaned_data['bike_registration'],
                id_number=form.cleaned_data['id_number']
            )
            
            messages.success(request, 'Your driver account has been created! Please wait for admin approval. You will be able to login within 24 hours.')
            return redirect('login')
    else:
        form = DriverSignupForm()
    
    return render(request, 'registration/driver_signup.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        
        if user.role == 'customer':
            profile_form = CustomerUpdateForm(request.POST, instance=user.customer)
        elif user.role == 'driver':
            profile_form = DriverUpdateForm(request.POST, instance=user.driver)
        else:
            profile_form = None
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=user)
        if user.role == 'customer':
            profile_form = CustomerUpdateForm(instance=user.customer)
        elif user.role == 'driver':
            profile_form = DriverUpdateForm(instance=user.driver)
        else:
            profile_form = None
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'registration/profile.html', context)