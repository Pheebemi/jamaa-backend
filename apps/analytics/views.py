from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.cases.models import Case
from apps.cases.permissions import IsOrgAdminOrAbove
from django.db.models import Count


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsOrgAdminOrAbove]

    def get(self, request):
        org = request.user.organization
        qs = Case.objects.filter(organization=org, deleted_at__isnull=True)

        by_status = dict(qs.values_list('status').annotate(count=Count('id')).values_list('status', 'count'))
        by_priority = dict(qs.values_list('priority').annotate(count=Count('id')).values_list('priority', 'count'))
        by_type = dict(qs.values_list('type').annotate(count=Count('id')).values_list('type', 'count'))

        high_risk = list(
            qs.filter(priority='high', status__in=['open', 'in_progress'])
            .order_by('-ai_urgency_score', '-created_at')
            .values('id', 'title', 'type', 'ai_urgency_score', 'location_lat', 'location_lng')[:20]
        )

        return Response({
            'total': qs.count(),
            'by_status': by_status,
            'by_priority': by_priority,
            'by_type': by_type,
            'high_risk_cases': high_risk,
        })
