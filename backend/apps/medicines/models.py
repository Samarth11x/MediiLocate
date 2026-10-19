"""
Medicine formulary models for MediLocate AI.
"""

from django.db import models

class Medicine(models.Model):
    """
    Standardized pharmaceutical medicine identity.
    Keeps compound/strength identity decoupled from pharmacy-specific inventory.
    """
    generic_name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Generic / Chemical Name",
        help_text="Active pharmaceutical ingredient (e.g. Paracetamol, Amoxicillin)",
    )
    brand_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Brand / Trade Name",
        help_text="Commercial trade name if applicable (e.g. Crocin, Augmentin)",
    )
    strength = models.CharField(
        max_length=100,
        verbose_name="Strength",
        help_text="Unit strength or concentration (e.g. 500mg, 250mg/5ml)",
    )
    dosage_form = models.CharField(
        max_length=100,
        verbose_name="Dosage Form",
        help_text="Physical formulation (e.g. Tablet, Capsule, Syrup, Suspension, Injection)",
    )
    pack_size = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Pack Size",
        help_text="Standard packaging unit (e.g. Strip of 10, Bottle of 100ml)",
    )
    search_aliases = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Search Aliases / Synonyms",
        help_text="Alternate spellings, common typos, or synonyms used for fuzzy search indexing",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medicine"
        verbose_name_plural = "Medicines"
        ordering = ['generic_name', 'brand_name', 'strength']
        indexes = [
            models.Index(fields=['generic_name', 'strength']),
            models.Index(fields=['brand_name']),
        ]

    def __str__(self):
        brand_part = f"{self.brand_name} (" if self.brand_name else ""
        closing = ")" if self.brand_name else ""
        return f"{brand_part}{self.generic_name}{closing} {self.strength} {self.dosage_form}"
