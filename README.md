# MediiLocate — MediLocate AI

**MediLocate AI** is an intelligent, location-aware medicine finder and pharmacy inventory platform. It empowers patients and caregivers to rapidly find prescribed and OTC medicines across local verified pharmacies, check real-time availability, calculate proximity and navigation routes, and interact with **MediBot**—a conversational assistant equipped with strict medical safety guardrails.

---

## 1. Product Purpose & Key Capabilities

- **Medicine Availability & Search:** Rapidly locate specific medicines (brand and generic formulations) across a network of pharmacies.
- **Intelligent Proximity Ranking:** Rank results dynamically using multi-factor heuristics: geographic distance, verified in-stock quantities, operational hours, and pricing.
- **Availability State Engine:** Clear classification of stock levels (`IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`) with batch tracking.
- **MediBot Conversational Assistant:** Provides a natural language interface for medicine inquiries, location assistance, and general guidance—strictly bounded by medical safety rules (never prescribes, diagnoses, or alters dosages).
- **Pharmacy Partner Integration:** Modular backend architecture supporting inventory synchronization, batch updates, and audit logging.

---

## 2. Technology Stack

| Layer | Technology | Rationale & Architectural Role |
| :--- | :--- | :--- |
| **Frontend** | React 18+ / Vite / JavaScript / Plain CSS | Lightweight, fast compilation, component-driven, plain modern CSS without bloated framework overhead. |
| **Backend API** | Python 3.11+ / Django REST Framework | Mature enterprise-grade API framework, robust request validation, ORM integration, and orchestration layer. |
| **Core Intelligence** | Python (Pure Algorithm Module) | Decoupled search indexing, Haversine geospatial math, multi-factor ranking, and availability classification. Independently testable. |
| **MediBot** | Python (Dialogue & Intent Engine) | Dialogue management, intent detection, tool integration with Core Intelligence, and strict safety guardrails. |
| **Database** | Supabase-hosted PostgreSQL | Managed relational database providing ACID compliance, spatial queries, and real-time schema capabilities. |
| **Testing** | Vitest + React Testing Library (Frontend)<br>Django Tests + Pytest (Backend & Modules) | Isolated unit testing, component testing, API integration testing, and algorithm verification. |
| **Documentation** | Markdown (`docs/`) | Comprehensive, version-controlled architecture, database design, setup, testing, and roadmap specifications. |

---

## 3. Project Structure

```text
MediLocate/
├── frontend/                     # React + Vite client application
│   ├── public/                   # Static assets, favicon, manifest
│   └── src/
│       ├── assets/               # SVGs, icons, illustrations
│       ├── components/           # Reusable UI component modules
│       │   ├── common/           # Buttons, modals, cards, inputs
│       │   ├── medicine/         # Medicine search, cards, details
│       │   ├── pharmacy/         # Pharmacy cards, badges, map pins
│       │   └── medibot/          # Chat widget, messages, suggestions
│       ├── layouts/              # Page layouts (Navbar, Footer, Sidebar)
│       ├── pages/                # Route views (Home, Search, Pharmacy, About)
│       ├── hooks/                # Custom React hooks (geolocation, debounce)
│       ├── services/             # Dedicated API service layer (Fetch/Axios)
│       ├── styles/               # Plain CSS stylesheets, variables, tokens
│       ├── utils/                # Formatting, date helpers, validators
│       └── tests/                # Frontend Vitest & React Testing Library tests
│
├── backend/                      # Django REST Framework application
│   ├── config/                   # Django project configuration (settings, urls, wsgi)
│   ├── apps/                     # Modular Django domain applications
│   │   ├── accounts/             # User authentication, roles, profiles
│   │   ├── pharmacies/           # Pharmacy directory, locations, operating hours
│   │   ├── medicines/            # Medicine catalog, active ingredients, dosages
│   │   ├── inventory/            # Pharmacy stock, batches, audit tracking
│   │   └── search/               # API endpoints exposing search orchestration
│   ├── services/                 # Cross-app service integrations
│   └── tests/                    # Backend API and integration tests
│
├── core_intelligence/            # Standalone domain algorithms (Zero Web/DB dependencies)
│   ├── search_engine/            # Fuzzy matching, generic-brand normalization
│   ├── ranking/                  # Multi-factor score calculator (distance, stock, price)
│   ├── availability/             # Stock thresholds and status determination
│   ├── location/                 # Haversine distance, radius filtering, geo bounding
│   └── tests/                    # Independent pytest suite for core logic
│
├── medibot/                      # Conversational assistant module
│   ├── intents/                  # Intent classification (find_medicine, store_hours, etc.)
│   ├── dialogue/                 # Dialogue state machine and response generation
│   ├── tools/                    # Tool adapters calling Core Intelligence
│   ├── safety/                   # Medical safety guardrails (emergency disclaimers)
│   └── tests/                    # Intent accuracy and safety rule test suite
│
├── database/                     # Version-controlled database assets
│   ├── migrations/               # SQL schema migration files
│   ├── schema/                   # DDL table schemas and constraints
│   ├── seeds/                    # Explicit fictional seed data for development
│   └── tests/                    # Database constraint and integrity test scripts
│
├── docs/                         # Engineering documentation & architecture specifications
│   ├── ARCHITECTURE.md           # System design, module boundaries, data flow
│   ├── DATABASE_DESIGN.md        # Relational schema, tables, constraints, keys
│   ├── DEVELOPMENT_ROADMAP.md    # 7-phase implementation plan
│   ├── SETUP_GUIDE.md            # Windows PowerShell developer onboarding
│   └── TESTING_STRATEGY.md       # Multi-tiered testing philosophy and execution
│
├── scripts/                      # Developer utility and verification scripts
├── .env.example                  # Environment variable configuration template
├── .gitignore                    # Git ignore file tailored for Windows, Node, Python
└── README.md                     # Project overview and index
```

---

## 4. Current Development Phase

> **Phase 5: MediBot Conversational Intelligence & Safety Layer (COMPLETED)**
> - Implemented pure-Python, rule-based conversational assistant in `medibot/` with zero database or framework coupling:
>   - `safety/`: Strict input validation ($\le 500$ chars, rejection of empty/malformed inputs), acute emergency interceptor (chest pain, breathing difficulty, stroke, overdose) with immediate regional emergency guidance (112 / 108 / 911), and medical advice guardrail redirecting diagnoses, prescriptions, and dosage calculations to licensed practitioners.
>   - `intents/`: Deterministic regex classifier recognizing 8 intent types (`EMERGENCY_CONCERN`, `MEDICAL_ADVICE`, `GREETING`, `HOW_IT_WORKS`, `PHARMACY_ONBOARDING`, `AVAILABILITY_HELP`, `PHARMACY_SEARCH`, `MEDICINE_SEARCH`, and `UNKNOWN`).
>   - `tools/`: Protocols and adapters connecting `MedicineSearchTool` to `core_intelligence.search_engine.matching.search_medicines` via injected providers; honest placeholder `PharmacySearchTool` returning unavailable status until Phase 6.
>   - `dialogue/`: `DialogueManager` handling multi-turn context (e.g. `awaiting_medicine_name`) and producing predictable `MediBotResponse` JSON schemas.
> - Built backend REST adapter `POST /api/v1/chat/` with payload validation, HTTP 400 for bad input, HTTP 405 for disallowed methods, and safe HTTP 500 fallback.
> - Maintained stateless privacy: Zero database storage of user chat queries or conversations.
> - Authored comprehensive engineering guide in `docs/MEDIBOT.md`.
> - Verified automated test suites:
>   - **115/115 pytest tests pass** (67 Core Intelligence + 48 MediBot).
>   - **29/29 Django backend tests pass** (including 13 Chat API tests).
>   - **7/7 frontend Vitest tests pass** with clean production build.

---

## 5. Next Steps

1. **Phase 6: Search & Pharmacy Workflows:** End-to-end integration between frontend React UI, backend DRF endpoints, Core Intelligence algorithms, and MediBot chat drawer.
2. **Phase 7: Integration, Security & QA:** E2E user journeys, rate limiting, audit logging, and production readiness.
