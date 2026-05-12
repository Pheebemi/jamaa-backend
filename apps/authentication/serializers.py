from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    org_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'org_id']

    def get_org_id(self, obj):
        return str(obj.organization_id) if obj.organization_id else None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
