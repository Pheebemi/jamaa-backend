from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Alert
from apps.cases.permissions import IsOrgAdminOrAbove


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'type', 'message', 'sent_by', 'created_at']


class AlertListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = Alert.objects.filter(organization=request.user.organization)
        return Response(AlertSerializer(alerts, many=True).data)


class AlertBroadcastView(APIView):
    permission_classes = [IsAuthenticated, IsOrgAdminOrAbove]

    def post(self, request):
        alert_type = request.data.get('type', 'general')
        message = request.data.get('message', '')
        if not message:
            return Response({'detail': 'message is required'}, status=status.HTTP_400_BAD_REQUEST)

        alert = Alert.objects.create(
            organization=request.user.organization,
            type=alert_type,
            message=message,
            sent_by=request.user,
        )
        return Response(AlertSerializer(alert).data, status=status.HTTP_201_CREATED)
