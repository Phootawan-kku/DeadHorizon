# DEAD HORIZON v14 — Game Feel & Presentation Overhaul

Enhancement of the existing game (not a rebuild). All results below come from real runs in headless Chromium
(Playwright, real keyboard/mouse input) against the shipped files. Raw output: `tests/LAST_RUN_RESULTS.txt`,
`tests/LAST_PERF_RESULTS.txt`. Anything not run is marked **NOT TESTED**.

## 1. Original architecture (what was already there)

* Single-page canvas game. `game.html` holds one IIFE (~680 dense lines): state (`S`, `P`, `Z`, `B`, `PT`, `Meta`, `inv`),
  `update(dt)` / `draw()` driven by one `requestAnimationFrame` loop, polled keyboard (`keys`) and mouse (`mouse`) state,
  a 960×540 logical canvas scaled to the stage (`image-rendering: pixelated`), DOM overlays for inventory / pause / META.
* Data lives in `game-data.js` (weapons, enemies, recipes, controls); `art.js` + `assets/` hold the pixel art.
* Save = `localStorage['deadHorizonMetaV5']` (coins, owned/equipped cosmetics, weapons, stats). **Unchanged format.**
* Player art is ONE front-facing 32×48 sprite (no frames). Audio was six `beep()` oscillator blips.
* `index.html` embeds `game.html` in an iframe and starts it with `postMessage`.

## 2. How the improvements were integrated

* **`audio.js` (new, standalone)** — procedural Web Audio engine: 50 synthesized sounds, sfx→compressor→master and
  ambience buses, voice cap, per-sound rate limiting, distance/pan for world events, offline-render hook for level tests.
  No audio files, no downloads.
* **V14 layer inside `game.html`** — `PA` (player animation state machine + rig), pooled particle system `FXP`,
  lighting, shadows, new canvas HUD, audio-settings UI. It is driven by the *existing* state and hooks into the existing
  functions with ~35 small, exact-match edits (jump takeoff, ground contact, shoot, reload, hit, kill, pickup, gather,
  heal, craft, weapon switch, save, wave start). Gameplay numbers (damage, fire rate, ammo, hitboxes, physics) are untouched.
* **Animation rig** — the single sprite is sliced at runtime (head / torso / left leg / right leg) from the
  *already cosmetic-tinted* asset, so every equipped character skin stays aligned. Legs swing about the hips, torso leans
  and bobs, head lags (follow-through), squash/stretch pivots at the feet.
* One animation state machine (priority-ordered, single source of truth):
  `idle · run · jump_start · jump_up · jump_apex · fall · land · hurt · death`. Shooting / reloading / melee swing are
  independent weapon overlays, so they cannot fight with body states.

## 3. Files

**Added:** `audio.js`, `V14_GAME_FEEL_REPORT.md`, `tests/` (26 files), `screenshots/` (19 files)
**Modified:** `game.html` (80.8 KB → 113.5 KB), `game-data.js` (one added control row: `M MUTE`), `README.txt` (appended V14 notes)
**Unchanged:** `index.html`, `art.js`, `assets/**`, all other docs.

## 4. Original bugs found (and what was done)

| Bug in the original | Action |
|---|---|
| **Terrain spike at spawn**: `gyAt(2000) = 0` — the "flatten near spawn" blend multiplied its base term by `.0`, so the player spawned at the top of the screen on a ~400 px needle. | **Fixed** (one expression). Player now spawns on ground (verified `y == groundY`). |
| `#statusFS` label never positioned → sat on top of the HP bar. | Fixed (tag now drawn in the HUD). |
| Fullscreen and Exit buttons overlapped by 6 px at every size. | Fixed (CSS offset). |
| `?debug=1` threw a `TypeError` every frame on the menu (`updateDebug` before `Z` exists). | Fixed (guard). |
| Knockback `P.vx` is overwritten each frame by input, so it never has effect. | **Not changed** (gameplay). |
| Headless only: the game is sometimes paused right after launch via `index.html` (focus/visibility race). Same ratio in original (3/5) and new (4/5) builds. | Pre-existing; not changed. |

## 5. What changed

**Animation** — breathing idle with head lag; run cycle driven by *distance travelled* (cadence follows speed, direction by
velocity sign, forward lean, bob, foot lift); jump = takeoff stretch → rise (legs tucked) → apex → fall → landing squash +
dust, recovery into idle/run; hurt flinch; death pose (previously none); blink-while-invulnerable now fades instead of vanishing.
Single movement speed exists in the game, so there is one run cycle (no separate walk).

**Weapons** — barrel tip is *measured from each weapon sprite's pixels*; bullets, tracers and flash spawn there (a short
sweep from the old spawn point keeps point-blank hits identical). Per-class recoil/flash size/shake (pistol, SMG, shotgun,
rifle, sniper, launcher, flamethrower, crossbow), pixel-stepped 3-stage muzzle flash, brass casings, barrel smoke, pump/bolt
sounds, melee swing arc, reload keyframes (mag drop, tilt, rack) bound to the real reload timer, "no ammo" click rate-limited.

**Effects** — dust (surface-coloured; grass blades), landing puffs, sparks on concrete/metal ground hits, wood splinters /
rock chips when gathering, blood on hit, enemy hit-recoil + flash, enemy **death animation** (topple + fade, max 24),
explosion smoke/sparks/light, exploder warning blink, pickup bursts, heal sparkle, red damage vignette. Fixed-size
particle pool (360), no per-frame allocation.

**Audio** — 50 sounds: 8 weapon-class shots, melee, reload parts (per class), empty click, weapon switch, footsteps on
dirt/grass/concrete/metal (per map), jump/land, hurt, heal, pickup, coin, chop/mine, UI hover/click/ok/fail/open/close, craft,
zombie groan/rasp/attack/hit/death, screamer, boss roar, spit, armor hit, explosion, wave horn, ambient wind bed + creaks/gusts.
World sounds are distance-attenuated and stereo-panned. Master / Effects / Ambience / Mute (key `M`), persisted in
`localStorage['deadHorizonAudioV1']` (separate from the gameplay save). Audio starts only after a real user gesture.
There was no music in the game, so there is no music slider (Ambience is the third slider).

**Lighting / shadows** — pixel-stepped ground shadows under player and enemies anchored to terrain height (shrink/fade while airborne);
half-resolution light map (320×180) with soft holes around player, enemies, bullets, loot, street lamps and burning barrels;
warm additive glow for muzzle flashes / explosions / lamps; vignette; map-dependent ambience; reacts to real events
(`BLOOD MOON` red, `POWER OUTAGE` darker with street lamps off); 46 ambient dust motes (leaves on the forest map).

**UI** — charcoal panels with muted tactical green, amber/red only for warnings. HUD: segmented health + damage trail +
`CRITICAL`, Horizon Coins, wave/hostiles/event timer, kills, consumables, 6-slot weapon bar (selected / available / locked /
empty-ammo / reload-needed states, lift animation, switch flash), ammo+reload block with progress, world-anchored `[E]` prompt
(only when a node is actually in range), reload bar over the head, weapon-name popup, "PROGRESS SAVED" note. Redesigned
title / game-over / pause overlays; DOM panels restyled (focus rings, hover, active, disabled striping). Unaffordable crafts are
now focusable `aria-disabled` buttons that give failure feedback instead of silent dead clicks. Thai `ใช้แล้ว` / `ใช้อยู่แล้ว`
logic untouched. Audio sliders in the pause menu and a new META → SETTINGS tab.

## 6. Test report (final run: 57 assertions PASS, 0 FAIL)

| # | Checklist item | Result | Evidence |
|---|---|---|---|
| 1 | Idle animation plays | **PASS** | State `idle` for the whole window; 481–1385 player-crop pixels differ from frame 0 over 2.5 s. Amplitude is intentionally small (~1 px). |
| 2 | Running loops smoothly, no foot sliding | **PASS** | 18 stance segments measured: planted-foot drift max **1.35** / mean **0.91** sprite px (before fix: 7.2 / 4.7). Contact-sheet reviewed. |
| 3 | Jump / rise / fall / land use correct states | **PASS** | Observed sequence `jump_up → jump_apex → fall → land → run`, no flicker; landing = exactly 1 sound + 1 effect; none while grounded. |
| 4 | Direction changes | **PASS (limited)** | Left/right aim + weapon mirroring checked on 6 weapons; A→D reversal across slopes: no state flicker, no false landings. Did not frame-review the reversal instant itself. |
| 5 | Shooting while moving | **PASS** | SMG fired while running; x advanced 2013→2139. |
| 6 | Shooting while jumping | **PASS** | 7 rounds fired during 14 airborne frames. |
| 7 | Recoil/flash match real shots | **PASS** | 48 shots (16 ranged weapons × 3 aims): recoil + flash set on every shot; shot count == bullet events. |
| 8 | Projectiles leave the barrel | **PASS** | 48/48 bullets on the barrel ray (cross-track ≈ 1e-13 px); 12 frozen frames show flash on the drawn barrel tip, both facings. |
| 9 | Reload / empty / switching | **PASS** | Mag unchanged and reserve not refilled until the timer ends; sounds `mag_out→mag_in→rack` once each; switch mid-reload cancels cleanly; empty click ≤ 6 in 2 s held. |
| 10 | Footstep + weapon audio timing | **PASS (event timing)** | 11 steps / 304 px; none while idle or airborne; stop immediately on stop. *Audible quality not auditioned — see limits.* |
| 11 | Volume controls and mute | **PASS** | Slider → bus gain (0.30/0.55 read back), mute → master 0 and no nodes created, unmute restores, settings survive reload. |
| 12 | Shadows follow real positions | **PASS (visual)** | Inspected in run/jump/combat frames (ground-anchored, fade when airborne). No automated pixel assertion. |
| 13 | Lighting doesn't hide enemies/projectiles | **PASS (visual)** | Normal night, `BLOOD MOON`, `POWER OUTAGE` screenshots: 6 enemy types + player readable. Subjective, not measured. |
| 14 | No UI overlap | **PASS** | 1280×720, 1366×768, 1920×1080, 2560×1440, 1024×768: 0 overlaps, 0 off-screen. **FAIL at 844×390** (see limits). |
| 15 | Inventory / crafting / cosmetics / equipment | **PASS** | Buy + equip cosmetic via real UI, Thai equipped states, craft consumes/yields, unavailable craft = feedback and no change, heal/gather flows. |
| 16 | Existing saves still work | **PASS** | A save written by the **original** build loads intact (coins, stats, cosmetics, weapons) and persists after edits. |
| 17 | Fullscreen enter/exit | **PASS (headless caveat)** | Auto-enter on Start preserved; toggle out/in; pointer→game mapping exact each time; shooting works. Headless does not resize the viewport. |
| 18 | No new console errors / failed assets | **PASS** | 0 errors, 0 failed requests in every run. One pre-existing warning from `index.html` (`allow` vs `allowfullscreen`). |
| 19 | No particle/audio buildup | **PASS** | After combat: pooled FX 0, lights 0, corpses 0, casings 0, projectiles 0; peak FX 35/360; voices ≤ 10 (cap 34). |
| 20 | Performance in real combat | **PASS (headless)** | Table below. |
| 21 | Original systems still work | **PASS (partial)** | Weapons, reload, melee, healing, gathering, crafting, cosmetics, save/load, damage → death → restart, wave start tested. **NOT TESTED:** boss waves, map switching, attachments, daily rewards, achievements UI beyond one payout, long multi-wave runs, spitter acid damage, screamer summon. |

### Performance (headless Chromium, software rendering, identical test: pistol, strafing + jumping, N zombies)

| Scenario | Build | FPS | P95 frame interval | JS ms/frame avg / P95 / max |
|---|---|---|---|---|
| 1280×720, 18 zombies | original | 59.8 | 16.8 ms | 0.95 / 4.4 / 8.6 |
|  | v14 | 59.8 | 16.7 ms | 1.96 / 4.5 / 8.5 |
| 1920×1080, 18 | original | 59.2 | 16.8 ms | 0.59 / 1.0 / 5.1 |
|  | v14 | 59.4 | 16.8 ms | 2.04 / 5.1 / 14.1 |
| 1920×1080, 40 | original | 59.4 | 16.8 ms | 0.67 / 1.1 / 10.5 |
|  | v14 | 59.7 | 16.7 ms | 2.21 / 4.9 / 16.2 |

v14 costs ~1.3–1.6 ms more JS per frame (≈10% of the 16.7 ms budget). Profiling found lighting was ~90% of it; the light map was
halved in resolution and sprites pre-warmed (1.0 → 0.5 ms, first-frame 29 ms hitch removed). Run-to-run noise is ±0.3 ms.
Occasional single-frame spikes (up to ~16 ms) exist in v14. These are software-rendered numbers, not GPU numbers.

Audio levels (offline render of all 50 sounds): none clipped (max peak 0.80), none silent; hierarchy
sniper 0.77 > shotgun 0.73 > launcher 0.58 > rifle 0.56 > pistol 0.46 > SMG 0.36. (This was found and fixed during testing:
the first mix was mostly < −18 dBFS.)

## 7. Bugs in my own work that testing caught

Spike/TDZ crash from init order (script died at load) · light map 2× too costly + first-frame hitch · sounds far too quiet ·
planted foot skating 7 px (low-passed leg swing) · death pose never played (`update()` returns when dead) · game-over
button hanging off its panel · status label overlapping the help bar · EXIT/fullscreen overlap. All fixed and re-verified.

## 8. Known limitations (honest list)

* **Audio was never listened to.** Timing, levels, clipping, gain routing and settings are verified; how it *sounds* is a human judgement. All sounds are synthesized, so expect a stylised/retro character; replacing them with recorded samples later is straightforward (`DEF` table in `audio.js`).
* **Phone landscape (844×390) overlaps** (META/EXIT buttons vs wave/kills). The original has no touch controls and was never laid out for phones; not fixed. Tablet landscape 1024×768 is clean.
* Fullscreen was verified in headless Chromium, where the viewport doesn't change size; real-monitor scaling is covered only by the multi-resolution layout test.
* Performance numbers are software-rendered headless; no real GPU measurement.
* Rig limits: arms are baked into the torso art, so there is no arm swing (the weapon carries the hand motion); backpack follow-through is approximated by head/torso lag. The jump crouch is a short *post-launch* squash/stretch so jump responsiveness is unchanged (physics launches on the same frame).
* Bullets don't collide with props/trees in this game, so wood-splinter effects occur on gathering, not on shots. No indoor/outdoor audio variants; no music (none existed).
* `?debug=1` hook (`window.__DH`) is for the test scripts only.
* iframe launch: audio unlocks on the first key press/click *inside* the game (browser autoplay policy), so the very first sound can be a frame later.

## 9. New assets and licenses

None. No third-party audio, images or fonts were added. Sounds are generated at runtime by `audio.js` (original work);
UI text uses the system monospace stack. Existing art is unchanged.

## 10. Run and deploy

```
cd dead-horizon-fullscreen-v4
python3 -m http.server 8080        # then open http://localhost:8080/index.html  (or /game.html)
```
Deployment is unchanged: static files, publish this folder as the site root (Netlify drag-and-drop / any static host).
Serve over http(s), not `file://` — barrel-tip measurement reads sprite pixels and browsers block that on `file://`
(verified: over `file://` the game still loads, shoots and renders with no console errors, using a fixed fallback tip position, but muzzle alignment is only exact over http).
