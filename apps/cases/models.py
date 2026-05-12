import uuid
from django.db import models
from django.conf import settings


class Organization(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name       = models.CharField(max_length=200)
    type       = models.CharField(max_length=50, choices=[
        ('ngo', 'NGO'),
        ('school', 'School'),
        ('clinic', 'Clinic'),
        ('government', 'Government'),
    ])
    country    = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Case(models.Model):
    PRIORITY_CHOICES = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    STATUS_CHOICES   = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    TYPE_CHOICES = [
        ('child_absenteeism', 'Child Absenteeism'),
        ('malnutrition', 'Malnutrition'),
        ('flood_impact', 'Flood Impact'),
        ('medical', 'Medical Follow-up'),
        ('emergency', 'Emergency'),
        ('child_protection', 'Child Protection'),
        ('other', 'Other'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='cases')
    title        = models.CharField(max_length=300)
    description  = models.TextField()
    type         = models.CharField(max_length=50, choices=TYPE_CHOICES)
    priority     = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to  = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='assigned_cases',
    )
    created_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name='created_cases',
    )
    is_sensitive = models.BooleanField(default=False)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)

    ai_summary          = models.TextField(blank=True)
    ai_category         = models.CharField(max_length=100, blank=True)
    ai_priority         = models.CharField(max_length=20, blank=True)
    ai_urgency_score    = models.IntegerField(null=True, blank=True)
    ai_suggested_action = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'priority']),
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        return self.title


class CaseNote(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case       = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='notes')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


class AuditLog(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    case       = models.ForeignKey(Case, on_delete=models.CASCADE)
    action     = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
