# 🎨 Green Naroda • Clean Naroda — Website Redesign Brief

> **What this file is:** A complete design + content specification for rebuilding the
> look and feel of the Green Naroda website. It is written so you can hand any single
> section to Claude (or a designer/developer) and say *"build this"* without re-explaining
> context.
>
> **How to use it:**
> 1. Read the **Design Direction** section to set the visual language.
> 2. Build the homepage **section by section** using the **Page Structure** blueprint.
> 3. Fill in every item from the **Placeholder Index** and **Asset Checklist** with real
>    content before going live.
>
> **Two hard rules (please respect these):**
> - **Quotes from real leaders must be real.** Do not invent words and attribute them to
>   Narendra Modi ji or Amit Shah ji. Paste verified quote text (from an actual speech or
>   official source) into the placeholders.
> - **Photos of real people must be real, licensed images** that you supply. Do not use
>   AI-generated faces of real politicians.

---

## 1. Project Summary

A civic-campaign website for **Naroda, Ahmedabad** — a drive to plant **28,855 trees** and
run cleanliness initiatives across all 14 wards, marking India's 80th Independence Year.
Multi-language: **English / Gujarati / Hindi**.

**Goal of the redesign:** Make it look like a premium, trustworthy government-backed civic
movement — warm, patriotic, and green — with modern motion and a clear organizer hierarchy.

---

## 2. Design Direction

### 2.1 Design principles
1. **Warm + patriotic + green.** Saffron energy of a national campaign, softened by the
   green of trees. Feels official, not corporate.
2. **Photo-led, not illustration-led.** Real people planting real trees builds trust.
   (The current cartoon hero should become authentic campaign photography.)
3. **Big, confident numbers.** The progress counters (trees planted, citizens joined) are
   the emotional core — give them space and motion.
4. **Restrained motion.** Smooth scroll reveals and a hero carousel — *not* heavy 3D. This
   is a civic site; it must feel fast and dignified, load quickly on mobile.
5. **Bilingual-first.** Every design must work in Gujarati/Hindi script, which runs longer
   and taller than English — leave breathing room.

### 2.2 Color palette

| Role | Color | Hex | Use |
|------|-------|-----|-----|
| **Primary — Saffron** | 🟧 | `#FF7500` | Buttons, highlights, active states, BJP-aligned accent |
| **Secondary — Forest Green** | 🟩 | `#1B7A3D` | Tree theme, success, progress bars, secondary buttons |
| **Deep Green (dark sections)** | 🟢⬛ | `#0E1B14` | Dark bands, footer, contrast sections |
| **India Green (accent)** | 🟩 | `#138808` | Small tricolor-nod accents |
| **Gold (accent)** | 🟨 | `#E0A500` | Certificate/award highlights, dividers |
| **Off-White (base)** | ⬜ | `#F8F8F8` | Page background |
| **Ink (text)** | ⬛ | `#141A16` | Body text |

> Tricolor nod: saffron + white + green already lives in this palette — lean into it for
> Independence-Year framing without literally printing a flag everywhere.

### 2.3 Typography

| Use | Font | Notes |
|-----|------|-------|
| Headings (EN) | **Poppins** or **Sora** (Bold/ExtraBold) | Geometric, confident |
| Body (EN) | **Inter** | Highly readable |
| Gujarati | **Noto Sans Gujarati** | Required for `gu` locale |
| Hindi | **Noto Sans Devanagari** | Required for `hi` locale |

Load via self-hosted files or Google Fonts. Set a clear type scale (e.g. hero 56–72px,
section titles 32–40px, body 16–18px). Increase line-height for Gujarati/Hindi.

### 2.4 Imagery & graphics
- Authentic campaign photos: plantation drives, volunteers, clean-up teams, students.
- Consistent duotone/green overlay on hero/background images for text legibility.
- Simple line icons (tree, leaf, broom, water drop, certificate) in one consistent style.
- Subtle SVG leaf/growth motifs as section dividers — decorative, never noisy.

### 2.5 Motion / animation guidance
| Element | Motion |
|---------|--------|
| Hero carousel | Auto-play (~6s), fade or slow horizontal slide, manual arrows + dots, pause on hover |
| Stat counters | Count-up animation when scrolled into view |
| Sections | Fade-up + slight rise on scroll (ScrollReveal / IntersectionObserver / GSAP) |
| Cards | Gentle lift + shadow on hover |
| Backgrounds | Light parallax on hero/section images (disable on mobile for performance) |
| Buttons | Smooth color/scale transition |

Keep it performant: lazy-load images, respect `prefers-reduced-motion`, target good
Core Web Vitals.

### 2.6 Reference sites (what to borrow from each)

**Tree-planting / environmental:**
- **[One Tree Planted](https://onetreeplanted.org/)** — warm nonprofit feel, big hero photo
  with bold overlay headline, authentic photography, region/stat blocks. *Primary tone reference.*
- **[Neoplants](https://www.awwwards.com/sites/neoplants)** — deep green + mint palette,
  full-bleed imagery, smooth scroll transitions. *Borrow the restrained motion, not the 3D.*
- **[Awwwards "plant" collection](https://www.awwwards.com/inspiration_search/plant/)**
  (Botanic Expo, etc.) — scroll-triggered growth/leaf animation ideas.

**Nonprofit / civic (structure & credibility):**
- **Gates Foundation** — minimalist big-number stat sections, generous whitespace.
- **National Geographic Society** — dark/light contrast bands, full-width photography.
- **WWF** — split-screen hero (image + action side-by-side).

**Political / government tone:**
- **BJP brand identity** — saffron `#FF7500`, white, black, lotus emblem; bold banners.
  *(bjp.org blocks bots — screenshot it yourself for exact layout if needed.)*
- **Swachh Bharat / MyGov microsites** — large hero banners, bilingual toggle, tricolor
  accents, simple achievement counters. Closest civic-campaign analog.

**The blend to aim for:** One Tree Planted's warmth + Gates Foundation's clean stats +
saffron/green accents + a restrained dose of Neoplants-style scroll motion.

---

## 3. Page Structure — Homepage Blueprint (top → bottom)

> New or changed sections are marked **🆕 NEW** / **✏️ CHANGED**.

### 3.1 Header / Navigation
- Logo lockup: **Pratham Priority NGO** logo as the main brand mark.
- Nav: Home · Green Naroda · Clean Naroda · Gallery · Events · News · Student Corner · Contact.
- **Organizer logos** (small, right side or top strip): Pratham Priority + BJP Naroda +
  My Naroda Samiti. *(See §4 organizer hierarchy.)*
- **Language toggle:** EN / ગુ / हि — clearly visible.
- Primary CTA button: **"Take The Pledge"** (saffron).
- Sticky on scroll, shrinks slightly, stays legible.

### 3.2 🆕 Hero Carousel / Slider  *(replaces the current single static hero)*
A full-width auto-rotating carousel. **Suggested slides:**

1. **Campaign hero slide** — headline *"Together for a Greener Tomorrow"*, Gujarati subline,
   plantation photo background, buttons: *Take The Pledge* / *Join the Mission*.
2. **Progress slide** — *"28,855 Trees for India's Future"*, 80th Independence Year framing,
   live counter.
3. **Clean Naroda slide** — cleanliness campaign across 14 wards.
4. **🆕 Leadership slide** — see spec below.

**🆕 Leadership carousel slide spec:**
- A dignified banner featuring **five leaders together** (portraits in a row or group image):
  - `[LEADER 1 — Narendra Modi ji, Hon'ble Prime Minister of India]`
  - `[LEADER 2 — Amit Shah ji, Hon'ble Home Minister of India]`
  - `[LEADER 3 — {{GUJARAT_CM_NAME}}, Hon'ble Chief Minister of Gujarat]`
  - `[LEADER 4 — {{GUJARAT_DYCM_NAME}}, Hon'ble Deputy Chief Minister of Gujarat]`
  - `[LEADER 5 — {{BJP_STATE_PRESIDENT_NAME}}, President, BJP Gujarat]`
- Caption line: *"Under the guidance and inspiration of our leaders."*
- Each portrait: photo + name + designation (name/title = placeholders until you confirm).
- **You must supply real, licensed photos** for this slide.

### 3.3 Quick-action tiles
Green Naroda · Clean Naroda · Take Pledge · Upload Photos · Student Corner
(keep existing five, restyle as elevated cards with icons + hover lift).

### 3.4 ✏️ Organizers Section  *(this is a key content change — see §4)*
Three clearly-ranked tiers: **Main Organizer**, **Co-Organizer**, **Supporting Group**.

### 3.5 ✏️ Visionary Leadership / Quotes
- Redesigned quote section for **Narendra Modi ji** and **Amit Shah ji**.
- Layout: large portrait + pull-quote card, saffron accent, designation, optional source line.
- **Quote text = placeholders** — paste verified quotes only (see §6).

### 3.6 Mission / Vision / Goal
Three cards (Vision, Mission, Goal) + the three highlight stats
(28,855 trees · 80 days · 1 mission). Restyle with icons and the new palette.

### 3.7 Campaign Progress
Big animated counters: Trees Planted, Citizens Joined, Organizations, Students,
Cleanliness Drives, Waste Removed. Progress bar to the 28,855 target.
> ⚠️ Confirm whether these numbers are live (from DB) or demo values — label honestly.

### 3.8 Gallery
Filterable photo grid (All / Tree Plantation / Clean Drives / Events / Awareness),
lightbox on click, "View All Photos" CTA.

### 3.9 News / Press + Events
Latest updates cards + upcoming events with date chips (existing content, restyled).

### 3.10 How It Works
4 steps: Take Pledge → Plant & Protect → Track Progress → Get Certificate.

### 3.11 FAQ
Accordion, existing Q&A.

### 3.12 Contact + Footer
- Contact form + real contact details.
  > ⚠️ Replace placeholder phone/address currently on the site with real info.
- Footer: organizer logos (all three), quick links, language toggle, social links, copyright.

---

## 4. ✏️ Organizer Hierarchy (important content change)

Replace any single-organizer framing with **three ranked tiers**:

| Tier | Name | Role description |
|------|------|------------------|
| **1 — Main Organizer** | **Pratham Priority (NGO)** | Lead organizer running and owning the campaign |
| **2 — Co-Organizer** | **BJP Naroda** | Co-organizing partner supporting the drive in Naroda |
| **3 — Supporting Group** | **My Naroda Samiti** | Community committee (group of local people) helping execute the program on the ground |

**Design:** Main organizer largest/most prominent (bigger logo, top row); co-organizer second;
supporting group third. Show logo + name + one-line role for each. Repeat compactly in the footer.

> Provide logos for all three. If BJP Naroda / My Naroda Samiti have no logo, use a clean
> text lockup or emblem placeholder.

---

## 5. Asset Checklist (what YOU need to supply)

- [ ] **Pratham Priority NGO** logo (SVG/PNG, transparent)
- [ ] **BJP Naroda** logo / emblem (or text lockup)
- [ ] **My Naroda Samiti** logo / emblem (or text lockup)
- [ ] Real photos of **Modi ji, Amit Shah ji, Gujarat CM, Gujarat Dy CM, BJP Gujarat President**
      — licensed/official, for the leadership carousel slide and quote section
- [ ] Campaign photography: plantation drives, clean-up drives, volunteers, students, events
- [ ] **Verified quote text** for Modi ji and Amit Shah ji (with source)
- [ ] Final campaign stats (real numbers) if the counters should be live
- [ ] Real contact details (phone, email, address) to replace placeholders

---

## 6. Placeholder Index (fill every one before launch)

| Placeholder | Fill with |
|-------------|-----------|
| `{{GUJARAT_CM_NAME}}` | Current Hon'ble Chief Minister of Gujarat |
| `{{GUJARAT_DYCM_NAME}}` | Current Hon'ble Deputy Chief Minister of Gujarat |
| `{{BJP_STATE_PRESIDENT_NAME}}` | Current President, BJP Gujarat |
| `{{MODI_QUOTE}}` | **Verified** quote from Narendra Modi ji + source |
| `{{AMIT_SHAH_QUOTE}}` | **Verified** quote from Amit Shah ji + source |
| `{{LEADER_PHOTO_*}}` | Real licensed portrait for each of the 5 leaders |
| `{{CONTACT_PHONE}}` / `{{CONTACT_ADDRESS}}` | Real campaign contact details |
| `{{CAMPAIGN_STATS}}` | Real, current numbers (or clearly mark as targets) |

---

## 7. Where to implement (Django project map)

| What | Where in the codebase |
|------|-----------------------|
| Homepage template | `templates/pages/landing.html` |
| Shared layout / header / footer | `templates/base.html` + `templates/partials/` (nav, footer) |
| CSS / JS / images | `static/` (add a redesign stylesheet + carousel JS) |
| Landing content / CMS | `apps/cms/` (views, models, urls) |
| Organizer / leadership data | Add fields/models in `apps/cms/` **or** hardcode in the template if content is static |
| Translations (EN/GU/HI) | `locale/` — run `python manage.py makemessages` after adding text, then `compilemessages` |
| Multi-language fields | `django-modeltranslation` (already installed) |

**Suggested workflow with Claude later:**
1. "Build the new base layout (header + footer) per §3.1 and §4 using this palette (§2.2) and fonts (§2.3)."
2. "Build the hero carousel per §3.2, including the leadership slide with placeholders."
3. "Build the organizers section per §4."
4. "Restyle the quotes, mission, progress, gallery, news, events, FAQ, contact sections."
5. "Wire up scroll animations and counter animations per §2.5."
6. "Add EN/GU/HI translations for all new strings."

---

## 8. Build Order (phased)

1. **Foundation** — palette, fonts, base layout, header, footer, language toggle.
2. **Hero carousel** — including the leadership slide (placeholders).
3. **Organizers section** — 3-tier hierarchy.
4. **Leadership quotes** — redesigned (placeholder quotes).
5. **Core content** — mission, progress counters, gallery, news, events, how-it-works, FAQ, contact.
6. **Motion pass** — scroll reveals, counters, hover states, parallax.
7. **Polish** — real assets, real stats, real contact info, bilingual copy, performance + accessibility.
8. **Review** — check on mobile, in all three languages, with `prefers-reduced-motion`, and confirm no placeholders remain.

---

*Design brief for a greener, cleaner Naroda. 🌱 Fill in every placeholder with real,
verified content before launch.*
