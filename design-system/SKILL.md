---
name: wireml-design
description: Use this skill to generate well-branded interfaces and assets for WireML, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

Key files:
- `README.md` — full design system documentation (content tone, visual foundations, iconography, index)
- `colors_and_type.css` — canonical CSS variables for colors, type, spacing, radii, shadows, motion
- `assets/` — brand logo SVG
- `preview/` — design system specimen cards (type, colors, spacing, components, brand)
- `ui_kits/workbench/` — React recreation of the node-graph authoring app (TopBar, NodeLibrary, GraphCanvas, Inspector, TemplateGallery)
- `ui_kits/marketing/` — React recreation of the cinematic marketing site chapters (Hero, ChapterGraph, ChapterResolution, ChapterRail)

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. Always `@import` the `colors_and_type.css` tokens. Icons come from Lucide only — no emoji, no custom SVG icons.

If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them:
1. Which surface they're designing for — workbench app, marketing site, or something new?
2. What's the chapter tint / category color if it's brand-adjacent?
3. Any hard constraints (print, mobile, small screen)?

Then act as an expert designer who outputs HTML artifacts or production code, depending on the need.

Rules to enforce:
- Dark-mode-first; background is never pure black (`#0a0e14` for app, `#0a0a0f` for site).
- Single lavender accent (`#8b5cf6`). Category colors for node type only.
- Inter + JetBrains Mono only. No emoji, no gradients on text.
- Every h2 gets a monospace uppercase overline above it (`CHAPTER 03 / 07 · THE GRAPH` pattern).
- `cubic-bezier(0.22, 1, 0.36, 1)` for enters, `0.55, 0, 0.68, 1` for exits.
- Respect `prefers-reduced-motion` in any animation.
