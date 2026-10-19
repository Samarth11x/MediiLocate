# MediLocate AI — Master Design System Specification

**Product:** MediLocate AI  
**Tagline:** "MediLocate — Find Your Medicine. Right Around You."  
**Category:** Healthcare Technology / Medicine Discovery & Pharmacy Inventory Locator  
**Design Direction:** Clinical Minimalism with Modern Healthcare Card Refinements  
**Reference Frameworks:** UI/UX Pro Max Design Intelligence + 21st.dev Component Patterns  

---

## 1. Visual Direction & Design Philosophy

MediLocate AI provides critical medicine discovery tools for patients, caregivers, and pharmacy staff. The interface adheres to **Clinical Minimalism**, characterized by:
- **Calm, Reassuring Tone:** Medical stress is mitigated through spacious layouts, soft contrast, and predictable interactions.
- **Immediate Information Hierarchy:** Search inputs, availability badges, and pharmacy details take precedence over decorative elements.
- **Zero Hallucination / Zero Deception:** Real capabilities are distinguished from planned roadmap items (Phases 3, 4, 6). The mandatory demo banner is always visible.
- **Anti-Patterns Strictly Avoided:**
  - No flashy neon colors or crypto-style bright saturated purple/pink gradients.
  - No emojis as functional UI icons (all iconography is semantic SVG).
  - No sluggish multi-second artificial loading animations.
  - No cramped cards or low-contrast muted gray text failing WCAG AA (4.5:1).

---

## 2. Approved Brand Palette & Semantic Tokens

### 2.1 Core Palette
| Token Name | Hex Code | Semantic Role |
| :--- | :--- | :--- |
| `--color-teal-green` | `#0F766E` | Primary brand accent, primary CTA buttons, active navigation states. |
| `--color-teal-hover` | `#0D655E` | Button hover and active feedback state. |
| `--color-teal-subtle` | `#CCFBF1` | Subtle chip background, badge highlight, focus fill. |
| `--color-deep-navy` | `#123047` | Dominant brand identity, headings, desktop header, site footer. |
| `--color-deep-navy-light` | `#1A4465` | Subtle gradient partner cards, elevated dark surfaces. |
| `--color-soft-white` | `#F8FAFC` | Global page background canvas (Slate-50 tone, prevents eye fatigue). |
| `--color-light-mint` | `#D1FAE5` | Tagline pill background, success badge, checkmark icons. |
| `--color-light-mint-text`| `#065F46` | High-contrast text on light mint backgrounds (7.2:1 contrast ratio). |
| `--color-dark-slate` | `#1E293B` | High-contrast primary body text (Slate-800, WCAG AAA compliant). |

### 2.2 Semantic & Surface Tokens
| Token Name | Hex Code | Role |
| :--- | :--- | :--- |
| `--color-surface-white` | `#FFFFFF` | Card surfaces, modals, search containers. |
| `--color-surface-subtle` | `#F1F5F9` | Secondary card fills, location preview card background. |
| `--color-border-subtle` | `#E2E8F0` | Structural hairpins, header bottom border, card outlines. |
| `--color-border-default` | `#CBD5E1` | Form inputs, inactive control borders. |
| `--color-demo-bg` | `#FEF3C7` | Mandatory demo warning banner background. |
| `--color-demo-border` | `#FCD34D` | Demo warning border line. |
| `--color-demo-text` | `#92400E` | Demo warning text (exceeds 4.5:1 contrast). |
| `--color-demo-badge` | `#B45309` | Bold notice indicator tag inside demo banner. |

---

## 3. Typography System & Font Pairing

### 3.1 Selected Font Stack
- **Primary Font Stack:** `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- **Monospace Stack:** `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`

### 3.2 Evaluation & Selection Rationale
- **Heading Family:** System Clean Geometric Sans (Weights: 600 SemiBold, 700 Bold)
- **Body Family:** System Clean Humanist Sans (Weights: 400 Regular, 500 Medium)
- **Why Selected:**
  - Zero network latency and 0 ms FOIT/FOUT (Flash of Unstyled Text).
  - Native rendering optimization on Windows (ClearType/DirectWrite), macOS/iOS (CoreText), and Android (Roboto).
  - Uncompromised clarity for small-format dosage numbers, units (mg/ml), batch numbers, and phone digits.

### 3.3 Typographic Scale
- `xs` (`0.75rem` / `12px`): Badge text, status tags, fine print disclaimers.
- `sm` (`0.875rem` / `14px`): Form labels, navigation links, secondary captions.
- `base` (`1rem` / `16px`): Standard body text, search input text.
- `lg` (`1.125rem` / `18px`): Card titles, lead paragraphs.
- `xl` (`1.25rem` / `20px`): Section subheadings, brand titles.
- `2xl` (`1.5rem` / `24px`): Major card headings, footer titles.
- `3xl` (`1.875rem` / `30px`): Section titles (`h2`).
- `4xl` (`2.25rem` to `2.75rem`): Hero display heading (`h1`).

---

## 4. Spacing, Radii, and Elevation Tokens

### 4.1 Spacing Scale
- `var(--space-1)`: `4px`
- `var(--space-2)`: `8px`
- `var(--space-3)`: `12px`
- `var(--space-4)`: `16px`
- `var(--space-6)`: `24px`
- `var(--space-8)`: `32px`
- `var(--space-10)`: `40px`
- `var(--space-12)`: `48px`
- `var(--space-16)`: `64px`

### 4.2 Radii
- `var(--radius-sm)`: `4px` (Notice badges, code pills)
- `var(--radius-md)`: `8px` (Buttons, form inputs, toggle buttons)
- `var(--radius-lg)`: `12px` (Cards, step blocks)
- `var(--radius-xl)`: `16px` (Hero search card, partner banner)
- `var(--radius-full)`: `9999px` (Tagline pills, step number avatars)

### 4.3 Shadows
- `var(--shadow-sm)`: `0 1px 2px 0 rgba(18, 48, 71, 0.05)`
- `var(--shadow-md)`: `0 4px 6px -1px rgba(18, 48, 71, 0.08)`
- `var(--shadow-lg)`: `0 10px 15px -3px rgba(18, 48, 71, 0.1)`

---

## 5. Component Patterns & 21st.dev Adaptations

### 5.1 Medicine Search Input & Form
- Inspired by 21st.dev elevated search container patterns.
- Adapted to pure semantic HTML `<form role="search">` and vanilla CSS.
- Explicit label for screen readers (`<label htmlFor="...">`).
- Visual feedback on empty validation (`role="alert"`) and planned feature status (`role="status"`).

### 5.2 Mandatory Demo Warning Banner
- Displays verbatim: `"DEMO MODE — All pharmacy listings, locations, prices, and inventory shown here are fictional examples and are not real-time pharmacy information."`
- Accessible region `<aside role="region" aria-label="Demo mode warning">`.
- Distinct high-contrast badge text ensuring compliance without relying on color alone.

### 5.3 Responsive Navigation Header
- Fixed desktop header with brand emblem and navigation links.
- Collapsible mobile navigation drawer with accessible hamburger toggle button (`aria-expanded`, `aria-controls`).
- Keyboard dismissable via `Escape` key.

### 5.4 Opening Splash Screen
- Brief 600–850 ms branded entrance.
- Strictly respects `prefers-reduced-motion` (instant 0 ms bypass when active).
- Clean unmount with zero state leaks or orphaned timers.

---

## 6. Accessibility & Compliance Checklist
- [x] All interactive controls provide visible `:focus-visible` outlines (`2px solid #0F766E`).
- [x] Touch targets measure at least 44x44px.
- [x] Text color contrast against backgrounds exceeds 4.5:1 (normal text) and 3:1 (large text).
- [x] Landmark tags used appropriately (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`, `<aside>`).
- [x] `prefers-reduced-motion` disables transitions and splash delays.
- [x] Clean reflow on viewport widths: 375px (Mobile), 768px (Tablet), 1024px (Laptop), 1280px+ (Desktop).
- [x] Zero external font or tracking script dependencies.
