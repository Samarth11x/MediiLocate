# MediLocate AI — Core Intelligence Engine Specification

## 1. Overview & Architectural Boundaries

The `core_intelligence` package is a standalone, pure Python algorithmic engine for **MediLocate AI**. It is strictly decoupled from web frameworks (Django, React), databases (PostgreSQL, Supabase), HTTP networking, and third-party AI APIs.

### Key Tenets:
1. **Pure Python Standard Library:** Uses standard library modules (`math`, `re`, `unicodedata`, `difflib`, `datetime`, `dataclasses`, `copy`). No heavy runtime machine-learning or vector database dependencies.
2. **Explicit Data In / Data Out:** Functions accept explicit arguments (primitives, dictionaries, or dataclasses) and return immutable or copy-on-write structured results.
3. **No Global Mutable State:** Fully deterministic calculations.
4. **Zero Medical Prescriptions or Alterations:** The engine only matches and ranks existing catalogue items; it never prescribes, diagnoses, or recommends modifying medication.
5. **Fail-Safe Missing Data Handling:** Unknown distances, prices, or quantities are never fabricated as 0 km, free (₹0.00), or available.

---

## 2. Package Structure

```text
core_intelligence/
├── __init__.py                # Package root exports
├── requirements-dev.txt       # Development-only test dependencies (pytest)
│
├── search_engine/             # Medicine search & normalization
│   ├── __init__.py
│   ├── normalization.py       # Unicode, case, punctuation, strength formatting
│   └── matching.py            # Exact, partial, fuzzy matching & identity safeguards
│
├── availability/              # Inventory stock & freshness classification
│   ├── __init__.py
│   ├── rules.py               # Canonical stock state thresholds (AVAILABLE, LOW_STOCK, etc.)
│   └── freshness.py           # Record age, freshness states, and safe display synthesis
│
├── location/                  # Geospatial math
│   ├── __init__.py
│   └── distance.py            # Haversine great-circle formula & radius filtering
│
├── ranking/                   # Composite multi-factor scoring
│   ├── __init__.py
│   ├── scoring.py             # Weighted heuristic ranker
│   └── explanations.py        # Machine-readable reason codes & human explanations
│
└── tests/                     # Isolated pytest test suite (67 unit tests)
    ├── __init__.py
    ├── conftest.py            # Synthetic fixtures & deterministic clock
    ├── test_normalization.py  # Normalization & tokenization unit tests
    ├── test_medicine_matching.py # Search matching & safeguard tests
    ├── test_availability.py   # Availability thresholds & validation tests
    ├── test_freshness.py      # Freshness & presentation safety tests
    ├── test_distance.py       # Haversine distance, bounds, & antimeridian tests
    └── test_ranking.py        # Multi-factor ranking, immutability & tie-break tests
```

---

## 3. Module Details & Public APIs

### 3.1 Search Engine Normalization (`core_intelligence/search_engine/normalization.py`)

#### Public Functions:
- `normalize_text(text: Optional[str]) -> str`:
  - Unicode NFKC normalization.
  - Case folding (`.lower()`).
  - Word-boundary microgram symbol standardization (`µg` / `ug` $\rightarrow$ `mcg`), preventing accidental replacement inside drug names like *Augmentin*.
  - Strips disruptive punctuation (`()[]{}<>"'?!:;,~*#@$^&=|\\``) while preserving medically meaningful characters (decimals `0.5`, slashes `mg / ml`, percentages `0.5 %`, hyphens in compound words like `co-amoxiclav`).
  - Collapses repeated internal whitespace.
- `normalize_strength(strength: Optional[str]) -> str`:
  - Standardizes numeric value and unit with a single space (e.g. `'500mg'` $\rightarrow$ `'500 mg'`, `'0.5%'` $\rightarrow$ `'0.5 %'`).
  - Normalizes concentration slashes (e.g. `'250mg/5ml'` $\rightarrow$ `'250 mg / 5 ml'`).
- `normalize_query(query: Optional[str]) -> str`:
  - Applies full text and strength normalization pipeline to user query string.
- `tokenize(text: Optional[str]) -> List[str]`:
  - Splits normalized query into discrete word and value tokens.
- `extract_strength_and_form(query: str) -> Tuple[Optional[str], Optional[str]]`:
  - Detects explicit strength (e.g. `'500 mg'`) and canonical dosage form (e.g. `'tablet'`, `'syrup'`, `'injection'`) in queries.

---

### 3.2 Search Engine Matching (`core_intelligence/search_engine/matching.py`)

#### Public Function:
```python
search_medicines(
    query: Optional[str],
    medicines: List[Dict[str, Any]],
    limit: Optional[int] = None,
    fuzzy_threshold: float = 0.70,
) -> List[Dict[str, Any]]
```

#### Match Hierarchy:
1. **Exact Generic / Brand Match (`match_score = 1.0`):** Query matches generic or brand name exactly.
2. **Exact Alias Match (`match_score = 0.98`):** Query matches an entry in `search_aliases` (e.g. *acetaminophen* $\rightarrow$ *Paracetamol*).
3. **Partial Name Match (`match_score = 0.90 - 0.95`):** Substring / word containment in brand or generic name.
4. **Partial Alias Match (`match_score = 0.85`):** Substring containment in aliases.
5. **Fuzzy Match (`match_score = 0.70 - 0.84`):** Standard library `difflib.SequenceMatcher` ratio meeting or exceeding `fuzzy_threshold`.

#### Medication Identity Safeguards:
- **Strict Strength Guard:** If query explicitly specifies a strength (e.g., `"Paracetamol 500mg"`), catalogue entries with conflicting strengths (e.g., `"650 mg"`) are excluded.
- **Strict Dosage Form Guard:** If query explicitly specifies a formulation (e.g., `"Paracetamol syrup"`), catalogue entries with conflicting forms (e.g., `"Tablet"`) are excluded.
- **No Medical Substitution:** Similarity of chemical names never implies equivalence; no alternative medicine recommendations are generated.

---

### 3.3 Availability Classification (`core_intelligence/availability/rules.py`)

#### Canonical Statuses:
- `AVAILABLE`: Quantity $\ge$ `low_stock_threshold`.
- `LOW_STOCK`: $0 < \text{quantity} < \text{low_stock_threshold}$.
- `OUT_OF_STOCK`: Explicitly reported confirmed zero stock ($\text{quantity} = 0$).
- `UNKNOWN`: Stock not reported or unverified ($\text{quantity} = \text{None}$).

#### Configuration:
```python
@dataclass(frozen=True)
class AvailabilityConfig:
    low_stock_threshold: int = 10  # default development threshold
```

#### Public Functions:
- `classify_availability(quantity: Optional[int], config: Optional[AvailabilityConfig] = None) -> str`:
  - Enforces that unknown quantity is **never** silently converted to zero.
  - Rejects negative quantities or invalid types with `ValueError`.
- `validate_quantity(quantity: Any) -> Optional[int]`:
  - Validates and coerces whole numbers; rejects booleans and negative numbers.

---

### 3.4 Inventory Freshness & Presentation (`core_intelligence/availability/freshness.py`)

#### Freshness Categories:
- `FRESH`: Record updated within `threshold` (default 24 hours).
- `STALE`: Record updated more than `threshold` ago.
- `MISSING`: Timestamp is `None`.
- `FUTURE_INVALID`: Timestamp is in the future beyond clock drift tolerance (60s).

#### User-Facing Display Statuses (`DisplayStatus`):
- `AVAILABLE`, `LOW_STOCK`, `OUT_OF_STOCK`: Confirmed fresh stock.
- `OUTDATED`: Stale known quantity (prevents misleading patients into believing expired reports reflect current stock).
- `UNKNOWN`: Unconfirmed stock.

#### Public Functions:
- `evaluate_freshness(last_updated: Optional[datetime], current_time: Optional[datetime] = None, threshold: timedelta = timedelta(hours=24)) -> FreshnessResult`
- `get_display_availability(quantity: Optional[int], last_updated: Optional[datetime], current_time: Optional[datetime] = None, availability_config: Optional[AvailabilityConfig] = None, freshness_threshold: timedelta = timedelta(hours=24)) -> DisplayAvailabilityResult`

---

### 3.5 Geospatial Distance (`core_intelligence/location/distance.py`)

#### Public Functions:
- `haversine_km(origin_lat: float, origin_lon: float, destination_lat: float, destination_lon: float) -> float`:
  - Spherical Earth radius $R = 6371.0\text{ km}$ (IUGG standard).
  - Formula:
    $$\Delta\phi = \text{radians}(\text{lat}_2 - \text{lat}_1), \quad \Delta\lambda = \text{radians}(\text{lon}_2 - \text{lon}_1)$$
    $$a = \sin^2(\Delta\phi/2) + \cos(\phi_1)\cos(\phi_2)\sin^2(\Delta\lambda/2)$$
    $$c = 2\text{ atan2}(\sqrt{a}, \sqrt{1-a}), \quad d = R \cdot c$$
  - Clamps $a \in [0.0, 1.0]$ against precision rounding errors.
  - Validates latitude in $[-90.0, 90.0]$, longitude in $[-180.0, 180.0]$, raises `ValueError` for out-of-bounds or non-finite values, and `TypeError` for non-numeric types.
  - Correctly calculates distances across the 180° antimeridian.
- `calculate_distance_safe(origin_lat, origin_lon, dest_lat, dest_lon) -> Optional[float]`:
  - Returns `None` instead of throwing on invalid/missing coordinates; **never fabricates distances**.
- `filter_by_radius(origin_lat, origin_lon, items, max_radius_km, lat_key='latitude', lon_key='longitude') -> List[Dict]`:
  - Filters items within radius and attaches sorted `distance_km`.

---

### 3.6 Transparent Result Ranking (`core_intelligence/ranking/scoring.py` & `explanations.py`)

#### Multi-Factor Composite Scoring:
$$\text{Composite Score} = w_{\text{rel}} \cdot S_{\text{rel}} + w_{\text{avail}} \cdot S_{\text{avail}} + w_{\text{dist}} \cdot S_{\text{dist}} + w_{\text{price}} \cdot S_{\text{price}}$$

#### Default Weights (`RankingConfig`):
- $w_{\text{rel}} = 0.45$ (Medicine relevance — primary factor; cheap/near irrelevant medicines cannot outrank target drugs)
- $w_{\text{avail}} = 0.30$ (Availability & freshness — confirmed fresh stock prioritized; stale stock penalized)
- $w_{\text{dist}} = 0.15$ (Geographic proximity — nearer preferred; missing distance receives 0.20 penalty, never 0 km)
- $w_{\text{price}} = 0.10$ (Unit price competitiveness — missing price receives neutral 0.50, never free ₹0.00)

#### Sub-Score Mapping:
- **Availability Sub-Score ($S_{\text{avail}}$):**
  - Confirmed `AVAILABLE`: `1.0`
  - Confirmed `LOW_STOCK`: `0.75`
  - `OUTDATED` (stale stock): `0.35`
  - `UNKNOWN` (missing quantity): `0.20`
  - Confirmed `OUT_OF_STOCK`: `0.05`
- **Distance Sub-Score ($S_{\text{dist}}$):**
  - Missing distance: `0.20` (penalized)
  - Known distance: $\max\left(0.0, 1.0 - \frac{\min(d, 50\text{ km})}{50\text{ km}}\right)$
- **Price Sub-Score ($S_{\text{price}}$):**
  - Missing price: `0.50` (neutral)
  - Known price: $\max\left(0.0, 1.0 - \frac{\min(p, 1000)}{1000}\right)$

#### Deterministic Multi-Key Tie-Breaking:
1. `ranking_score` (descending)
2. `match_score` (descending)
3. `distance_km` (ascending; `None` treated as $+\infty$)
4. `unit_price` (ascending; `None` treated as $+\infty$)
5. `pharmacy.id` (alphabetical string)

#### Input Immutability:
Original input candidate dictionaries are **never mutated**. Output items are clean deep-copied entries with metadata attached (`rank`, `ranking_score`, `relevance_score`, `availability_score`, `distance_score`, `price_score`, `display_status`, `is_confirmed`, `reason_codes`, `explanation`).

---

## 4. Backend Canonical Delegation (`Inventory.get_availability_status`)

In `backend/apps/inventory/models.py`, `Inventory.get_availability_status()` acts as a thin adapter delegating canonical stock classification to `core_intelligence.availability.rules.classify_availability`:

```python
def get_availability_status(self, low_stock_threshold=10):
    try:
        from core_intelligence.availability.rules import classify_availability, AvailabilityConfig
        cfg = AvailabilityConfig(low_stock_threshold=low_stock_threshold)
        status_key = classify_availability(self.quantity, cfg)
    except ImportError:
        # Graceful fallback if core_intelligence is not on PYTHONPATH
        ...
```

---

## 5. Automated Verification & Test Commands

### Core Intelligence Pytest Suite:
```powershell
.\venv\Scripts\python.exe -m pytest core_intelligence/tests -q
```
**Results:** **67 / 67 passed (100%) in 0.19s**

### Django Backend Test Suite:
```powershell
.\venv\Scripts\python.exe backend/manage.py test tests apps
```
**Results:** **16 / 16 passed (100%) in 0.096s**

### Frontend Vitest Suite:
```powershell
npm.cmd test -- --run (in frontend/)
```
**Results:** **7 / 7 passed (100%) in 3.58s**

### Frontend Production Build:
```powershell
npm.cmd run build (in frontend/)
```
**Results:** **Compiled cleanly in 1.23s**

---

## 6. Known Limitations & Deferred Work

1. **Fuzzy Search Language Support:** Currently optimized for Latin-script brand and generic names. Non-Latin multilingual aliases are deferred to future phases.
2. **Road Travel Distance:** Distance calculates straight-line great-circle distance. Road routing / traffic estimation will integrate via external routing services in later phases if approved.
3. **Real-time Inventory Sync:** Seed catalogues and live inventory synchronization endpoints are scheduled for Phase 6.
