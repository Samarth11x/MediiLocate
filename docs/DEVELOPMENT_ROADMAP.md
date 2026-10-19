# MediLocate AI — Development Roadmap

This roadmap establishes the phased engineering plan for developing the **MediLocate AI** platform. Each phase is gated by strict deliverables, verification checkpoints, and quality standards.

---

## Roadmap Overview

| Phase | Milestone | Primary Objective | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **Project Foundation** | Engineering standards, directory hierarchy, environment templates, docs | **COMPLETED** |
| **Phase 2** | **Frontend Foundation** | React + Vite setup, UI design system, component hierarchy, mock services | Planned |
| **Phase 3** | **Backend & Supabase** | Django REST Framework, database schema, ORM models, API serializers | Planned |
| **Phase 4** | **Core Intelligence** | Medicine search normalization, ranking heuristics, location engine | Planned |
| **Phase 5** | **MediBot Conversational Layer** | Intent recognition, dialogue flows, safety interceptors, tool integration | Planned |
| **Phase 6** | **Search & Pharmacy Workflows** | End-to-end integration of search, availability, inventory management, chat | Planned |
| **Phase 7** | **Integration, Security & QA** | E2E testing, penetration checks, performance optimization, release readiness | Planned |

---

## Detailed Phase Breakdown

### Phase 1: Project Foundation (Current Milestone)
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

### Phase 2: Frontend Foundation
- **Status:** Planned
- **Objectives:**
  - Initialize React application using Vite (`npm create vite@latest frontend -- --template react`).
  - Configure plain CSS design tokens (typography, colors, spacing, card elevations, accessibility states).
  - Scaffold core component structures:
    - `common/`: Buttons, Cards, Badges, Modals, Spinners, Inputs.
    - `medicine/`: SearchBar, MedicineCard, MedicineDetailModal.
    - `pharmacy/`: PharmacyList, PharmacyCard, DistanceBadge, AvailabilityTag.
    - `medibot/`: ChatWidget, MessageList, QuickReplies, SafetyDisclaimerBanner.
  - Build abstracted API service layer (`frontend/src/services/apiClient.js`).
  - Setup Vitest and React Testing Library for frontend component unit tests.
- **Verification Gate:**
  - Vite dev server runs without errors.
  - Component unit tests pass in Vitest.
  - Mock service layer renders simulated pharmacy and medicine search results.

---

### Phase 3: Backend & Supabase Database
- **Status:** Planned
- **Objectives:**
  - Initialize Python virtual environment (`venv`) and install Django & Django REST Framework.
  - Create Django apps: `accounts`, `pharmacies`, `medicines`, `inventory`, `search`.
  - Connect Django ORM to Supabase-hosted PostgreSQL instance via environment variables.
  - Author and apply initial database migrations for `pharmacies`, `medicines`, and `inventory`.
  - Create REST serializers and basic CRUD/query endpoints with request validation.
  - Populate database with safe, fictional seed data for development.
- **Verification Gate:**
  - Django server starts (`python manage.py runserver`).
  - Database migrations apply cleanly to Supabase PostgreSQL.
  - Health check endpoint `/api/v1/health/` returns `200 OK`.

---

### Phase 4: Core Intelligence Module
- **Status:** Planned
- **Objectives:**
  - Build standalone, framework-independent Python package in `core_intelligence/`.
  - Implement **Location Engine**: Great-circle Haversine formula, bounding box calculation, radius filtering.
  - Implement **Availability Engine**: Stock threshold evaluation (`IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`).
  - Implement **Ranking Engine**: Composite scoring algorithm weighting distance, stock availability, and operational hours.
  - Implement **Search Engine**: Case-insensitive substring and fuzzy matching for generic and brand names.
- **Verification Gate:**
  - 100% pytest pass rate across edge cases in `core_intelligence/tests/`.
  - Zero imports of Django, database drivers, or frontend libraries in `core_intelligence`.

---

### Phase 5: MediBot Conversational Layer
- **Status:** Planned
- **Objectives:**
  - Build standalone conversational logic in `medibot/`.
  - Implement **Intent Classifier**: Pattern matching and rule-based parsing for user queries (`FIND_MEDICINE`, `CHECK_AVAILABILITY`, `PHARMACY_HOURS`, etc.).
  - Implement **Safety & Guardrails**:
    - Emergency symptom detector (chest pain, breathing difficulty, acute trauma).
    - Prescription restriction filter (prevents diagnosing or altering dosages).
    - Mandatory medical disclaimer injection.
  - Implement **Tool Adapters**: Bridges conversational intents to Core Intelligence search and ranking methods.
- **Verification Gate:**
  - Automated test suite validating that dangerous queries (e.g., "how much medicine should I take?") are intercepted with safety disclaimers.
  - MediBot operates purely via provided tools without direct database coupling.

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
