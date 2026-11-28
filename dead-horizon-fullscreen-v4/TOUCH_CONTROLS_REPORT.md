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

## Performance on phones (adaptive render resolution)
Cause of the lag: the canvas was rendered at `min(devicePixelRatio, 2)` x 960x540 = 1920x1080 on every phone (4x the pixel work).
Measured in a throttled run (4x CPU, 26 zombies): 124 ms/frame at 1920px vs 46 ms at 960px (2.7x faster); the same scene went from ~8 fps to ~22 fps.
Now `RS` in game.html picks the resolution: touch devices start at 1.0x (cap 1.5x), desktop at min(dpr,2); AUTO steps down after 1 s of
slow frames (floor 0.75x), restores if the step did not help (resolution was not the bottleneck), and probes back up after 8 s of smooth play.
Settings -> Graphics quality: AUTO / HIGH / LOW (LOW = 0.75x + smaller particle pool). The 2D context is opaque (`alpha:false`).
touch.js no longer calls getComputedStyle every frame.

## Phone bag sheet (inventory + crafting)
In touch mode the side panel becomes a full-height sheet: BAG tab (item tiles, HEAL, ARMORY) and CRAFT tab (ALL / READY / WEAPONS / SUPPLIES
filters, recipe cards with have/need chips, one big button each, craftable first). Game is frozen while it is open. Desktop is unchanged.
Tests: `tests/t_bag_touch.py`.
