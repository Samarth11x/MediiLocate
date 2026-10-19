from django.contrib import admin
from .models import Pharmacy

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'city',
        'pin_code',
        'verification_status',
        'is_demo',
        'contact_number',
        'updated_at',
    )
    list_filter = ('verification_status', 'city', 'is_demo')
    search_fields = ('name', 'area', 'city', 'pin_code', 'address')
    ordering = ('name',)
