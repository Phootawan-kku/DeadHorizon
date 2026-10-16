/* Dead Horizon visual asset pipeline.
 * Assets are authored as hard-edged PNG pixel art and loaded once at startup.
 * Gameplay state, hitboxes and data remain independent from visual assets.
 */
(() => {
  const D = window.DEAD_HORIZON_DATA;
  const root = 'assets/';
  const images = Object.create(null);
  const paths = new Set();
  for (const w of Object.values(D?.weapons || {})) if (w.image) paths.add(w.image);
  for (const z of Object.values(D?.enemies || {})) if (z.image) paths.add(z.image);
  /* Rigged weapon-skin layers, HUD icons and shop thumbnails (baked by tools/bake_skin_layers.py). */
  const SKINS={pistol_redline:['body','mag','slide'],pistol_ct:['body','mag','slide'],shotgun_heirloom:['body','pump'],shotgun_bluearc:['body','pump']};
  for (const [id, layers] of Object.entries(SKINS)) ['icon','thumb',...layers].forEach(n => paths.add(root + 'weapons/skins/' + id + '/' + n + '.png'));
  ['pistol','shotgun','rifle'].forEach(w => paths.add(root + 'weapons/skins/' + w + '_default_thumb.png'));
  /* Single-sprite AK-47 skins (baked by tools/bake_ak_skins.py) + the default AK HUD icon. */
  ['rifle_arctic_ghost','rifle_neon_circuit','rifle_royal_bengal'].forEach(id => ['body','icon','thumb'].forEach(n => paths.add(root + 'weapons/skins/' + id + '/' + n + '.png')));
  paths.add(root + 'weapons/rifle_icon.png');
  paths.add(root + 'ui/wave_panel.png');   /* wave / hostiles HUD frame (tools/bake_wave_panel.py) */
  [
    'characters/player.png','weapons/pistol_icon.png','weapons/shotgun_icon.png','weapons/shotgun_body.png','weapons/shotgun_pump.png','weapons/pistol_slide.png','weapons/pistol_body.png','weapons/pistol_mag.png','weapons/m9/default.png','weapons/m9/default_thumb.png','weapons/m9/tigertooth.png','weapons/m9/tigertooth_thumb.png','weapons/m9/fade.png','weapons/m9/fade_thumb.png','weapons/m9/gold.png','weapons/m9/gold_thumb.png','enemies/walker_sheet.png','enemies/runner_sheet.png','characters/farmer_sheet.png','environment/hero.png',
    'items/scrap.png','items/cloth.png','items/bone.png','items/meat.png','items/ammo.png','items/wood.png','items/stone.png',
    'items/part.png','items/metal.png','items/electronics.png','items/fuel.png','items/chemicals.png','items/bandage.png','items/medkit.png','items/grenade.png','items/molotov.png',
    'environment/props/crate.png','environment/props/barrel.png','environment/props/trash.png','environment/props/vehicle.png',
    'environment/props/streetlight.png','environment/props/fence.png','environment/props/sign.png','environment/props/barricade.png',
    'environment/props/tree.png','environment/props/dead_tree_a.png','environment/props/dead_tree_b.png','environment/props/dead_tree_c.png','environment/props/tree_wide.png','environment/props/tree_tall.png','environment/props/tree_pine.png','environment/props/tree_dead.png','environment/props/rubble.png','environment/props/rock_a.png','environment/props/rock_b.png','environment/props/rock_c.png','environment/props/rock_d.png','environment/props/window.png','environment/props/door.png',
    'environment/tiles/dirt_floor.png','environment/tiles/dirt_block_1.png','environment/tiles/dirt_block_2.png','environment/tiles/dirt_block_3.png','environment/tiles/dirt_block_4.png','environment/tiles/dirt_block_5.png','environment/tiles/dirt_block_6.png','environment/tiles/ground01.png','environment/tiles/ground02.png','environment/tiles/concrete01.png','environment/tiles/dirt01.png','environment/tiles/grass01.png','environment/tiles/rubble01.png',
    'effects/muzzle.png','effects/spark.png','effects/blood.png','effects/dust.png','effects/pickup.png'
  ].forEach(p => paths.add(root + p));

  let loaded = 0;
  for (const path of paths) {
    const im = new Image();
    im.decoding = 'async';
    im.onload = () => { loaded++; };
    im.onerror = () => { loaded++; };
    im.src = path;
    images[path] = im;
  }

  window.DEAD_HORIZON_ART = Object.freeze({
    images,
    get(path) { return images[path] || null; },
    ready(path) { const im = images[path]; return !!(im && im.complete && im.naturalWidth > 0); },
    loaded() { return loaded; },
    total() { return paths.size; }
  });
})();
