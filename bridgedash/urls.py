from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', include('bridgedash.apps.users.urls')),
    path('deliveries/', include('bridgedash.apps.deliveries.urls')),
    path('chat/', include('bridgedash.apps.chat.urls')),
    path('notifications/', include('bridgedash.apps.notifications.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)