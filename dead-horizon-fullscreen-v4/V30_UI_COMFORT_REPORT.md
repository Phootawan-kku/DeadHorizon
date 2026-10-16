# V30 - UI comfort + META auto-pause

Presentation-only pass on game.html. No damage, fire-rate, ammo, physics or save-data changes.

## META pauses the run
- `GameState.metaOpen` makes the main loop skip `update()`; closing resumes.
- Close with Esc, O, backdrop click or the RESUME button. If the pause card was already open, closing META returns to it.
- Gameplay keys (R/E/H/1-9) are ignored while paused or in META. Held input is cleared on open/close.
- Time ramps 30% -> 100% over 0.45 s after any resume.
- Test: `tests/t_meta_pause.py` (needs a static server on :8802).

## HUD / feel
- Crosshair (spread, reload ring, `[R] RELOAD` / `NO AMMO`), hit and kill markers, floating damage numbers (data existed, was never drawn).
- Coin count-up + `+N` chip, kill pulse, health shake / heal float, pickup floaters.
- Wave progress / countdown bar, off-screen enemy arrows, message log with backing plate and slide-in.
- Locked slots dimmed, low-ammo amber, small text enlarged, "SURVIVAL MODE" tag removed.
- META: fixed header/tabs with scrolling content, larger targets, fade-in, Tab focus trap.
- Toggles (META -> SETTINGS and pause card): crosshair, damage numbers, edge arrows. Saved in localStorage `deadHorizonUIV30`.

## Debug
`?debug=1` now also exposes `UX`, `UXS`, `DN` on `window.__DH`.
