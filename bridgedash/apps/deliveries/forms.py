from django import forms
from .models import Delivery

class DeliveryRequestForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['pickup_address', 'delivery_address', 'item_description']
        widgets = {
            'pickup_address': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Where should we pick up the item? Include shop name and address...',
                'class': 'form-control'
            }),
            'delivery_address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Where should we deliver it? Include full address and any landmarks...',
                'class': 'form-control'
            }),
            'item_description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe what you want delivered (e.g., "2kg sugar from OK Supermarket", "Documents from Town Council")',
                'class': 'form-control'
            }),
        }
        labels = {
            'pickup_address': '📦 Pickup Location',
            'delivery_address': '🏠 Delivery Address',
            'item_description': '📝 Item Description',
        }

class DeliveryCancelForm(forms.Form):
    REASON_CHOICES = (
        ('customer_not_available', 'I will not be available'),
        ('wrong_address', 'Wrong address provided'),
        ('item_not_found', 'Item not available'),
        ('driver_unavailable', 'Driver is taking too long'),
        ('other', 'Other reason'),
    )
    
    reason = forms.ChoiceField(choices=REASON_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    note = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={
            'rows': 3, 
            'placeholder': 'Additional details (optional)',
            'class': 'form-control'
        })
    )