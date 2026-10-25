"""
Management command to seed local development database with demo data for all three portals:
- Admin Portal (/admin/dashboard)
- Pharmacist Portal (/pharmacist/dashboard) - Verified, Pending, and Rejected states
- Patient Portal (/app)

Features:
- Exactly 20 primary user-provided demonstration pharmacies (Belagavi & Bengaluru).
- Fictional demonstration network with Paracetamol 500mg in all 20 verified pharmacies.
- Demonstrates all 4 stock availability states: AVAILABLE (>=10), LOW_STOCK (1-9), OUT_OF_STOCK (0), UNKNOWN (None).
- Unique pharmacist accounts for each pharmacy owner (pharmacist_demo_01 through pharmacist_demo_20).
- Dedicated pending and rejected pharmacist accounts (pharmacist_demo_pending, pharmacist_demo_rejected).
- Pending and Rejected pharmacy applications preserved for Admin Dashboard verification queues.
- Retires previous fictional placeholders so only the 20 primary listings appear in patient search.
- Safe & Idempotent: Refuses to execute in production or when DEBUG=False.
- Preserves manual inventory edits and admin status changes upon subsequent runs.
- Strictly keeps coordinates null where not provided (no distance fabrication).
"""

from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserProfile, UserRole, AuditLog
from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.medicines.models import Medicine
from apps.inventory.models import Inventory


# ------------------------------------------------------------------------------
# Fictional Demonstration Formulary
# ------------------------------------------------------------------------------

DEMO_MEDICINES = [
    {
        "generic_name": "Paracetamol",
        "brand_name": "Crocin",
        "strength": "500mg",
        "dosage_form": "Tablet",
        "pack_size": "Strip of 10",
        "search_aliases": ["pcm", "crocin 500", "fever tablet", "paracetamol 500"],
    },
    {
        "generic_name": "Paracetamol",
        "brand_name": "Dolo",
        "strength": "650mg",
        "dosage_form": "Tablet",
        "pack_size": "Strip of 15",
        "search_aliases": ["dolo 650", "fever tablet", "pcm 650", "paracetamol 650"],
    },
    {
        "generic_name": "Paracetamol",
        "brand_name": "Calpol",
        "strength": "250mg/5ml",
        "dosage_form": "Syrup",
        "pack_size": "Bottle of 60ml",
        "search_aliases": ["calpol syrup", "pediatric paracetamol", "paracetamol syrup"],
    },
    {
        "generic_name": "Amoxicillin",
        "brand_name": "Novamox",
        "strength": "250mg",
        "dosage_form": "Capsule",
        "pack_size": "Strip of 10",
        "search_aliases": ["amox 250", "novamox 250"],
    },
    {
        "generic_name": "Amoxicillin",
        "brand_name": "Novamox",
        "strength": "500mg",
        "dosage_form": "Capsule",
        "pack_size": "Strip of 10",
        "search_aliases": ["amox 500", "amoxicillin 500", "novamox 500"],
    },
    {
        "generic_name": "Amoxicillin and Potassium Clavulanate",
        "brand_name": "Augmentin",
        "strength": "625mg",
        "dosage_form": "Tablet",
        "pack_size": "Strip of 10",
        "search_aliases": ["augmentin 625", "co-amoxiclav", "amoxyclav"],
    },
    {
        "generic_name": "Cetirizine Hydrochloride",
        "brand_name": "Cetzine",
        "strength": "10mg",
        "dosage_form": "Tablet",
        "pack_size": "Strip of 10",
        "search_aliases": ["cetzine", "allergy tablet", "cetirizine 10"],
    },
    {
        "generic_name": "Ibuprofen",
        "brand_name": "Brufen",
        "strength": "400mg",
        "dosage_form": "Tablet",
        "pack_size": "Strip of 15",
        "search_aliases": ["brufen 400", "pain killer", "ibuprofen 400"],
    },
    {
        "generic_name": "Azithromycin",
        "brand_name": "Azee",
        "strength": "500mg",
        "dosage_form": "Tablet",
        "pack_size": "Strip of 5",
        "search_aliases": ["azee 500", "azithral", "azithromycin 500"],
    },
    {
        "generic_name": "Metformin Hydrochloride",
        "brand_name": "Glycomet",
        "strength": "500mg",
        "dosage_form": "Tablet",
        "pack_size": "Strip of 20",
        "search_aliases": ["glycomet 500", "diabetes tablet", "metformin 500"],
    },
]


# ------------------------------------------------------------------------------
# 20 Primary User-Provided Pharmacy Listings
# Coordinates are strictly kept None (no fabrication).
# ------------------------------------------------------------------------------

PRIMARY_DEMO_PHARMACIES = [
    {
        "name": "Apollo Pharmacy Peeranwadi Belagavi",
        "owner_username": "pharmacist_demo_01",
        "license_number": "DL-KA-BEL-DEMO-001",
        "address": "2250, Ground Floor, Main Road, near Shivaji Maharaj Statue",
        "area": "Peeranwadi",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "079 4281 4489",
        "opening_hours": {"display": "Open until 11 PM", "services": ["Delivery", "Website", "Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Laxmi Medical",
        "owner_username": "pharmacist_demo_02",
        "license_number": "DL-KA-BEL-DEMO-002",
        "address": "peeranwadi, road",
        "area": "Peeranwadi",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "094488 75838",
        "opening_hours": {"display": "Standard Hours", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Zainab Medical & General Stores",
        "owner_username": "pharmacist_demo_03",
        "license_number": "DL-KA-BEL-DEMO-003",
        "address": "Piranawadi, Karnataka",
        "area": "Piranawadi",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "097317 99835",
        "opening_hours": {"display": "Open until 11 PM", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Piraji medical and general store",
        "owner_username": "pharmacist_demo_04",
        "license_number": "DL-KA-BEL-DEMO-004",
        "address": "QFV9+FWM, Hunchanatti Rd",
        "area": "Hunchanatti Rd",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": None,
        "opening_hours": {"display": "Open until 5 PM", "services": ["Delivery", "Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Genericart Medicine Store | Dhanvantari Swast Aushadhi Seva | Belgaum",
        "owner_username": "pharmacist_demo_05",
        "license_number": "DL-KA-BEL-DEMO-005",
        "address": "Jamboti, Belagavi, Karnataka",
        "area": "Jamboti",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "091136 29299",
        "opening_hours": {"display": "Open until 10:30 PM", "services": ["Delivery", "Website", "Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Health Pro Medicals",
        "owner_username": "pharmacist_demo_06",
        "license_number": "DL-KA-BEL-DEMO-006",
        "address": "RF2J+MJP",
        "area": "RF2J+MJP",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": None,
        "opening_hours": {"display": "Standard Hours", "services": ["Delivery", "Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Paraji Medical And General Stores",
        "owner_username": "pharmacist_demo_07",
        "license_number": "DL-KA-BEL-DEMO-007",
        "address": "Shop No 01, opp. Sateri General Store",
        "area": "Shop No 01",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "063645 41916",
        "opening_hours": {"display": "Standard Hours", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "ANAND MEDICAL & GENERAL STORE",
        "owner_username": "pharmacist_demo_08",
        "license_number": "DL-KA-BEL-DEMO-008",
        "address": "Piranawadi, Karnataka",
        "area": "Piranawadi",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": None,
        "opening_hours": {"display": "Standard Hours", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "HEALTH PRO PHARMACY",
        "owner_username": "pharmacist_demo_09",
        "license_number": "DL-KA-BEL-DEMO-009",
        "address": "QFW7+9RJ",
        "area": "QFW7+9RJ",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": None,
        "opening_hours": {"display": "Standard Hours", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Genericart Medicine Store | Sanjeevini Swast Aushadhi Seva | Belgaum",
        "owner_username": "pharmacist_demo_10",
        "license_number": "DL-KA-BEL-DEMO-010",
        "address": "Piranawadi, Karnataka",
        "area": "Piranawadi",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "099017 75148",
        "opening_hours": {"display": "Open until 11 PM", "services": ["In-store shopping", "Delivery", "Website", "Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "PADMASHREE MEDICAL AND GENERAL STORES",
        "owner_username": "pharmacist_demo_11",
        "license_number": "DL-KA-BLR-DEMO-011",
        "address": "Bengaluru, Karnataka",
        "area": "Bengaluru",
        "city": "Bengaluru",
        "pin_code": "560001",
        "contact_number": "087927 53824",
        "opening_hours": {"display": "Standard Hours", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Varsha Medical",
        "owner_username": "pharmacist_demo_12",
        "license_number": "DL-KA-BEL-DEMO-012",
        "address": "RF3J+5Q9",
        "area": "RF3J+5Q9",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "098443 65143",
        "opening_hours": {"display": "Open until 11 PM", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Pandurang Medical & General Store",
        "owner_username": "pharmacist_demo_13",
        "license_number": "DL-KA-BEL-DEMO-013",
        "address": "Piranawadi, Karnataka",
        "area": "Piranawadi",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": None,
        "opening_hours": {"display": "Standard Hours", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Vedang Medicals",
        "owner_username": "pharmacist_demo_14",
        "license_number": "DL-KA-BEL-DEMO-014",
        "address": "Piranawadi, Karnataka",
        "area": "Piranawadi",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "095356 48974",
        "opening_hours": {"display": "Closed; opens at 7:30 PM", "services": ["Delivery", "Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "SHRI CHANDRA PRABHA MEDICAL AND GENERAL STORE",
        "owner_username": "pharmacist_demo_15",
        "license_number": "DL-KA-BEL-DEMO-015",
        "address": "S No 02, Goa, Khanapur Rd, near Bus Stop, opposite Axis Atm",
        "area": "Khanapur Rd",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "083102 83693",
        "opening_hours": {"display": "7:30 AM to 11 PM", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Wellness Forever Pharmacy - Khanapur Road, Tilakwadi, Belagavi",
        "owner_username": "pharmacist_demo_16",
        "license_number": "DL-KA-BEL-DEMO-016",
        "address": "Belagavi, Karnataka",
        "area": "Tilakwadi",
        "city": "Belagavi",
        "pin_code": "590006",
        "contact_number": "0831 421 0815",
        "opening_hours": {"display": "Open 24 hours", "services": ["In-store shopping", "In-store pick-up", "Delivery", "Website", "Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Pragati Pharma",
        "owner_username": "pharmacist_demo_17",
        "license_number": "DL-KA-BEL-DEMO-017",
        "address": "Shivakrupa, 48/49, Gurudev Ranade Rd",
        "area": "Gurudev Ranade Rd",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "0831 420 1498",
        "opening_hours": {"display": "Open until 10 PM", "services": ["Delivery", "Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Mediclass Medicals CA",
        "owner_username": "pharmacist_demo_18",
        "license_number": "DL-KA-BLR-DEMO-018",
        "address": "Bengaluru, Karnataka",
        "area": "Bengaluru",
        "city": "Bengaluru",
        "pin_code": "560001",
        "contact_number": "094817 52975",
        "opening_hours": {"display": "Standard Hours", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Shree Laxmi Medical & General Stores",
        "owner_username": "pharmacist_demo_19",
        "license_number": "DL-KA-BEL-DEMO-019",
        "address": "QFRJ+CX7",
        "area": "QFRJ+CX7",
        "city": "Belagavi",
        "pin_code": "590014",
        "contact_number": "0831 249 4314",
        "opening_hours": {"display": "Open until 10:30 PM", "services": ["Directions"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
    {
        "name": "Apollo Pharmacy Rani Channamma Nagar",
        "owner_username": "pharmacist_demo_20",
        "license_number": "DL-KA-BEL-DEMO-020",
        "address": "Belagavi, Karnataka",
        "area": "Rani Channamma Nagar",
        "city": "Belagavi",
        "pin_code": "590006",
        "contact_number": "079 4281 4505",
        "opening_hours": {"display": "Open until 11 PM", "services": ["In-store shopping", "In-store pick-up", "Delivery"]},
        "verification_status": VerificationStatus.VERIFIED,
    },
]

# Stale fictional placeholder names to retire so they do not clutter search results
STALE_DEMO_PHARMACIES = [
    "Demo CarePoint Pharmacy (Fictional)",
    "Demo Metro Health Pharmacy (Fictional)",
    "Demo CityCare Pharmacy (Fictional)",
    "Demo GreenLeaf Pharmacy (Fictional)",
    "Demo MedBridge Pharmacy (Fictional)",
    "Demo Wellness Pharmacy (Fictional)",
    "Demo LifeSpring Pharmacy (Fictional)",
    "Demo HealthFirst Pharmacy (Fictional)",
    "Demo CommunityCare Pharmacy (Fictional)",
    "Demo PrimeCare Pharmacy (Fictional)",
    "Demo CarePoint Pharmacy (Fictional Dev)",
    "Demo Metro Chemist (Fictional Dev)",
    "Demo Apollo Life Chemist (Fictional Dev)",
    "Demo GreenCross Meds (Fictional Dev - Unverified)",
]


class Command(BaseCommand):
    help = "Seed local development database with 20 primary user-provided demo pharmacies and varied inventory."

    def handle(self, *args, **options):
        # 1. Strict environment and database safety checks
        env_mode = getattr(settings, 'DJANGO_ENV', '').lower()
        is_debug = getattr(settings, 'DEBUG', False)

        if env_mode == 'production' or not is_debug:
            raise CommandError(
                "Demo seed commands are strictly prohibited in production environments or when DEBUG=False. "
                "Refusing execution to protect production database integrity."
            )

        db_engine = settings.DATABASES['default']['ENGINE']
        db_name = str(settings.DATABASES['default']['NAME'])
        self.stdout.write("=" * 80)
        self.stdout.write("MEDILOCATE AI -- DEMO PORTAL SEEDING (20 PRIMARY PHARMACIES NETWORK)")
        self.stdout.write(f"Active database: {db_engine}")
        self.stdout.write(f"Database target: {db_name}")
        self.stdout.write(f"Environment: {env_mode or 'development'} | DEBUG: {is_debug}")
        self.stdout.write("=" * 80)

        with transaction.atomic():
            # ------------------------------------------------------------------
            # 2. Retire stale placeholder pharmacies safely
            # ------------------------------------------------------------------
            Inventory.objects.filter(pharmacy__name__in=STALE_DEMO_PHARMACIES).delete()
            Pharmacy.objects.filter(name__in=STALE_DEMO_PHARMACIES).delete()

            # ------------------------------------------------------------------
            # 3. Seed Admin Accounts
            # ------------------------------------------------------------------
            admin_user, _ = User.objects.get_or_create(
                username='admin_demo',
                defaults={
                    'email': 'admin_demo@medilocate.local',
                    'first_name': 'MediLocate',
                    'last_name': 'Administrator',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            admin_user.set_password('AdminDemoPass123!')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

            admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
            admin_profile.role = UserRole.ADMIN
            admin_profile.phone_number = '+91 98765 00000'
            admin_profile.save()

            # Preserve legacy admin if exists
            legacy_admin = User.objects.filter(username='admin').first()
            if legacy_admin:
                legacy_admin.set_password('AdminPass123!')
                legacy_admin.save()

            # ------------------------------------------------------------------
            # 4. Seed Patient Accounts
            # ------------------------------------------------------------------
            patient_1, _ = User.objects.get_or_create(
                username='patient_demo_01',
                defaults={
                    'email': 'patient_01@medilocate.local',
                    'first_name': 'Priya',
                    'last_name': 'Patel',
                }
            )
            patient_1.set_password('PatientPass123!')
            patient_1.save()
            p1_profile, _ = UserProfile.objects.get_or_create(user=patient_1)
            p1_profile.role = UserRole.USER
            p1_profile.phone_number = '+91 91234 56781'
            p1_profile.save()

            patient_2, _ = User.objects.get_or_create(
                username='patient_demo_02',
                defaults={
                    'email': 'patient_02@medilocate.local',
                    'first_name': 'Rahul',
                    'last_name': 'Verma',
                }
            )
            patient_2.set_password('PatientPass123!')
            patient_2.save()
            p2_profile, _ = UserProfile.objects.get_or_create(user=patient_2)
            p2_profile.role = UserRole.USER
            p2_profile.phone_number = '+91 91234 56782'
            p2_profile.save()

            # Preserve legacy patient_demo
            legacy_patient = User.objects.filter(username='patient_demo').first()
            if legacy_patient:
                legacy_patient.set_password('PatientPass123!')
                legacy_patient.save()

            # ------------------------------------------------------------------
            # 5. Seed Pharmacist Owner Accounts (pharmacist_demo_01 to 20, plus pending/rejected)
            # ------------------------------------------------------------------
            pharmacist_specs = [
                ("pharmacist_demo_01", "Apollo", "Peeranwadi", "pharma01@medilocate.local", "+91 99999 00001"),
                ("pharmacist_demo_02", "Laxmi", "Pharmacist", "pharma02@medilocate.local", "+91 99999 00002"),
                ("pharmacist_demo_03", "Zainab", "Pharmacist", "pharma03@medilocate.local", "+91 99999 00003"),
                ("pharmacist_demo_04", "Piraji", "Pharmacist", "pharma04@medilocate.local", "+91 99999 00004"),
                ("pharmacist_demo_05", "Genericart", "Dhanvantari", "pharma05@medilocate.local", "+91 99999 00005"),
                ("pharmacist_demo_06", "HealthPro", "Medicals", "pharma06@medilocate.local", "+91 99999 00006"),
                ("pharmacist_demo_07", "Paraji", "Pharmacist", "pharma07@medilocate.local", "+91 99999 00007"),
                ("pharmacist_demo_08", "Anand", "Pharmacist", "pharma08@medilocate.local", "+91 99999 00008"),
                ("pharmacist_demo_09", "HealthPro", "Pharmacy", "pharma09@medilocate.local", "+91 99999 00009"),
                ("pharmacist_demo_10", "Genericart", "Sanjeevini", "pharma10@medilocate.local", "+91 99999 00010"),
                ("pharmacist_demo_11", "Padmashree", "Pharmacist", "pharma11@medilocate.local", "+91 99999 00011"),
                ("pharmacist_demo_12", "Varsha", "Pharmacist", "pharma12@medilocate.local", "+91 99999 00012"),
                ("pharmacist_demo_13", "Pandurang", "Pharmacist", "pharma13@medilocate.local", "+91 99999 00013"),
                ("pharmacist_demo_14", "Vedang", "Pharmacist", "pharma14@medilocate.local", "+91 99999 00014"),
                ("pharmacist_demo_15", "Chandra", "Prabha", "pharma15@medilocate.local", "+91 99999 00015"),
                ("pharmacist_demo_16", "Wellness", "Tilakwadi", "pharma16@medilocate.local", "+91 99999 00016"),
                ("pharmacist_demo_17", "Pragati", "Pharmacist", "pharma17@medilocate.local", "+91 99999 00017"),
                ("pharmacist_demo_18", "Mediclass", "Pharmacist", "pharma18@medilocate.local", "+91 99999 00018"),
                ("pharmacist_demo_19", "ShreeLaxmi", "Pharmacist", "pharma19@medilocate.local", "+91 99999 00019"),
                ("pharmacist_demo_20", "Apollo", "RaniChannamma", "pharma20@medilocate.local", "+91 99999 00020"),
                ("pharmacist_demo_pending", "GreenCross", "Applicant", "pharma_pending@medilocate.local", "+91 99999 00021"),
                ("pharmacist_demo_rejected", "Sunrise", "Applicant", "pharma_rejected@medilocate.local", "+91 99999 00022"),
            ]

            pharmacists = {}
            for uname, fname, lname, email, phone in pharmacist_specs:
                pharma_user, _ = User.objects.get_or_create(
                    username=uname,
                    defaults={
                        'email': email,
                        'first_name': fname,
                        'last_name': lname,
                    }
                )
                pharma_user.set_password('PharmaPass123!')
                pharma_user.save()
                ph_profile, _ = UserProfile.objects.get_or_create(user=pharma_user)
                ph_profile.role = UserRole.PHARMACIST
                ph_profile.phone_number = phone
                ph_profile.save()
                pharmacists[uname] = pharma_user

            # ------------------------------------------------------------------
            # 6. Seed 20 Primary Demonstration Pharmacies (VERIFIED)
            # Uses get_or_create to preserve admin approval/rejection edits.
            # Coordinates are strictly None (no fabricated coordinates).
            # ------------------------------------------------------------------
            pharmacies = {}
            for p_spec in PRIMARY_DEMO_PHARMACIES:
                owner = pharmacists[p_spec["owner_username"]]
                pharm, created = Pharmacy.objects.get_or_create(
                    name=p_spec["name"],
                    defaults={
                        "owner": owner,
                        "license_number": p_spec["license_number"],
                        "address": p_spec["address"],
                        "area": p_spec["area"],
                        "city": p_spec["city"],
                        "pin_code": p_spec["pin_code"],
                        "latitude": None,
                        "longitude": None,
                        "contact_number": p_spec["contact_number"],
                        "verification_status": p_spec["verification_status"],
                        "verified_by": admin_user,
                        "verified_at": timezone.now(),
                        "rejection_reason": None,
                        "opening_hours": p_spec["opening_hours"],
                        "is_demo": True,
                    }
                )
                if not created:
                    # Preserve admin edits; associate owner or license if blank
                    fields_to_update = []
                    if pharm.owner is None and owner is not None:
                        pharm.owner = owner
                        fields_to_update.append("owner")
                    if not pharm.license_number:
                        pharm.license_number = p_spec["license_number"]
                        fields_to_update.append("license_number")
                    if fields_to_update:
                        pharm.save(update_fields=fields_to_update)

                pharmacies[p_spec["name"]] = pharm

            # ------------------------------------------------------------------
            # 7. Seed Admin Queue Demonstration Pharmacies (PENDING & REJECTED)
            # ------------------------------------------------------------------
            greencross_owner = pharmacists["pharmacist_demo_pending"]
            pharm_greencross, _ = Pharmacy.objects.get_or_create(
                name="Demo GreenCross Pharmacy (Fictional)",
                defaults={
                    "owner": greencross_owner,
                    "license_number": "DL-DEMO-KA-2026-002",
                    "address": "Corner Store 7, Fictional Tech Corridor, Whitefield Main Road",
                    "area": "Whitefield",
                    "city": "Bengaluru",
                    "pin_code": "560066",
                    "latitude": None,
                    "longitude": None,
                    "contact_number": "+91 99999 00021",
                    "verification_status": VerificationStatus.PENDING,
                    "rejection_reason": None,
                    "opening_hours": {"mon_fri": "10:00 - 19:00", "sat_sun": "Closed"},
                    "is_demo": True,
                }
            )
            if pharm_greencross.owner != greencross_owner:
                pharm_greencross.owner = greencross_owner
                pharm_greencross.save(update_fields=["owner"])

            sunrise_owner = pharmacists["pharmacist_demo_rejected"]
            pharm_sunrise, _ = Pharmacy.objects.get_or_create(
                name="Demo Sunrise Pharmacy (Fictional)",
                defaults={
                    "owner": sunrise_owner,
                    "license_number": "DL-DEMO-KA-2023-003",
                    "address": "Building 22, Fictional Sunrise Market, 5th Block, Jayanagar",
                    "area": "Jayanagar",
                    "city": "Bengaluru",
                    "pin_code": "560041",
                    "latitude": None,
                    "longitude": None,
                    "contact_number": "+91 99999 00022",
                    "verification_status": VerificationStatus.REJECTED,
                    "verified_by": admin_user,
                    "verified_at": timezone.now(),
                    "rejection_reason": (
                        "Fictional Dev Notice: Submitted drug license document DL-DEMO-SUNRISE-99 expired on 2024-12-31. "
                        "Please upload a renewed valid license certificate for compliance review."
                    ),
                    "opening_hours": {"mon_sat": "09:00 - 21:00", "sun": "Closed"},
                    "is_demo": True,
                }
            )
            if pharm_sunrise.owner != sunrise_owner:
                pharm_sunrise.owner = sunrise_owner
                pharm_sunrise.save(update_fields=["owner"])

            # ------------------------------------------------------------------
            # 8. Seed Medicines Formulary
            # ------------------------------------------------------------------
            medicines = {}
            for med_data in DEMO_MEDICINES:
                key = (med_data["generic_name"], med_data["strength"], med_data["dosage_form"])
                med_obj, _ = Medicine.objects.update_or_create(
                    generic_name=med_data["generic_name"],
                    strength=med_data["strength"],
                    dosage_form=med_data["dosage_form"],
                    defaults={
                        "brand_name": med_data["brand_name"],
                        "pack_size": med_data["pack_size"],
                        "search_aliases": med_data["search_aliases"],
                    }
                )
                medicines[key] = med_obj

            # ------------------------------------------------------------------
            # 9. Seed Diverse Sample Inventory Across All 20 Verified Pharmacies
            #
            # Requirements:
            # - EVERY verified pharmacy stocks Paracetamol 500mg Tablet (Crocin).
            # - Paracetamol 500mg stock states cover:
            #     AVAILABLE (>=10): 10 pharmacies
            #     LOW_STOCK (1-9): 6 pharmacies
            #     OUT_OF_STOCK (0): 2 pharmacies
            #     UNKNOWN (None): 2 pharmacies
            # - Varied medicine combinations across pharmacies (e.g. Wellness Tilakwadi superstore).
            # - Uses get_or_create to preserve manual inventory edits upon reseeding.
            # - Unverified pharmacies (GreenCross, Sunrise) have 0 stock records.
            # ------------------------------------------------------------------
            pcm_500 = medicines[("Paracetamol", "500mg", "Tablet")]
            pcm_650 = medicines[("Paracetamol", "650mg", "Tablet")]
            pcm_syrup = medicines[("Paracetamol", "250mg/5ml", "Syrup")]
            amox_250 = medicines[("Amoxicillin", "250mg", "Capsule")]
            amox_500 = medicines[("Amoxicillin", "500mg", "Capsule")]
            augmentin_625 = medicines[("Amoxicillin and Potassium Clavulanate", "625mg", "Tablet")]
            cetz_10 = medicines[("Cetirizine Hydrochloride", "10mg", "Tablet")]
            ibup_400 = medicines[("Ibuprofen", "400mg", "Tablet")]
            azee_500 = medicines[("Azithromycin", "500mg", "Tablet")]
            glyco_500 = medicines[("Metformin Hydrochloride", "500mg", "Tablet")]

            p1 = pharmacies["Apollo Pharmacy Peeranwadi Belagavi"]
            p2 = pharmacies["Laxmi Medical"]
            p3 = pharmacies["Zainab Medical & General Stores"]
            p4 = pharmacies["Piraji medical and general store"]
            p5 = pharmacies["Genericart Medicine Store | Dhanvantari Swast Aushadhi Seva | Belgaum"]
            p6 = pharmacies["Health Pro Medicals"]
            p7 = pharmacies["Paraji Medical And General Stores"]
            p8 = pharmacies["ANAND MEDICAL & GENERAL STORE"]
            p9 = pharmacies["HEALTH PRO PHARMACY"]
            p10 = pharmacies["Genericart Medicine Store | Sanjeevini Swast Aushadhi Seva | Belgaum"]
            p11 = pharmacies["PADMASHREE MEDICAL AND GENERAL STORES"]
            p12 = pharmacies["Varsha Medical"]
            p13 = pharmacies["Pandurang Medical & General Store"]
            p14 = pharmacies["Vedang Medicals"]
            p15 = pharmacies["SHRI CHANDRA PRABHA MEDICAL AND GENERAL STORE"]
            p16 = pharmacies["Wellness Forever Pharmacy - Khanapur Road, Tilakwadi, Belagavi"]
            p17 = pharmacies["Pragati Pharma"]
            p18 = pharmacies["Mediclass Medicals CA"]
            p19 = pharmacies["Shree Laxmi Medical & General Stores"]
            p20 = pharmacies["Apollo Pharmacy Rani Channamma Nagar"]

            inventory_definitions = [
                # Pharmacy 1: Apollo Peeranwadi (AVAILABLE)
                {"pharmacy": p1, "medicine": pcm_500, "quantity": 45, "price": Decimal("28.50")},
                {"pharmacy": p1, "medicine": pcm_650, "quantity": 30, "price": Decimal("40.00")},
                {"pharmacy": p1, "medicine": cetz_10, "quantity": 25, "price": Decimal("18.00")},
                {"pharmacy": p1, "medicine": augmentin_625, "quantity": 15, "price": Decimal("120.00")},
                {"pharmacy": p1, "medicine": azee_500, "quantity": 10, "price": Decimal("110.00")},

                # Pharmacy 2: Laxmi Medical (LOW_STOCK)
                {"pharmacy": p2, "medicine": pcm_500, "quantity": 8, "price": Decimal("29.00")},
                {"pharmacy": p2, "medicine": cetz_10, "quantity": 12, "price": Decimal("19.00")},
                {"pharmacy": p2, "medicine": ibup_400, "quantity": 0, "price": Decimal("30.00")},

                # Pharmacy 3: Zainab Medical (AVAILABLE)
                {"pharmacy": p3, "medicine": pcm_500, "quantity": 22, "price": Decimal("28.00")},
                {"pharmacy": p3, "medicine": pcm_650, "quantity": 18, "price": Decimal("39.00")},
                {"pharmacy": p3, "medicine": amox_500, "quantity": 15, "price": Decimal("85.00")},
                {"pharmacy": p3, "medicine": glyco_500, "quantity": 20, "price": Decimal("42.00")},

                # Pharmacy 4: Piraji medical (OUT_OF_STOCK)
                {"pharmacy": p4, "medicine": pcm_500, "quantity": 0, "price": Decimal("30.00")},
                {"pharmacy": p4, "medicine": pcm_syrup, "quantity": 8, "price": Decimal("52.00")},
                {"pharmacy": p4, "medicine": cetz_10, "quantity": 5, "price": Decimal("18.50")},

                # Pharmacy 5: Genericart Dhanvantari (AVAILABLE)
                {"pharmacy": p5, "medicine": pcm_500, "quantity": 60, "price": Decimal("25.00")},
                {"pharmacy": p5, "medicine": pcm_650, "quantity": 45, "price": Decimal("35.00")},
                {"pharmacy": p5, "medicine": amox_250, "quantity": 20, "price": Decimal("42.00")},
                {"pharmacy": p5, "medicine": amox_500, "quantity": 25, "price": Decimal("78.00")},
                {"pharmacy": p5, "medicine": glyco_500, "quantity": 40, "price": Decimal("38.00")},
                {"pharmacy": p5, "medicine": ibup_400, "quantity": 30, "price": Decimal("26.00")},

                # Pharmacy 6: Health Pro Medicals (LOW_STOCK)
                {"pharmacy": p6, "medicine": pcm_500, "quantity": 5, "price": Decimal("29.50")},
                {"pharmacy": p6, "medicine": augmentin_625, "quantity": 12, "price": Decimal("125.00")},
                {"pharmacy": p6, "medicine": azee_500, "quantity": 4, "price": Decimal("115.00")},

                # Pharmacy 7: Paraji Medical (UNKNOWN)
                {"pharmacy": p7, "medicine": pcm_500, "quantity": None, "price": Decimal("30.00")},
                {"pharmacy": p7, "medicine": cetz_10, "quantity": 15, "price": Decimal("19.00")},
                {"pharmacy": p7, "medicine": pcm_650, "quantity": 10, "price": Decimal("38.50")},

                # Pharmacy 8: ANAND MEDICAL (AVAILABLE)
                {"pharmacy": p8, "medicine": pcm_500, "quantity": 14, "price": Decimal("28.00")},
                {"pharmacy": p8, "medicine": ibup_400, "quantity": 20, "price": Decimal("28.50")},
                {"pharmacy": p8, "medicine": pcm_syrup, "quantity": 12, "price": Decimal("54.00")},

                # Pharmacy 9: HEALTH PRO PHARMACY (LOW_STOCK)
                {"pharmacy": p9, "medicine": pcm_500, "quantity": 2, "price": Decimal("29.00")},
                {"pharmacy": p9, "medicine": amox_500, "quantity": 8, "price": Decimal("88.00")},
                {"pharmacy": p9, "medicine": cetz_10, "quantity": 18, "price": Decimal("18.00")},

                # Pharmacy 10: Genericart Sanjeevini (AVAILABLE)
                {"pharmacy": p10, "medicine": pcm_500, "quantity": 50, "price": Decimal("25.00")},
                {"pharmacy": p10, "medicine": pcm_650, "quantity": 35, "price": Decimal("35.00")},
                {"pharmacy": p10, "medicine": amox_500, "quantity": 20, "price": Decimal("80.00")},
                {"pharmacy": p10, "medicine": glyco_500, "quantity": 30, "price": Decimal("38.00")},
                {"pharmacy": p10, "medicine": cetz_10, "quantity": 25, "price": Decimal("17.50")},
                {"pharmacy": p10, "medicine": ibup_400, "quantity": 15, "price": Decimal("27.00")},

                # Pharmacy 11: PADMASHREE MEDICAL - Bengaluru (AVAILABLE)
                {"pharmacy": p11, "medicine": pcm_500, "quantity": 18, "price": Decimal("31.00")},
                {"pharmacy": p11, "medicine": pcm_650, "quantity": 14, "price": Decimal("41.00")},
                {"pharmacy": p11, "medicine": azee_500, "quantity": 6, "price": Decimal("118.00")},
                {"pharmacy": p11, "medicine": augmentin_625, "quantity": 0, "price": Decimal("130.00")},

                # Pharmacy 12: Varsha Medical (LOW_STOCK)
                {"pharmacy": p12, "medicine": pcm_500, "quantity": 7, "price": Decimal("28.50")},
                {"pharmacy": p12, "medicine": cetz_10, "quantity": 20, "price": Decimal("18.00")},
                {"pharmacy": p12, "medicine": glyco_500, "quantity": None, "price": Decimal("44.00")},

                # Pharmacy 13: Pandurang Medical (OUT_OF_STOCK)
                {"pharmacy": p13, "medicine": pcm_500, "quantity": 0, "price": Decimal("29.00")},
                {"pharmacy": p13, "medicine": pcm_650, "quantity": 12, "price": Decimal("39.00")},
                {"pharmacy": p13, "medicine": ibup_400, "quantity": 15, "price": Decimal("29.50")},

                # Pharmacy 14: Vedang Medicals (AVAILABLE)
                {"pharmacy": p14, "medicine": pcm_500, "quantity": 12, "price": Decimal("28.00")},
                {"pharmacy": p14, "medicine": pcm_syrup, "quantity": 15, "price": Decimal("55.00")},
                {"pharmacy": p14, "medicine": amox_250, "quantity": 10, "price": Decimal("44.00")},

                # Pharmacy 15: SHRI CHANDRA PRABHA (LOW_STOCK)
                {"pharmacy": p15, "medicine": pcm_500, "quantity": 3, "price": Decimal("29.50")},
                {"pharmacy": p15, "medicine": cetz_10, "quantity": 8, "price": Decimal("19.00")},
                {"pharmacy": p15, "medicine": pcm_650, "quantity": 20, "price": Decimal("40.00")},
                {"pharmacy": p15, "medicine": augmentin_625, "quantity": 10, "price": Decimal("122.00")},

                # Pharmacy 16: Wellness Forever Tilakwadi - Superstore (AVAILABLE)
                {"pharmacy": p16, "medicine": pcm_500, "quantity": 80, "price": Decimal("30.00")},
                {"pharmacy": p16, "medicine": pcm_650, "quantity": 60, "price": Decimal("42.00")},
                {"pharmacy": p16, "medicine": pcm_syrup, "quantity": 30, "price": Decimal("58.00")},
                {"pharmacy": p16, "medicine": amox_250, "quantity": 25, "price": Decimal("46.00")},
                {"pharmacy": p16, "medicine": amox_500, "quantity": 30, "price": Decimal("85.00")},
                {"pharmacy": p16, "medicine": augmentin_625, "quantity": 25, "price": Decimal("125.00")},
                {"pharmacy": p16, "medicine": cetz_10, "quantity": 50, "price": Decimal("18.00")},
                {"pharmacy": p16, "medicine": ibup_400, "quantity": 40, "price": Decimal("30.00")},
                {"pharmacy": p16, "medicine": azee_500, "quantity": 20, "price": Decimal("112.00")},
                {"pharmacy": p16, "medicine": glyco_500, "quantity": 50, "price": Decimal("40.00")},

                # Pharmacy 17: Pragati Pharma (AVAILABLE)
                {"pharmacy": p17, "medicine": pcm_500, "quantity": 15, "price": Decimal("28.50")},
                {"pharmacy": p17, "medicine": amox_500, "quantity": 12, "price": Decimal("86.00")},
                {"pharmacy": p17, "medicine": glyco_500, "quantity": 25, "price": Decimal("41.00")},
                {"pharmacy": p17, "medicine": azee_500, "quantity": 8, "price": Decimal("116.00")},

                # Pharmacy 18: Mediclass Medicals CA - Bengaluru (UNKNOWN)
                {"pharmacy": p18, "medicine": pcm_500, "quantity": None, "price": Decimal("32.00")},
                {"pharmacy": p18, "medicine": cetz_10, "quantity": 10, "price": Decimal("19.50")},
                {"pharmacy": p18, "medicine": pcm_650, "quantity": 0, "price": Decimal("42.00")},

                # Pharmacy 19: Shree Laxmi Medical (LOW_STOCK)
                {"pharmacy": p19, "medicine": pcm_500, "quantity": 6, "price": Decimal("29.00")},
                {"pharmacy": p19, "medicine": ibup_400, "quantity": 14, "price": Decimal("29.00")},
                {"pharmacy": p19, "medicine": pcm_syrup, "quantity": 5, "price": Decimal("53.00")},

                # Pharmacy 20: Apollo Rani Channamma Nagar (AVAILABLE)
                {"pharmacy": p20, "medicine": pcm_500, "quantity": 35, "price": Decimal("28.50")},
                {"pharmacy": p20, "medicine": pcm_650, "quantity": 25, "price": Decimal("39.00")},
                {"pharmacy": p20, "medicine": augmentin_625, "quantity": 15, "price": Decimal("120.00")},
                {"pharmacy": p20, "medicine": cetz_10, "quantity": 30, "price": Decimal("18.00")},
                {"pharmacy": p20, "medicine": amox_500, "quantity": 18, "price": Decimal("84.00")},
                {"pharmacy": p20, "medicine": glyco_500, "quantity": 35, "price": Decimal("39.00")},
            ]

            for inv_spec in inventory_definitions:
                Inventory.objects.get_or_create(
                    pharmacy=inv_spec["pharmacy"],
                    medicine=inv_spec["medicine"],
                    defaults={
                        "quantity": inv_spec["quantity"],
                        "price": inv_spec["price"],
                        "is_demo": True,
                    }
                )

            # ------------------------------------------------------------------
            # 10. Seed Initial Audit Log Entries
            # ------------------------------------------------------------------
            for p_name, pharm in pharmacies.items():
                if pharm.verification_status == VerificationStatus.VERIFIED:
                    AuditLog.objects.get_or_create(
                        action='PHARMACY_VERIFIED',
                        target_type='Pharmacy',
                        target_id=str(pharm.id),
                        defaults={
                            'actor': admin_user,
                            'metadata': {'pharmacy_name': pharm.name, 'license': pharm.license_number},
                            'ip_address': '127.0.0.1',
                        }
                    )

            AuditLog.objects.get_or_create(
                action='PHARMACY_REJECTED',
                target_type='Pharmacy',
                target_id=str(pharm_sunrise.id),
                defaults={
                    'actor': admin_user,
                    'metadata': {'pharmacy_name': pharm_sunrise.name, 'reason': pharm_sunrise.rejection_reason},
                    'ip_address': '127.0.0.1',
                }
            )

        # ----------------------------------------------------------------------
        # 11. Output Local Development Demonstration Report
        # ----------------------------------------------------------------------
        self.stdout.write("\n" + self.style.SUCCESS("[OK] 20 Primary demo pharmacies seeded successfully."))
        self.stdout.write("\n" + "-" * 115)
        self.stdout.write("DEMONSTRATION USER ACCOUNTS (DEVELOPMENT ONLY):")
        self.stdout.write("-" * 115)

        accounts_data = [
            ("admin_demo", "AdminDemoPass123!", "ADMIN", admin_user.id, "N/A", "N/A", "Admin Portal (/admin/dashboard)"),
            ("patient_demo_01", "PatientPass123!", "USER", patient_1.id, "N/A", "N/A", "Patient Portal (/app)"),
            ("patient_demo_02", "PatientPass123!", "USER", patient_2.id, "N/A", "N/A", "Patient Portal (/app)"),
        ]

        for p_spec in PRIMARY_DEMO_PHARMACIES:
            uname = p_spec["owner_username"]
            u = pharmacists[uname]
            pharm = pharmacies[p_spec["name"]]
            accounts_data.append(
                (uname, "PharmaPass123!", "PHARMACIST", u.id, str(pharm.id), "VERIFIED", f"Pharmacist Portal ({pharm.name[:25]}...)")
            )

        accounts_data.append(
            ("pharmacist_demo_pending", "PharmaPass123!", "PHARMACIST", pharmacists["pharmacist_demo_pending"].id, str(pharm_greencross.id), "PENDING", "Pharmacist Portal (GreenCross Pending)")
        )
        accounts_data.append(
            ("pharmacist_demo_rejected", "PharmaPass123!", "PHARMACIST", pharmacists["pharmacist_demo_rejected"].id, str(pharm_sunrise.id), "REJECTED", "Pharmacist Portal (Sunrise Rejected)")
        )

        header = f"{'Username':<26} | {'Role':<11} | {'User ID':<8} | {'Pharma ID':<10} | {'Status':<10} | {'Portal Destination':<40}"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))
        for u, _, r, uid, pid, st, dest in accounts_data:
            self.stdout.write(f"{u:<26} | {r:<11} | {uid:<8} | {pid:<10} | {st:<10} | {dest:<40}")

        self.stdout.write("\n" + "-" * 115)
        self.stdout.write("20 PRIMARY DEMO PHARMACIES NETWORK (EXACT LISTINGS):")
        self.stdout.write("-" * 115)

        p_header = f"{'Pharmacy Name':<48} | {'ID':<4} | {'City':<9} | {'Phone':<15} | {'Stock':<5} | {'PCM 500mg Status'}"
        self.stdout.write(p_header)
        self.stdout.write("-" * len(p_header))
        for p_spec in PRIMARY_DEMO_PHARMACIES:
            pharm = pharmacies[p_spec["name"]]
            inv_count = pharm.inventory_records.count()
            pcm_inv = pharm.inventory_records.filter(medicine=pcm_500).first()
            if pcm_inv:
                status_key, _ = pcm_inv.get_availability_status()
                qty_str = f"qty: {pcm_inv.quantity}" if pcm_inv.quantity is not None else "qty: Unknown"
                pcm_label = f"{status_key} ({qty_str}, Rs {pcm_inv.price})"
            else:
                pcm_label = "No Record"
            phone_display = pharm.contact_number or "None"
            self.stdout.write(f"{pharm.name:<48} | {pharm.id:<4} | {pharm.city:<9} | {phone_display:<15} | {inv_count:<5} | {pcm_label}")

        self.stdout.write("-" * len(p_header))
        self.stdout.write(f"{pharm_greencross.name:<48} | {pharm_greencross.id:<4} | {pharm_greencross.city:<9} | {pharm_greencross.contact_number:<15} | {pharm_greencross.inventory_records.count():<5} | PENDING ADMIN APPROVAL")
        self.stdout.write(f"{pharm_sunrise.name:<48} | {pharm_sunrise.id:<4} | {pharm_sunrise.city:<9} | {pharm_sunrise.contact_number:<15} | {pharm_sunrise.inventory_records.count():<5} | REJECTED (Expired License)")

        self.stdout.write("\n" + "-" * 115)
        self.stdout.write("DATABASE METRICS OVERVIEW:")
        self.stdout.write(f"Total Users: {User.objects.count()} (Patients: {UserProfile.objects.filter(role=UserRole.USER).count()}, Pharmacists: {UserProfile.objects.filter(role=UserRole.PHARMACIST).count()}, Admins: {UserProfile.objects.filter(role=UserRole.ADMIN).count()})")
        self.stdout.write(f"Total Pharmacies: {Pharmacy.objects.count()} (Verified: {Pharmacy.objects.filter(verification_status=VerificationStatus.VERIFIED).count()}, Pending: {Pharmacy.objects.filter(verification_status=VerificationStatus.PENDING).count()}, Rejected: {Pharmacy.objects.filter(verification_status=VerificationStatus.REJECTED).count()})")
        self.stdout.write(f"Total Formulary Medicines: {Medicine.objects.count()}")
        self.stdout.write(f"Total Inventory Records: {Inventory.objects.count()} (Available: {Inventory.objects.filter(quantity__gte=10).count()}, Low Stock: {Inventory.objects.filter(quantity__gt=0, quantity__lt=10).count()}, Out of Stock: {Inventory.objects.filter(quantity=0).count()}, Unknown: {Inventory.objects.filter(quantity__isnull=True).count()})")
        self.stdout.write(f"Total Audit Entries: {AuditLog.objects.count()}")
        self.stdout.write("=" * 115 + "\n")
