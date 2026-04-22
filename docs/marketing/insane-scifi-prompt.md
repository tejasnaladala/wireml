# WireML — Maximalist Sci-Fi Frontend Prompt

A single-paste, reference-dense, no-budget design brief for the most ambitious possible marketing site for **WireML**. Targets Awwwards-SOTD-tier output: custom WebGL shaders, cinematic scroll-driven 3D, liquid cursor behavior, sci-fi HUD language, and transitions that feel engineered rather than templated.

Paste **Section Z — THE ONE PROMPT** directly into Claude (Opus or Sonnet). Use the support sections as `<context>` attachments when refining a specific scene.

---

## Section Z — THE ONE PROMPT

```
You are designing the marketing site for WireML — an open-source node-graph ML workbench that reimagines Google Teachable Machine for the foundation-model era. Runs in-browser on WebGPU or locally on any GPU (CUDA / MPS / MLX / ROCm / DirectML / XPU / CPU). Repo: https://github.com/tejasnaladala/wireml.

REFERENCE POSTURE — NO SAFE CHOICES

The site must sit at the intersection of these references. If your output looks like a generic landing page template, you have failed. Study and emulate the confidence of:

Visual & motion reference:
- bruno-simon.com — interactive 3D portfolio, physics, spatial wayfinding.
- activetheory.net — kinetic typography, WebGL transitions, custom cursor behaviors.
- lusion.co — morphing geometry, scroll-linked 3D, shader-driven light.
- unseen.co / olivierlarose.com / robin-noguier.com — distortion displacement, image hover shaders.
- cult.lu — cinematic pinned scenes, particle flows.
- igloo.inc — editorial WebGL, scroll-synced cinematography.
- rauno.me — monochrome precision, micro-motion, type-forward.
- linear.app — premium dark-mode developer aesthetic, Inter typography, lavender restraint.
- vercel.com/home — product-forward WebGL (not decorative).
- anthropic.com — restraint, typography as hierarchy, confidence in negative space.
- arena.im/explore — editorial grids, archive energy.
- threejs.org/examples — technical specimens (volumetric lighting, postprocessing stacks, GPGPU).

Sci-fi visual grammar:
- Dune (Villeneuve) — NNA/Navigator interfaces: schematic linework, orange-amber accents on black, floating topographic contours.
- Blade Runner 2049 — melancholy neon, volumetric fog, holographic type, off-white UI panels.
- 2001: A Space Odyssey — HAL's panel legibility, grid discipline, red pinprick accents.
- Alien (1979) — MOTHER terminal: monospace green-on-black, CRT scanlines, procedural boot sequence.
- Severance — desaturated Mac-like workstation, restrained beige/teal/off-red, sans-humanity geometry.
- Minority Report — diegetic glass interfaces, particle-thin grids, multitouch gestures visualized.
- Mirror's Edge — white-dominant sky, single red accent, architectural clarity.
- Arrival — heptapod ink rings dissolving, slow meaningful motion.
- The Expanse — practical HUDs, orbital vector overlays, engineering-honest readouts.

Absorb the spirit, not the literal graphics. Don't put a starship on screen.

STACK (pin these versions, no substitutions)

- Vite 5 + React 18 + TypeScript 5.6
- three ^0.170, @react-three/fiber ^9, @react-three/drei ^10
- @react-three/postprocessing ^3 (Bloom, ChromaticAberration, DepthOfField, Noise, Vignette, ToneMapping, SMAA, GodRays)
- @react-three/rapier ^2 (physics for Scene 1 card swarm — optional, fall back to custom spring)
- gsap ^3.12 + @gsap/react + ScrollTrigger + SplitText + Observer
- lenis ^1.1 (smooth scroll; hand to ScrollTrigger via proxy)
- framer-motion ^11 (UI transitions only — Three.js owns the canvas)
- maath ^0.10 (buffer-backed easing, noise utilities)
- troika-three-text ^0.52 (SDF 3D text with no crunch)
- lamina ^1.1 (shader authoring abstraction; optional — hand-write GLSL if tighter)
- splitting.js or SplitText (letter/word/line splits for kinetic type)
- lucide-react (icons; no emoji, ever)
- tailwindcss ^3.4 (utility UI only — never for the canvas)

If any of the above is unavailable in the artifact environment, substitute with raw three + inline GLSL. Never ship with mockup-grade geometry — every mesh is procedural or imported GLB.

CORE EXPERIENCE

The site is a 7-chapter, scroll-driven, single-page cinematic. Not a listicle. Not a feature tour. A short film about a tool. It starts dark, builds through the product's argument, and climaxes on a call to action that feels earned.

Total length: ~7 × 110vh = ~770vh of scroll. Lenis smooth-scroll ratio 1.2, momentum carry 0.08s. ScrollTrigger pins each chapter and scrubs its animation timeline with `scrub: 0.6`.

GLOBAL TREATMENTS

1. Background — never a flat color. Always a two-stop radial gradient from `#0a0a0f` (outer) to a chapter-tinted `#050508` (inner, 30% vignette center), modulated by a noise shader (uv × 120, time × 0.08) to avoid banding on OLED. Never true `#000000`.

2. Ambient blobs — every scene has 2–3 absolutely-positioned circular blurs (radius 30–50vw, opacity 0.08–0.14) that trace Perlin-noise curves over 30–45s. Colors taken from the chapter's assigned accent. Use `transform: translate3d()` only; never animate `filter` or `box-shadow`.

3. Grain + scanlines — a full-viewport postprocess overlay:
   - Animated film grain (noise at 16fps, 6% opacity, blend multiply).
   - Sparse CRT scanlines (`repeating-linear-gradient(transparent 0 3px, rgba(255,255,255,.02) 3px 4px)`).
   - Chromatic aberration at the viewport edge only (use @react-three/postprocessing's ChromaticAberration with a radial `offset` uniform driven by distance-from-center).

4. Lighting — one key light, one fill, one rim. Key: `#d4b5ff` from upper-right. Fill: `#3b82f6` at 20% intensity from below. Rim: `#8b5cf6` from behind camera. Shadows: baked, never real-time.

5. Depth of field — enabled (FocusDistance = scroll-linked, pulses slightly with breathing: `0.5 + 0.05 * sin(t)`). Bokeh scale 1.2. Aperture 0.01.

6. Camera — not static. Default dolly drift of 0.1 units/sec along z-axis; scroll modulates y-offset and FOV (52 → 46 across each chapter). Easing: `cubic-bezier(0.16, 1, 0.3, 1)` (Linear's Expo.out — industry premium-dark standard).

7. Tonemapping — ACESFilmic, exposure 1.15, gamma 2.2. Don't ship with Linear or Reinhard — ACES is what makes the glow read cinematic.

8. Bloom — threshold 0.55, intensity 0.6, kernelSize 5 (LARGE). Applied only to meshes with `userData.bloom = true`. Emissive materials selectively bloom.

9. Cursor — replaced. See CURSOR section below.

10. Sound (optional, off by default with a toggle in bottom-right) — a 12-second ambient loop of a breathy synth pad in C minor, -24 LUFS, fades in over 3s after first user interaction. One earcon on primary CTA click (single soft 440→660Hz swell). Never autoplay.

CURSOR — a custom pointer system, not `cursor: none` cheese

- A small solid dot (8px, white at 80% opacity) follows the actual mouse position with 0ms lag (precise hit).
- A larger soft ring (40px, 1.5px border `#8b5cf6`, mix-blend-difference) follows with lerp ~0.12 — gives the signature drag-and-catch-up feel.
- On hover over interactive elements, the ring:
  - Expands to match the element's bounding box with a 12px outset (magnetic capture).
  - Borrows the element's category color.
  - Snaps the dot to the element's center with a spring (stiffness 400, damping 28).
- On hover over 3D elements inside the canvas, the ring shows the element's schema id in a monospace caption (12px, appears 4px right of ring, fades in over 120ms).
- On press, the ring contracts to 24px and the dot ripples a WebGL distortion shader on the underlying canvas at the press position, radius 200px, decay 0.6s.
- On drag (for the node graph scene), the ring becomes a hollow crosshair, the dot leaves a 6-frame trail of decaying copies, and the WebGL canvas receives a mouseTrail uniform that paints a velvet lavender trail on a fluid-simulation buffer (persistent for 2s).
- On reduced-motion, the cursor is standard browser default. No ring, no trail.

SCROLL — every pixel of scroll is earned

- Lenis smooth scroll; expose its `scroll` and `velocity` as CSS custom properties on `:root` (`--scroll`, `--vel`). Every chapter can animate against these.
- ScrollTrigger pins each chapter for ~110vh and `scrub: 0.6` the GSAP timeline. Small forgiving hysteresis on enter/leave so back-scrolling replays the chapter.
- A right-edge chapter rail (section G6 of the existing prompt pack): 7 dots, the active one a capsule, tinted to the chapter. Click scrolls via Lenis.
- A top-edge hairline progress bar (1px tall, lavender) tied directly to scroll (0–100%).
- Snap mode: `scrollSnapType: 'y proximity'` with 5% tolerance — feels cinematic without feeling locked.
- Scroll velocity drives subtle but visible effects globally:
  - Chromatic aberration strength = base + vel × 0.6 (capped).
  - Bloom intensity = base + vel × 0.2.
  - Depth of field blur = base + vel × 0.4.
  - A very subtle RGB-split on all h1s tied to `--vel`.
- A small "SCROLL ↓" indicator on the hero with a slow 2s pulse, fading out the moment user scrolls 5vh.

TRANSITIONS — between chapters, not within

- Scene-to-scene transition: a radial wipe combined with a shader morph. As the next scene enters, a circular mask expands from cursor position (or screen center if no recent cursor movement) over 700ms with a GodRays burst along the edge. Matching exit from the previous scene uses `MeshTransmissionMaterial` ramping opacity to 0 while its ior twists from 1.5 → 1.05 (glass shattering into air).
- For Scene 3 (node graph) → Scene 4 (foundation models) transition: the nodes explode outward in a radial burst, each converting into one of the orbs in Scene 4. Use a shared layout technique: before the transition, render the destination orbs at the source node positions (opacity 0), animate them together. This is the single most important transition — it communicates "nodes contain models".
- Every section also has a **letterbox bar animation**: the top and bottom black bars slide in 8% viewport height during the transition, hold for 400ms, and slide out during the next scene's entrance. Gives the chapter-break a cinema feel.

SHADER LIBRARY — exact GLSL snippets to generate

Generate the site using these custom fragment shaders inline. Don't use MeshBasicMaterial for any hero geometry.

1. Fresnel rim (on every orb, card edge, wire):
```glsl
vec3 viewDir = normalize(-vViewPosition);
float fresnel = pow(1.0 - dot(viewDir, vNormal), 3.0);
vec3 rim = uRimColor * fresnel * uRimIntensity;
```

2. Animated wire-pulse (on tube geometries between nodes):
```glsl
float pulse = smoothstep(0.48, 0.5, fract(vUv.x - uTime * 0.4))
            - smoothstep(0.5, 0.52, fract(vUv.x - uTime * 0.4));
vec3 pulseColor = uWireColor * (0.3 + 1.8 * pulse);
```

3. Holographic interference (on the GraphJSON token in Scene 5):
```glsl
float bands = sin((vUv.y + uTime * 0.3) * 180.0) * 0.5 + 0.5;
float iridescence = mix(0.6, 1.0, bands);
vec3 color = mix(uColorA, uColorB, bands) * iridescence;
```

4. Fluid cursor trail (fullscreen effect; renders to a framebuffer, sampled back):
```glsl
// A FBO ping-pong at 1/2 resolution. Each frame:
//   1. Decay previous buffer by 0.98.
//   2. Paint a radial gradient at uMouse scaled by uVelocity.
//   3. Blur with a 5-tap separable Gaussian.
// In the main pass, sample this buffer and displace the scene's UVs by its R channel × 0.008.
```

5. Godray (scene 5 & transitions):
Use drei's `Rays` with `<Effects>` stack, or write a radial lightshaft shader keyed to a light source position in screen space.

6. CRT glitch (once per scene, lasting ~120ms at scroll-entry):
```glsl
float slice = step(0.98, fract(vUv.y * 50.0 + uTime * 4.0));
vec2 offset = vec2(slice * (sin(uTime * 50.0) * 0.03), 0.0);
vec3 col = vec3(
  texture2D(uTex, vUv + offset + vec2(0.004, 0.0)).r,  // R split
  texture2D(uTex, vUv + offset).g,                      // G center
  texture2D(uTex, vUv + offset - vec2(0.004, 0.0)).b    // B split
);
```

7. Displacement on image hover (Scene 3 node preview tooltips): ship `RawShaderMaterial` with a noise-driven displacement uniform driven by `pointer.x/y` distance from the element center. Max displacement 16 pixels.

8. Volumetric fog (scene 1, 5, 7): a simple ray-march in the fragment shader of a fullscreen quad, stepping through a 3D Perlin noise field, intensity keyed to scroll progress.

SEVEN CHAPTERS — extended cinematic brief

CHAPTER 1 — AWAKENING. Empty black screen for the first 300ms. A single lavender dot appears at screen center. It breathes once (scale 1 → 1.1 → 1 over 900ms). Then it shatters into ~40 floating node-cards (InstancedMesh, thin rectangles like seen-edge-on business cards) that scatter with physics, drifting in 3D Perlin noise. Each card has a 1px emissive border in its category color. As scroll starts:
  0.0–0.3: Cards drift; camera dollies slightly forward.
  0.3–0.5: A GodRay burst from upper-right. Cards rotate to face camera.
  0.5–0.7: Cards assemble into a kinetic "W" — but it's the W formed by the letters W-I-R-E-M-L crashing in from off-screen at varied speeds, each word flying past camera. SplitText applied. Final word stops at center.
  0.7–0.9: The wordmark dissolves — each letter becomes a small data-flow block. The W becomes Data. The I becomes Backbone. The R becomes Head. The E becomes Preview. They line up horizontally and grow a glowing bezier wire between them.
  0.9–1.0: Camera pulls back revealing the full hero layout with h1 "Wire up ML." composed in `clamp(4rem, 11vw, 11rem)`, subhead, two CTAs, device badge strip.
Ambient: 3 lavender blobs tracing Perlin paths. Background grain at 8%. Heavy bloom on the node edges. Audio fade-in trigger if sound is enabled.

CHAPTER 2 — INDICTMENT. Hard cut (black frame for 1 frame) to a split-screen diptych. Left half: a pixel-perfect 3D recreation of Google Teachable Machine's 2019 UI rendered as a flat 3D plane at 15° tilt, lit harshly, desaturated to 40%. An etched-glass "2019" numeral hovers over it. Right half: the WireML node graph canvas rendered bright, clean, with CLIP / DINOv2 / Zero-shot labels visible. Scroll does the following:
  0.0–0.4: Camera slides from dead center to right, pushing the 2019 panel off-screen over a cliff (actual 3D motion, not just slide).
  0.4–0.7: The right panel zooms in as if the graph were the new operating theater. A horizontal scroll bar of backbone names (CLIP ViT-B/32, DINOv2, SigLIP, Whisper, MediaPipe) streams past in monospace at 40px/sec.
  0.7–1.0: h2 assembles from SplitText letters flying in from edges: "TM was built for 2019 models. We rebuilt it for 2026." The period is typeset as a bright lavender dot.
Mini-CTA: "See the full node library →" in monospace 14px at bottom-right, magnetic cursor target.

CHAPTER 3 — THE GRAPH (centerpiece). Full-canvas 3D React-Flow-style scene. The canvas is perspective-tilted (y 8°, x 6°) and floats in a void. Nodes are real 3D meshes with troika-three-text labels. Wires are `TubeGeometry` with the animated wire-pulse shader. A particle field (instanced points, ~1200) drifts behind the canvas, tinted green (data flow).
  On scroll:
  0.0–0.2: Camera tilts further, 4 nodes appear (Data → CLIP → Linear → Preview). Each node's edges draw on in a schematic-style stroke animation (like CAD software).
  0.2–0.5: A bright pulse of light enters Webcam → travels left-to-right through CLIP → Linear → Preview, lighting each node for 400ms in turn.
  0.5–0.8: Cursor hover tooltip demo: three tooltips appear one after another, showing each node's schema id in monospace. Each tooltip is its own 3D plane with fresnel edges.
  0.8–1.0: A tiny HUD in the bottom-left reads `graph.nodes: 4 · graph.edges: 3 · runtime: webgpu` with each value counting up in SplitText digits.
Mini-CTA: "Try the image-classifier template →" anchored bottom-right.

CHAPTER 4 — THE ARSENAL. An orbit of 6 translucent capability orbs (Icosphere subdivisions 5, MeshTransmissionMaterial with transmission 0.95, thickness 0.5, ior 1.45, chromatic aberration 0.06). Each orb has a particle shader inside it (fragment shader ray-marching a 3D volume of simplex noise tinted to the model family). Labels: CLIP / DINOv2 / SigLIP / Whisper / MediaPipe / LoRA.
  On scroll:
  0.0–0.2: Orbit tilts toward camera. Each orb's label fades in from 0 opacity with a subtle chromatic fringe.
  0.2–0.7: Orbit rotates slowly. Whichever orb crosses the screen center gets a spec panel fading in to its right (model name, feature dim, download size, supported devices as chips). The panel uses the holographic interference shader.
  0.7–1.0: All 6 orbs assemble into a column on the right. h2: "Ten years of backbones in a drag-and-drop library." Each orb now has a 1px outline of category color.
Mini-CTA: "Browse the backbone catalog →"

CHAPTER 5 — THE FORK IN THE ROAD. Split stage with TransmissionMaterial glass meshes.
  Left: a glass browser-window frame floating in the void. Inside its viewport, a tiny animated node graph. A small emissive WebGPU chip badge floats below it, faintly pulsing.
  Right: a detailed low-poly 3D server rack (procedural — boxGeometry 1U shelves stacked 8 high with fan meshes). On its face, a GPU die (roundedBoxGeometry with emboss for fan blades) slowly rotates. The die's surface is a render target that displays cycling labels: "CUDA" → "MPS" → "MLX" → "ROCm" → "DirectML" with a CRT glitch transition between each, 1.2s per label. STOPS after one full cycle (5 labels) and holds on the last for the rest of the scene (motion-safety rule).
  Between them: a thin blue wire renders GraphJSON — a small 3D `{ ... }` glyph flies back and forth. As scroll happens, the JSON token flies left-to-right, then right-to-left.
  Camera: dolly-in, then pan to reveal parity — both stages equal size, equal luminance. Copy aside: "One graph. Two runtimes. Same result."
Mini-CTA: "Clone the repo to unlock Power Mode →"

CHAPTER 6 — THE UNIVERSE. Horizontal scroll sub-section (pinned vertical, scroll maps to horizontal translate). A plane of 7 abstract geometric glyphs tiled horizontally, each representing one backend. Marquee moves at 40px/sec continuously + is scrubbed by scroll (both motions composed).
  Glyphs (all procedurally drawn with shader lines, no images):
  1. CUDA — interlocking hexagons.
  2. MLX — 3 concentric rings with off-center dot.
  3. MPS — curved "M" from two crescents.
  4. ROCm — descending chevrons.
  5. DirectML — square in square.
  6. XPU — plus sign in circle.
  7. WebGPU — triangle split into gradient thirds.
  8. CPU — 2×2 grid.
  As each glyph crosses screen center, it enlarges 1.35×, emits a brief flare of sparks (instanced points) in its associated vendor-color tint, and a spec line types in underneath in SplitText monospace.
  Background: a grid of dots at 30% parallax speed — moves slower than the glyphs.
Mini-CTA: "Run WireML on your hardware →"

CHAPTER 7 — RESOLUTION. The card swarm from Chapter 1 returns in reverse. Cards drift in, assemble into a single enormous "W" ligature (angular custom geometry, Blender-style hand-drafted, not a font). The W rim uses the fresnel shader, glowing lavender. It holds absolutely still — the first time in the site anything has truly stopped moving.
  Below: three monospace terminal-style rows, rendered as 3D text (troika-three-text) on a faint plane:
    $ git clone https://github.com/tejasnaladala/wireml
    $ docker compose up
    $ pnpm dev
  Each row has a faint blinking block cursor at its end. On hover, a "copy" icon fades in at the right; on click, the text briefly flickers to "✓ copied" with a glitch shader, and a lavender line slides under it.
  Primary CTA: "Star on GitHub" — filled lavender button with a single spinning star icon. On hover, the button gains a volumetric glow (a real 3D halo mesh behind it). On click, the whole scene flashes white for 80ms.
  Footer (HTML, not 3D):
    [ left: "MIT · © 2026 WireML Contributors" ]
    [ center: 4 placeholder avatar rings ]
    [ right: "Made with Claude" → anthropic.com ]
  A single closing 1-frame letterbox bar animation exits the scene.

TEXT TREATMENT

- Display h1 in hero: `clamp(4rem, 11vw, 11rem)`, weight 900, tracking -0.05em, line-height 0.92. Inter with feature settings `"ss01", "cv11"`.
- Secondary h2: `clamp(2.5rem, 5vw, 4rem)`, weight 700, tracking -0.02em. Uppercase overline in monospace 11px with letter-spacing 0.18em above.
- Body: 16/26, weight 400. Max line length 68ch.
- Monospace: JetBrains Mono weight 500 for code/captions, weight 400 for long lines. Ligatures ON.
- Kinetic SplitText on every h1/h2 entry. Letters stagger 18ms with ease `expo.out`. Subtle y translate -40px → 0.
- Scroll-variable axis: the h1 weight is animated via font-variation-settings `'wght' X` from 700 at start to 900 at mid-scroll back to 700 at end. Requires Inter variable font.

COLOR + TINT

Base palette — the product's tokens (locked):
  bg-a #0a0a0f · bg-b #050508 · bg-c #020203 · surface #131921 · border #2a3240
  text #e5ecf4 · muted #6c7a8c · accent #8b5cf6 · data #10b981 · backbone #3b82f6
  head #f59e0b · eval #ef4444 · deploy #14b8a6

Per-chapter accent tint (soft hue on blobs/rim lighting only — never on body text):
  Ch1 Awakening      → lavender #8b5cf6
  Ch2 Indictment     → cool grey  #6c7a8c
  Ch3 The Graph      → data green #10b981
  Ch4 The Arsenal    → backbone   #3b82f6
  Ch5 Fork           → head amber #f59e0b
  Ch6 Universe       → eval red   #ef4444
  Ch7 Resolution     → deploy teal #14b8a6

MOTION CONTRACT (non-negotiable)

- Every animation respects `prefers-reduced-motion: reduce`. Reduced = fades only, no scrub. Copy still delivers the full pitch.
- `pointer: fine` required for cursor ring. Touch devices use a simplified tap-ripple.
- No infinite-loop decorations (blobs fade after 45s or only animate while section is in view).
- GPU die label cycle stops after one complete pass.
- Max 2 focal motion elements per chapter at any instant.
- No horizontal page-level scroll except the pinned Chapter 6 sub-section.
- 60fps minimum on a 2023 M1 MacBook Air in Chrome stable. If unsure, cull.

ACCESSIBILITY (hardened)

- Canvas has an `aria-hidden="true"` but every semantic beat has an `sr-only` text equivalent positioned after it.
- Every interactive 3D element gets a parallel HTML focusable proxy (div positioned at its screen projection with aria-label, tabIndex 0). Tab order matches visual left-to-right.
- On focus, the 3D element gains a visible 2px outline (a second scaled-up mesh with additive blending tinted to the chapter color).
- All icon buttons have aria-label. Click targets are 44×44 minimum.
- WCAG AA on all text over backgrounds. h1 on hero passes AAA.
- `prefers-color-scheme: light` opens a minimal light-mode fallback (no 3D, same copy, same CTAs, typography intact). The link is `?lite` too, for share cards.
- Axe-core CI blocks the deploy on any serious issue.

PERFORMANCE BUDGET

- LCP element is the hero h1 text (rendered to HTML, not canvas). Canvas loads after LCP.
- Initial JS payload ≤ 280 KB gzipped excluding the 3D canvas chunk.
- 3D canvas chunk ≤ 700 KB gzipped. Models generated procedurally. Any imported GLB ≤ 200 KB.
- Images (there should be ~3 max: OG card, maybe one photo in the footer) ≤ 60 KB each, WebP with AVIF fallback, srcset.
- Lighthouse 95+ on desktop; 85+ on mobile (lower target acceptable because of canvas).

DELIVERABLE

One runnable project, either:
  (a) Single-file Vite React artifact at `App.tsx` with all shaders as inline strings, or
  (b) A full mini-repo under `apps/site/` in this monorepo with its own `package.json`, `src/`, `vite.config.ts`, and `index.html`.

Either format is fine but shaders live in `src/shaders/*.glsl.ts` (template literal exports). Components live in `src/chapters/Chapter1.tsx` through `Chapter7.tsx`. Shared effects in `src/effects/`. Postprocessing stack in `src/scene/PostFX.tsx`.

Include a `README.md` at the site root with:
  - One-liner pitch.
  - 3-second demo gif or recording instructions.
  - `pnpm dev` / `pnpm build` / `pnpm preview`.
  - "Go" button to `localhost:5173` after install.

DO NOT include:
  - A cookie banner. There's no tracking.
  - A newsletter signup form.
  - Lorem ipsum.
  - Stock photos.
  - Emoji in UI copy (allowed in README body only).
  - Comparison tables of competitors.
  - A pricing section — this is open source.
  - Testimonials — the repo is new.
  - Gradients on text (use real color + weight for hierarchy; gradient type reads cheap at display sizes).

THE TEST

If an engineer visiting the site scrolls through once and immediately clones the repo because the site felt more alive than most product demos — you shipped it right.

If a designer visiting the site saves 3 screenshots to their reference folder — you shipped it right.

If a hiring manager visiting the site opens the GitHub and stars it without reading the README — you shipped it right.

If the site feels like a portfolio template, you failed. Rebuild.

BEGIN.
```

---

## Section A — Cursor System Full Spec

Extend the cursor with these interaction modes. Render via a single full-viewport React component with absolute positioning and GSAP `quickTo` for smooth per-frame updates.

### Idle mode (default)
- 8px solid white dot at exact pointer position.
- 40px ring: `border: 1.5px solid #8b5cf6`, `mix-blend-mode: difference`, lerp 0.12.

### Link hover
- Ring grows to match link bounding box + 12px outset, opacity 0.9.
- Dot snaps to link center via spring (stiffness 400, damping 28).
- Shows link's `data-cursor-label` attribute as a 12px JetBrains Mono caption, 6px to the right of the ring, fades in 120ms.
- On `a[href^="http"]` external links, caption reads `↗ external`.

### Button hover
- Ring expands to 72px, fills with button's accent at 12% opacity.
- A subtle scale pump: 72 → 76 → 72 every 1.4s while hovered.

### Drag hover (any element with `data-cursor="drag"`)
- Ring transforms into a hollow square crosshair with corner brackets.
- Dot becomes a 4×4 plus sign.
- Caption: "CLICK + DRAG".

### 3D canvas hover
- Ring becomes a circle with a faint inner crosshair.
- Reads the raycast-hit object's `userData.schemaId` as caption.
- Ring borrows the hit object's category color.

### Press
- Ring contracts to 24px over 90ms with `ease-out`.
- The underlying WebGL canvas receives a distortion pulse: a circular displacement centered on the press, radius 200px, decaying over 600ms via fragment shader.

### Text-select mode (over any `<p>`, `<li>`, `h2–h6`)
- Ring replaced by an I-beam caret (tall thin vertical rectangle, 2px × 24px, lavender).
- Dot hides.
- On drag-select, leaves a transient selection highlight trail (rectangle fading 200ms).

### Magnetic regions
Add `data-magnetic="0.3"` to an element. On cursor within 80px, translate the ring toward the element center by `(distance × 0.3)`. Creates an "attraction field" around primary CTAs.

### Reduced motion
Disable the entire custom cursor system — restore native `cursor: auto`.

---

## Section B — Scroll System Full Spec

### Library stack
- **Lenis** for smooth scroll (proxied into ScrollTrigger).
- **ScrollTrigger** with Observer for inertial detection.
- **@studio-freight/tempus** if needed for raf batching (optional).

### Smoothness
- Lenis options: `duration: 1.2, easing: (t) => 1 - Math.pow(1 - t, 4), wheelMultiplier: 0.9, lerp: 0.08`.
- Never exceed `duration: 1.6` — past that feels drunk.

### Snap
- `scroll-snap-type: y proximity` with 5% tolerance — section edges attract but don't trap.
- Escape hatch: hold shift while scrolling to disable snap momentarily (common power-user expectation).

### Scrub
- Each chapter timeline: `scrub: 0.6`. Not instant, not lazy. Feels analog.
- Anti-stutter: wrap timeline calls in `gsap.ticker.add` inside a `useGSAP` hook.

### Scroll-velocity uniforms
Expose CSS custom properties on `:root` — updated every frame:
- `--scroll` (0–1 across whole page)
- `--chapter-progress` (0–1 within current chapter)
- `--vel` (abs velocity in viewport heights per second, capped at 3)

Use these in both CSS animations and as shader uniforms (via `useThree((s) => s.invalidate)` trigger).

### Velocity-driven global effects
- Chromatic aberration offset = `0.001 + vel × 0.002`
- DoF focus distance = `base ± vel × 0.05`
- h1 letter-spacing oscillates `-0.05em + vel × 0.003em` (subtle, readable)
- Ambient blobs translate `vel × 12vw` on x-axis (parallax-in-time)

### Horizontal scroll for Chapter 6
- Inside a pinned section: `transform: translateX(calc(var(--chapter-progress) * -100%))` on a wide inner track.
- Wheel/touch event delta composes with native vertical scroll — Lenis handles this naturally.

### Reduced motion
- Disable Lenis; use native scroll.
- All scrubs become instant (scrub: false).
- Scene transitions become 200ms fades.

---

## Section C — Sci-Fi Visual Vocabulary (distilled)

Lift these patterns:

1. **Schematic line drawing entrances.** Elements appear not fading, but being drawn — SVG `stroke-dasharray` animation, 600ms, like CAD software plotting a blueprint.
2. **Monospace overlines** in uppercase 11px with letter-spacing 0.18em, above every h2. Labels like `CHAPTER 03 / 07 · THE GRAPH`.
3. **Floating HUD corner brackets** — 4 small L-shaped glyphs at the corners of hero content, 1px white at 20% opacity. Suggests a viewfinder/targeting reticle without being literal.
4. **Measurement annotations** — thin lavender lines with dimension labels floating next to key geometry, like an architectural drawing. "224 × 224 px" next to the input frame. "512d" next to the CLIP feature vector.
5. **Data-tick streams** at scene edges — a thin vertical line of fast-moving monospace digits (like a stock ticker rotated 90°). Low opacity (10%). Gives ambient "computation is happening" energy.
6. **Letterbox bars** during chapter transitions — black top/bottom bars slide in 8vh over 400ms, hold, retract. Cinema language.
7. **Selectable-feeling text** — body copy has a subtle cursor blink at the end of the last line in each block, only while that block is in view. Suggests the text was "typed".
8. **Glitch punctuation** — very rarely (once or twice per scene), a character briefly RGB-splits for 120ms before resolving. Seasons the feed of motion.

---

## Section D — The Stack Lockfile

Pin exactly these versions in `apps/site/package.json` (or whatever the site's package is named):

```json
{
  "dependencies": {
    "@gsap/react": "^2.1.2",
    "@react-three/drei": "^10.0.4",
    "@react-three/fiber": "^9.0.4",
    "@react-three/postprocessing": "^3.0.4",
    "@studio-freight/lenis": "^1.0.42",
    "clsx": "^2.1.1",
    "framer-motion": "^11.15.0",
    "gsap": "^3.12.5",
    "lucide-react": "^0.469.0",
    "maath": "^0.10.8",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "splitting": "^1.0.6",
    "three": "^0.170.0",
    "troika-three-text": "^0.52.4"
  }
}
```

If a version is unavailable, move latest minor — never substitute libraries.

---

## Section E — Launch Gate

Reject a candidate build if any of these fail:

- [ ] First pixel lit under 1.2s on Fast 3G emulated.
- [ ] Hero h1 readable before canvas loads.
- [ ] Cursor ring tracks at 60fps on 2022 Dell XPS running stable Chrome.
- [ ] `prefers-reduced-motion: reduce` produces a coherent, text-complete experience.
- [ ] Scene 3's pulse animation traces the Webcam → CLIP → Linear → Preview order exactly, in order.
- [ ] Scene 5's GPU label cycle stops after one full pass.
- [ ] No flash of unstyled text.
- [ ] Axe-core: 0 critical, 0 serious.
- [ ] Lighthouse desktop: ≥ 95 Performance, 100 Accessibility.
- [ ] A visitor using only a keyboard can reach, trigger, and leave all CTAs.
- [ ] The `?lite` URL param loads a no-3D static variant with identical copy.

Ship or rebuild. No halfway.
