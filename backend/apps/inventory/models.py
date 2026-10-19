"""
Pharmacy inventory models for MediLocate AI.
"""

from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Inventory(models.Model):
    """
    Inventory link tracking stock quantities and pricing for a specific Medicine at a Pharmacy.
    Uniqueness is strictly enforced per (pharmacy, medicine) pairing.
    """
    pharmacy = models.ForeignKey(
        'pharmacies.Pharmacy',
        on_delete=models.CASCADE,
        related_name='inventory_records',
        verbose_name="Pharmacy",
    )
    medicine = models.ForeignKey(
        'medicines.Medicine',
        on_delete=models.RESTRICT,
        related_name='inventory_records',
        verbose_name="Medicine",
    )
    quantity = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Available Quantity",
        help_text="Stock count. NULL indicates unknown/unreported stock; 0 indicates confirmed out-of-stock.",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Unit Selling Price",
        help_text="Unit selling price in INR",
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Stock Update",
        help_text="Timestamp of latest inventory update or verification",
    )
    is_demo = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Demo Record Indicator",
        help_text="Flag indicating this stock record is for fictional demonstration only",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pharmacy Inventory"
        verbose_name_plural = "Pharmacy Inventories"
        ordering = ['pharmacy', 'medicine']
        constraints = [
            models.UniqueConstraint(
                fields=['pharmacy', 'medicine'],
                name='unique_pharmacy_medicine_inventory',
            ),
            models.CheckConstraint(
                check=models.Q(quantity__gte=0) | models.Q(quantity__isnull=True),
                name='inventory_quantity_non_negative',
            ),
            models.CheckConstraint(
                check=models.Q(price__gte=Decimal('0.00')) | models.Q(price__isnull=True),
                name='inventory_price_non_negative',
            ),
        ]
        indexes = [
            models.Index(fields=['pharmacy', 'medicine']),
            models.Index(fields=['last_updated']),
            models.Index(fields=['is_demo']),
        ]

    def clean(self):
        super().clean()
        if self.quantity is not None and self.quantity < 0:
            raise ValidationError({'quantity': 'Quantity cannot be negative.'})
        if self.price is not None and self.price < Decimal('0.00'):
            raise ValidationError({'price': 'Price cannot be negative.'})

    def get_availability_status(self, low_stock_threshold=10):
        """
        Calculated availability interpretation.
        Delegates classification to core_intelligence.availability.rules.classify_availability
        when available, maintaining consistent status keys and labels.

        NOTE: Availability is NOT stored as a redundant database column to prevent
        desynchronization with actual stock counts.
        - None  -> 'UNKNOWN' (Availability Unknown)
        - 0     -> 'OUT_OF_STOCK' (Out of Stock)
        - 1..9  -> 'LOW_STOCK' (Low Stock)
        - >=10  -> 'AVAILABLE' (Available)
        """
        try:
            from core_intelligence.availability.rules import classify_availability, AvailabilityConfig
            cfg = AvailabilityConfig(low_stock_threshold=low_stock_threshold)
            status_key = classify_availability(self.quantity, cfg)
        except ImportError:
            if self.quantity is None:
                status_key = 'UNKNOWN'
            elif self.quantity == 0:
                status_key = 'OUT_OF_STOCK'
            elif 0 < self.quantity < low_stock_threshold:
                status_key = 'LOW_STOCK'
            else:
                status_key = 'AVAILABLE'

        labels = {
            'UNKNOWN': 'Availability Unknown',
            'OUT_OF_STOCK': 'Out of Stock',
            'LOW_STOCK': 'Low Stock',
            'AVAILABLE': 'Available',
        }
        return status_key, labels.get(status_key, 'Availability Unknown')

    def __str__(self):
        qty_str = f"Qty: {self.quantity}" if self.quantity is not None else "Qty: Unknown"
        return f"{self.medicine} at {self.pharmacy.name} ({qty_str})"
