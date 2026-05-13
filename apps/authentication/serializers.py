from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    org_id   = serializers.SerializerMethodField()
    org_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'org_id', 'org_name']

    def get_org_id(self, obj):
        return str(obj.organization_id) if obj.organization_id else None

    def get_org_name(self, obj):
        return obj.organization.name if obj.organization else None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
