# Dead Horizon V13 — High-detail Pixel Art Overhaul

## Platform and scope
This is the existing HTML5/JavaScript Canvas 2D project. This pass changes visual PNG assets and the existing asset/render integration only. `game-data.js` was not modified; weapon stats, enemy stats, collision values, loot tables, recipes and save schema remain untouched.

## Artwork authored and integrated
- `assets/characters/player.png`: detailed 32×48 hooded survivor with amber goggles, mask, backpack, tactical vest, straps, pouches, gloves, knee pads and boots.
- `assets/enemies/*.png`: re-authored all 14 implemented enemy types (`normal`, `fast`, `tank`, `spitter`, `screamer`, `exploder`, `armored`, `crawler`, `leaper`, `brute`, `swarm`, `mutant`, `hunter`, `boss`) with distinct silhouettes and type-specific accents.
- `assets/weapons/*.png`: re-authored all 20 existing weapon sprites with weapon-family-specific forms and mechanical details. Existing filenames/IDs are preserved.
- `assets/environment/props/tree.png` plus `tree_wide.png`, `tree_tall.png`, `tree_pine.png`, `tree_dead.png`: five different canopy/trunk silhouettes, loaded via `art.js`. `game.html` chooses variants deterministically from world position.
- Re-authored key props: crate, barrel, rubble, fence, vehicle, streetlight, sign, trash, barricade, window, door.
- Re-authored six terrain textures: grass01, dirt01, ground01, ground02, concrete01, rubble01.

## Source changes
- `art.js`: registers and preloads the additional tree variant PNGs in the existing shared asset pipeline.
- `game.html`: draws one of five tree variants for tree resources, deterministically from world position. Resource interaction, hitpoints, collision, and drops are unchanged.
- `VISUAL_STYLE_GUIDE.txt`: documents dimensions, palette and art families.
- `README.txt`: adds V13 notes.
- `V13_PIXEL_ART_OVERHAUL_REPORT.md`: this report.

## Verification performed
- `node --check game-data.js`: passed.
- `node --check art.js`: passed.
- `node --check` on the non-empty inline JavaScript in `game.html`: passed.
- Validated 79 PNG files for readable image data: no corrupt PNGs found.
- Checked static PNG paths referenced by the game data and art loader: 34 paths checked, none missing.
- Generated a contact sheet of representative assets for visual inspection: `dead-horizon-art-contact-sheet.png`.

## Not verified
An interactive browser/Chromium session was not available here, so this report does not claim that gameplay screenshots, FPS, animation quality, cosmetic equip/persistence, save/load, or every resolution passed an end-to-end test. Please open `index.html` through a local static server and check a gameplay scene, weapon hotbar, META → COSMETICS, movement/combat, and save/load before deploying.
