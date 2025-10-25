from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Customer, Driver

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone', 'role', 'status', 'is_active', 'date_joined']
    list_filter = ['role', 'status', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'phone']
    actions = ['approve_users', 'suspend_users', 'activate_users']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('BridgeDash Info', {
            'fields': ('role', 'status', 'phone')
        }),
    )
    
    def approve_users(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} users approved successfully.')
    approve_users.short_description = "Approve selected users"
    
    def suspend_users(self, request, queryset):
        updated = queryset.update(status='suspended')
        self.message_user(request, f'{updated} users suspended.')
    suspend_users.short_description = "Suspend selected users"
    
    def activate_users(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} users activated.')
    activate_users.short_description = "Activate selected users"

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'address']
    search_fields = ['user__username', 'user__email', 'user__phone', 'address']

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'bike_registration', 'id_number', 'is_online', 'total_earnings', 'commission_owed']
    list_filter = ['is_online']
    search_fields = ['user__username', 'user__email', 'user__phone', 'bike_registration', 'id_number']
    actions = ['go_online', 'go_offline', 'reset_commission']
    
    def go_online(self, request, queryset):
        updated = queryset.update(is_online=True)
        self.message_user(request, f'{updated} drivers set to online.')
    go_online.short_description = "Set selected drivers online"
    
    def go_offline(self, request, queryset):
        updated = queryset.update(is_online=False)
        self.message_user(request, f'{updated} drivers set to offline.')
    go_offline.short_description = "Set selected drivers offline"
    
    def reset_commission(self, request, queryset):
        updated = queryset.update(commission_owed=0)
        self.message_user(request, f'{updated} drivers commission reset.')
    reset_commission.short_description = "Reset commission to zero"