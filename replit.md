# STRATA — The Composite Compendium

A single-file interactive web reference for materials science: elements, alloys, ceramics, polymers, and fibers. Users select two constituents, watch a composite assemble via 3D animation, and explore the resulting mechanical properties.

## Stack

- Single-file frontend: `strata.html` (HTML/CSS/JS, no build step)
- Flask backend: `server.py` — serves the HTML and proxies Gemini AI calls
- Three.js (r128, CDN) for 3D hero and forge animations
- Google Fonts: Fraunces, Inter, Space Mono
- Gemini 2.0 Flash API (key stored as `GEMINI_API_KEY` secret)

## How to run

```
python server.py
```

Opens on port 5000. The root `/` serves `strata.html`.

## AI chat

The floating chat button (bottom-right) opens STRATA AI — powered by Gemini 2.0 Flash.
It reads the current Forge state (matrix, reinforcements, computed properties) as context.
The `/api/chat` endpoint in `server.py` proxies requests to Gemini server-side so the API key is never exposed to the browser.

## File layout

- `strata.html` — the entire app (styles, markup, and JS in one file)

## User preferences

<!-- Record explicit user preferences here -->
