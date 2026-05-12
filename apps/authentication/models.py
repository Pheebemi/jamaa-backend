import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('org_admin', 'Organisation Admin'),
        ('field_officer', 'Field Officer'),
        ('school_staff', 'School Staff'),
        ('clinic_staff', 'Clinic Staff'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email        = models.EmailField(unique=True)
    name         = models.CharField(max_length=200)
    role         = models.CharField(max_length=20, choices=ROLE_CHOICES, default='field_officer')
    organization = models.ForeignKey(
        'cases.Organization',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='members',
    )
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def org_id(self):
        return str(self.organization_id) if self.organization_id else None
