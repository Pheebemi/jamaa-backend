from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from apps.cases.models import Case, CaseNote
from apps.cases.serializers import CaseSerializer, CaseNoteSerializer
from apps.alerts.models import Alert
from apps.alerts.views import AlertSerializer


class SyncPushView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.organization is None:
            return Response({'error': 'User has no organization assigned.'}, status=400)

        created, updated, conflicts = [], [], []
        ai_case_ids = []

        with transaction.atomic():
            for item in request.data.get('cases', []):
                local_id  = item['local_id']
                server_id = item.get('server_id')
                device_ts = item['updated_at']
                data      = item['data']

                if not server_id:
                    case = Case.objects.create(
                        created_by=request.user,
                        organization=request.user.organization,
                        **self._safe_fields(data),
                    )
                    created.append({'local_id': local_id, 'server_id': str(case.id)})
                    ai_case_ids.append(str(case.id))
                else:
                    try:
                        case = Case.objects.get(id=server_id)
                    except Case.DoesNotExist:
                        case = Case.objects.create(
                            created_by=request.user,
                            organization=request.user.organization,
                            **self._safe_fields(data),
                        )
                        created.append({'local_id': local_id, 'server_id': str(case.id)})
                        ai_case_ids.append(str(case.id))
                        continue

                    if device_ts >= case.updated_at.isoformat():
                        for field, value in self._safe_fields(data).items():
                            setattr(case, field, value)
                        case.save()
                        updated.append({'local_id': local_id, 'server_id': str(case.id)})
                    else:
                        conflicts.append({
                            'local_id': local_id,
                            'server_version': CaseSerializer(case).data,
                        })

            for item in request.data.get('notes', []):
                self._process_note(item, request.user, created, updated, conflicts)

        # Run AI in background thread — returns immediately, doesn't block the response
        try:
            from apps.ai.tasks import analyze_case
            import threading
            for case_id in ai_case_ids:
                t = threading.Thread(target=analyze_case, args=(case_id,), daemon=True)
                t.start()
        except Exception:
            pass

        return Response({'created': created, 'updated': updated, 'conflicts': conflicts})

    def _safe_fields(self, data: dict) -> dict:
        exclude = {'id', 'server_id', 'local_id', 'sync_status', 'org_id',
                   'created_by', 'assigned_to', 'organization'}
        return {k: v for k, v in data.items() if k not in exclude and v is not None}

    def _process_note(self, item, user, created, updated, conflicts):
        local_id  = item['local_id']
        server_id = item.get('server_id')
        device_ts = item['updated_at']
        data      = item['data']

        if not server_id:
            note = CaseNote.objects.create(
                author=user,
                case_id=data.get('case_id'),
                body=data.get('body', ''),
            )
            created.append({'local_id': local_id, 'server_id': str(note.id)})
        else:
            try:
                note = CaseNote.objects.get(id=server_id)
                if device_ts >= note.updated_at.isoformat():
                    note.body = data.get('body', note.body)
                    note.save()
                    updated.append({'local_id': local_id, 'server_id': str(note.id)})
                else:
                    conflicts.append({'local_id': local_id, 'server_version': {'body': note.body}})
            except CaseNote.DoesNotExist:
                note = CaseNote.objects.create(
                    author=user,
                    case_id=data.get('case_id'),
                    body=data.get('body', ''),
                )
                created.append({'local_id': local_id, 'server_id': str(note.id)})


class SyncPullView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        last_sync = request.query_params.get('last_sync', '1970-01-01T00:00:00Z')
        org = request.user.organization

        if org is None:
            return Response({'cases': [], 'notes': [], 'server_time': timezone.now().isoformat()})

        try:
            cases = Case.objects.filter(
                organization=org,
                updated_at__gt=last_sync,
            ).select_related('assigned_to', 'created_by')

            notes = CaseNote.objects.filter(
                case__organization=org,
                updated_at__gt=last_sync,
            )

            alerts = Alert.objects.filter(
                organization=org,
                created_at__gt=last_sync,
            )

            return Response({
                'cases': CaseSerializer(cases, many=True).data,
                'notes': CaseNoteSerializer(notes, many=True).data,
                'alerts': AlertSerializer(alerts, many=True).data,
                'server_time': timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z',
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
