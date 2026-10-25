"""
Accounts models for MediLocate AI.
Provides UserProfile with role-based access control (USER, PHARMACIST, ADMIN)
and AuditLog for tracking significant administrative actions.
"""

from django.db import models
from django.conf import settings


class UserRole(models.TextChoices):
    USER = 'USER', 'User / Patient'
    PHARMACIST = 'PHARMACIST', 'Pharmacist'
    ADMIN = 'ADMIN', 'Admin'


class UserProfile(models.Model):
    """
    User profile extending Django auth user with MediLocate role and contact details.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="User Account",
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        db_index=True,
        verbose_name="Role",
    )
    phone_number = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        verbose_name="Phone Number",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        indexes = [
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.user.is_staff or self.user.is_superuser

    @property
    def is_pharmacist(self):
        return self.role == UserRole.PHARMACIST

    @property
    def is_regular_user(self):
        return self.role == UserRole.USER


class AuditLog(models.Model):
    """
    Immutable audit history log recording significant administrative and verification actions.
    Stores no sensitive data (no passwords, tokens, or conversation text).
    """
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_actions',
        verbose_name="Actor",
    )
    action = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Action Type",
    )
    target_type = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Target Entity Type",
    )
    target_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Target Entity ID",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Safe Metadata",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP Address",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Timestamp",
    )

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['target_type', 'target_id']),
        ]

    def __str__(self):
        actor_name = self.actor.username if self.actor else "System"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {actor_name} -> {self.action} on {self.target_type} ({self.target_id})"
