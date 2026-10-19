# Design System Decision Record (DSDR-001)

**Project:** MediLocate AI  
**Author:** Lead UI/UX Designer & Senior Frontend Architect  
**Status:** Approved & Implemented  
**Date:** 2026-10-19  

---

## 1. Context & Objectives

MediLocate AI requires a trustworthy, calm, accessible, and responsive user interface for medicine discovery, pharmacy lookup, and inventory verification. The target audience includes patients seeking urgent medications, caregivers, pharmacy managers, and administrators.

This record details the evaluation of design directions, font pairings, component patterns, and reference tooling findings from **UI/UX Pro Max** and **21st.dev**.

---

## 2. Reference Tools Setup & Findings

### 2.1 UI/UX Pro Max Evaluation
- **Reference:** [`https://github.com/nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- **Tooling State:** Checked CLI availability. The global CLI (`npm install -g ui-ux-pro-max-cli`) was not previously installed on the host. In accordance with user-permission directives, installation commands and instructions are documented for interactive execution.
- **Rules & Heuristics Applied:**
  - *Domain Profile:* Healthcare / Pharmacy & Drug Store.
  - *Core Needs:* Clinical clarity, high readability, calming reassurance, high contrast.
  - *Anti-Patterns Avoided:* Bright neon colors, AI purple/pink gradients, decorative low-contrast muted text, emojis as functional icons.
  - *Pre-delivery Checklist:* Explicit `:focus-visible` styles, touch targets >= 44x44px, `prefers-reduced-motion` compliance, light-mode text contrast >= 4.5:1.

### 2.2 21st.dev Component Catalog Evaluation
- **Reference:** [`https://21st.dev/mcp`](https://21st.dev/mcp)
- **Tooling State:** Evaluated CLI (`@21st-dev/cli`) and MCP connectivity. 21st.dev requires interactive web browser authentication (`21st login`) which is not pre-authenticated in headless background processes.
- **Architectural Policy:** Evaluated public 21st.dev component patterns (Search inputs, status alerts, step grids, partner cards). All selected patterns were adapted cleanly into **React and plain CSS**, strictly adhering to project boundaries and rejecting third-party framework bloat (no Next.js, no Tailwind, no shadcn/ui runtime dependencies).

---

## 3. Evaluation of Design Directions

Three candidate directions were evaluated against five weighted criteria:

| Evaluation Criteria | Weight | Direction A: Clinical Minimalism | Direction B: Modern Healthcare SaaS | Direction C: Editorial Healthcare Discovery |
| :--- | :---: | :---: | :---: | :---: |
| **Healthcare Trust & Credibility** | 25% | **24 / 25** | 21 / 25 | 18 / 25 |
| **Medicine-Search Usability & Clarity** | 25% | **24 / 25** | 22 / 25 | 18 / 25 |
| **Readability & Accessibility** | 20% | **20 / 20** | 18 / 20 | 17 / 20 |
| **Mobile & Desktop Responsiveness** | 15% | **14 / 15** | 14 / 15 | 12 / 15 |
| **Brand Compatibility & Consistency** | 15% | **14 / 15** | 14 / 15 | 11 / 15 |
| **Total Weighted Score** | **100%** | **96 / 100 (WINNER)** | **89 / 100** | **76 / 100** |

### Selected Direction: Direction A (Clinical Minimalism with Card Refinements)
- **Why It Won:** Patients searching for medicines are frequently under stress or experiencing time-sensitive health concerns. Clinical minimalism eliminates visual clutter, places immediate prominence on the search form, ensures high-contrast readability, and projects calm medical competence.
- **Why Direction B Was Ranked Second:** Modern SaaS card styling is clean but carries commercial software overtones that feel slightly transactional rather than clinical.
- **Why Direction C Was Rejected:** Editorial layouts with serif typography are suited for health journalism or long-form medical articles, but severely hinder rapid visual scanning of drug names, dosages, and operational store hours.

---

## 4. Typography & Font Pairing Selection

### Evaluated Options:
1. **System Humanist & Geometric Stack (`Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`) — SELECTED**
   - *Headings:* SemiBold 600 / Bold 700
   - *Body:* Regular 400 / Medium 500
   - *Readability:* Exceptional across all display densities.
   - *Performance:* 0 ms font load latency, zero layout shift (CLS: 0.0), 0 kB download overhead.
   - *Personality:* Objective, reassuring, modern healthcare precision.
2. **Plus Jakarta Sans / Inter**
   - *Rejected Rationale:* High aesthetic appeal, but introduces external Google Font network dependencies and render blocking without substantial legibility gains over the system stack.
3. **Merriweather / Source Sans 3**
   - *Rejected Rationale:* Serif headings create a literary aesthetic that degrades scanning speed for pharmaceutical search results.

---

## 5. Design Tokens & Palette Implementation

Implemented in [`frontend/src/styles/tokens.css`](file:///c:/Users/K%20A%20PATIL/OneDrive/Attachments/Desktop/MediLocate/frontend/src/styles/tokens.css):
- Primary Teal: `#0F766E`
- Deep Navy: `#123047`
- Soft White: `#F8FAFC`
- Light Mint: `#D1FAE5`
- Dark Slate: `#1E293B`
- Demo Warning Background: `#FEF3C7` (Border: `#FCD34D`, Text: `#92400E`)

---

## 6. Persisted Design System Assets

- Master System: [`design-system/medilocate-ai/MASTER.md`](file:///c:/Users/K%20A%20PATIL/OneDrive/Attachments/Desktop/MediLocate/design-system/medilocate-ai/MASTER.md)
- Homepage Specification: [`design-system/medilocate-ai/pages/homepage.md`](file:///c:/Users/K%20A%20PATIL/OneDrive/Attachments/Desktop/MediLocate/design-system/medilocate-ai/pages/homepage.md)

---

## 7. Known Limitations & Deferred Capabilities

1. **No Backend or Database Coupling:** Neither Django REST Framework nor Supabase is connected in Phase 2.
2. **No Geolocation Requests:** The browser geolocation API is intentionally uninvoked; location-based radius calculations are scheduled for Phase 4 (Core Intelligence).
3. **Search Inactivity:** Submitting queries displays an informative inline phase notice confirming that live search is scheduled for integration in Phase 4 and Phase 6.
