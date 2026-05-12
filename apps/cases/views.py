from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Case, CaseNote, AuditLog
from .serializers import CaseSerializer, CaseNoteSerializer
from .permissions import CanViewSensitiveCase


class CaseViewSet(viewsets.ModelViewSet):
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Case.objects.filter(
            organization=user.organization,
            deleted_at__isnull=True,
        ).select_related('assigned_to', 'created_by')
        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_sensitive:
            AuditLog.objects.create(
                user=request.user,
                case=instance,
                action='view',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization,
        )

    @action(detail=True, methods=['get', 'post'], url_path='notes')
    def notes(self, request, pk=None):
        case = self.get_object()
        if request.method == 'GET':
            notes = CaseNote.objects.filter(case=case, deleted_at__isnull=True)
            return Response(CaseNoteSerializer(notes, many=True).data)
        serializer = CaseNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(case=case, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
