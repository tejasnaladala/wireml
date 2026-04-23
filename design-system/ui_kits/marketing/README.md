# Marketing UI Kit

Static-prototype recreation of key chapters from the WireML marketing site (`docs/marketing/website-prompt-pack.md`). Omits the full 3D stack — this is the hi-fi 2D layer that sits in front of the Three.js canvas and survives without it (the `?lite` URL variant required by the brief).

## Components

- `Chrome.jsx` — `ChapterRail` (right-edge 7-dot nav), `Overline` (monospace eyebrow), `DeviceBadges` (CUDA/MPS/MLX/ROCm/DirectML/WebGPU pills), `CornerBrackets` (floating HUD corner glyphs).
- `Hero.jsx` — Chapter 1 Awakening. h1 "Wire up ML.", subhead, Open demo + View on GitHub CTAs, device badges, SCROLL ↓ indicator.
- `ChapterGraph.jsx` — Chapter 3 The Graph centerpiece. Perspective-tilted canvas with Webcam → CLIP → Linear → Preview pipeline and the `graph.nodes: 4 · edges: 3 · runtime: webgpu` HUD.
- `ChapterResolution.jsx` — Chapter 7 Resolution. Giant lavender-stroked "W" ligature, three terminal command rows, Star on GitHub CTA, footer.

## Global treatments
- Full-page scanline overlay (`repeating-linear-gradient` at 2% white, 3/4px stripes).
- SVG film-grain overlay at 6% opacity.
- 1px lavender progress bar pinned to top.
- Custom cursor (8px dot + 40px lerped lavender ring with mix-blend-difference).

## Chapters covered
Only 3 of the 7 chapters (1, 3, 7) to keep the UI kit size reasonable. The other four (Indictment / Arsenal / Fork / Universe) follow the same pattern — overline + h2 + chapter-tinted radial-gradient background + per-chapter procedural geometry.

## Run
Open `index.html` and scroll. Move the cursor to see the ring lerp.
