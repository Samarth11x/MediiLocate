"""
Management command to seed local development database with demonstration data.

Provides:
- Representative medicine catalog entries (including Paracetamol 500mg and distinct strengths/forms
  to verify Core Intelligence matching safeguards).
- Fictional, clearly-labeled demonstration pharmacies with valid WGS84 coordinates.
- Demonstration inventory links covering all availability states (Available, Low Stock, Out of Stock, Unknown).

Idempotent: Rerunning this command updates or preserves existing records without duplicates.
Safe: Refuses to execute in production environments.
"""

from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

from apps.medicines.models import Medicine
from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.inventory.models import Inventory


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

DEMO_PHARMACIES = [
    {
        "name": "Demo CarePoint Pharmacy (Fictional Dev)",
        "address": "Plot 101, Fictional Healthcare Lane, Koramangala 4th Block",
        "area": "Koramangala",
        "city": "Bengaluru",
        "pin_code": "560034",
        "latitude": Decimal("12.935242"),
        "longitude": Decimal("77.624480"),
        "contact_number": "+91 99999 00001",
        "verification_status": VerificationStatus.VERIFIED,
        "opening_hours": {"mon_fri": "09:00 - 21:00", "sat": "09:00 - 20:00", "sun": "Closed"},
    },
    {
        "name": "Demo Metro Chemist (Fictional Dev)",
        "address": "Shop 12, Fictional Retail Arcade, 100ft Road, Indiranagar",
        "area": "Indiranagar",
        "city": "Bengaluru",
        "pin_code": "560038",
        "latitude": Decimal("12.971891"),
        "longitude": Decimal("77.641154"),
        "contact_number": "+91 99999 00002",
        "verification_status": VerificationStatus.VERIFIED,
        "opening_hours": {"mon_sat": "08:00 - 22:00", "sun": "10:00 - 18:00"},
    },
    {
        "name": "Demo Apollo Life Chemist (Fictional Dev)",
        "address": "Building 45, Fictional Hospital Road, 4th T Block, Jayanagar",
        "area": "Jayanagar",
        "city": "Bengaluru",
        "pin_code": "560041",
        "latitude": Decimal("12.929869"),
        "longitude": Decimal("77.584347"),
        "contact_number": "+91 99999 00003",
        "verification_status": VerificationStatus.VERIFIED,
        "opening_hours": {"mon_sun": "24 Hours Open (Demo)"},
    },
    {
        "name": "Demo GreenCross Meds (Fictional Dev - Unverified)",
        "address": "Corner Store 7, Fictional Tech Corridor, Whitefield Main Road",
        "area": "Whitefield",
        "city": "Bengaluru",
        "pin_code": "560066",
        "latitude": Decimal("12.969819"),
        "longitude": Decimal("77.749942"),
        "contact_number": "+91 99999 00004",
        "verification_status": VerificationStatus.PENDING,
        "opening_hours": {"mon_fri": "10:00 - 19:00", "sat_sun": "Closed"},
    },
]


class Command(BaseCommand):
    help = "Seed local development database with fictional demo medicines, pharmacies, and inventory."

    def handle(self, *args, **options):
        # 1. Environment and database safety check
        env_mode = getattr(settings, "DJANGO_ENV", "").lower()
        if env_mode == "production":
            raise CommandError(
                "Refusing to seed demonstration data: DJANGO_ENV is set to 'production'."
            )

        db_engine = settings.DATABASES["default"]["ENGINE"]
        db_name = str(settings.DATABASES["default"]["NAME"])
        self.stdout.write(
            f"Active database: {db_engine} (Target: {db_name}, Environment: {env_mode or 'development'})"
        )

        with transaction.atomic():
            # 2. Seed Medicines
            med_created_count = 0
            med_updated_count = 0
            medicines_by_key = {}

            for med_data in DEMO_MEDICINES:
                lookup_key = (
                    med_data["generic_name"],
                    med_data["strength"],
                    med_data["dosage_form"],
                )
                med_obj, created = Medicine.objects.update_or_create(
                    generic_name=med_data["generic_name"],
                    strength=med_data["strength"],
                    dosage_form=med_data["dosage_form"],
                    defaults={
                        "brand_name": med_data["brand_name"],
                        "pack_size": med_data["pack_size"],
                        "search_aliases": med_data["search_aliases"],
                    },
                )
                medicines_by_key[lookup_key] = med_obj
                if created:
                    med_created_count += 1
                else:
                    med_updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Medicines: {med_created_count} created, {med_updated_count} updated (Total: {len(medicines_by_key)})"
                )
            )

            # 3. Seed Pharmacies
            pharm_created_count = 0
            pharm_updated_count = 0
            pharmacies_by_name = {}

            for pharm_data in DEMO_PHARMACIES:
                pharm_obj, created = Pharmacy.objects.update_or_create(
                    name=pharm_data["name"],
                    city=pharm_data["city"],
                    defaults={
                        "address": pharm_data["address"],
                        "area": pharm_data["area"],
                        "pin_code": pharm_data["pin_code"],
                        "latitude": pharm_data["latitude"],
                        "longitude": pharm_data["longitude"],
                        "contact_number": pharm_data["contact_number"],
                        "verification_status": pharm_data["verification_status"],
                        "opening_hours": pharm_data["opening_hours"],
                        "is_demo": True,
                    },
                )
                pharmacies_by_name[pharm_data["name"]] = pharm_obj
                if created:
                    pharm_created_count += 1
                else:
                    pharm_updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Pharmacies: {pharm_created_count} created, {pharm_updated_count} updated (Total: {len(pharmacies_by_name)})"
                )
            )

            # 4. Seed Inventory Links
            # Demonstrates all 4 availability states: AVAILABLE, LOW_STOCK, OUT_OF_STOCK, UNKNOWN
            p1 = pharmacies_by_name["Demo CarePoint Pharmacy (Fictional Dev)"]
            p2 = pharmacies_by_name["Demo Metro Chemist (Fictional Dev)"]
            p3 = pharmacies_by_name["Demo Apollo Life Chemist (Fictional Dev)"]
            p4 = pharmacies_by_name["Demo GreenCross Meds (Fictional Dev - Unverified)"]

            pcm_500 = medicines_by_key[("Paracetamol", "500mg", "Tablet")]
            pcm_650 = medicines_by_key[("Paracetamol", "650mg", "Tablet")]
            pcm_syrup = medicines_by_key[("Paracetamol", "250mg/5ml", "Syrup")]
            amox_500 = medicines_by_key[("Amoxicillin", "500mg", "Capsule")]
            cetz_10 = medicines_by_key[("Cetirizine Hydrochloride", "10mg", "Tablet")]
            ibup_400 = medicines_by_key[("Ibuprofen", "400mg", "Tablet")]
            azee_500 = medicines_by_key[("Azithromycin", "500mg", "Tablet")]

            demo_inventory_data = [
                # Paracetamol 500mg in all 4 availability states across different stores
                {"pharmacy": p1, "medicine": pcm_500, "quantity": 45, "price": Decimal("30.50")},    # AVAILABLE
                {"pharmacy": p2, "medicine": pcm_500, "quantity": 5, "price": Decimal("32.00")},     # LOW_STOCK
                {"pharmacy": p3, "medicine": pcm_500, "quantity": 0, "price": Decimal("29.00")},     # OUT_OF_STOCK
                {"pharmacy": p4, "medicine": pcm_500, "quantity": None, "price": Decimal("31.00")},  # UNKNOWN
                # Different strengths and forms to test safeguards
                {"pharmacy": p1, "medicine": pcm_650, "quantity": 25, "price": Decimal("40.00")},    # Dolo 650mg
                {"pharmacy": p2, "medicine": pcm_syrup, "quantity": 12, "price": Decimal("55.00")},  # Calpol syrup
                {"pharmacy": p1, "medicine": amox_500, "quantity": 18, "price": Decimal("85.00")},   # Amox 500mg
                {"pharmacy": p2, "medicine": cetz_10, "quantity": 60, "price": Decimal("25.00")},    # Cetzine 10mg
                {"pharmacy": p3, "medicine": ibup_400, "quantity": 22, "price": Decimal("35.00")},   # Brufen 400mg
                {"pharmacy": p1, "medicine": azee_500, "quantity": 8, "price": Decimal("110.00")},   # Azee 500mg (LOW_STOCK)
            ]

            inv_created_count = 0
            inv_updated_count = 0

            for inv_item in demo_inventory_data:
                inv_obj, created = Inventory.objects.update_or_create(
                    pharmacy=inv_item["pharmacy"],
                    medicine=inv_item["medicine"],
                    defaults={
                        "quantity": inv_item["quantity"],
                        "price": inv_item["price"],
                        "is_demo": True,
                    },
                )
                if created:
                    inv_created_count += 1
                else:
                    inv_updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Inventory: {inv_created_count} created, {inv_updated_count} updated (Total: {len(demo_inventory_data)})"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully populated local development database with demo data."
            )
        )
