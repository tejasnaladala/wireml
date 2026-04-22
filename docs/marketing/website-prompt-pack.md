# WireML — 3D Immersive Scroll Site Prompt Pack

A drop-in prompt suite for generating an Apple-grade, 3D scroll-animated marketing site for WireML. Tested to pair well with Claude (Sonnet / Opus) in Claude Code artifacts, claude.ai Artifacts, or a Cursor/Claude workspace. Also compatible with Google Stitch and v0 with minor adaptation.

Use the prompts in order:

1. **The master prompt** — paste once to generate the whole site in a single artifact.
2. **Section micro-prompts** — paste individually to refine a specific scene after the master.
3. **Design-token & stack appendix** — paste alongside any prompt as `<context>`.

---

## Section A — The Master Prompt (one-shot, full site)

> Paste this verbatim into Claude. Attach `README.md` + `docs/specs/2026-04-22-wireml-design.md` as project knowledge for grounding. Expect a single-file React app as output.

```
You are designing a 3D immersive scroll-animated marketing website for WireML — an open-source node-graph visual ML workbench that reimagines Google Teachable Machine for the foundation-model era. The site must feel like Apple's product pages, Linear's homepage, and a ComfyUI demo reel had a child: refined, technical, confident.

THE PRODUCT IN ONE SENTENCE
Teachable Machine, re-imagined as a node-graph workbench on modern foundation models — runs in your browser on WebGPU, or locally on any GPU (CUDA / MPS / MLX / ROCm / DirectML).

TONE & TASTE
- Frontier-lab-engineer aesthetic: monospaced accents, precise measurements, no marketing fluff.
- No stock photos. No "AI" clichés (brain icons, glowing circuitry). Use real typography and geometry.
- Micro-motion everywhere (breathing, drift, parallax) — but never gimmicky or motion-sick-inducing.
- Dark mode first. Desaturated background with one strong accent color used sparingly.
- Inspiration: linear.app, vercel.com, threejs.org, framer.com/motion, cursor.com, anthropic.com.

STACK (use exactly these)
- Vite + React 18 + TypeScript
- @react-three/fiber, @react-three/drei, three (for all 3D)
- gsap + @gsap/react with ScrollTrigger (for scroll-driven animations)
- framer-motion (for UI micro-interactions)
- tailwindcss v3 (utility styling; avoid tailwind v4 beta syntax)
- lucide-react (icons only; no emoji)

PERFORMANCE & ACCESSIBILITY (non-negotiable)
- Respect `prefers-reduced-motion`: replace scroll-linked animations with fades; disable continuous drift.
- Lazy-load the 3D canvas with Suspense; ship a static SVG fallback for initial paint.
- Total JS payload budget: < 300 KB gzipped for the initial route (excluding the 3D canvas which loads after LCP).
- All text maintains WCAG AA contrast against backgrounds; focus rings are visible.
- Semantic HTML: one <h1>, sections with proper landmarks, skip-to-content link.
- No layout shift on scene transitions. LCP element is text, not 3D.

SITE STRUCTURE (seven vertical full-viewport scenes)

Scene 1 — HERO. A 3D cloud of ~40 small node cards floats in depth, slowly drifting. As the user scrolls, they snap together into the WireML logo wordmark, then into a clean horizontal data-flow graph (Data → Backbone → Head → Preview). Background: deep navy (#0a0e14) with a single faint lavender (#8b5cf6) light source in the upper-right. Foreground copy:
  h1: "Wire up ML."
  subhead: "Teachable Machine, re-imagined as a node-graph workbench on modern foundation models."
  Two buttons: "Open demo" (primary) and "View on GitHub" (ghost, monospace).
  A small row of device-support badges underneath: CUDA · MPS · MLX · ROCm · DirectML · WebGPU.

Scene 2 — THE PROBLEM. Split-screen parallax. Left: a faithful recreation of Google Teachable Machine's 3-panel UI, shown dimmed with a "2019" overlay. Right: a live WireML node graph, bright and in focus, with labels like "CLIP ViT-B/32", "DINOv2", "Zero-shot CLIP". As the user scrolls, the left side scales down and fades; the right side zooms forward. Headline: "TM was built for 2019 models. We rebuilt it for 2026."

Scene 3 — THE NODE GRAPH (centerpiece). A full-width interactive React Flow-style canvas rendered in 3D with slight perspective tilt. Nodes float at subtly different z-depths. On scroll, a beam of light traces a pipeline from left to right: Webcam → CLIP → Linear → Preview, each node lighting up in turn. User hover reveals a tooltip with the node's schema id. Headline overlay (right side, monospace caption): "Every feature is a node. Compose instead of configure."

Scene 4 — FOUNDATION MODELS. An orbit of six floating "capability orbs" (3D spheres with subtle internal particle shaders), each labeled with a model: CLIP · DINOv2 · SigLIP · Whisper · MediaPipe · LoRA. As the user scrolls, the orbit rotates and a spec panel fades in next to whichever orb is centered, showing: model name, feature dim, download size, device support (CUDA/MPS/MLX/...). Headline: "Ten years of backbones in a drag-and-drop library."

Scene 5 — RUNTIME SPLIT. Two 3D "stages" side by side: a glass browser-window mesh on the left (pulsing with a small WebGPU chip badge), a glass server-rack mesh on the right (with an animated GPU die cycling through CUDA/MPS/MLX/ROCm/DirectML labels). A single graph JSON flies up from below and splits into two identical copies, landing on each stage. Headline: "One graph. Two runtimes. Same result." Small caption: "Zero-backend by default. Clone the repo to unlock your GPU."

Scene 6 — GPU UNIVERSE. A flat scene, slow ticker of GPU vendor logos rendered as geometric marks (not real logos — generic stylizations). Each lights up as the camera pans, with a spec line: "NVIDIA — CUDA 12 · Apple — MLX & MPS · AMD — ROCm · Intel — XPU · Any Windows GPU — DirectML · Any browser — WebGPU · Fallback — CPU". Headline: "Any hardware. Zero configuration."

Scene 7 — CTA. A final snap-back to the node cloud from Scene 1 but now assembled into a single giant "W" glyph. Calm, still. Below: three links styled as monospace rows (`git clone ...`, `docker compose up`, `pnpm dev`) that copy to clipboard on click with a subtle check animation. Primary button: "Star on GitHub" — arrow icon. Small footer with MIT license, contributor avatars placeholder, and a "Made with Claude" credit.

INTERACTIONS
- Scroll is snapped per-scene (CSS scroll-snap with Framer Motion fallback). Each scene takes ~100vh of scroll distance.
- Cursor shows a faint custom pointer glow on hover over interactive 3D elements.
- Reduced motion: replace all scrolltrigger animations with simple fades; keep the content and copy identical.
- No autoplay audio. No pop-ups. No cookie banner.

CODE ORGANIZATION (in the artifact)
- Single file App.tsx with clear section comments.
- A `tokens.ts` export at the top with design tokens (below).
- Three.js scenes written as components in the same file, each wrapped in its own Canvas.
- Use `useGSAP` hook for scroll triggers; register ScrollTrigger with `gsap.registerPlugin`.
- Add a small FPS counter (bottom-right, `text-xs text-white/30 font-mono`) that's hidden unless URL has `?debug`.

DESIGN TOKENS
- Colors: bg #0a0e14, surface #131921, surface-2 #1a222d, border #2a3240, muted #6c7a8c, text #e5ecf4, accent #8b5cf6 (lavender). Category colors: data #10b981, backbone #3b82f6, head #f59e0b, eval #ef4444, deploy #14b8a6.
- Type: Inter (sans) for UI, JetBrains Mono (mono) for code and captions. H1 72/80, h2 40/48, body 16/26, caption 12/18 (px).
- Radius: 6 / 10 / 16 / 24. Shadows use lavender-tinted luminance at 12% opacity.
- Motion: primary ease `cubic-bezier(0.22, 1, 0.36, 1)` for enter, `cubic-bezier(0.55, 0, 0.68, 1)` for exit. Scroll-linked scrub duration 0.6.

OUT OF SCOPE
- No forms, no signup, no analytics SDK.
- No raster images besides an OG social card (which you do NOT need to generate in code).
- No testimonials section. No pricing. No feature comparison tables.

DELIVERABLE
A single React artifact that runs in claude.ai Artifacts or a Vite starter. It should be immediately runnable — no external asset URLs that need to exist. Generate any 3D geometry procedurally.
```

---

## Section B — Per-Scene Refinement Prompts

Use after the master prompt to sharpen a specific scene. Prepend each with: _"In the WireML marketing site we built, refine only Scene X. Keep all other scenes untouched."_

### B1. Hero — node-cloud → logo → graph

```
Scene 1 (HERO) refinement. The 3D node cloud should be made of ~40 thin rectangular cards (like business cards seen edge-on), each with a faint glow in one of the five category colors (data, backbone, head, eval, deploy). Use InstancedMesh for the cards — no individual Mesh instances (performance).

Animation timeline (scrub on scroll, 0 → 1 across 100vh):
  0.0–0.3: cards drift independently in a 3D Perlin-noise field.
  0.3–0.6: cards converge toward a shared center, rotating to face camera.
  0.6–0.8: cards snap into a flat grid shape forming the "W" of WireML.
  0.8–1.0: "W" dissolves into a left-to-right horizontal pipeline: 4 cards labeled Data, Backbone, Head, Preview, with glowing bezier wires connecting them.

Lighting: single directional light from upper-right (#d4b5ff), ambient 0.15. Add a subtle volumetric fog layer to soften depth. Camera slowly orbits 10° counter-clockwise during the whole scene.

Copy constraints: h1 must use `font-feature-settings: "ss01", "cv11"` on Inter for the refined "Wire up ML." feel. Subhead max 72 chars per line.
```

### B2. Node graph centerpiece

```
Scene 3 (NODE GRAPH) refinement. Render the graph as real flat meshes in a tilted 3D plane (perspective ~15°), not an HTML canvas. Each node is a card with:
- 8px radius
- 1px border in its category color
- an icon (use lucide-react mapped into <Html> via drei), a bold title, a subtle secondary label
- handles on left/right with a 2px glow ring

Wires between nodes are curved 3D tubes with an animated dashed pattern flowing left→right, velocity ~0.4 units/sec. When the user scrolls past the mid-point, a bright pulse travels through one wire at a time, and the node it enters lights up briefly. The sequence: Webcam → CLIP ViT-B/32 → Linear → Live Preview.

Add a tiny HUD in the bottom-left reading `graph.nodes: 4 · graph.edges: 3 · runtime: webgpu` in monospace, with each value animated to update if user clicks a node.
```

### B3. Runtime split (browser vs local)

```
Scene 5 (RUNTIME SPLIT) refinement. Two glass meshes side by side:

LEFT — browser stage. A rounded rectangle frosted-glass frame (use MeshTransmissionMaterial from drei). Inside, render a small node graph as flat geometry with subtle drift. A "WebGPU" chip floats below it, pulsing with a subtle emissive lavender rim.

RIGHT — server stage. A detailed low-poly server rack mesh (model it procedurally with BoxGeometry stacked into 1U shelves). On its face, mount a rotating GPU die (rounded box with fan details). The die surface cycles every 3s through text labels: "CUDA", "MPS", "MLX", "ROCm", "DirectML" — switched with a soft CRT-style glitch.

Between them: a transparent blue cable (thin tube) labeled "GraphJSON" in mid-air. A small JSON object token (rendered as a 3D "{ ... }" glyph) travels back and forth on loop.

Camera dolly-in on scroll, then pan left and right to emphasize parity. Never show one stage as "better" — they are peers.
```

### B4. GPU universe ticker

```
Scene 6 (GPU UNIVERSE) refinement. Horizontal marquee with 7 positions (CUDA, MLX, MPS, ROCm, DirectML, XPU, WebGPU, CPU). Each position is a stylized geometric glyph — no real vendor logos. Pick a single abstract mark per backend:
- CUDA: interlocking hexagons
- MLX: three concentric rings with an off-center dot
- MPS: a curved "M" formed by two crescents
- ROCm: a pair of descending chevrons
- DirectML: a square-within-a-square
- XPU: a plus sign inside a circle
- WebGPU: a triangle split into three gradient triangles
- CPU: a simple 2×2 grid

Glyphs sit on a slow-moving plane that the camera flies through horizontally. As each passes the center, it enlarges 1.3x and a spec line fades in beneath it in monospace (e.g., "NVIDIA · CUDA 12.4"). Background: deep navy with a faint dotted grid that parallaxes at 30% scroll speed.
```

### B5. CTA glyph assembly

```
Scene 7 (CTA) refinement. The same node cards from Scene 1 return. They drift in, then execute a final assembly: they form a large serif-style "W" ligature (actual angular geometry, not a font glyph) centered on the screen. The W has a faint lavender outline glow.

Below the W, three terminal-style rows:
  $ git clone https://github.com/OWNER/wireml
  $ docker compose up
  $ pnpm dev

Each row:
- monospace, 14px, white at 80% opacity
- on hover, full opacity + a small "copy" icon appears at the right end
- on click, the text briefly changes to "✓ copied" and a subtle lavender line slides under it

Primary button "Star on GitHub" centered below, with a star icon that spins once on hover. Button uses the accent color filled with 90% opacity; border-radius 8; shadow `0 6px 24px rgba(139,92,246,0.25)`.

Footer:
- left: "MIT · © 2026 WireML Contributors"
- center: row of 4 placeholder avatar circles (grey, subtle)
- right: small link "Made with Claude" → anthropic.com
```

---

## Section C — Design-Token & Stack Appendix

Paste this block alongside any prompt as shared context. It mirrors the WireML product palette so the marketing site feels native.

```
<context name="wireml-design-system">
Fonts:
  sans:  Inter (self-host via Inter.css) — weights 400, 500, 600, 700.
  mono:  JetBrains Mono — weights 400, 500.

Colors:
  --wire-bg:            #0a0e14
  --wire-surface:       #131921
  --wire-surface-2:     #1a222d
  --wire-border:        #2a3240
  --wire-muted:         #6c7a8c
  --wire-text:          #e5ecf4
  --wire-accent:        #8b5cf6     # lavender, used sparingly
  --cat-data:           #10b981
  --cat-preprocess:     #8b5cf6
  --cat-backbone:       #3b82f6
  --cat-head:           #f59e0b
  --cat-eval:           #ef4444
  --cat-deploy:         #14b8a6

Typography scale (px / leading):
  display:  96 / 100   -2%  letter-spacing
  h1:       72 / 80    -2%
  h2:       40 / 48    -1%
  h3:       28 / 34     0
  body:     16 / 26     0
  small:    14 / 22     0
  caption:  12 / 18    +2%  uppercase for labels

Radius scale:   2 · 4 · 6 · 10 · 16 · 24 · 32
Shadow scale:   0 2px 8px rgba(0,0,0,0.25)
                0 12px 32px -8px rgba(0,0,0,0.5)
                0 4px 24px -4px rgba(139,92,246,0.25)  (accent)

Motion:
  enter: cubic-bezier(0.22, 1, 0.36, 1), duration 500ms
  exit:  cubic-bezier(0.55, 0, 0.68, 1), duration 280ms
  scroll-scrub: GSAP scrub=0.6

Lib versions (pin these):
  three@^0.170
  @react-three/fiber@^9
  @react-three/drei@^10
  gsap@^3.12
  @gsap/react@^2
  framer-motion@^11
  tailwindcss@^3.4
</context>
```

---

## Section D — One-Shot "v0-style" Mini Prompt

If you're short on context budget (Claude Code Fast mode, or a constrained artifact window), paste this single prompt.

```
Build a dark, 3D, scroll-animated marketing site for WireML — an open-source node-graph ML workbench (Teachable Machine reimagined on CLIP/DINOv2 foundation models, runs in browser via WebGPU or locally via CUDA/MPS/MLX/ROCm/DirectML).

Stack: Vite + React + TypeScript + @react-three/fiber + drei + gsap/ScrollTrigger + @gsap/react + tailwind + lucide-react. Dark theme: bg #0a0e14, accent #8b5cf6. Fonts: Inter (UI) + JetBrains Mono (code).

Seven full-viewport scroll scenes:
1. HERO: 3D cloud of ~40 instanced node cards drifts, then snaps into a "WireML" wordmark then into a horizontal data→backbone→head→preview pipeline. Copy: "Wire up ML." + subhead + two CTAs.
2. PROBLEM: split parallax — dimmed 2019 Teachable Machine mock on left vs bright WireML graph on right. "TM was built for 2019 models. We rebuilt it for 2026."
3. NODE GRAPH: tilted 3D canvas, animated dashed wires, a pulse travels Webcam→CLIP→Linear→Preview on scroll.
4. FOUNDATION MODELS: orbit of 6 glowing orbs labeled CLIP / DINOv2 / SigLIP / Whisper / MediaPipe / LoRA, with a spec panel that updates as each centers.
5. RUNTIME SPLIT: glass-browser mesh vs glass-server-rack mesh, a GraphJSON token pings between them, GPU die cycles CUDA/MPS/MLX/ROCm/DirectML labels.
6. GPU UNIVERSE: horizontal marquee of 7 abstract geometric glyphs for each backend, spec line fades in as each centers.
7. CTA: node cards re-assemble into a large W glyph, three monospace copy-to-clipboard install rows, "Star on GitHub" primary button.

Rules: CSS scroll-snap between scenes; respect prefers-reduced-motion (swap scrolltriggers for fades); semantic HTML; one <h1>; WCAG AA; no stock images; no emoji; no forms; InstancedMesh for particle-like geometry. Provide FPS counter behind `?debug`. Deliver as a single runnable React file.
```

---

## Section E — Using This With Stitch

If you have the Stitch MCP installed (we already installed all `stitch-skills` globally — `stitch-design`, `stitch-loop`, `enhance-prompt`, `taste-design`, `design-md`, `react-components`, `remotion`, `shadcn-ui`):

1. **Synthesize the design system first:**
   - Invoke `taste-design` with the design-token appendix above as input to produce a `DESIGN.md` with enforced premium standards.
2. **Enhance the master prompt:**
   - Invoke `enhance-prompt` on Section A's prompt. This injects UI/UX keywords and tightens specificity.
3. **Generate the site:**
   - Invoke `stitch-loop` with the enhanced prompt to iteratively build each scroll section as its own screen, then stitch them.
4. **Convert screens to React:**
   - Invoke `react-components` on the generated Stitch output to produce Vite + React components with design-token consistency.
5. **Add a walkthrough video:**
   - (Optional) Invoke `remotion` to generate a screen-recorded teaser video for the README and README social cards.

---

## Section F — Handoff Checklist

After generating the site, verify:

- [ ] Lighthouse performance ≥ 95 on desktop (3D canvas must be lazy-loaded).
- [ ] All scroll animations have a reduced-motion variant.
- [ ] Keyboard reaches every CTA.
- [ ] The site loads in under 300 KB of gzipped JS excluding the 3D canvas chunk.
- [ ] The demo link points to the hosted WireML demo (`https://wireml.dev` or `https://OWNER.github.io/wireml/`).
- [ ] GitHub link is correct.
- [ ] OG image and Twitter card are present in `<head>`.
