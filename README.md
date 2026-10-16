# DEAD HORIZON
### 2D Pixel-Art Zombie Survival

Dead Horizon is a browser-based, 2D pixel-art zombie survival shooter. Fight through waves of undead, collect materials, craft and unlock weapons, and build long-term progression between runs.

## Features

- **Wave-based survival:** fight Walkers, Runners, Tanks, and other specialized undead.
- **Weapon variety:** melee weapons, pistols, SMGs, shotguns, rifles, heavy weapons, and special weapons, including the Pump Shotgun.
- **Loot and crafting:** collect resources and ammunition from enemies and the environment, then use materials in the crafting system.
- **Progression:** earn Horizon Coins, track your profile and collection, and access meta-progression and cosmetic systems.
- **Pixel-art presentation:** crisp sprites, environment props, combat effects, and a dark post-apocalyptic visual style.
- **Responsive game stage:** a 16:9 canvas designed to scale to different display sizes, with fullscreen support.
- **Browser-based:** no game-engine installation or build step is required for basic local play.

## Run the game locally

### Option 1 — Open the website

Open `index.html` in a modern desktop browser. Use the site's **Play Now** button to launch the game.

### Option 2 — Serve the project locally (recommended)

Some browsers restrict local-file access to assets and scripts. If opening the HTML file directly does not work as expected, run a local HTTP server from the project directory.

**Python**
```bash
python -m http.server 8000
```

Then visit:

- Website: `http://localhost:8000/`
- Game directly: `http://localhost:8000/game.html`

Stop the server with `Ctrl+C`.

You can also use another static local server, such as the Live Server extension in Visual Studio Code.

## Controls

| Input | Action |
|---|---|
| `W` / `A` / `S` / `D` | Move |
| Mouse movement | Aim |
| Left mouse button | Fire or attack with the equipped weapon |
| `1`–`9` | Select a weapon in the hotbar, when available |
| `R` | Reload |
| `E` | Gather or interact |
| `H` | Use healing item |
| `Tab` | Toggle inventory / crafting panel |
| `O` | Open the profile / meta menu (pauses the game; `O` or `Esc` resumes) |
| `P` | Toggle optional relative pointer aiming |
| `M` | Toggle sound |
| `F` | Toggle screen effects |
| `Esc` | Pause / resume during gameplay |
| Fullscreen control | Toggle fullscreen |
| Exit Game | Leave the current game session |

Controls may vary slightly with the current game state. Some actions require the game to be actively running, and weapons or items must be available before they can be selected or used.

### Trackpad and pointer aiming

Normal aiming uses the pointer and does not require Pointer Lock. Press `P` to toggle optional relative pointer aiming. If relative aiming is unavailable, the game falls back to normal pointer aiming. For the best experience, use a current version of Chrome, Edge, or Firefox.

## Project structure

```text
dead-horizon-fullscreen-v4/
├── index.html                    # Public landing page and game launcher
├── game.html                     # Playable game and in-game interface
├── game-data.js                  # Shared weapon, enemy, item, recipe, and game data
├── art.js                        # Visual asset loading pipeline
├── audio.js                      # Audio and sound effects
├── assets/
│   ├── characters/               # Player art and sprite data
│   ├── enemies/                  # Enemy sprites and sprite data
│   ├── environment/              # Background, tiles, and environment props
│   ├── effects/                  # Combat and pickup effects
│   ├── items/                    # Inventory, crafting, and pickup icons
│   └── weapons/                  # Weapon sprites and icons
├── tests/                        # Development test scripts and test notes
└── README.md
```

The exact asset list may grow as the project is updated. Keep the `assets/` directory alongside the HTML and JavaScript files so relative asset paths continue to resolve.

## Data and customization

- `game-data.js` is the shared data source for weapon and enemy definitions and other game content.
- Weapon definitions include properties such as damage, fire rate, magazine size, reload time, spread, projectile behavior, and rarity where applicable.
- Enemy definitions include their stats and configured loot drops.
- `art.js` handles loading visual assets; keep gameplay data and rendering assets in sync when adding content.
- `index.html` contains the public-facing landing page and launcher.
- `game.html` contains the playable game, HUD, menus, controls, and gameplay implementation.

When editing the project, preserve existing item IDs and data references unless all dependent systems are updated too. Test crafting, loot, weapon switching, and save/progression behavior after changing shared data.

## Debugging and testing

For development diagnostics, open the game with the query parameter:

```text
game.html?debug=1
```

The debug mode can expose development diagnostics such as FPS, entity/input state, and data or loot logging where implemented. Do not use debug mode as a substitute for normal-play testing.

Recommended manual checks after making changes:

1. Load the landing page and start the game.
2. Verify movement, mouse/trackpad aiming, firing, weapon switching, and reloading.
3. Hold a movement key while opening or closing the inventory panel.
4. Test enemy damage, deaths, material drops, and pickup collection.
5. Test gathering, crafting, and weapon unlock requirements.
6. Test pause/resume, game over/restart, sound controls, and fullscreen/exit controls.
7. Check the layout at several viewport sizes and in landscape orientation.
8. Refresh the page and verify any persistent progression or save data.

The included `tests/` folder contains development test scripts and notes. Some scripts may contain machine-specific paths or server ports that need to be adjusted before running them. Automated checks do not replace testing in a real browser with a mouse or trackpad.

## Deployment

This is a static browser project. You can host the folder on a static hosting service such as GitHub Pages, Netlify, or Vercel.

1. Upload or push the **contents** of `dead-horizon-fullscreen-v4/` to your hosting project's root directory.
2. Ensure `index.html`, `game.html`, JavaScript files, and the complete `assets/` directory are included.
3. Configure the host to serve `index.html` as the site entry point.
4. Open the deployed website and test the Play Now flow, asset loading, fullscreen behavior, and save/progression features.

No server-side API is required for basic static hosting. Features that rely on browser storage are generally tied to the same browser and origin; changing domains or browsers may not transfer locally stored progress automatically.

## Troubleshooting

- **Blank or missing visuals:** run the project through a local HTTP server and check the browser developer console for missing files or JavaScript errors.
- **Sprites or icons missing:** confirm the `assets/` directory was uploaded without changing its folder names.
- **Game does not start:** verify that `game.html`, `game-data.js`, `art.js`, and `audio.js` are present and load successfully.
- **Controls stop responding:** click the game area to focus it; check whether the browser tab or window has lost focus.
- **Fullscreen does not activate:** browser fullscreen generally requires a direct user interaction and may be restricted by the browser or embedded preview.
- **No material drops:** check the configured enemy drop tables in `game-data.js` and verify the corresponding item IDs still exist.
- **Audio is silent:** check the in-game mute control and browser/site audio permissions. Browsers may block audio until the first user interaction.

## Credits and project status

Dead Horizon is an evolving game project. The files include project-specific visual assets, gameplay data, and development reports. Consult the reports included in the project for notes on prior visual, input, and game-feel passes.

Before publishing, review the project and asset licenses and add any required third-party credits. Do not claim compatibility or testing on a platform unless it has been verified on that platform.

---

**Project:** Dead Horizon  
**Genre:** 2D pixel-art zombie survival shooter  
**Platform:** Modern desktop web browsers  
**Technology:** HTML, CSS, JavaScript, Canvas, and local image/audio assets
