# Dead Horizon V14 test scripts

Playwright (Python) scripts used to verify the V14 build. They drive the real game with real keyboard/mouse
input in headless Chromium. Paths inside the scripts point at the original authoring sandbox
(`/home/claude/...`, ports 8801 = original build, 8802 = new build); adjust `h.py`, `with_srv.sh` and the
URLs if you re-run them elsewhere.

* The debug hook `window.__DH` only exists when the page is opened with `?debug=1`. Normal play does not expose it.
* `t_gun` barrel origin x16 weapons · `t_misc` reload/empty/switch/air-fire/melee/death · `t_sync` footsteps/landing/voice cap/cleanup
* `t_audio` autoplay, offline level analysis, settings UI, mute, persistence · `t_fs` fullscreen · `t_save` old-save load, cosmetics, crafting
* `t_more` heal/gather/death/restart · `t_feet` foot-slide + idle motion · `t_layout` DOM-vs-HUD overlap at 6 viewports · `perf.py` frame cost
* `normalize.py` + `t_levels` were used to level-match all 50 synthesized sounds.
* LAST_RUN_RESULTS.txt / LAST_PERF_RESULTS.txt are the raw outputs of the final run.
