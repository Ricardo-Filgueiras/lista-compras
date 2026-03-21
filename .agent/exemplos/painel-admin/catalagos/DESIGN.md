# Design System Strategy: The Digital Atelier

## 1. Overview & Creative North Star
**Creative North Star: The Digital Atelier**
The stationery business is built on the tactile beauty of paper, the precision of ink, and the elegance of organization. To reflect this, this design system moves beyond the generic "admin dashboard" to create a high-end editorial experience. 

We break the "template" look through **The Digital Atelier** concept: a workspace that feels like stacked sheets of premium cardstock. We utilize intentional asymmetry—where large display type anchors a page while data sits in refined, offset containers. This system prioritizes breathing room and rhythmic spacing over rigid grid lines, ensuring that managing complex order pipelines feels like an exercise in professional curation rather than data entry.

---

## 2. Colors & Surface Philosophy
The palette is a sophisticated blend of cool slates (`primary: #565e74`) and airy neutrals.

### The "No-Line" Rule
Standard UI relies on 1px borders to separate content. In this system, **solid 1px borders for sectioning are prohibited.** Boundaries are defined strictly through background color shifts. A dashboard module should sit on `surface-container-low` against a `surface` background. This creates a softer, more professional transition that mimics the way light hits physical objects.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers. Use the `surface-container` tiers to define "nested" depth:
*   **Base Layer:** `surface` (#f7f9fb)
*   **Secondary Sections:** `surface-container-low` (#f0f4f7)
*   **Interactive Cards:** `surface-container-lowest` (#ffffff)
*   **Raised Accents:** `surface-container-high` (#e1e9ee)

### The "Glass & Gradient" Rule
To elevate the experience, floating elements (like side navigation or active popovers) must use **Glassmorphism**. Apply a semi-transparent `surface` color with a `backdrop-blur` of 12px-20px. 
*   **Signature Textures:** For primary CTAs or high-level analytics headers, use a subtle linear gradient transitioning from `primary` (#565e74) to `primary_dim` (#4a5268) at a 135-degree angle. This adds "visual soul" that flat colors lack.

---

## 3. Typography
The system employs a high-contrast pairing of **Manrope** for editorial expression and **Inter** for functional precision.

*   **Editorial Anchors (Manrope):** Use `display-lg` and `headline-lg` for page titles and key metrics. The geometric nature of Manrope provides an authoritative, premium feel. 
*   **Functional Data (Inter):** Use `body-md` and `label-md` for order details and catalog management. Inter’s high x-height ensures legibility when managing complex task pipelines.
*   **Hierarchy:** To convey brand identity, headers should use `primary_fixed` or `on_surface` colors, while secondary metadata should use `on_surface_variant`. This creates a clear "read-first" path for the user.

---

## 4. Elevation & Depth
Depth is achieved through **Tonal Layering** rather than heavy drop shadows.

*   **The Layering Principle:** Stacking tiers (e.g., a `surface-container-lowest` card sitting on a `surface-container-low` background) creates a natural lift.
*   **Ambient Shadows:** When a "floating" effect is necessary for modals or menus, use an extra-diffused shadow: `box-shadow: 0 10px 40px -10px rgba(86, 94, 116, 0.08)`. The shadow color is a tinted version of the `primary` token, mimicking natural light.
*   **The "Ghost Border" Fallback:** If a container requires definition against a similar tone, use a **Ghost Border**: the `outline-variant` token at 15% opacity. Never use 100% opaque borders.

---

## 5. Components

### Buttons
*   **Primary:** Uses the signature gradient (Primary to Primary-Dim). Roundedness: `md` (0.375rem).
*   **Secondary:** `surface-container-highest` background with `on_surface` text. No border.
*   **Tertiary/Ghost:** No background. Uses `primary` text and `sm` rounding on hover.

### Input Fields & Search
Forbid the high-contrast box. Use `surface-container-highest` with a `sm` (0.125rem) "Ghost Border." On focus, transition the background to `surface-container-lowest` and increase the ghost border opacity to 40%.

### Cards & Order Lists
*   **No Dividers:** Forbid the use of horizontal lines. Separate list items using the spacing scale (e.g., `2` or `3`) and subtle background shifts.
*   **Order Chips:** Use `secondary_container` with `on_secondary_container` text. Keep roundedness at `full` for a soft, pill-like aesthetic.

### Stationery-Specific Components
*   **The Pipeline Tracker:** A horizontal sequence of cards using `surface-container-low`. The "Active" state should use a `primary` tint and a subtle `xl` (0.75rem) shadow to indicate focus.
*   **Catalog Thumbnails:** Images should have an `xl` corner radius and a `1px` inner ghost-stroke to ensure the product (often white stationery) doesn't bleed into the white card background.

---

## 6. Do's and Don'ts

### Do
*   **DO** use whitespace as a structural element. If a section feels crowded, increase spacing to `8` (2.75rem) or `10` (3.5rem).
*   **DO** use `surface-tint` at 5% opacity for large background areas to give the neutral greys a "premium paper" warmth.
*   **DO** align text-heavy data to a strict baseline, but allow imagery and headlines to break the alignment slightly for an editorial look.

### Don'ts
*   **DON'T** use pure black (#000000). Use `on_surface` (#2a3439) to maintain a soft, ink-on-paper contrast.
*   **DON'T** use traditional Material Design "Elevation" shadows (0dp to 24dp). Stick to Tonal Layering and the Ambient Shadow spec.
*   **DON'T** use 1px dividers to separate table rows. Use `surface-container-low` alternating row backgrounds or simply generous vertical padding (`3`).