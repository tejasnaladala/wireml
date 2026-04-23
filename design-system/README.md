# WireML Design System

> Teachable Machine, re-imagined as a node-graph workbench on modern foundation models — browser-first via WebGPU, local GPU via CUDA / MPS / MLX / ROCm / DirectML / XPU / CPU.

This design system captures the visual, motion, and content language for **WireML** across its two surfaces: the **workbench app** (`apps/web`, a React-Flow node graph) and the **cinematic marketing site** (`apps/site`, a 7-chapter scroll film). It's sourced from the `tejasnaladala/wireml` monorepo and the canonical marketing brief in `docs/marketing/website-prompt-pack.md`.

---

## Sources

- **Repo:** https://github.com/tejasnaladala/wireml (branch `main`)
- **Codebase:** `apps/web/` (React 18 + Vite + Tailwind + React Flow)
- **Tokens file:** `apps/web/tailwind.config.js` + `apps/web/src/index.css`
- **Cinematic brief:** `docs/marketing/website-prompt-pack.md` + the "Insane Sci-Fi" extension
- **Node registry:** `packages/nodes/src/registry.ts` (18 node schemas across 6 categories)
- **Spec:** `docs/specs/2026-04-22-wireml-design.md`

## Products

1. **The Workbench App** — dark-mode React Flow canvas. Top bar, left node library, right inspector, central graph. Cinematic but dense; optimized for authoring.
2. **The Marketing Site** — 7-chapter scroll cinematic. Three.js + GSAP ScrollTrigger + Lenis. Heavy on postprocessing (bloom, DoF, chromatic aberration, grain).

Both share the same token set. The site takes the same palette and makes it cinematic; the app keeps it functional.

---

## CONTENT FUNDAMENTALS — how WireML writes

**Voice:** Frontier-lab engineer. Confident, technical, unadorned. We respect the reader's time and intelligence. Short declarations beat long explanations.

**Tone:** Restraint. We don't hype, we measure. If we need to impress, we show — specs, counts, GPU badges — not adjectives.

**Casing:**
- Sentence case for UI buttons and labels: "Run graph", "Toggle", "Open demo"
- TitleCase for product nouns: Node Library, Template Gallery, Power Mode, Web Mode
- UPPERCASE + monospace for eyebrows and system chrome: `CHAPTER 03 / 07 · THE GRAPH`, `GRAPH.NODES: 4 · GRAPH.EDGES: 3 · RUNTIME: WEBGPU`
- lowercase for code-path captions: `backbone.clip.vit-b-32`, `head.linear`

**Pronouns:** Product-first, not you/we-heavy. Prefer "Wire up ML." over "You can wire ML." The node does the talking. When "you" appears, it's direct and imperative ("Clone the repo to unlock your GPU").

**Emoji:** Never in UI, never in site copy. Allowed in README body only. Icons are Lucide-React.

**The vibe:** Engineering-honest, like The Expanse's practical HUDs or Alien's MOTHER terminal — not hype-reel, not Apple keynote. A designer should close the tab wanting to clone the repo, not fill out a form.

### Specific copy examples (lifted verbatim)

- Hero h1: **"Wire up ML."**
- Hero sub: "Teachable Machine, re-imagined as a node-graph workbench on modern foundation models."
- Ch2 headline: **"TM was built for 2019 models. We rebuilt it for 2026."**
- Ch3 caption: "Every feature is a node. Compose instead of configure."
- Ch4 h2: "Ten years of backbones in a drag-and-drop library."
- Ch5 h2: "One graph. Two runtimes. Same result."
- Ch6 h2: "Any hardware. Zero configuration."
- Runtime status pill: "Power mode · cuda" / "Web mode · webgpu"
- Inspector empty state: "Select a node to configure."
- Template gallery: "Every template is a pre-wired graph. Load, tweak, train."
- CTA text: "Star on GitHub", "Open demo", "View on GitHub", "Clone the repo to unlock Power Mode →"

### Rules
- No lorem ipsum.
- No testimonials — the repo is new.
- No pricing — it's open source.
- No comparison tables, no cookie banner, no newsletter signup.
- Gradients on text are banned. Hierarchy comes from weight and color, not fades.

---

## VISUAL FOUNDATIONS

### Colors — the palette is locked

- **Bases** desaturate from `#0a0e14` (canonical app bg) through `#131921` surface → `#1a222d` raised → `#2a3240` borders. The marketing site deepens further to `#0a0a0f / #050508 / #020203` for cinema.
- **Foreground** is `#e5ecf4` text and `#6c7a8c` muted — never pure white, never pure grey.
- **Accent** is a single lavender `#8b5cf6`. Used sparingly: brand marks, active state, CTA fills, rim lighting. Never on body text.
- **Category colors** encode node type (and double as chapter tints on the site):
  `data #10b981` · `backbone #3b82f6` · `head #f59e0b` · `eval #ef4444` · `deploy #14b8a6`
  These appear as 10%-alpha card washes, 100% pilot dots, and full-opacity edges.
- Background is **never a flat color** on the marketing site — always a two-stop radial gradient with a noise shader to kill OLED banding. The app can be flat `#0a0e14`.

### Type

- **Inter** (sans) with feature settings `"ss01", "cv11", "ss03"` for UI and headlines. Weight range 400–900.
- **JetBrains Mono** (mono) with ligatures for captions, code, eyebrows, and cinematic overlines.
- **No serifs**, no other display faces. Inter's `-0.05em` tracking at display sizes is the whole signature.
- Cinematic h1 is `clamp(4rem, 11vw, 11rem)` at weight 900, line-height 0.92. App h1 is a tame 72/80.
- Monospace overlines sit above h2s, UPPERCASE, 11px, letter-spacing 0.18em.

### Backgrounds

- No stock photos. No illustrations.
- The marketing site is procedural geometry (InstancedMesh card swarms, transmission-material orbs, tube-geometry wires). No imagery at all.
- Ambient "blobs" are circular blurs (30–50vw, 8–14% opacity) tracing Perlin paths on GPU-only transforms. Strictly `transform: translate3d`, never `filter` or `box-shadow` on keyframes.
- A grain + scanline overlay sits on top of every chapter. CRT scanlines are 3px/4px stripes at 2% white.

### Animation

- **Primary ease** is `cubic-bezier(0.22, 1, 0.36, 1)` (enter) and `cubic-bezier(0.55, 0, 0.68, 1)` (exit). The Linear/Apple standard.
- **Expo.out** (`cubic-bezier(0.16, 1, 0.3, 1)`) for hero/display entrances.
- Scroll is **smooth** (Lenis, duration 1.2, lerp 0.08) and **scrubbed** (ScrollTrigger `scrub: 0.6`) — not instant, not lazy.
- Micro-motion everywhere: breathing orbs (0.5 + 0.05·sin(t)), drifting blobs over 30–45s, drifting camera (0.1u/s dolly).
- No bounces. No infinite loops that don't fade out. Max 2 focal elements moving at once per chapter.
- All motion respects `prefers-reduced-motion` — falls back to fades only, copy still lands.

### Hover states

- Links and ghost buttons: background jumps to `--wire-surface-2`, `transition: colors 200ms`.
- Primary buttons: `brightness(1.1)` (no color change).
- Nodes in the graph: border goes from category-color @ 1px to category-color @ 2px + lavender outer glow (`--shadow-node-selected`).
- Template cards: border `--wire-border` → `--wire-accent`, background lightens slightly.
- 3D canvas elements: the custom cursor ring expands to the element's bounding box + 12px outset, borrows the element's category color, and shows the `userData.schemaId` as a monospace caption.

### Press states

- No shrink transforms. The design is flat against the viewport — pressing is communicated by opacity (0.8) and a 90ms ring contraction on the custom cursor, not scale.
- On the marketing site, press triggers a circular WebGL displacement pulse radiating 200px from the press point, decaying over 600ms.

### Borders

- Always 1px. Hairline. `--wire-border` (`#2a3240`) is the default. 2px only for focus rings and selected nodes.
- Cards, panels, dialogs, and the top bar all carry `border-bottom` or `border-right` lines, never full surrounds — gives the UI a paneled, architectural feel.

### Shadows

- Three elevations:
  - `--shadow-node` — default card: `0 4px 24px -4px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04)`
  - `--shadow-node-selected` — lavender ring: `0 0 0 2px #8b5cf6, 0 4px 32px -4px rgba(139,92,246,0.5)`
  - `--shadow-overlay` — modals & dialogs: `0 24px 64px -16px rgba(0,0,0,0.8)`
- No inner shadows. No colored drop shadows except the lavender-tinted selected ring.

### Transparency & blur

- Backdrop blur (`backdrop-filter: blur(12px)`) is used sparingly, only on (a) the template gallery scrim, (b) the run-log HUD, (c) the optional floating captions. Never on primary panels.
- Category color washes are `/10` alpha (10% opacity over the surface color). That's the whole transparency vocabulary.

### Corner radii

- **6px** — inputs, buttons, small controls. The default.
- **10px** — menus, popovers, the run-log HUD.
- **12px / 16px** — node cards, template cards.
- **24px** — modal dialogs, hero cards on the site.
- **Fully rounded (`999px`)** — status pills, chapter-rail dots, category dots.

### Card anatomy

- Background `--wire-surface`, 1px `--wire-border`, radius 12–16px, `--shadow-node`.
- A top "eyebrow" row in monospace 10–11px uppercase (category label) with a small Lucide icon.
- A body with name + description (sans; 14/12px).
- An optional footer row in muted mono (execution mode, capability flags).
- Selected state swaps the border to `--wire-accent` and adds `--shadow-node-selected`.

### Layout rules

- Three-column hard-pinned app shell: 272px node library, fluid center, 300px inspector. Top bar is 48px high.
- Marketing site is `110vh` per chapter × 7 chapters = ~770vh total scroll.
- Full-width elements are rare — hero, node graph scene (Chapter 3), horizontal-scroll GPU universe (Chapter 6). Everything else has breathing room.
- 4px grid, 24px gutter inside panels, 48px gutter on the site between chapters.

### Depth / DoF

- Marketing site has real depth-of-field (bokeh scale 1.2, aperture 0.01). Focus distance pulses subtly `0.5 + 0.05·sin(t)`.
- App is flat. No simulated depth. The only z-axis feel comes from the node-selected shadow.

---

## ICONOGRAPHY

- **Lucide-React** is the only icon system. No emoji, no custom SVGs, no Unicode glyphs. Every icon in the codebase comes from `lucide-react` and is imported as `import * as icons from 'lucide-react'`.
- Default icon size is **14px** at `--wire-muted`. On active/hover states icons flip to the category color (`CATEGORY_TEXT` map in `NodeView.tsx`).
- For design work outside the repo, load from CDN: `https://unpkg.com/lucide-static@latest/` or `<script src="https://unpkg.com/lucide@latest"></script>`.
- **Logo / brand mark** — the gradient rounded square with a 3-node wire diagram (from `apps/web/public/favicon.svg`, copied to `assets/wireml-logo.svg`). It's never drawn differently; it's always the SVG.
- **Category dots** (`.category-dot` in `index.css`) are 8×8 filled circles — the unofficial second mark of the system. Used in library rows, chapter rails, run logs.
- **Glyphs for GPU backends** on the marketing site (Chapter 6) are procedurally drawn with shader-line primitives — interlocking hexagons (CUDA), concentric rings (MLX), chevrons (ROCm), etc. These are generated, not stored.
- **No iconography is ever drawn inline** in a design — always use the Lucide React component, or fall back to a `<i data-lucide="name">` + script init for HTML mocks.

---

## Index

| Path | Purpose |
| --- | --- |
| `README.md` | This document |
| `SKILL.md` | Agent-invocable skill manifest |
| `colors_and_type.css` | Canonical CSS var tokens + semantic element styles |
| `assets/wireml-logo.svg` | Brand mark (copied from `apps/web/public/favicon.svg`) |
| `preview/*.html` | Design-system cards (typography, color, spacing, components, brand) |
| `ui_kits/workbench/` | Pixel-accurate React recreation of the node-graph app |
| `ui_kits/marketing/` | Marketing-site UI kit: hero, chapter rail, chapter blocks, CTAs |
| *(source mirrors)* `apps/`, `packages/`, `docs/` | Imported from the repo for reference — do not edit |

### Font note

Inter + JetBrains Mono are loaded from Google Fonts in `colors_and_type.css`. The Inter variable font is required for the `font-variation-settings 'wght' X` scroll-linked animation on hero h1s. The system uses the static weight axis here; swap to `Inter var` if you need the full scroll-linked variable-weight effect from the sci-fi brief.
