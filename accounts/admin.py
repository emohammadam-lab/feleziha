from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'phone_number', 'role', 'company_name', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'phone_number', 'company_name', 'national_id')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات تکمیلی و حقوق دسترسی سازمانی', {
            'fields': (
                'role',
                'phone_number',
                'company_name',
                'national_id',
                'economic_code',
                'address',
                'postal_code',
                'is_verified'
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('اطلاعات پایه و نقش کاربر', {
            'fields': (
                'role',
                'phone_number',
                'company_name',
                'first_name',
                'last_name',
                'email'
            )
        }),
    )
