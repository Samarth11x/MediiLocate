"""
Deliberate, safe initial population command for hosted demonstration environments.

PURPOSE:
Populates the hosted PostgreSQL database with the 20 primary user-provided pharmacy
directory listings and a standard medicine formulary for demonstration purposes.

SECURITY & ARCHITECTURAL SAFEGUARDS:
1. ZERO CREDENTIAL EXPOSURE:
   Does NOT create any User accounts, passwords, or pharmacist credentials.
   Pharmacies are created with owner=None (unclaimed/directory listing).
2. NO LOCAL DATA COPYING:
   Does not import local SQLite files or export local development passwords.
3. CONSPICUOUS DEMONSTRATION DISCLOSURE:
   All created records have is_demo=True.
   Inventory stock levels and prices are explicitly marked as sample values.
4. NO DISTANCE FABRICATION:
   Coordinates (latitude, longitude) remain strictly NULL where not provided.
5. IDEMPOTENT & PRESERVES MANUAL EDITS:
   Uses get_or_create; if a record already exists, manual edits by administrators
   or newly registered pharmacists are preserved and not overwritten.
6. DELIBERATE EXECUTION ONLY:
   Requires explicit --confirm flag to run.
   Never executed automatically during build.sh or application startup.
"""

from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.medicines.models import Medicine
from apps.inventory.models import Inventory


# ------------------------------------------------------------------------------
# Standard Demonstrative Formulary (Non-confidential medical reference)
# ------------------------------------------------------------------------------

HOSTED_DEMO_MEDICINES = [
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
# Coordinates strictly None (no fabrication).
# Owner strictly None (no insecure demo accounts).
# ------------------------------------------------------------------------------

HOSTED_PRIMARY_PHARMACIES = [
    {
        "name": "Apollo Pharmacy Peeranwadi Belagavi",
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


# ------------------------------------------------------------------------------
# Diverse Sample Inventory Configuration (Paracetamol 500mg in all 20 stores)
# Demonstrates: AVAILABLE (>=10), LOW_STOCK (1-9), OUT_OF_STOCK (0), UNKNOWN (None)
# ------------------------------------------------------------------------------

SAMPLE_STOCK_DISTRIBUTION = [
    # (quantity, unit_price)
    (45, Decimal("30.00")),  # AVAILABLE
    (5,  Decimal("32.00")),  # LOW_STOCK
    (0,  Decimal("28.50")),  # OUT_OF_STOCK
    (None, Decimal("30.00")),# UNKNOWN
    (30, Decimal("31.00")),  # AVAILABLE
    (8,  Decimal("29.50")),  # LOW_STOCK
    (0,  Decimal("30.00")),  # OUT_OF_STOCK
    (55, Decimal("31.50")),  # AVAILABLE
    (None, None),            # UNKNOWN
    (22, Decimal("30.00")),  # AVAILABLE
    (4,  Decimal("33.00")),  # LOW_STOCK
    (60, Decimal("29.00")),  # AVAILABLE
    (0,  Decimal("30.50")),  # OUT_OF_STOCK
    (15, Decimal("31.00")),  # AVAILABLE
    (3,  Decimal("32.50")),  # LOW_STOCK
    (80, Decimal("30.00")),  # AVAILABLE
    (None, Decimal("29.00")),# UNKNOWN
    (25, Decimal("31.00")),  # AVAILABLE
    (7,  Decimal("30.50")),  # LOW_STOCK
    (50, Decimal("32.00")),  # AVAILABLE
]


class Command(BaseCommand):
    help = (
        "Deliberately populates the hosted PostgreSQL database with 20 user-provided "
        "pharmacies and standard demonstrative inventory. Zero user accounts or passwords created."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Explicit confirmation flag required to run this command.',
        )

    def handle(self, *args, **options):
        if not options.get('confirm'):
            raise CommandError(
                "Safety requirement: You must provide the --confirm flag to execute this command.\n"
                "Example: python manage.py seed_hosted_directory --confirm"
            )

        self.stdout.write("=" * 80)
        self.stdout.write("MEDILOCATE AI -- HOSTED DIRECTORY INITIALIZATION")
        self.stdout.write("Populating 20 verified pharmacies (owner=None, zero credentials created)...")
        self.stdout.write("=" * 80)

        with transaction.atomic():
            # 1. Seed standard demonstrative formulary
            created_meds = 0
            med_objects = {}
            for med_data in HOSTED_DEMO_MEDICINES:
                med, created = Medicine.objects.get_or_create(
                    generic_name=med_data["generic_name"],
                    brand_name=med_data["brand_name"],
                    strength=med_data["strength"],
                    dosage_form=med_data["dosage_form"],
                    defaults={
                        "pack_size": med_data["pack_size"],
                        "search_aliases": med_data["search_aliases"],
                    }
                )
                if created:
                    created_meds += 1
                med_objects[f"{med.brand_name}_{med.strength}"] = med

            self.stdout.write(f"[+] Medicines initialized: {len(med_objects)} ({created_meds} newly created)")

            # Primary medicine for stock demonstration across all stores
            primary_med = med_objects.get("Crocin_500mg")
            if not primary_med:
                primary_med = Medicine.objects.filter(generic_name="Paracetamol", strength="500mg").first()

            # 2. Seed the 20 primary user-provided pharmacies
            pharmacies_created = 0
            pharmacies_existing = 0
            inventory_created = 0

            for idx, p_data in enumerate(HOSTED_PRIMARY_PHARMACIES):
                pharm, created = Pharmacy.objects.get_or_create(
                    name=p_data["name"],
                    city=p_data["city"],
                    defaults={
                        "license_number": p_data["license_number"],
                        "address": p_data["address"],
                        "area": p_data["area"],
                        "pin_code": p_data["pin_code"],
                        "contact_number": p_data["contact_number"],
                        "opening_hours": p_data["opening_hours"],
                        "verification_status": p_data["verification_status"],
                        "owner": None,           # Invariant: No user account is attached or created!
                        "is_demo": True,         # Invariant: Conspicuous demonstration flag
                        "latitude": None,        # Invariant: No distance fabrication
                        "longitude": None,
                    }
                )

                if created:
                    pharmacies_created += 1
                else:
                    pharmacies_existing += 1

                # 3. Create sample inventory link for demonstrative search
                if primary_med:
                    qty, price = SAMPLE_STOCK_DISTRIBUTION[idx % len(SAMPLE_STOCK_DISTRIBUTION)]
                    inv, inv_created = Inventory.objects.get_or_create(
                        pharmacy=pharm,
                        medicine=primary_med,
                        defaults={
                            "quantity": qty,
                            "price": price,
                            "is_demo": True,
                        }
                    )
                    if inv_created:
                        inventory_created += 1

            self.stdout.write(
                f"[+] 20 Directory Pharmacies: {pharmacies_created} created, "
                f"{pharmacies_existing} preserved existing."
            )
            self.stdout.write(f"[+] Sample Inventory Links: {inventory_created} created.")
            self.stdout.write("=" * 80)
            self.stdout.write("HOSTED DIRECTORY POPULATION COMPLETE.")
            self.stdout.write("All listings are verified, owner=None, coordinates=None, and marked is_demo=True.")
            self.stdout.write("=" * 80)
