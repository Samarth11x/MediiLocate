# MediLocate AI — Homepage Design Specification

**Page:** Homepage Shell (`frontend/src/pages/HomePage.jsx`)  
**Parent System:** [`design-system/medilocate-ai/MASTER.md`](file:///c:/Users/K%20A%20PATIL/OneDrive/Attachments/Desktop/MediLocate/design-system/medilocate-ai/MASTER.md)  
**Layout Container:** [`frontend/src/layouts/MainLayout.jsx`](file:///c:/Users/K%20A%20PATIL/OneDrive/Attachments/Desktop/MediLocate/frontend/src/layouts/MainLayout.jsx)  

---

## 1. Page Component Hierarchy

```text
App
├── SplashScreen (brief entrance, 600-850ms, reduced-motion bypass)
└── MainLayout
    ├── SkipLink ("Skip to main content")
    ├── DemoModeBanner (mandatory fictional data warning)
    ├── SiteHeader (brandmark, title, tagline pill, desktop links, mobile drawer)
    ├── main#main-content
    │   └── HomePage
    │       ├── Section: Hero (heading, tagline badge, subtitle)
    │       ├── Section: SearchCard (search form, validation, planned feature notice)
    │       ├── Section: LocationPreview (planned proximity ranking callout)
    │       ├── Section: HowItWorks (3-step patient discovery explanation)
    │       └── Section: ForPharmacies (partner value proposition, CTA placeholder)
    └── SiteFooter (branding, tagline, legal context, navigation anchors)
```

---

## 2. Section Specific Decisions

### 2.1 Hero Section
- **Tagline Badge:** Displays exact brand tagline: `"MediLocate — Find Your Medicine. Right Around You."` styled as a rounded mint pill (`#D1FAE5` bg, `#065F46` text).
- **Heading:** Prominent, high-contrast H1: `"Find your medicine. Right around you."` in Deep Navy (`#123047`).
- **Support Copy:** Explains medicine discovery across local verified pharmacies in Dark Slate (`#1E293B`).

### 2.2 Search Preview Card
- **Component ID:** `#search-section`
- **Surface:** White card with 16px radius, subtle border (`#E2E8F0`), and multi-layer drop shadow (`0 10px 15px -3px rgba(18, 48, 71, 0.1)`).
- **Input Field:**
  - Placeholder: `"Search medicine name, strength or brand..."`
  - Accessible label: `"Search Medicine or Generic Compound"`
  - Autocomplete disabled to avoid browser autofill overlay clashes.
- **Submit Button:** Teal Green (`#0F766E`), 52px height to provide a generous touch target.
- **Validation State (`empty_error`):**
  - Trigger: Submitting whitespace or empty string.
  - Alert: `"Please enter a medicine name, strength, or brand to search."` with `role="alert"`.
- **Planned Notice State (`planned_info`):**
  - Trigger: Submitting a search term (e.g., `"Amoxicillin 500mg"`).
  - Status: Clearly informs the user that Core Intelligence (Phase 4) and Backend APIs (Phase 3) will handle live catalogue matching, and confirms that no fake results were generated.

### 2.3 Location Preview Card
- Explains that location discovery will utilize great-circle algorithms in Phase 4.
- Explicitly assures the user that browser location is **not** requested during this phase.

### 2.4 How It Works Grid
- Three sequential cards outlining the patient discovery flow:
  1. *Search for a Medicine:* Brand and generic compound matching.
  2. *Explore Pharmacy Listings:* Verified nearby pharmacies.
  3. *Check Freshness & Stock:* Real-time inventory states (`IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`).
- Each card displays a distinct `"Planned Capability"` badge.

### 2.5 Pharmacy Partner Section
- Anchor ID: `#for-pharmacies`.
- Contrast surface: Deep Navy gradient (`#123047` to `#1A4465`) with mint checkmarks.
- Highlights inventory sync, stock thresholds, verified licensing, and patient navigation.
- Action button points in-page to `#top` and notes dashboard release in Phase 6.

---

## 3. Responsive Breakpoints

| Breakpoint | Layout Adaptations |
| :--- | :--- |
| **Mobile (<640px)** | Search input and button stack vertically; hero typography scales to 1.875rem; step cards display in single column. |
| **Tablet (640px - 1023px)** | Search form displays inline (horizontal row); partner card flexes to side-by-side layout; navigation maintains accessible hamburger toggle. |
| **Desktop (1024px+)** | Header displays full horizontal nav list; tagline pill appears beside brand logo; step cards form a 3-column grid; max width constrained to 1200px. |
