# Touch controls (phones & tablets)

Files: `touch.js` (the whole feature), a 3-line bridge `window.DH_API` at the end of the main script in `game.html`
(the game's script is an IIFE, so touch.js can only see what the bridge publishes), viewport/dvh tweaks in `game.html`,
`manifest.webmanifest` + icons, and a "Touch" note in the website's Controls section.

Layout (landscape): LEFT half = floating move stick (left/right walk, push up = jump) · RIGHT half = floating aim stick
(drag = aim, hold = fire, light aim assist within ~17 deg of a zombie) · right edge = JUMP, RELOAD, HEAL, USE (hold repeats),
SKILL (only with a skill weapon), BAG, PAUSE · tap a hotbar slot on the canvas to equip.

Mode: `(pointer: coarse)` devices start ON; laptops with a touchscreen switch on at the first touch and off at the first mouse move;
`?touch=1` / `?touch=0` force it.  The layer goes inert for title, pause, game-over, META and perk draft so their normal taps work.
Semi-auto / melee weapons get a pulsed trigger while the aim stick is held; empty mags auto-reload.

Test: `tests/t_touch.py` (needs the server on :8802, see tests/with_srv.sh).
