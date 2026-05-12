from django.contrib import admin
from .models import Organization, Case, CaseNote, AuditLog


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'country', 'created_at']
    list_filter = ['type', 'country']
    search_fields = ['name']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'priority', 'status', 'organization', 'created_by', 'is_sensitive', 'sync_status_display', 'created_at']
    list_filter = ['type', 'priority', 'status', 'is_sensitive', 'organization']
    search_fields = ['title', 'description']
    readonly_fields = ['ai_summary', 'ai_category', 'ai_priority', 'ai_urgency_score', 'ai_suggested_action', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Case Info', {'fields': ('title', 'description', 'type', 'priority', 'status')}),
        ('Assignment', {'fields': ('organization', 'created_by', 'assigned_to', 'is_sensitive')}),
        ('Location', {'fields': ('location_lat', 'location_lng')}),
        ('AI Analysis', {'fields': ('ai_summary', 'ai_category', 'ai_priority', 'ai_urgency_score', 'ai_suggested_action')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'deleted_at')}),
    )

    def sync_status_display(self, obj):
        return '—'
    sync_status_display.short_description = 'Sync'


@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ['case', 'author', 'body_preview', 'created_at']
    search_fields = ['body', 'case__title']
    readonly_fields = ['created_at', 'updated_at']

    def body_preview(self, obj):
        return obj.body[:60] + '…' if len(obj.body) > 60 else obj.body
    body_preview.short_description = 'Note'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'case', 'action', 'ip_address', 'timestamp']
    list_filter = ['action']
    readonly_fields = ['user', 'case', 'action', 'ip_address', 'timestamp']
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
