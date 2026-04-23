# Workbench UI Kit

Pixel-accurate recreation of the WireML workbench app (React Flow node graph authoring environment). Based on `apps/web/src/` in the wireml repo.

## Components

- `TopBar.jsx` — 48px app bar with logo, graph name, templates button, runtime pill, toggle, run button.
- `NodeLibrary.jsx` — 272px left rail with search + grouped node catalog. Lock icon on `localOnly` nodes when Web Mode is active.
- `GraphCanvas.jsx` — 3D-tilt-free node graph. Cards with category color washes, SVG bezier wires, dotted background, bottom-left zoom controls, bottom-right HUD counters.
- `Inspector.jsx` — 300px right rail with node metadata and parameter inputs.
- `TemplateGallery.jsx` — modal dialog with beginner/advanced filter pills and 2-col template cards.

## Fidelity sources
- `apps/web/src/panels/TopBar.tsx`, `NodeLibrary.tsx`, `Inspector.tsx`, `TemplateGallery.tsx`
- `apps/web/src/canvas/NodeView.tsx`
- `apps/web/tailwind.config.js` + `apps/web/src/index.css`

## Run
Open `index.html` in the preview — the default view loads the "Image classifier" template (Upload + Webcam → CLIP → Linear → Live Preview) with node `n3` selected in the Inspector.
