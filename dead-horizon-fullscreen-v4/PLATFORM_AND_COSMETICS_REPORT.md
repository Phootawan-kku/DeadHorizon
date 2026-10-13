# Dead Horizon V12 — Platform and Cosmetic Implementation Report

## Platform audit
- Entry points: `index.html` (site shell) embeds `game.html` in an iframe.
- Gameplay implementation: `game.html`, Canvas 2D renderer, plain JavaScript.
- Data/assets: `game-data.js`, `art.js`, `assets/`.
- No `package.json`, WebAssembly module, native binary, or native build configuration exists in the supplied project.
- This is a browser game, not a standalone x64/ARM64 executable. It can run in modern 64-bit browsers, whose runtime architecture is supplied by the browser/OS. No false 64-bit label or switch was added.
- Static deployment remains compatible with Netlify when the project folder is published as the site root.

## Changes
- `game.html`: cosmetic catalog selection, large sprite preview, DEFAULT/PREVIEW comparison, rarity/ownership/equipped status, Thai notifications, buy/equip/unequip flows, cached tinted sprite rendering, and per-weapon cosmetic assignment.
- `game.html`: validates ownership and currency before purchase, prevents duplicate purchase charges, persists cosmetic IDs in the existing `deadHorizonMetaV5` save object, and normalizes invalid equipped IDs to safe defaults.
- Character cosmetics affect the player sprite; weapon cosmetics affect the held weapon for the corresponding weapon ID; effect cosmetics tint existing combat effect sprites. Cosmetic rendering does not change gameplay stats or hitboxes.
- `README.txt`: platform audit and validation notes.

## Verification
- Passed Node.js syntax check of inline JavaScript in `game.html`.
- Checked 36 distinct referenced image asset paths from `game.html`, `art.js`, and `game-data.js`; no missing paths found.
- Tried browser testing. Local navigation was blocked by the environment policy, and headless Chromium failed during GPU initialization. Therefore visual behavior, purchase/equip end-to-end flow, save/reload persistence, and regression controls are not certified as passed and should be tested interactively.

## Run
1. Extract the ZIP.
2. Serve the `dead-horizon-fullscreen-v4` folder as a static site (recommended) or open `index.html` from a local web server.
3. The site shell embeds `game.html`; select META → COSMETICS.
4. For Netlify, publish the contents of `dead-horizon-fullscreen-v4` as the site root. No build command is required.
