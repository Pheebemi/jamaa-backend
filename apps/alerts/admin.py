from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['type', 'organization', 'sent_by', 'message_preview', 'created_at']
    list_filter = ['type', 'organization']
    search_fields = ['message']
    readonly_fields = ['created_at']

    def message_preview(self, obj):
        return obj.message[:80] + '…' if len(obj.message) > 80 else obj.message
    message_preview.short_description = 'Message'
