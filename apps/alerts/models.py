import uuid
from django.db import models
from django.conf import settings


class Alert(models.Model):
    TYPE_CHOICES = [
        ('emergency', 'Emergency'),
        ('outbreak', 'Outbreak'),
        ('flood', 'Flood'),
        ('missing_child', 'Missing Child'),
        ('general', 'General'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('cases.Organization', on_delete=models.CASCADE, related_name='alerts')
    type         = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message      = models.TextField()
    sent_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='sent_alerts',
    )
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
