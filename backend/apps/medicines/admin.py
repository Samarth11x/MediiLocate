from django.contrib import admin
from .models import Medicine

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        'generic_name',
        'brand_name',
        'strength',
        'dosage_form',
        'pack_size',
        'created_at',
    )
    list_filter = ('dosage_form',)
    search_fields = ('generic_name', 'brand_name')
    ordering = ('generic_name', 'brand_name')
