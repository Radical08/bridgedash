from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Customer, Driver

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(max_length=15, required=True, help_text='Required. Format: +263 XXX XXX XXX')
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'role', 'password1', 'password2')

class CustomerSignupForm(CustomUserCreationForm):
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = 'customer'
        self.fields['role'].widget = forms.HiddenInput()
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'role', 'address', 'password1', 'password2')

class DriverSignupForm(CustomUserCreationForm):
    bike_registration = forms.CharField(max_length=50, required=True)
    id_number = forms.CharField(max_length=20, required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = 'driver'
        self.fields['role'].widget = forms.HiddenInput()
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'role', 'bike_registration', 'id_number', 'password1', 'password2')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone']

class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['address', 'location_lat', 'location_lng']

class DriverUpdateForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['bike_registration', 'id_number']