from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class AccountApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None
        
        # Skip for authentication pages and home page
        if request.path in ['/', '/users/login/', '/users/logout/', '/users/signup/', '/users/signup/customer/', '/users/signup/driver/']:
            return None
        
        if request.path.startswith('/password-reset'):
            return None
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if user is approved
            if request.user.status == 'pending':
                messages.error(request, 'Your account is pending approval. Please wait for admin approval. You will be able to login within 24 hours.')
                return redirect('logout')
            
            if request.user.status == 'suspended':
                messages.error(request, 'Your account has been suspended. Please contact support.')
                return redirect('logout')
        
        return None