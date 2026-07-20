# STRATA — The Composite Compendium

A single-file interactive web reference for materials science: elements, alloys, ceramics, polymers, and fibers. Users select two constituents, watch a composite assemble via 3D animation, and explore the resulting mechanical properties.

## Stack

- Pure HTML/CSS/JS — no build step
- Three.js (r128, CDN) for 3D hero and forge animations
- Google Fonts: Fraunces, Inter, Space Mono

## How to run

```
python3 -m http.server 5000
```

Then open `/strata.html` in the preview.

## File layout

- `strata.html` — the entire app (styles, markup, and JS in one file)

## User preferences

<!-- Record explicit user preferences here -->
