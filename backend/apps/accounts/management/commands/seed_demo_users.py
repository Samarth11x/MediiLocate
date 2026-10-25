"""
Management command to seed local development database with demonstration user accounts.
Creates role accounts:
- admin (ADMIN)
- pharmacist_demo (PHARMACIST - Verified CarePoint Pharmacy)
- pharmacist_pending (PHARMACIST - Pending GreenCross Meds)
- patient_demo (USER - Patient account)
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile, UserRole
from apps.pharmacies.models import Pharmacy, VerificationStatus


class Command(BaseCommand):
    help = "Seed local development database with demo accounts for all roles."

    def handle(self, *args, **options):
        # Production guardrail: strictly refuse in production or when DEBUG is False
        if getattr(settings, 'DJANGO_ENV', '').lower() == 'production' or not getattr(settings, 'DEBUG', False):
            raise CommandError(
                "Demo seed commands are strictly prohibited in production environments or when DEBUG=False. "
                "Refusing execution to protect production database integrity."
            )

        # 1. Admin Account
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@medilocate.local',
                'first_name': 'MediLocate',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('AdminPass123!')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        admin_profile.role = UserRole.ADMIN
        admin_profile.phone_number = '+91 98765 00000'
        admin_profile.save()
        self.stdout.write(self.style.SUCCESS(f"Admin account: admin / AdminPass123! (ID: {admin_user.id})"))

        # 2. Verified Pharmacist Account
        pharma_user, created = User.objects.get_or_create(
            username='pharmacist_demo',
            defaults={
                'email': 'pharmacist@medilocate.local',
                'first_name': 'Rajesh',
                'last_name': 'Kumar',
            }
        )
        pharma_user.set_password('PharmaPass123!')
        pharma_user.save()

        pharma_profile, _ = UserProfile.objects.get_or_create(user=pharma_user)
        pharma_profile.role = UserRole.PHARMACIST
        pharma_profile.phone_number = '+91 99999 00001'
        pharma_profile.save()

        # Link to verified pharmacy
        verified_pharmacy = Pharmacy.objects.filter(name__icontains="CarePoint").first()
        if verified_pharmacy:
            verified_pharmacy.owner = pharma_user
            verified_pharmacy.license_number = 'DL-KA-2024-00129'
            verified_pharmacy.verification_status = VerificationStatus.VERIFIED
            verified_pharmacy.verified_by = admin_user
            verified_pharmacy.save()
        self.stdout.write(self.style.SUCCESS(f"Verified Pharmacist: pharmacist_demo / PharmaPass123!"))

        # 3. Pending Pharmacist Account
        pending_pharma_user, created = User.objects.get_or_create(
            username='pharmacist_pending',
            defaults={
                'email': 'pending_pharmacist@medilocate.local',
                'first_name': 'Ananya',
                'last_name': 'Sharma',
            }
        )
        pending_pharma_user.set_password('PharmaPass123!')
        pending_pharma_user.save()

        pending_profile, _ = UserProfile.objects.get_or_create(user=pending_pharma_user)
        pending_profile.role = UserRole.PHARMACIST
        pending_profile.phone_number = '+91 99999 00004'
        pending_profile.save()

        pending_pharmacy = Pharmacy.objects.filter(name__icontains="GreenCross").first()
        if pending_pharmacy:
            pending_pharmacy.owner = pending_pharma_user
            pending_pharmacy.license_number = 'DL-KA-2026-99881'
            pending_pharmacy.verification_status = VerificationStatus.PENDING
            pending_pharmacy.save()
        self.stdout.write(self.style.SUCCESS(f"Pending Pharmacist: pharmacist_pending / PharmaPass123!"))

        # 4. Patient / Regular User Account
        patient_user, created = User.objects.get_or_create(
            username='patient_demo',
            defaults={
                'email': 'patient@medilocate.local',
                'first_name': 'Priya',
                'last_name': 'Patel',
            }
        )
        patient_user.set_password('PatientPass123!')
        patient_user.save()

        patient_profile, _ = UserProfile.objects.get_or_create(user=patient_user)
        patient_profile.role = UserRole.USER
        patient_profile.phone_number = '+91 91234 56789'
        patient_profile.save()
        self.stdout.write(self.style.SUCCESS(f"Patient User: patient_demo / PatientPass123!"))
