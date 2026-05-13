from rest_framework import serializers
from .models import Case, CaseNote, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'type', 'country']


class CaseNoteSerializer(serializers.ModelSerializer):
    author_id = serializers.SerializerMethodField()

    class Meta:
        model = CaseNote
        fields = ['id', 'case_id', 'author_id', 'body', 'created_at', 'updated_at', 'deleted_at']

    def get_author_id(self, obj):
        return str(obj.author_id)


class CaseSerializer(serializers.ModelSerializer):
    org_id           = serializers.SerializerMethodField()
    assigned_to      = serializers.SerializerMethodField()
    created_by       = serializers.SerializerMethodField()
    created_by_name  = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = [
            'id', 'org_id', 'title', 'description', 'type', 'priority', 'status',
            'assigned_to', 'created_by', 'created_by_name', 'created_by_email',
            'is_sensitive', 'location_lat', 'location_lng',
            'ai_summary', 'ai_category', 'ai_priority', 'ai_urgency_score', 'ai_suggested_action',
            'created_at', 'updated_at', 'deleted_at',
        ]

    def get_org_id(self, obj):
        return str(obj.organization_id)

    def get_assigned_to(self, obj):
        return str(obj.assigned_to_id) if obj.assigned_to_id else None

    def get_created_by(self, obj):
        return str(obj.created_by_id)

    def get_created_by_name(self, obj):
        return obj.created_by.name if obj.created_by else None

    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else None
