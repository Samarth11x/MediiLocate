# MediLocate AI — Development Roadmap

This roadmap establishes the phased engineering plan for developing the **MediLocate AI** platform. Each phase is gated by strict deliverables, verification checkpoints, and quality standards.

---

## Roadmap Overview

| Phase | Milestone | Primary Objective | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **Project Foundation** | Engineering standards, directory hierarchy, environment templates, docs | **COMPLETED** |
| **Phase 2** | **Frontend Foundation** | React + Vite setup, UI design system, component hierarchy, test suite | **COMPLETED** |
| **Phase 3** | **Backend & Supabase** | Django REST Framework, database schema, ORM models, API serializers | **COMPLETED** |
| **Phase 4** | **Core Intelligence** | Medicine search normalization, ranking heuristics, location engine | **COMPLETED** |
| **Phase 5** | **MediBot Conversational Layer** | Intent recognition, dialogue flows, safety interceptors, tool integration | **COMPLETED** |
| **Phase 6** | **Search & Pharmacy Workflows** | End-to-end integration of search, availability, inventory management, chat | Planned |
| **Phase 7** | **Integration, Security & QA** | E2E testing, penetration checks, performance optimization, release readiness | Planned |

---

## Detailed Phase Breakdown

### Phase 1: Project Foundation
- **Status:** **Completed**
- **Objectives:**
  - Establish complete project folder hierarchy according to the CTO directive.
  - Define system architecture, data models, setup guide, testing plan, and roadmap.
  - Configure `.gitignore` for Windows, Python, Django, Node.js, and Git.
  - Define `.env.example` with secure placeholder variables and no exposed secrets.
  - Verify baseline developer tooling (Node.js, npm, Python, Git) on the host environment.
- **Verification Gate:**
  - Directory structure matches specification exactly.
  - No secret credentials present in repository.
  - All documentation files authored and reviewed.

---

### Phase 2: Frontend Foundation & Design System
- **Status:** **Completed**
- **Objectives:**
  - Initialize React 18 + Vite JavaScript application inside `frontend/` using plain CSS.
  - Formulate and persist Clinical Minimalism design system (`design-system/medilocate-ai/MASTER.md` and `pages/homepage.md`).
  - Configure CSS design tokens (approved brand colors, typography, spacing, elevations, accessibility focus states).
  - Scaffold core component structures:
    - `common/`: `BrandMark`, `SiteHeader`, `SiteFooter`, `DemoModeBanner`, `SplashScreen`.
    - `layouts/`: `MainLayout`.
    - `pages/`: `HomePage` shell with hero, search validation preview, location preview, How It Works, and partner section.
  - Setup Vitest and React Testing Library for frontend component unit tests (7/7 tests passing).
  - Verify production compilation build (`vite build` succeeds).
- **Verification Gate:**
  - Vite dev server runs without errors.
  - Component unit tests pass in Vitest (7/7 passing).
  - Production build succeeds without errors.
  - Mandatory demo warning present and verified.

---

### Phase 3: Backend & Supabase Database
- **Status:** **Completed**
- **Objectives:**
  - Initialize Python virtual environment (`venv`) and install pinned dependencies: Django 5.1+, Django REST Framework 3.17+, Psycopg 3 (with precompiled Windows wheels), and django-cors-headers.
  - Structure modular Django applications under `backend/apps/`: `pharmacies`, `medicines`, `inventory`, `accounts`, `search`.
  - Implement enterprise-grade database configuration in `backend/config/settings.py` for Supabase PostgreSQL (SSL `require`, session pooler support) with automatic fallback to local SQLite for offline development.
  - Implement relational domain models with database-level constraints:
    - `Pharmacy`: WGS84 latitude/longitude range validation (`[-90, 90]`, `[-180, 180]`), verification status workflow (`PENDING`, `VERIFIED`, `REJECTED`), JSON operating hours, and demo flag.
    - `Medicine`: Catalog model decoupled from pharmacy stock, capturing generic and brand names, dosage form, strength, and search aliases.
    - `Inventory`: Links pharmacy and medicine via `UniqueConstraint(pharmacy, medicine)`, non-negative price/quantity checks, nullable quantity for unknown stock, and dynamic `get_availability_status()` evaluation.
  - Generate initial Django migrations (`0001_initial.py` for medicines, pharmacies, inventory).
  - Implement lightweight `/api/v1/health/` liveness check endpoint returning `{ "status": "ok", "service": "MediLocate API" }`.
  - Register domain models with Django Admin interface (`apps/*/admin.py`).
  - Construct comprehensive automated backend test suite (16/16 tests passing).
- **Verification Gate:**
  - Django system check passes with 0 issues (`python backend/manage.py check`).
  - Health check endpoint `/api/v1/health/` returns `200 OK`.
  - Backend test suite passes 100% (16/16 tests in `backend/tests/`).
  - Frontend test suite remains intact with zero regressions (7/7 Vitest tests).

---

### Phase 4: Core Intelligence Module
- **Status:** **Completed**
- **Objectives:**
  - Perform backend dependency upgrade to supported Django 5.2.18 LTS and DRF 3.18.3 without schema or migration rewrites.
  - Build standalone, framework-independent pure Python package in `core_intelligence/`:
    - **Search Engine (`search_engine/`):** Unicode/case normalization, strength unit spacing, punctuation stripping, tokenization, exact/partial/alias matching, and difflib fuzzy matching.
    - **Medication Identity Safeguards:** Strict strength matching (e.g. 500mg request rejects 650mg) and dosage form matching (e.g. syrup request rejects tablets); no unauthorized substitution.
    - **Availability & Freshness (`availability/`):** Canonical thresholds (`AVAILABLE`, `LOW_STOCK`, `OUT_OF_STOCK`, `UNKNOWN`), negative quantity rejection, record age evaluation, and `OUTDATED` unconfirmed presentation state.
    - **Location Engine (`location/`):** Validated Haversine distance formula ($R = 6371.0\text{ km}$), coordinate bounds validation, antimeridian crossing handling, and radius filtering.
    - **Ranking Engine (`ranking/`):** Transparent composite heuristic scoring (relevance 45%, availability & freshness 30%, distance 15%, price 10%), deterministic multi-key tie-breaking, input immutability, and human-readable explanation generation.
  - Refactor `Inventory.get_availability_status()` in Django to delegate to `core_intelligence.availability.rules.classify_availability`.
  - Construct comprehensive isolated pytest suite in `core_intelligence/tests/` (67/67 tests passing).
- **Verification Gate:**
  - 100% pytest pass rate across edge cases in `core_intelligence/tests/` (67/67 passed).
  - Zero imports of Django, database drivers, or frontend libraries in `core_intelligence`.
  - Django test suite passes 100% (16/16 passed).
  - Frontend test suite and build pass cleanly (7/7 tests passed, build clean).

---

### Phase 5: MediBot Conversational Layer
- **Status:** **Completed**
- **Objectives:**
  - Build standalone conversational logic in `medibot/` completely decoupled from Django ORM and PostgreSQL.
  - Implement **Safety Subsystem (`safety/`)**:
    - `input_validation.py`: Strict type enforcement, length bounding ($\le 500$ chars), and non-string/empty rejection.
    - `emergency.py`: Acute medical emergency detection (chest pain, breathing difficulty, stroke, overdose, severe hemorrhage) with immediate emergency hotline guidance (112 / 108 / 911).
    - `safety_rules.py`: Medical advice guardrail intercepting prescription, diagnosis, dosage calculation, and drug alteration requests.
  - Implement **Intent Classifier (`intents/`)**: Deterministic regex-based classifier with safety precedence covering 8 intents (`EMERGENCY_CONCERN`, `MEDICAL_ADVICE`, `GREETING`, `HOW_IT_WORKS`, `PHARMACY_ONBOARDING`, `AVAILABILITY_HELP`, `PHARMACY_SEARCH`, `MEDICINE_SEARCH`, and `UNKNOWN`).
  - Implement **Tool Adapters (`tools/`)**:
    - `MedicineSearchTool`: Delegates to `core_intelligence.search_engine.matching.search_medicines` via injected catalogue provider.
    - `PharmacySearchTool`: Honest placeholder returning unavailable status without fabricating fake stores.
  - Implement **Dialogue Manager (`dialogue/`)**: Stateless and multi-turn state coordination (`awaiting_medicine_name`), producing standardized `MediBotResponse` JSON payloads.
  - Implement **Backend DRF Endpoint**: `POST /api/v1/chat/` with strict payload validation, HTTP 400 for bad inputs, HTTP 405 for invalid methods, and safe HTTP 500 fallback.
  - Enforce **Stateless Privacy by Design**: Zero database persistence of chat transcripts or queries.
- **Verification Gate:**
  - 100% pytest pass rate in `medibot/tests/` (48/48 passed).
  - 100% pass rate in Django test suite (29/29 passed, including 13 chat API tests).
  - 100% pass rate in `core_intelligence/tests/` (67/67 passed).
  - Frontend test suite and build remain 100% intact (7/7 Vitest tests, Vite build clean).

---

### Phase 6: Search & Pharmacy Workflows (Integration)
- **Status:** Planned
- **Objectives:**
  - Wire Frontend React components to Backend DRF endpoints:
    - User location detection (Browser Geolocation API + fallback manual zip/city input).
    - Real-time medicine search with debouncing.
    - Interactive search result list with availability badges and distance sorting.
    - MediBot chat drawer integrated on all main views.
  - Implement pharmacy inventory update endpoints for pharmacy managers.
- **Verification Gate:**
  - End-to-end user journey verified: Search query -> Backend search endpoint -> Core Intelligence ranking -> Frontend card render.
  - MediBot chat queries accurately trigger Core Intelligence tools and present ranked pharmacy results in conversation.

---

### Phase 7: Integration, Security & QA
- **Status:** Planned
- **Objectives:**
  - Full regression testing suite (Unit, Integration, and UI Component tests).
  - Security audit:
    - Verify CORS whitelist enforcement.
    - Ensure zero sensitive environment variables in frontend production bundle.
    - Check rate-limiting on search and chat endpoints.
  - Performance optimization:
    - Database indexing on spatial and text search fields.
    - Asset bundling, tree-shaking, and minification.
  - Production deployment documentation and readiness review.
- **Verification Gate:**
  - All automated tests passing with zero failures.
  - Security review sign-off.
  - Production build succeeds cleanly.
