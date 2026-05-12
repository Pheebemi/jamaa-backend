from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'name', 'role', 'organization', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'organization']
    search_fields = ['email', 'name']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('name',)}),
        ('Role & Org', {'fields': ('role', 'organization')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'organization', 'password1', 'password2'),
        }),
    )
