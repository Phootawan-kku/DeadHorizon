DEAD HORIZON — Expanded Build / Input + Visual Sync Pass

Files
- index.html: public website / launcher
- game.html: playable game
- game-data.js: shared source of truth for weapons, enemies, recipes and controls
- assets/enemies/*.png: authored pixel-art enemy sprites used by the game and website
- assets/weapons/*.png: authored pixel-art weapon sprites used by the game and website
- assets/characters/player.png: player pixel-art sprite
- assets/items/*.png: pickup/inventory/crafting item icons
- assets/environment/: pixel-art hero scene, terrain tiles and props
- assets/effects/*.png: pixel-art combat, blood, dust and pickup effects
- art.js: single-load visual asset pipeline; gameplay state/collision remain independent

Input fix
- Pointer Events are now the primary mouse/trackpad path.
- Normal pointer aiming never depends on Pointer Lock.
- pointerup/pointercancel/window mouseup/blur/visibility/fullscreen all clear transient fire/input state.
- Canvas coordinates use getBoundingClientRect() and logical 960x540 coordinates, so CSS scaling, fullscreen and high-DPI displays are handled correctly.
- Pointer Lock is optional and can be toggled with P. It uses movementX/movementY only while document.pointerLockElement is the game canvas.
- pointerlockerror falls back to normal pointer aiming.
- Canvas does not use permanent pointer capture.
- Resize no longer steals focus on every resize.

Visual assets
The existing project did not contain external PNG/WebP/SVG enemy or weapon art; the game renders these entities procedurally with canvas rectangles. Therefore the website assets in this pass are compact SVG pixel-art representations built from those same implemented enemy/weapon identities and visual silhouettes. They are referenced by stable IDs from game-data.js rather than duplicated website-only data.

Debugging
- Add ?debug=1 to game.html to show FPS/entity/input/data diagnostics.
- P toggles optional relative pointer aiming.

Validation
- JavaScript syntax checked with Node.js.
- All 34 shared asset references were checked against files in the package.
- No while/for(;;) gameplay loops were found in the existing source.
- Full physical laptop-trackpad/manual browser testing cannot be simulated reliably in this container; the input paths were audited and the code was statically validated.


Loot/drop fix (V8)
- Root cause: the shared game-data.js enemy definitions no longer contained the original V3 `drops` tables, while game.html still read `ZT[z.t].drops`. Horizon Coins were awarded directly by `kill()`, so coins continued to work while the material loop had no entries to process.
- Restored the original V3 material/ammo/component drop tables for Walker, Runner, Tank, Spitter (the current ranged-enemy equivalent), Exploder and Boss using the existing item IDs.
- Kept the existing `PK` world-pickup pipeline, collision pickup, `add()` inventory path and crafting recipes unchanged.
- Added development-only `?debug=1` loot logging and shared drop-data validation.
- No new inventory, currency, or loot system was introduced. Newly added enemy types without a legacy drop table were left unchanged rather than inventing new balance.

Loot validation
- Node syntax checks passed for game-data.js and game.html's inline script.
- All configured drop IDs resolve to existing inventory items.
- Drop chances and quantity ranges are valid.
- Restored tables were compared against the original V3 configuration.
- 10,000-roll simulation produced loot for every configured enemy type.
- Full physical browser/manual gameplay testing is not available in this container; Chromium headless could not complete because the persistent RAF game loop prevents the headless command from terminating in this environment.

Input/multi-control fix (V9)
- Root cause: the prior transient-input helper mixed unrelated domains. `clearTransientInput()` cleared the entire keyboard map, so pressing TAB or losing Pointer Lock could erase held W/A/D/Space states. Pointer and keyboard state were therefore not independent.
- Replaced that behavior with separate held-key, pointer, and one-shot action state domains.
- TAB now only toggles the existing inventory/crafting panel and never clears movement or pointer/fire state.
- Pointer down/up/cancel/lost-pointer-capture only affect pointer/fire state; they never clear keyboard movement.
- Pointer Lock exit only clears pointer state; keyboard state remains intact.
- One-shot keyboard actions ignore auto-repeat while held movement keys continue to be represented continuously.
- Pointer movement is also observed at the game-stage level, so moving the cursor over a non-gameplay HUD element does not erase/freeze the aim coordinate.
- Visibility/blur still clear all input for stuck-key safety when the browser/window loses focus. Fullscreen changes clear pointer/action state without erasing held keyboard state.
- Existing Pause/Game Over/Fullscreen architecture and control bindings remain intact.

Multi-input validation
- Node syntax checks passed after the V9 changes.
- Static audit confirms there is no code path where pointer down/up clears the keyboard held-key map.
- Static audit confirms TAB no longer calls an all-input reset.
- Static audit confirms W/A/D/Space are stored independently and movement reads those independent states each frame.
- Static audit confirms pointer movement and mouse button state are separate from keyboard state.
- Automated headless browser interaction could not be completed reliably in this container because Chromium cannot finish the persistent requestAnimationFrame game loop; therefore physical laptop trackpad/Chrome/Edge/Firefox testing remains a local-machine validation item.


V10 VISUAL QUALITY PASS
- Replaced the previous presentation SVGs with authored hard-edged PNG pixel-art assets.
- Added a consistent dark post-apocalyptic palette, 2px-style block detailing, shared outlines and upper-left-biased highlights.
- Added player, all 14 enemy sprites, all 20 weapon sprites, item icons, terrain tiles, 12 environment props, a website/game hero scene and combat/loot effect sprites.
- Added art.js to preload visual assets once; no Image objects are created per frame.
- Gameplay collision, enemy dimensions, weapon stats, loot tables, recipes, inventory IDs, save data and controls were not changed.
- The canvas keeps imageSmoothingEnabled=false and the CSS pixel-art rendering path.
- Environment decoration is visual-only; resource nodes and gameplay hitboxes retain their existing state and dimensions.
- Website weapon/enemy cards now consume the same PNG paths from game-data.js.
- Browser automation in this environment is limited; syntax, asset-reference and static integration checks were performed.


V11 PATCH NOTES — BLANK CANVAS REPAIR
-------------------------------------
Root cause found in game.html:
- The renderer calls px(x, y, w, h, color) throughout the menu, world, effects,
  and HUD, but the px drawing primitive was missing. The first frame therefore
  threw a ReferenceError before drawing the scene.
- The requestAnimationFrame callback scheduled its next frame only after all
  rendering code completed. Any frame exception stopped the loop permanently.

Fixes:
- Restored a guarded pixel-rectangle drawing helper using Canvas 2D fillRect.
- Scheduled the next animation frame before processing the current frame, so a
  single frame exception cannot silently kill the game loop.
- Added a visible render-error overlay and console diagnostics in ?debug=1 mode.
- Kept existing gameplay data, controls, weapons, enemies, assets, save keys,
  crafting recipes, and progression logic unchanged.

Validation performed:
- JavaScript syntax check passed with Node.js.
- Audited 75 referenced PNG asset paths; no referenced assets were missing.
- Automated Chromium gameplay validation could not run in this environment
  because browser navigation was blocked by the environment policy. Please
  verify interactively after extraction using the run instructions above.


V12 — PLATFORM COMPATIBILITY + COSMETIC PREVIEW / EQUIP
-------------------------------------------------------
Platform audit:
- This project is a static browser HTML5 game using Canvas 2D and JavaScript.
- It has no package.json, native executable, native compiler target, or WebAssembly
  module in this distribution. Therefore it is not a standalone 64-bit executable.
- It runs inside the architecture of the installed browser/runtime. Modern 64-bit
  browsers can run it, but the HTML project itself does not have an x64/ARM64 binary.
- No unsupported “64-bit edition” label or fake architecture switch was added.
- Deployment remains static-host compatible (including Netlify drag-and-drop or
  publishing this folder as the site root).

Cosmetic system:
- Added a real collection grid with selectable items, rarity, owned/locked status,
  coin price, DEFAULT/PREVIEW mode, and a large sprite preview.
- The preview uses the same player, weapon, and effect PNG assets as gameplay.
- Character and weapon skins are applied through cached, tinted copies of the
  actual sprites; effect skins tint existing impact/spark art.
- Equipped character/effect IDs persist in the existing deadHorizonMetaV5 save.
- Weapon skins are stored per weapon ID in equipped.weapons, and are applied to
  the player's currently held weapon. The existing generic equipped.weapon field
  remains readable for compatibility.
- Purchase checks ownership and coin balance before charging; duplicate purchase
  is blocked. Equipping is free and does not alter gameplay statistics.
- Thai status messages and temporary success/failure toasts are included.
- Cosmetic sprites do not change collision, hitboxes, weapon stats, or damage.

Validation performed for V12:
- Node.js syntax check passed for the inline JavaScript in game.html.
- Audited 36 distinct referenced asset paths across game.html, art.js, and
  game-data.js; all referenced paths exist in this project.
- Browser end-to-end testing could not be completed in this environment:
  navigation to the local test server was blocked by policy, and headless
  Chromium exited during GPU initialization. Cosmetic interactions and gameplay
  visuals therefore still require interactive verification on a desktop browser.
- No native binary was produced because this is a static HTML5/Canvas project.


V13 — HIGH-DETAIL PIXEL ART PASS
--------------------------------
- Re-authored the player sprite with hood, amber goggles, face covering, tactical
  vest, backpack, layered clothing, gloves, knee pads, boots, and material shading.
- Re-authored all implemented enemy sprites and weapon sprites with distinct
  silhouettes and details.
- Added five tree variants and deterministic in-world variation.
- Re-authored key props and terrain tile textures.
- Updated art.js to preload the tree family; updated game.html to choose a tree
  variant by world position. Gameplay logic and collision/data files are unchanged.
- Automated checks performed: JavaScript syntax, referenced asset paths, PNG
  readability and dimensions. Browser gameplay screenshot/regression tests were
  not available in this environment; please verify in the running game.


V14 GAME FEEL & PRESENTATION OVERHAUL (see V14_GAME_FEEL_REPORT.md)
- New: audio.js (procedural WebAudio engine, no audio files). New control: M = mute/unmute.
- Audio settings: pause menu and META -> SETTINGS (master / effects / ambience / mute), saved on this device.
- Run locally:  python3 -m http.server 8080   then open http://localhost:8080/index.html
- Debug/test hook: open game.html?debug=1 (exposes window.__DH for the scripts in tests/). Not present in normal play.
- Deployment is unchanged: static files, publish this folder as the site root (Netlify drag-and-drop works).


Runner zombie sprites (V19)
- assets/enemies/runner_sheet.png (+ .json): 48x48 frames, cols = idle, jump, then 8 run frames, row 0 faces right, row 1 faces left.
- game.html runnerDraw(): picks idle (next to player), run (moving, 8-frame cycle with swinging legs) or jump (airborne).
- Applies to enemy type 'fast' (Runner). assets/enemies/fast.png (website/fallback/corpse icon) is now the idle runner.

Rock sprites (V21)
- assets/environment/props/rock_a..rock_d.png (48x48): harvestable rocks (E = mine, drops stone) now use these 4 sprites instead of the old rubble sprite.
- game.html drawResource(): variant chosen from the rock's world x, so every rock keeps the same look; rock health bar sits just above the rock.

Dirt block floor (V22)
- assets/environment/tiles/dirt_block_1..6.png (48x48, 40x40 body): the floor is now built from these blocks (pixelTexturedGround in game.html).
- 40px cells in rows under the surface, drawn in 8px strips so the top edge follows gyAt() exactly. Block 5 (grass top) is used mostly on the surface row; the other five fill the rows below. Variant per cell is a fixed hash of world column + row.
- The old 32px ground tiles are still loaded but no longer used for the floor.

Continuous dirt floor (V23)
- The floor is now one continuous texture, assets/environment/tiles/dirt_floor.png, baked from the six dirt blocks by tools/bake_dirt_floor.py.
- Block outlines are removed and neighbouring blocks are dither-blended horizontally and vertically, so there are no grid lines. Grass tufts sit on top.
- game.html pixelTexturedGround() draws it in 8px strips that follow gyAt(). To re-roll the layout or change blend width, edit the constants in tools/bake_dirt_floor.py and run it from the project root.
- dirt_block_1..6.png are kept as the bake inputs.

ESC = pause fix (V24)
- Cause 1: in fullscreen the browser uses ESC to leave fullscreen, and index.html treated "left fullscreen" as "exit game". Now it only pauses (game stays open, windowed) and RESUME re-enters fullscreen. Only the EXIT GAME buttons close the game.
- Chromium: Keyboard Lock is requested while fullscreen so ESC reaches the game and pauses without leaving fullscreen (hold ESC ~2s to leave fullscreen).
- Cause 2: RESUME and EXIT GAME in the pause menu were both position:absolute on the same spot, so clicking RESUME hit EXIT GAME. They are now side by side.
- ESC while the pointer is locked also pauses now.

Crafting materials now drop (V25)
- Metal, Electronics, Fuel and Chemicals had no source, so 17 of 22 recipes (and all 8 attachments) could never be crafted. They now drop from zombies (game-data.js enemies[*].drops):
  Metal: Walker 10%, Crawler 20%, Brute 50%, Armored 60%, Tank 80%, Boss 8-14
  Electronics: Runner 12%, Leaper 18%, Screamer 30%, Hunter 35%, Boss 3-6
  Fuel: Tank 20%, Exploder 50% (1-3), Boss 3-6
  Chemicals: Walker 4%, Swarm 6%, Exploder 15%, Spitter 40%, Mutant 55%, Boss 3-5
- Enemies that spawn from a given wave onward are the main source for that material, so early waves give Metal (Walker/Crawler) and a little Electronics/Chemicals, and the rest unlock as new zombie types appear.
- The MAPS[*].loot lists in game.html are still unused.

M9 bayonet combat knife + skins (V26)
- The Combat Knife now uses the M9 bayonet art (assets/weapons/knife.png = default M9; the old knife art is replaced).
- Four M9 skins live in the COSMETICS shop (game.html COS: knife_m9_*). Sprites: assets/weapons/m9/<name>.png (horizontal, used in hand/HUD/armory) and <name>_thumb.png (diagonal original, used in the shop).
    Default  - free, owned and equipped from the start (new saves and migrated old saves)
    Tiger Tooth - Rare, 1500 coins
    Fade        - Epic, 3000 coins
    Gold        - Legendary, 4800 coins
- Skins marked wp:'knife' always target the Combat Knife (no need to wield it to equip). Unequipping a skin returns to the default M9. Generic weapon tints (Rusted/Military/...) still work and replace the M9 skin on that weapon while equipped.
- weaponArt(id) returns the equipped skin's image for HUD slots, the ammo panel and the armory list.

Glock pistol + animation (V27)
- Pistol sprite replaced with the new Glock. Layers (48x24 canvas, built by tools/bake_glock_layers.py): assets/weapons/pistol_body.png, pistol_mag.png, pistol_slide.png; assets/weapons/pistol.png is the assembled idle sprite (used for the muzzle position); pistol_icon.png (64x24) is used for the HUD, armory and shop.
- Animation rig in game.html (drawPistolRig / pistolRigState, PISTOL_SLIDE_T):
    Fire    - slide kicks back ~3px and returns in 0.13s, plus the existing recoil, muzzle flash and casing
    Empty   - slide locks back when the magazine is empty
    Reload  - magazine slides out (12-30% of the reload), is gone (30-50%), slides back in (50-58%), then the slide is racked (85-97%). Matches the existing reload sounds.
- Weapon skins (Rusted/Military/...) tint every layer. weaponDims("pistol") is 48x24 and muzzleWorld() now uses the real image size instead of a fixed 64x24.
- V28: pistol made smaller in hand (about 0.75x of V27, 22x17 px) so it matches the character; rebuilt with tools/bake_glock_layers.py (S=0.51). Change S/CW/CH there and weaponDims('pistol') in game.html to resize again.

Pump shotgun + animation (V29)
- Shotgun sprite replaced with the new pump shotgun, rotated horizontal and built by tools/bake_shotgun_layers.py. Layers (54x20): assets/weapons/shotgun_body.png, shotgun_pump.png; shotgun.png is the assembled idle sprite (muzzle position); shotgun_icon.png (64x24) for HUD/armory/shop.
- Animation rig in game.html (drawShotgunRig / shotgunRigState):
    Fire   - recoil + muzzle flash as before; then ~0.16s later the pump racks back and forward (0.46s total), ejecting the red spent shell at full back (replaces the old instant casing)
    Reload - shells are pushed up into the loading port one at a time at the existing shell_in marks (10/30/50/70%), then the pump is racked at 88-98%
- Weapon skins (tints) apply to both layers.

Rigged weapon skins: Pistol + Pump Shotgun (V30)
- Four new weapon cosmetics in the COSMETICS shop (META -> COSMETICS), all cosmetic-only (no stat changes):
    Pistol | Redline          Rare   1500   black Glock 19, red trim, red-dot sight
    Pistol | CT Tactical      Epic   2500   Glock 19 with weapon light + red-dot sight
    Pump Shotgun | Heirloom   Rare   1200   dark-red wood stock, brass barrel
    Pump Shotgun | Blue Arc   Epic   3000   black with blue energy lines
  Names, rarities and prices are plain entries in the COS table in game.html (search "pistol_redline") - edit freely.
- Each skin carries its own animation layers so the slide kick / magazine drop / pump rack keep working:
    Glock  : assets/weapons/skins/<id>/body.png, slide.png, mag.png   (48x24, same canvas as the default rig)
    Shotgun: assets/weapons/skins/<id>/body.png, pump.png             (54x20, same canvas as the default rig)
    Both  : icon.png (64x24 HUD / armory icon), thumb.png (48x48 original export used by the shop preview)
  Skins are aligned so the barrel tip sits on the same pixel as the default gun, so muzzle flash / bullet origin are unchanged.
- tools/bake_skin_layers.py rebuilds everything from the original 48x48 exports kept in tools/skin_sources/.
  To add another skin: drop the 48x48 export in tools/skin_sources/, add it to SRC (+ PISTOL split rows or SHOTGUN forend rect)
  in the script, run `python3 tools/bake_skin_layers.py` from the project root, add its id to SKINS in art.js, and add a
  COS entry using skinArt(id, layers, weaponId) in game.html.
- game.html changes: COS entries + skinArt() helper, COS_DESC (Thai), weaponArt() (rig skins use their own icon),
  drawPistolRig/drawShotgunRig take an optional layer set (per-skin shell-port offset via rig.shell), shop DEFAULT/PREVIEW
  falls back to <weapon>_default_thumb.png when a weapon has no default-skin entry.
- No default-skin entry was added for pistol/shotgun on purpose: the existing generic tints (Rusted/Military/Toxic/Carbon/Gold)
  keep working on the stock guns. "Unequip" on a rigged skin returns to the stock gun.
- Verified in headless Chromium (tests/t_weapon_skins.py): all assets load with no failed requests or console errors; buy/equip/
  unequip through the real UI; coins charged once; equipped skin persists across reload; unknown/un-owned ids are stripped on load;
  in-hand rendering checked while idle, firing and reloading for all four skins.

AK-47 art + skins for the Assault Rifle (V30)
- The default Assault Rifle now looks like a wood-and-steel AK-47 (assets/weapons/rifle.png 48x24, HUD icon rifle_icon.png 64x24).
  Stats are unchanged. weaponDims() draws it 1:1 (48x24) like the pistol.
- Three cosmetic-only skins in META -> COSMETICS (they only apply while wielding the Assault Rifle):
    AK-47 | Arctic Ghost    Rare        1500   ice-white receiver, blue-grey shading
    AK-47 | Neon Circuit    Epic        3000   deep-purple body, cyan circuit lines
    AK-47 | Royal Bengal    Legendary   4800   gold with black tiger stripes, dark wood furniture
  Names / rarities / prices are plain COS entries in game.html (search "rifle_neon_circuit") - edit freely.
- These are single-sprite skins (the AK has no animated parts): COS entries use the new skinImgArt(id, weaponId) helper
  (img = skins/<id>/body.png drawn in hand, icon.png for the HUD / armory, thumb.png = the original 48x48 export for the shop).
- tools/bake_ak_skins.py rebuilds everything from the original exports in tools/skin_sources/rifle_*.png. Each skin is shifted
  vertically so its barrel row matches the default AK (game.html measures the muzzle from rifle.png), so flash / bullets are unchanged.
- Tests: tests/t_ak_skins.py (buy / equip / unequip / persistence / un-owned id stripping / asset loading, plus close-up screenshots).
