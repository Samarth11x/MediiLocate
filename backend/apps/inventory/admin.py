from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        'pharmacy',
        'medicine',
        'quantity',
        'price',
        'last_updated',
        'is_demo',
    )
    list_filter = ('is_demo', 'last_updated')
    search_fields = (
        'pharmacy__name',
        'medicine__generic_name',
        'medicine__brand_name',
    )
    raw_id_fields = ('pharmacy', 'medicine')
    ordering = ('pharmacy', 'medicine')
