# MediLocate AI — System Architecture

This document defines the architectural boundaries, dependency directions, communication contracts, and component responsibilities across the **MediLocate AI** platform.

---

## 1. System Overview & Dependency Direction

MediLocate AI is designed around a **clean, layered architecture** with strict separation of concerns. Modules interact only through designated interfaces, preventing tight coupling and circular dependencies.

```mermaid
graph TD
    classDef client fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef backend fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef core fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    classDef bot fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    classDef db fill:#fbe9e7,stroke:#d84315,stroke-width:2px;

    Client["Frontend Client (React + Vite + Plain CSS)"]:::client
    BackendAPI["Backend API Layer (Django REST Framework)"]:::backend
    CoreIntel["Core Intelligence Module (Search, Ranking, Location)"]:::core
    MediBotModule["MediBot Conversational Engine (Dialogue & Safety)"]:::bot
    DatabaseLayer["Database Layer (Supabase PostgreSQL)"]:::db

    Client -->|HTTPS / JSON REST API| BackendAPI
    BackendAPI -->|Coordinates Domain Queries| CoreIntel
    BackendAPI -->|Dispatches Chat Queries| MediBotModule
    BackendAPI -->|ORM / SQL Queries| DatabaseLayer
    MediBotModule -->|Invokes Search Tools| CoreIntel

    %% Prohibited Direct Interactions (Security & Separation Rules)
    Client -.->|FORBIDDEN: No Direct Access| DatabaseLayer
    MediBotModule -.->|FORBIDDEN: No Direct Access| DatabaseLayer
    CoreIntel -.->|FORBIDDEN: No Dependency on Bot| MediBotModule
```

### Dependency Rules:
1. **Unidirectional Flow:** Higher-level layers consume lower-level domain modules. Lower-level modules never hold references to upper layers.
2. **Frontend Independence:** The Frontend communicates exclusively with the Django REST Framework backend API via an abstracted HTTP service layer. Direct calls to database instances or exposing Supabase service credentials in client bundles are strictly forbidden.
3. **Core Intelligence Independence:** `core_intelligence` has **zero** dependencies on the Django web framework, the database, or `medibot`. It is a pure algorithmic library that accepts structured data and returns calculated results.
4. **MediBot Isolation:** `medibot` never queries the database directly. When MediBot needs to look up pharmacies or medicines, it uses tool interfaces provided by `core_intelligence`, fed with data retrieved by the backend orchestrator.

---

## 2. Module Responsibilities

### 2.1 Frontend (`frontend/`)
- **User Interface & Interaction:** Provides responsive search, interactive pharmacy listing, stock badges, distance calculation displays, and an expandable MediBot chat interface.
- **Dedicated Service Layer:** All network calls are encapsulated in `frontend/src/services/` (e.g., `apiClient.js`, `medicineService.js`, `chatService.js`).
- **No Secrets Policy:** Only public environment variables (such as `VITE_API_BASE_URL`) may be bundled. No database connection strings or administrative API keys are ever stored in frontend assets.

### 2.2 Backend (`backend/`)
- **API Endpoints & Routing:** Exposes RESTful endpoints built with Django REST Framework (DRF). Currently serving `/api/v1/health/` liveness check, with modular routers for medicine lookup, pharmacy geolocation, stock inquiries, and chat interactions.
- **Request Validation & Security:** Sanitizes and validates all client payloads before processing. Configured with explicit CORS headers (`django-cors-headers`), secure session cookies, and standardized JSON error formatting.
- **Domain Orchestration:** Coordinates data fetching from PostgreSQL, formats inputs for `core_intelligence`, and dispatches conversation inputs to `medibot`.
- **Modular App Architecture:**
  - `apps.pharmacies`: Manages licensed pharmacy records, WGS84 geo-coordinates, operating hours, and verification status.
  - `apps.medicines`: Standardized pharmaceutical product catalog (generic and brand names, forms, dosages, search aliases) decoupled from pharmacy inventory.
  - `apps.inventory`: Relational junction mapping medicines to pharmacies with stock quantities, unit pricing, timestamps, and dynamic availability classification (`get_availability_status`).
  - `apps.accounts`: Authentication and user profile scaffolding (planned for future phase).
  - `apps.search`: Search orchestration endpoints (planned for Phase 6).
- **Database Connection Strategy:** Uses `psycopg` (Psycopg 3) with SSL (`require`) connecting to Supabase PostgreSQL (IPv4 session-pooler or direct IPv6), with an automatic fallback to local SQLite for offline developer environments.

### 2.3 Core Intelligence (`core_intelligence/`)
A pure Python algorithm engine completely decoupled from web frameworks, network calls, and databases.
- **Search Engine (`search_engine/`):**
  - `normalization.py`: Unicode NFKC normalization, lowercase folding, word-safe microgram unit standardization (`µg`/`ug` $\rightarrow$ `mcg`), punctuation stripping, and strength formatting (e.g., `500mg` $\rightarrow$ `500 mg`, `0.5%` $\rightarrow$ `0.5 %`).
  - `matching.py`: Multi-tier matching (exact generic/brand, exact aliases, partial names, difflib fuzzy matching) with strict **medication identity safeguards** preventing unauthorized dosage or formulation substitutions (e.g. 500mg request excludes 650mg; syrup request excludes tablets).
- **Availability & Freshness Engine (`availability/`):**
  - `rules.py`: Canonical stock level classification (`AVAILABLE`, `LOW_STOCK`, `OUT_OF_STOCK`, `UNKNOWN`) with configurable thresholds and strict validation rejecting negative quantities.
  - `freshness.py`: Timezone-aware record age evaluation against configurable thresholds (default 24h). Enforces presentation safety: stale known stock displays `OUTDATED` / `UNCONFIRMED` rather than false `AVAILABLE` or `OUT_OF_STOCK`.
- **Location Engine (`location/`):**
  - `distance.py`: Validated great-circle Haversine formula ($R = 6371.0\text{ km}$), boundary checks ($[-90, 90]$, $[-180, 180]$), antimeridian crossing handling, and radius filtering with safe null handling (never fabricates distances).
- **Ranking Engine (`ranking/`):**
  - `scoring.py`: Multi-factor composite heuristic scoring:
    $$\text{Composite Score} = 0.45 \cdot S_{\text{rel}} + 0.30 \cdot S_{\text{avail}} + 0.15 \cdot S_{\text{dist}} + 0.10 \cdot S_{\text{price}}$$
    Guarantees relevance dominates over cheap/near irrelevant drugs; ensures missing distance (0.20) and missing price (0.50) are never treated as 0 km or free.
  - `explanations.py`: Generates standardized machine-readable reason codes (`EXACT_MATCH`, `IN_STOCK_CONFIRMED`, `STALE_STOCK_CAUTION`, `PROXIMITY_ADVANTAGE`) and transparent human explanations.
  - Guarantees complete **input immutability** and deterministic multi-key tie-breaking.

### 2.4 MediBot (`medibot/`)
- **Intent Detection (`intents/`):** Identifies user intent (e.g., `FIND_MEDICINE`, `CHECK_AVAILABILITY`, `PHARMACY_HOURS`, `GENERAL_INQUIRY`, `EMERGENCY_DETECTED`).
- **Dialogue State Machine (`dialogue/`):** Manages multi-turn conversation context and synthesizes structured, helpful responses.
- **Tool Adapter Layer (`tools/`):** Exposes search functions that wrap `core_intelligence` capabilities.
- **Safety & Guardrails (`safety/`):**
  - **Zero-Prescription Rule:** Strictly prevents the assistant from prescribing medicines, suggesting dosages, or recommending alternatives for prescription drugs.
  - **Emergency Interceptor:** Detects acute medical emergencies (e.g., chest pain, difficulty breathing, acute poisoning) and immediately instructs the user to contact local emergency services (e.g., 911 / 112 / 108).
  - **Mandatory Disclaimers:** Appends medical guidance disclaimers emphasizing that information provided is for educational/locational purposes only.

### 2.5 Database (`database/`)
- **Source of Truth:** Hosted on Supabase PostgreSQL.
- **Schema Management:** Version-controlled DDL scripts and Django database migrations.
- **Audit Trails:** Tracks stock updates, batch expirations, and inventory adjustments for compliance.

---

## 3. End-to-End Request Flows

### 3.1 Medicine Search & Location Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Patient
    participant FE as Frontend Client
    participant BE as Django API (Backend)
    participant DB as Supabase PostgreSQL
    participant CI as Core Intelligence

    User->>FE: Enters "Amoxicillin 500mg" + Shares Location
    FE->>BE: GET /api/v1/search/medicines/?query=Amoxicillin&lat=...&lon=...
    BE->>BE: Validate request parameters
    BE->>DB: Query pharmacies & inventory within bounding box
    DB-->>BE: Return matching pharmacy rows & inventory records
    BE->>CI: rank_pharmacies(user_coord, pharmacy_records, stock_data)
    CI->>CI: Compute Haversine distance
    CI->>CI: Evaluate availability thresholds
    CI->>CI: Calculate composite ranking score
    CI-->>BE: Return sorted & categorized results
    BE-->>FE: HTTP 200 OK (JSON with ranked pharmacies & stock statuses)
    FE-->>User: Renders ranked list & map view with stock badges
```

### 3.2 MediBot Conversational Query Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Patient
    participant FE as Frontend (Chat Widget)
    participant BE as Django API (/api/v1/chat/)
    participant MB as MediBot Module
    participant CI as Core Intelligence
    participant DB as Supabase PostgreSQL

    User->>FE: Types "Where can I find Paracetamol nearby?"
    FE->>BE: POST /api/v1/chat/message (user_message, session_id, location)
    BE->>MB: process_message(user_message, session_state)
    MB->>MB: Check safety filters (No diagnosis / No prescription)
    alt Emergency or Prescribing Detected
        MB-->>BE: Intercept with Safety Disclaimer / Emergency Protocol
    else Safe Search Intent
        MB->>BE: Request inventory data for "Paracetamol"
        BE->>DB: Query nearby inventory
        DB-->>BE: Return inventory rows
        BE->>CI: Rank by distance and availability
        CI-->>BE: Sorted inventory
        BE-->>MB: Tool execution result
        MB->>MB: Formulate conversational response with safety footnote
        MB-->>BE: Return formatted assistant reply
    end
    BE-->>FE: HTTP 200 OK (Assistant response payload)
    FE-->>User: Displays message in chat window
```

---

## 4. Database Abstraction Decisions

1. **Centralized Backend Gatekeeper:** The frontend client **never** talks directly to Supabase via `@supabase/supabase-js` for domain queries. All data access is routed through Django REST Framework.
   - *Rationale:* Eliminates exposed database credentials, enforces server-side business rules, guarantees audit logging on inventory adjustments, and prevents client tampering with stock levels.
2. **PostgreSQL Relational Integrity:** We use foreign keys with cascading restrictions (`ON DELETE RESTRICT`) on critical medical and inventory records to prevent orphaned stock data.
3. **Fictional Test Data Isolation:** Initial development and demonstration environments utilize strictly fictional pharmacies and medicine inventory records to prevent confusion with real medical establishments.
4. **Dynamic Stock Classification vs Redundant Columns:** Rather than persisting a static, desynchronized `stock_status` text column in the `inventory` table, availability status is dynamically evaluated via the `get_availability_status()` model method based on real-time `quantity` (`NULL` -> `UNKNOWN`, `0` -> `OUT_OF_STOCK`, `<10` -> `LOW_STOCK`, `>=10` -> `AVAILABLE`), ensuring single source of truth.
