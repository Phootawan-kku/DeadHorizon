/* =====================================================================
   DEAD HORIZON - touch controls for phones & tablets
   Loaded by game.html AFTER the main script. It only drives the game through its existing inputs
   (keys.* / mouse.* and the same reload() / useHeal() / gather() / cycleSkill() the keyboard calls),
   so gameplay rules are untouched and desktop play is unaffected.

   LEFT  half   floating MOVE stick   (left/right = walk, push up = jump)
   RIGHT half   floating AIM stick    (drag = aim, holding = fire; light aim assist toward nearby zombies)
   RIGHT edge   JUMP / RELOAD / HEAL / USE (hold to repeat) / SKILL / BAG / PAUSE
   HOTBAR       tap a weapon slot on the canvas to equip it
   Menus, perk draft, pause, game-over and the title keep their normal tap handling (this layer goes inert).

   Mode:  phones/tablets ((pointer: coarse)) start ON.  Laptops with a touchscreen switch ON at the first touch and OFF
          again at the first mouse move.  ?touch=1 forces ON, ?touch=0 forces OFF.
   ===================================================================== */
(function () {
  'use strict';
  const shell = document.getElementById('game-shell'), stage = document.getElementById('game-stage');
  const cvs = document.getElementById('c');
  const G = window.DH_API;                       // published by game.html (the main script is an IIFE, so nothing else is global)
  if (!shell || !cvs || !G) return;

  const qp = new URLSearchParams(location.search).get('touch');
  const forced = qp === '1' ? true : qp === '0' ? false : null;
  const coarse = matchMedia('(pointer: coarse)').matches;
  let on = false;

  /* ---------- styles ---------- */
  const css = document.createElement('style');
  css.textContent = `
  #touch-ui{position:absolute;inset:0;z-index:19;display:none;touch-action:none;user-select:none;-webkit-user-select:none;-webkit-touch-callout:none;-webkit-tap-highlight-color:transparent;pointer-events:none;
    --sr:clamp(44px,13vh,66px);--tb:clamp(40px,12.5vh,56px);--amber:#e0a928;--ink:#f1e6c8}
  body.touch-on #touch-ui{display:block}
  #touch-ui.live{pointer-events:auto}
  body.touch-on #game-help,body.touch-on #touchHint{display:none!important}
  .ts{position:absolute;width:calc(var(--sr)*2);height:calc(var(--sr)*2);margin:calc(var(--sr)*-1) 0 0 calc(var(--sr)*-1);border-radius:50%;opacity:.28;transition:opacity .15s;pointer-events:none}
  .ts.act{opacity:.9}
  .ts .b{position:absolute;inset:0;border-radius:50%;border:3px solid var(--amber);background:radial-gradient(circle,#1a120d66 0,#0a0705aa 100%);box-shadow:0 0 0 2px #050302,inset 0 0 18px #000}
  .ts .b:before{content:"";position:absolute;inset:26%;border-radius:50%;border:1px dashed #e0a92866}
  .ts .k{position:absolute;left:50%;top:50%;width:calc(var(--sr)*.82);height:calc(var(--sr)*.82);margin:calc(var(--sr)*-.41) 0 0 calc(var(--sr)*-.41);border-radius:50%;background:radial-gradient(circle at 35% 30%,#8a6a2a,#3a2a10 70%);border:3px solid #050302;box-shadow:0 0 0 2px var(--amber),0 4px 8px #000a}
  .ts-aim .k{background:radial-gradient(circle at 35% 30%,#b8372a,#4a0f0a 70%);box-shadow:0 0 0 2px #dc3b2c,0 4px 8px #000a}
  .ts-aim .b{border-color:#dc3b2c}
  .tcl{position:absolute;right:max(10px,env(safe-area-inset-right));top:50%;transform:translateY(-46%);display:grid;grid-template-columns:repeat(2,var(--tb));gap:8px}
  .tb{position:relative;height:var(--tb);padding:0;border:2px solid var(--amber);border-radius:8px;background:linear-gradient(#2b221a,#140e0a);color:var(--ink);font:700 11px/1 ui-monospace,Menlo,Consolas,monospace;letter-spacing:.06em;text-transform:uppercase;box-shadow:0 0 0 2px #050302,0 4px 0 #050302;touch-action:none;-webkit-tap-highlight-color:transparent;opacity:.86}
  .tb.down{transform:translateY(3px);box-shadow:0 0 0 2px #050302,0 1px 0 #050302;background:linear-gradient(#5a3f12,#2a1c08);opacity:1}
  .tb small{display:block;margin-top:3px;font-size:10px;color:var(--amber)}
  .tb-jump{grid-column:1/3;background:linear-gradient(#b8372a,#6e1511);border-color:#ffb199;font-size:13px}
  .tb[hidden]{display:none}
  #t-rotate{position:absolute;inset:0;z-index:100;display:none;place-items:center;text-align:center;background:#0a0705f2;color:var(--ink);font:700 18px/1.5 ui-monospace,Menlo,monospace;letter-spacing:.1em;pointer-events:auto}
  #t-rotate.show{display:grid}
  #t-rotate .ph{width:54px;height:92px;margin:0 auto 18px;border:4px solid var(--amber);border-radius:10px;animation:tRot 2.4s ease-in-out infinite}
  #t-rotate button{margin-top:20px;border:2px solid var(--amber);background:#1b130d;color:var(--ink);padding:10px 16px;font:700 13px ui-monospace,monospace;letter-spacing:.1em}
  @keyframes tRot{0%,25%{transform:rotate(0)}60%,100%{transform:rotate(-90deg)}}
  @media (prefers-reduced-motion:reduce){#t-rotate .ph{animation:none}}`;
  document.head.appendChild(css);

  /* ---------- DOM ---------- */
  const ui = document.createElement('div'); ui.id = 'touch-ui'; ui.setAttribute('aria-hidden', 'true');
  ui.innerHTML = `
    <div class="ts ts-move"><i class="b"></i><i class="k"></i></div>
    <div class="ts ts-aim"><i class="b"></i><i class="k"></i></div>
    <div class="tcl">
      <button class="tb tb-jump" data-a="jump">JUMP</button>
      <button class="tb" data-a="reload">RELOAD</button><button class="tb" data-a="heal">HEAL<small id="t-heal">x0</small></button>
      <button class="tb" data-a="use">USE</button><button class="tb" data-a="skill" id="t-skill" hidden>SKILL</button>
      <button class="tb" data-a="bag">BAG</button><button class="tb" data-a="pause">PAUSE</button>
    </div>`;
  const rot = document.createElement('div'); rot.id = 't-rotate';
  rot.innerHTML = '<div><div class="ph"></div>ROTATE YOUR DEVICE<br><span style="font-size:12px;color:#b3a78f">Dead Horizon plays best in landscape</span><br><button id="t-rot-ok">PLAY ANYWAY</button></div>';
  shell.appendChild(rot);
  shell.appendChild(ui);
  const elMove = ui.querySelector('.ts-move'), elAim = ui.querySelector('.ts-aim'), elHeal = ui.querySelector('#t-heal'), elSkill = ui.querySelector('#t-skill'), elRot = rot;

  /* ---------- state ---------- */
  let mv = null, aim = null;                  // active sticks {id, ox, oy, x, y}
  let kA = false, kD = false, kJ = false, jumpBtn = false;
  let firing = false, lastAim = { x: 1, y: 0 }, parity = false, useTimer = 0, rotDismissed = false, live = false;
  const slotPtr = new Set();
  const sr = () => parseFloat(getComputedStyle(ui).getPropertyValue('--sr')) || 56;
  const px = (el, x, y) => { el.style.left = x + 'px'; el.style.top = y + 'px'; };
  const knob = (el, dx, dy) => { const k = el.querySelector('.k'); k.style.transform = 'translate(' + dx + 'px,' + dy + 'px)'; };

  function placeGhosts() {
    const R = sr(), W = innerWidth, H = innerHeight;
    if (!mv) { px(elMove, Math.max(28, 0) + R + 26, H - R - 26); knob(elMove, 0, 0); }
    if (!aim) { px(elAim, W * 0.7, H - R - 26); knob(elAim, 0, 0); }
  }

  function setOn(v) {
    if (on === v) return; on = v;
    document.body.classList.toggle('touch-on', on);
    try { G.UX.LB.k = on ? .8 : .68; } catch (e) {}                 // bigger hotbar = easier tapping
    if (!on) releaseAll();
    placeGhosts(); updateOrientation();
  }

  /* ---------- helpers into the game ---------- */
  const pressKey = c => { const o = { code: c, key: c, bubbles: true, cancelable: true }; window.dispatchEvent(new KeyboardEvent('keydown', o)); window.dispatchEvent(new KeyboardEvent('keyup', o)); };
  function playing() { try { const S = G.S, GS = G.GameState; return on && S.state === 'play' && GS.isPlaying && !GS.isPaused && !GS.metaOpen && !GS.perkOpen; } catch (e) { return false; } }

  function hotbarHit(cx, cy) {
    try {
      const W = G.W, H = G.H, UX = G.UX;
      const r = cvs.getBoundingClientRect(), gx = (cx - r.left) / r.width * W, gy = (cy - r.top) / r.height * H;
      const L = UX.LB, sc = L.sc, k = L.k, OX = Math.round((W - L.sheetW * sc) / 2), LY = H - 10 - Math.round(L.slotH * sc);
      const tx = v => W / 2 + (v - W / 2) * k, ty = v => (H - 10) + (v - (H - 10)) * k;
      for (let i = 0; i < 6; i++) {
        const x0 = OX + L.slotX[i] * sc, x1 = x0 + 93 * sc;
        if (gx >= tx(x0) - 3 && gx <= tx(x1) + 3 && gy >= ty(LY - 6) - 6 && gy <= ty(LY + L.slotH * sc) + 6) return i;
      }
    } catch (e) {}
    return -1;
  }

  /* ---------- pointer routing (move / aim / hotbar) ---------- */
  ui.addEventListener('pointerdown', e => {
    if (e.pointerType === 'mouse' || !live) return;
    if (e.target.closest('.tb') || e.target.closest('#t-rotate')) return;
    e.preventDefault();
    try { window.DH_AUDIO && DH_AUDIO.unlock && DH_AUDIO.unlock(); } catch (er) {}
    const slot = hotbarHit(e.clientX, e.clientY);
    if (slot >= 0) { pressKey('Digit' + (slot + 1)); slotPtr.add(e.pointerId); return; }
    const R = sr(), left = e.clientX < innerWidth / 2;
    if ((left && mv) || (!left && aim)) return;
    const ox = Math.max(R + 8, Math.min(innerWidth - R - 8, e.clientX)), oy = Math.max(R + 8, Math.min(innerHeight - R - 8, e.clientY));
    const st = { id: e.pointerId, ox, oy, x: e.clientX, y: e.clientY };
    try { ui.setPointerCapture(e.pointerId); } catch (er) {}
    if (left) { mv = st; elMove.classList.add('act'); px(elMove, ox, oy); } else { aim = st; elAim.classList.add('act'); px(elAim, ox, oy); }
    drawSticks();
  });
  ui.addEventListener('pointermove', e => {
    if (mv && e.pointerId === mv.id) { mv.x = e.clientX; mv.y = e.clientY; drawSticks(); }
    else if (aim && e.pointerId === aim.id) { aim.x = e.clientX; aim.y = e.clientY; drawSticks(); }
  });
  const up = e => {
    slotPtr.delete(e.pointerId);
    if (mv && e.pointerId === mv.id) { mv = null; elMove.classList.remove('act'); placeGhosts(); }
    if (aim && e.pointerId === aim.id) { aim = null; elAim.classList.remove('act'); placeGhosts(); }
  };
  ui.addEventListener('pointerup', up); ui.addEventListener('pointercancel', up);
  ui.addEventListener('contextmenu', e => e.preventDefault());

  function vec(s) { const R = sr(), dx = s.x - s.ox, dy = s.y - s.oy, len = Math.hypot(dx, dy), k = len > R ? R / len : 1; return { dx: dx * k, dy: dy * k, nx: dx * k / R, ny: dy * k / R, len: len }; }
  function drawSticks() { if (mv) { const v = vec(mv); knob(elMove, v.dx, v.dy); } if (aim) { const v = vec(aim); knob(elAim, v.dx, v.dy); } }

  /* ---------- buttons ---------- */
  function act(a, down) {
    if (a === 'jump') { jumpBtn = down; return; }
    if (a === 'use') { clearInterval(useTimer); if (down) { try { G.gather(); } catch (e) {} useTimer = setInterval(() => { try { G.gather(); } catch (e) {} }, 230); } return; }
    if (!down) return;
    try {
      if (a === 'reload') G.reload();
      else if (a === 'heal') G.useHeal();
      else if (a === 'skill') { if (!G.cycleSkill()) G.AU.play('ui_fail'); }
      else if (a === 'bag') pressKey('Tab');
      else if (a === 'pause') G.setPaused(true);
    } catch (e) {}
  }
  ui.querySelectorAll('.tb').forEach(b => {
    const a = b.dataset.a;
    b.addEventListener('pointerdown', e => { e.preventDefault(); e.stopPropagation(); try { b.setPointerCapture(e.pointerId); } catch (er) {} b.classList.add('down'); act(a, true); });
    const end = e => { b.classList.remove('down'); act(a, false); };
    b.addEventListener('pointerup', end); b.addEventListener('pointercancel', end); b.addEventListener('lostpointercapture', end);
  });

  /* ---------- release everything we are holding ---------- */
  function releaseAll() {
    const keys = G.keys, mouse = G.mouse;
    if (kA) { keys.KeyA = false; kA = false; } if (kD) { keys.KeyD = false; kD = false; } if (kJ) { keys.Space = false; kJ = false; }
    if (firing) { mouse.down = false; firing = false; }
    clearInterval(useTimer); jumpBtn = false;
    mv = null; aim = null; slotPtr.clear(); elMove.classList.remove('act'); elAim.classList.remove('act'); ui.querySelectorAll('.tb.down').forEach(b => b.classList.remove('down'));
    placeGhosts();
  }

  /* ---------- per-frame: sticks -> keys / mouse ---------- */
  function assistAim(ax, ay, sx, sy) {
    const Z = G.Z, ZT = G.ZT, cx = G.cx;
    let best = null, bs = 1e9;
    for (const z of Z) {
      if (z.dead) continue;
      const d = ZT[z.t]; if (!d) continue;
      const tx = z.x - cx - sx, ty = z.y - (d.h || 50) * .5 - sy, dist = Math.hypot(tx, ty);
      if (dist < 24 || dist > 560) continue;
      let diff = Math.abs(Math.atan2(ty, tx) - Math.atan2(ay, ax)); if (diff > Math.PI) diff = 2 * Math.PI - diff;
      if (diff > 0.3) continue;
      const score = diff * 300 + dist * .2; if (score < bs) { bs = score; best = { x: tx / dist, y: ty / dist }; }
    }
    return best;
  }

  function tick() {
    requestAnimationFrame(tick);
    const p = playing();
    if (p !== live) { live = p; ui.classList.toggle('live', p); if (!p) releaseAll(); }
    if (!p) return;
    const P = G.P, cx = G.cx, mouse = G.mouse, keys = G.keys, W = G.W, H = G.H, WP = G.WP;

    // MOVE
    let L = false, R = false, J = jumpBtn;
    if (mv) { const v = vec(mv); L = v.nx < -.3; R = v.nx > .3; if (v.ny < -.62) J = true; }
    if (L !== kA) { keys.KeyA = L; kA = L; } if (R !== kD) { keys.KeyD = R; kD = R; } if (J !== kJ) { keys.Space = J; kJ = J; }

    // AIM / FIRE
    const sx = P.x - cx, sy = P.y - 22;
    if (aim) {
      const v = vec(aim);
      if (v.len > 10) lastAim = { x: v.dx / (Math.hypot(v.dx, v.dy) || 1), y: v.dy / (Math.hypot(v.dx, v.dy) || 1) };
      else if (!firing) lastAim = { x: P.dir || 1, y: 0 };
      const as = assistAim(lastAim.x, lastAim.y, sx, sy), a = as || lastAim;
      mouse.x = Math.max(4, Math.min(W - 4, sx + a.x * 170)); mouse.y = Math.max(4, Math.min(H - 4, sy + a.y * 170));
      const w = WP[P.wp] || {};
      parity = !parity;
      mouse.down = (w.auto ? true : parity); firing = true;      // semi-auto / melee: pulse the trigger so held = rapid fire
      if (!w.melee && (P.mag[P.wp] || 0) <= 0 && P.rl <= 0 && G.reserveOf(w) > 0) { try { G.reload(); } catch (e) {} }
    } else {
      if (firing) { mouse.down = false; firing = false; }
      if (L || R) { mouse.x = sx + (R ? 170 : -170); mouse.y = sy; }     // face where you walk
    }
  }

  /* ---------- HUD-ish labels ---------- */
  setInterval(() => {
    if (!on) return;
    try { const inv = G.inv, P = G.P, WP = G.WP; elHeal.textContent = 'x' + ((inv.bandage || 0) + (inv.meat || 0)); elSkill.hidden = !(WP[P.wp] && WP[P.wp].skills); } catch (e) {}
  }, 300);

  /* ---------- orientation hint ---------- */
  function updateOrientation() { elRot.classList.toggle('show', on && !rotDismissed && matchMedia('(orientation: portrait)').matches && innerHeight > innerWidth); }
  rot.querySelector('#t-rot-ok').addEventListener('click', () => { rotDismissed = true; updateOrientation(); });
  addEventListener('resize', () => { placeGhosts(); if (!(matchMedia('(orientation: portrait)').matches)) rotDismissed = false; updateOrientation(); });
  addEventListener('orientationchange', () => setTimeout(() => { placeGhosts(); updateOrientation(); }, 200));
  document.addEventListener('visibilitychange', () => { if (document.hidden) releaseAll(); });

  /* ---------- device mode detection ---------- */
  if (forced !== null) setOn(forced);
  else {
    setOn(coarse);
    if (!coarse) {                                                   // hybrid laptop: follow the last input type used
      document.addEventListener('pointerdown', e => { if (e.pointerType === 'touch') setOn(true); }, true);
      document.addEventListener('pointermove', e => { if (e.pointerType === 'mouse') setOn(false); }, true);
    }
  }
  // stop the browser from scrolling / zooming / rubber-banding while playing
  document.addEventListener('touchmove', e => { if (on && ui.contains(e.target)) e.preventDefault(); }, { passive: false });
  ['gesturestart', 'gesturechange', 'dblclick'].forEach(t => document.addEventListener(t, e => { if (on) e.preventDefault(); }, { passive: false }));
  // landscape lock where the browser allows it (Android Chrome while fullscreen)
  document.addEventListener('fullscreenchange', () => { try { if (document.fullscreenElement && on) screen.orientation.lock('landscape').catch(() => {}); } catch (e) {} });

  placeGhosts(); requestAnimationFrame(tick);
  window.DH_TOUCH = { get on() { return on; }, setOn };              // handy for tests / settings
})();
