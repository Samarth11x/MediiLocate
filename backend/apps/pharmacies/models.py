"""
Pharmacy domain models for MediLocate AI.
"""

from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class VerificationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    VERIFIED = 'VERIFIED', 'Verified'
    REJECTED = 'REJECTED', 'Rejected'

class Pharmacy(models.Model):
    """
    Licensed pharmacy establishment stocking medicines.
    """
    name = models.CharField(
        max_length=255,
        verbose_name="Pharmacy Name",
        help_text="Registered trading name of the pharmacy establishment",
    )
    address = models.TextField(
        verbose_name="Street Address",
        help_text="Physical door/building and street address",
    )
    area = models.CharField(
        max_length=150,
        verbose_name="Area / Locality",
        help_text="Neighborhood, sector, or local municipal area",
    )
    city = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="City",
    )
    pin_code = models.CharField(
        max_length=10,
        db_index=True,
        verbose_name="PIN / Postal Code",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal('-90.0')),
            MaxValueValidator(Decimal('90.0')),
        ],
        help_text="WGS 84 Latitude (-90.0 to 90.0)",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal('-180.0')),
            MaxValueValidator(Decimal('180.0')),
        ],
        help_text="WGS 84 Longitude (-180.0 to 180.0)",
    )
    contact_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Contact Phone Number",
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        db_index=True,
        verbose_name="Verification Status",
    )
    opening_hours = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Opening Hours",
        help_text="Structured operational hours schedule",
    )
    is_demo = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Demo Record Indicator",
        help_text="Flag indicating this record is for fictional demonstration only",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pharmacy"
        verbose_name_plural = "Pharmacies"
        ordering = ['name', 'city']
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(latitude__gte=Decimal('-90.0')) & models.Q(latitude__lte=Decimal('90.0')))
                    | models.Q(latitude__isnull=True)
                ),
                name='pharmacy_latitude_range',
            ),
            models.CheckConstraint(
                check=(
                    (models.Q(longitude__gte=Decimal('-180.0')) & models.Q(longitude__lte=Decimal('180.0')))
                    | models.Q(longitude__isnull=True)
                ),
                name='pharmacy_longitude_range',
            ),
        ]
        indexes = [
            models.Index(fields=['city', 'pin_code']),
            models.Index(fields=['verification_status', 'is_demo']),
        ]

    def clean(self):
        super().clean()
        if self.latitude is not None:
            if self.latitude < Decimal('-90.0') or self.latitude > Decimal('90.0'):
                raise ValidationError({'latitude': 'Latitude must be between -90.0 and 90.0 degrees.'})
        if self.longitude is not None:
            if self.longitude < Decimal('-180.0') or self.longitude > Decimal('180.0'):
                raise ValidationError({'longitude': 'Longitude must be between -180.0 and 180.0 degrees.'})

    def __str__(self):
        return f"{self.name} ({self.area}, {self.city})"
