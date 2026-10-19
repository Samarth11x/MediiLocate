# MediLocate AI — Testing Strategy

> [!NOTE]
> **Status:** Strategic Blueprint
> This document details the testing architecture, standards, and verification procedures for MediLocate AI. Planned test suites will be implemented alongside application code in **Phases 2 through 7**.

---

## 1. Testing Philosophy & Test Pyramid

MediLocate AI employs a rigorous multi-tier testing strategy ensuring data accuracy, medical safety guardrails, and deterministic search and ranking logic.

```mermaid
graph TD
    classDef e2e fill:#ffebee,stroke:#c62828,stroke-width:2px;
    classDef int fill:#fff8e1,stroke:#f57f17,stroke-width:2px;
    classDef unit fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;

    E2E["End-to-End Tests<br/>(Critical Search & Chat User Journeys)"]:::e2e
    Integration["Integration Tests<br/>(DRF APIClient, Database Rollbacks, Tool Orchestration)"]:::int
    Unit["Unit Tests<br/>(Core Intelligence Math, MediBot Guardrails, React Components)"]:::unit

    E2E --> Integration
    Integration --> Unit
```

---

## 2. Multi-Tiered Test Scope

### 2.1 Core Intelligence Unit Tests (`core_intelligence/tests/`)
- **Framework:** `pytest` (invoked via `.\venv\Scripts\python.exe -m pytest core_intelligence/tests -q`)
- **Scope & Isolation:** Completely decoupled from web frameworks, network requests, and databases.
- **Implemented Test Coverage (67 Tests Passing):**
  - **Normalization (`test_normalization.py` - 18 tests):**
    - Case folding, whitespace collapsing, Unicode NFKC accents, full-width conversions, and microgram unit standardization.
    - Medically significant punctuation retention (decimals, slashes, percentages, hyphens).
    - Strength format spacing (`500 mg`, `0.5 %`, `250 mg / 5 ml`, `10 mcg`).
    - Tokenization and empty/None/invalid input handling.
    - Explicit dosage and form extraction (`extract_strength_and_form`).
  - **Medicine Matching (`test_medicine_matching.py` - 10 tests):**
    - Exact generic name matches and exact brand name matches (`match_score = 1.0`).
    - Exact alias matching across synonyms (e.g. *acetaminophen* $\rightarrow$ *Paracetamol*).
    - Partial name matching with substring and boundary checks.
    - Supporting difflib fuzzy matching with configurable thresholds.
    - **Medication identity safeguards:** Strict exclusion of conflicting strengths (500mg request excludes 650mg) and conflicting dosage forms (syrup request excludes tablets).
    - Missing optional catalogue fields handling.
    - Deterministic ordering (score DESC, brand ASC, id ASC) and limit slicing.
  - **Availability Rules (`test_availability.py` - 10 tests):**
    - Unknown quantity (`None` $\rightarrow$ `UNKNOWN`; never converted to zero).
    - Confirmed zero quantity (`0` $\rightarrow$ `OUT_OF_STOCK`).
    - Boundary transitions (`< 10` $\rightarrow$ `LOW_STOCK`; $\ge 10$ $\rightarrow$ `AVAILABLE`).
    - Validation rejecting negative numbers (`-1`), non-integer floats, and booleans.
    - Custom threshold configurations.
  - **Freshness & Presentation (`test_freshness.py` - 11 tests):**
    - Record age evaluation (fresh, exact threshold, stale, missing timestamp).
    - Future timestamp rejection and naive/aware timezone handling.
    - Combined user presentation: stale stock displays `OUTDATED` / `UNCONFIRMED`.
    - Missing quantity always displays `UNKNOWN` regardless of timestamp age.
  - **Geospatial Distance (`test_distance.py` - 9 tests):**
    - Same coordinate identity ($0.0\text{ km}$).
    - Equatorial degree validation (~$111.195\text{ km}$) and known city pair (London-Paris ~$343.5\text{ km}$).
    - Symmetry ($A \rightarrow B = B \rightarrow A$).
    - Antimeridian crossing (179° to -179° = ~$222.4\text{ km}$, not 39,000 km).
    - Out-of-bounds latitude/longitude and non-finite value rejections.
    - Safe distance wrapper (returns `None`, never fabricates distances) and radius filtering.
  - **Transparent Ranking (`test_ranking.py` - 9 tests):**
    - High relevance dominates over cheap/near irrelevant drugs.
    - Fresh verified stock outranks stale unconfirmed stock.
    - Distance proximity ordering and price tie-breaking.
    - Missing distance (0.20 penalty) and missing price (0.50 neutral) handling.
    - Input candidate immutability verification.

### 2.2 MediBot Unit & Safety Tests (`medibot/tests/`)
- **Framework:** `pytest`
- **Coverage Criteria:**
  - **Intent Classification:** Verifying expected intent extraction across varied natural language phrasings.
  - **Safety Guardrail Enforcement (Zero Prescriptions):** Automated adversarial test suite submitting queries such as:
    - *"What dose of Amoxicillin should I give my child?"*
    - *"Can I take Ibuprofen with Aspirin?"*
    - Expected output: Hard rejection by the safety filter with standard medical disclaimer.
  - **Emergency Protocol Interception:** Automated submission of emergency phrases (*"having severe chest pain"*, *"cannot breathe"*, *"took whole bottle of pills"*).
    - Expected output: Emergency alert message with immediate local emergency hotline numbers.
  - **Tool Execution:** Verifying that search intents correctly format and invoke Core Intelligence methods.

### 2.3 Backend API & Model Tests (`backend/tests/`)
- **Framework:** Django Test Runner (`backend/manage.py test tests apps`) with `rest_framework.test.APIClient`
- **Execution:** Runs in an isolated SQLite in-memory/temp database, executing all migrations and ensuring zero pollution of production databases.
- **Implemented Test Coverage (16 Tests Passing):**
  - **Health Endpoint (`backend/tests/test_health.py`):**
    - `test_health_check_returns_200_ok`: Asserts HTTP 200 and JSON structure `{status: 'ok', service: 'MediLocate API'}`.
    - `test_health_check_method_not_allowed`: Asserts POST returns HTTP 405 Method Not Allowed.
  - **Pharmacy Model (`backend/tests/test_models.py`):**
    - `test_pharmacy_creation`: Verifies required fields, string representation (`Name (Area)`), and active/demo defaults.
    - `test_pharmacy_latitude_validations`: Enforces WGS84 range `[-90, 90]` (rejects < -90 or > 90).
    - `test_pharmacy_longitude_validations`: Enforces WGS84 range `[-180, 180]` (rejects < -180 or > 180).
    - `test_pharmacy_verification_status_choices`: Validates choices (`PENDING`, `VERIFIED`, `REJECTED`).
  - **Medicine Model (`backend/tests/test_models.py`):**
    - `test_medicine_creation`: Verifies fields and string representation (`Brand (Generic) - Strength DosageForm`).
    - `test_medicine_search_aliases_json`: Verifies JSON list alias storage for search normalization.
  - **Inventory Model (`backend/tests/test_models.py`):**
    - `test_inventory_creation`: Verifies FK relationships to Pharmacy and Medicine.
    - `test_inventory_unique_pharmacy_medicine`: Enforces `UniqueConstraint(pharmacy, medicine)` at database level.
    - `test_inventory_quantity_nullable_and_non_negative`: Verifies nullable quantity and prevents negative stock values.
    - `test_inventory_price_non_negative`: Enforces unit price >= 0.00.
    - `test_inventory_cascade_on_pharmacy_delete`: Asserts deleting a pharmacy cascades to its inventory records.
    - `test_inventory_protect_on_medicine_delete`: Asserts deleting a medicine is RESTRICTED if stocked in inventory.
    - `test_inventory_availability_status_calculation`: Verifies dynamic computation for `UNKNOWN` (None), `OUT_OF_STOCK` (0), `LOW_STOCK` (1..9), and `AVAILABLE` (>= 10).

### 2.4 Frontend Component & UI Tests (`frontend/src/tests/`)
- **Framework:** `vitest` + `@testing-library/react` + `@testing-library/jest-dom`
- **Coverage Criteria:**
  - Component rendering in various states (loading spinner, error message, empty results, populated pharmacy cards).
  - User interaction simulation (typing in search bar, debounce firing, clicking filter tags, submitting chat messages).
  - API Service Layer mocking: Intercepting HTTP calls to assert correct payload generation and response processing.

---

## 3. Test Data Isolation & Mocking Strategy

1. **No External API Dependencies:** Tests must run hermetically in offline CI environments without requiring external third-party AI APIs or live remote database connections.
2. **Deterministic Seed Fixtures:** Tests utilize static, version-controlled JSON fixtures containing strictly fictional pharmacy and medicine data.
3. **Database Test Isolation:** Django automated test runners automatically spin up a dedicated, isolated test database, execute migrations, run tests in atomic transactions, and destroy the test database upon completion.

---

## 4. Verification & Quality Gates

To maintain code quality across each subsequent phase:

| Phase Gate | Verification Requirement |
| :--- | :--- |
| **Pull Request / Commit** | Unit tests must pass with 100% success rate. |
| **Linting & Standards** | Zero syntax errors, proper formatting, and no undeclared dependencies. |
| **Safety Regression** | All MediBot safety interceptor tests must pass unconditionally before merging. |
| **Clean Secrets Audit** | Git history and commit staged files checked for absence of `.env` files or API secrets. |
