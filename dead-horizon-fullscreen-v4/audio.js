/* Dead Horizon audio engine (V14).
 * All sounds are synthesized at runtime with the Web Audio API: no audio files,
 * no third-party assets, no licensing concerns. The AudioContext is only created
 * after a real user gesture, so there are no autoplay warnings.
 *
 * Buses: sfx -> compressor -> master ; ambience -> master.
 * Settings (master / sfx / ambience / mute) persist in localStorage key
 * "deadHorizonAudioV1", separate from the gameplay save so save data is untouched.
 */
(() => {
  'use strict';
  const KEY = 'deadHorizonAudioV1';
  const S = { master: .8, sfx: .85, amb: .5, mute: false };
  try { Object.assign(S, JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (e) {}
  for (const k of ['master', 'sfx', 'amb']) { S[k] = Math.min(1, Math.max(0, Number(S[k]))); if (!Number.isFinite(S[k])) S[k] = .7; }
  S.mute = !!S.mute;

  let ctx = null, master, sfxBus, ambBus, comp, E = null, unlocked = false, ambT = 6;
  const log = [], lastPlay = Object.create(null), ends = [];
  const A = { settings: S, debug: false, log, stats: { played: 0, dropped: 0 } };
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} };

  function noiseBuffer(c) {
    const n = c.sampleRate, b = c.createBuffer(1, n, c.sampleRate), d = b.getChannelData(0);
    let s = 12345; for (let i = 0; i < n; i++) { s = (s * 1664525 + 1013904223) >>> 0; d[i] = s / 2147483648 - 1; }
    return b;
  }

  /* ---------- synthesis helpers ---------- */
  function osc(E, t, type, f0, f1, dur, vol, o = {}) {
    const c = E.c, n = c.createOscillator(), g = c.createGain();
    n.type = type; n.frequency.setValueAtTime(f0, t);
    if (f1 !== f0) n.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
    const att = o.att || .003;
    g.gain.setValueAtTime(.0001, t); g.gain.linearRampToValueAtTime(vol, t + att);
    g.gain.exponentialRampToValueAtTime(.0001, t + dur);
    let tail = n;
    if (o.lp) { const f = c.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = o.lp; n.connect(f); tail = f; }
    if (o.vib) { const l = c.createOscillator(), lg = c.createGain(); l.frequency.value = o.vib; lg.gain.value = f0 * .06; l.connect(lg); lg.connect(n.frequency); l.start(t); l.stop(t + dur + .03); }
    tail.connect(g); g.connect(E.out); n.start(t); n.stop(t + dur + .03);
  }
  function nz(E, t, dur, vol, type, f0, f1, q = 1, att = .002) {
    const c = E.c, s = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
    s.buffer = E.nb; s.loop = true; f.type = type; f.Q.value = q;
    f.frequency.setValueAtTime(f0, t); if (f1 !== f0) f.frequency.exponentialRampToValueAtTime(Math.max(30, f1), t + dur);
    g.gain.setValueAtTime(.0001, t); g.gain.linearRampToValueAtTime(vol, t + att); g.gain.exponentialRampToValueAtTime(.0001, t + dur);
    s.connect(f); f.connect(g); g.connect(E.out); s.start(t, Math.random() * .8); s.stop(t + dur + .03);
  }

  /* ---------- sound definitions: f(E, t, vol, rate, opts) -> duration ---------- */
  const DEF = {
    shot_pistol: { vol: 3.454, min: .03, f(E, t, v, r) { nz(E, t, .09, .55 * v, 'bandpass', 1900 * r, 600, 1); osc(E, t, 'square', 230 * r, 70, .08, .22 * v); nz(E, t, .2, .16 * v, 'lowpass', 3500, 300); return .25; } },
    shot_smg: { vol: 2.321, min: .035, f(E, t, v, r) { nz(E, t, .06, .42 * v, 'highpass', 2300 * r, 900, .8); osc(E, t, 'sawtooth', 300 * r, 120, .05, .14 * v); return .12; } },
    shot_rifle: { vol: 4.824, min: .04, f(E, t, v, r) { nz(E, t, .12, .6 * v, 'bandpass', 1500 * r, 400, .9); osc(E, t, 'sawtooth', 170 * r, 60, .12, .28 * v); nz(E, t, .28, .18 * v, 'lowpass', 2500, 200); return .32; } },
    shot_shotgun: { vol: 2.373, min: .05, f(E, t, v, r) { nz(E, t, .3, .8 * v, 'lowpass', 3000 * r, 200, .7); osc(E, t, 'sine', 115 * r, 35, .24, .5 * v); nz(E, t, .06, .35 * v, 'bandpass', 900, 500); return .36; } },
    shot_sniper: { vol: 2.735, min: .1, f(E, t, v, r) { nz(E, t, .38, .7 * v, 'bandpass', 2500 * r, 300, .8); osc(E, t, 'sine', 95 * r, 30, .42, .55 * v); nz(E, t + .05, .95, .22 * v, 'lowpass', 1500, 100); return 1; } },
    shot_launcher: { vol: 4.001, min: .1, f(E, t, v, r) { osc(E, t, 'sawtooth', 210 * r, 50, .32, .38 * v, { lp: 900 }); nz(E, t, .38, .5 * v, 'lowpass', 1400, 150); return .45; } },
    shot_flame: { vol: 4.523, min: .06, f(E, t, v, r) { nz(E, t, .13, .35 * v, 'bandpass', 700 * r, 1300, .6, .01); return .18; } },
    shot_crossbow: { vol: 2.184, min: .1, f(E, t, v, r) { osc(E, t, 'triangle', 620 * r, 170, .14, .3 * v, { vib: 38 }); nz(E, t, .05, .3 * v, 'highpass', 3000, 2000); return .2; } },
    melee_swing: { vol: 3.154, min: .08, f(E, t, v, r) { nz(E, t, .15, .32 * v, 'bandpass', 900 * r, 2300, 1.2, .03); return .2; } },
    melee_hit: { vol: 2.299, min: .04, f(E, t, v, r) { nz(E, t, .1, .5 * v, 'lowpass', 2500, 300); osc(E, t, 'sine', 130 * r, 60, .1, .4 * v); return .15; } },
    mag_out: { vol: 4.335, min: .08, f(E, t, v, r) { nz(E, t, .04, .36 * v, 'bandpass', 2200 * r, 1800, 2); osc(E, t, 'square', 720 * r, 500, .035, .1 * v); return .08; } },
    mag_in: { vol: 2.878, min: .08, f(E, t, v, r) { nz(E, t, .05, .4 * v, 'bandpass', 1200 * r, 900, 1.5); osc(E, t, 'sine', 185 * r, 120, .07, .3 * v); return .1; } },
    rack: { vol: 0.899, min: .08, f(E, t, v, r) { nz(E, t, .03, .36 * v, 'highpass', 3000 * r, 2500); nz(E, t + .07, .035, .32 * v, 'highpass', 2600 * r, 2200); return .15; } },
    shell_in: { vol: 3.199, min: .06, f(E, t, v, r) { osc(E, t, 'triangle', 900 * r, 700, .04, .2 * v); nz(E, t, .03, .25 * v, 'bandpass', 3500, 3000, 2); return .08; } },
    pump: { vol: 1.294, min: .1, f(E, t, v, r) { nz(E, t, .06, .4 * v, 'bandpass', 1600 * r, 900); nz(E, t + .1, .07, .4 * v, 'bandpass', 1300 * r, 1900); osc(E, t + .1, 'sine', 140, 90, .07, .2 * v); return .2; } },
    empty: { vol: 1.648, min: .1, f(E, t, v, r) { nz(E, t, .025, .3 * v, 'highpass', 4000 * r, 3500); osc(E, t, 'square', 1500 * r, 1300, .02, .08 * v); return .06; } },
    switch: { vol: 4.702, min: .05, f(E, t, v, r) { nz(E, t, .035, .25 * v, 'bandpass', 2800 * r, 2400, 2); osc(E, t, 'square', 400 * r, 300, .04, .07 * v); return .08; } },
    step_dirt: { vol: 8.901, min: .09, pri: 2, f(E, t, v, r) { nz(E, t, .09, .24 * v, 'lowpass', 900 * r, 300); return .12; } },
    step_grass: { vol: 3.663, min: .09, pri: 2, f(E, t, v, r) { nz(E, t, .11, .13 * v, 'bandpass', 2600 * r, 1500, .7, .01); nz(E, t, .06, .12 * v, 'lowpass', 500, 250); return .14; } },
    step_concrete: { vol: 3.379, min: .09, pri: 2, f(E, t, v, r) { nz(E, t, .05, .24 * v, 'bandpass', 1800 * r, 900); osc(E, t, 'sine', 125 * r, 80, .05, .14 * v); return .08; } },
    step_metal: { vol: 3.740, min: .09, pri: 2, f(E, t, v, r) { osc(E, t, 'triangle', 480 * r, 400, .1, .1 * v); nz(E, t, .04, .2 * v, 'bandpass', 2600, 2000); return .13; } },
    jump: { vol: 6.373, min: .1, f(E, t, v, r) { nz(E, t, .12, .14 * v, 'bandpass', 600 * r, 1200, 1, .02); osc(E, t, 'sine', 150 * r, 300, .1, .1 * v); return .15; } },
    land: { vol: 2.717, min: .1, f(E, t, v, r) { nz(E, t, .16, .42 * v, 'lowpass', 1000 * r, 150); osc(E, t, 'sine', 90 * r, 45, .16, .36 * v); return .2; } },
    hurt: { vol: 4.089, min: .12, pri: 1, f(E, t, v, r) { osc(E, t, 'sawtooth', 230 * r, 90, .22, .32 * v, { lp: 1200 }); nz(E, t, .18, .3 * v, 'lowpass', 1800, 300); return .25; } },
    heal: { vol: 1.518, min: .15, f(E, t, v, r) { [520, 660, 880].forEach((f, i) => osc(E, t + i * .07, 'sine', f * r, f * r, .16, .16 * v, { att: .01 })); return .4; } },
    level_up: { vol: 1.6, min: .5, pri: 1, f(E, t, v, r) { [523, 659, 784, 1047].forEach((f, i) => osc(E, t + i * .08, 'triangle', f * r, f * r, .22, .17 * v, { att: .01 })); osc(E, t + .32, 'sine', 1568 * r, 1568 * r, .4, .1 * v, { att: .02 }); return .8; } },
    perk: { vol: 2.2, min: .2, f(E, t, v, r) { osc(E, t, 'square', 392 * r, 392 * r, .07, .08 * v); osc(E, t + .07, 'square', 587 * r, 587 * r, .07, .08 * v); osc(E, t + .14, 'sine', 784 * r, 784 * r, .2, .14 * v, { att: .01 }); return .4; } },
    pickup: { vol: 4.763, min: .04, f(E, t, v, r) { osc(E, t, 'sine', 800 * r, 1250, .09, .16 * v); return .12; } },
    coin: { vol: 3.462, min: .06, f(E, t, v, r) { osc(E, t, 'square', 1320 * r, 1320, .05, .07 * v); osc(E, t + .05, 'square', 1760 * r, 1760, .09, .07 * v); return .16; } },
    chop: { vol: 3.533, min: .1, f(E, t, v, r) { nz(E, t, .1, .5 * v, 'lowpass', 1200 * r, 200); osc(E, t, 'sine', 140 * r, 70, .1, .34 * v); return .14; } },
    mine: { vol: 1.740, min: .1, f(E, t, v, r) { osc(E, t, 'triangle', 1800 * r, 1500, .08, .2 * v); nz(E, t, .05, .35 * v, 'highpass', 3000, 2500); return .12; } },
    ui_hover: { vol: 5.026, min: .05, pri: 2, f(E, t, v) { osc(E, t, 'square', 900, 900, .025, .05 * v); return .05; } },
    ui_click: { vol: 7.183, min: .03, f(E, t, v) { osc(E, t, 'square', 620, 420, .05, .09 * v); return .08; } },
    ui_ok: { vol: 1.877, min: .05, f(E, t, v) { osc(E, t, 'sine', 660, 660, .08, .14 * v); osc(E, t + .07, 'sine', 990, 990, .12, .14 * v); return .22; } },
    ui_fail: { vol: 6.002, min: .08, f(E, t, v) { osc(E, t, 'sawtooth', 210, 150, .13, .12 * v, { lp: 900 }); return .16; } },
    ui_open: { vol: 4.803, min: .08, f(E, t, v) { nz(E, t, .07, .2 * v, 'bandpass', 1500, 2500, 1.5); osc(E, t, 'sine', 500, 720, .08, .1 * v); return .12; } },
    ui_close: { vol: 4.050, min: .08, f(E, t, v) { nz(E, t, .07, .2 * v, 'bandpass', 2500, 1500, 1.5); osc(E, t, 'sine', 720, 480, .08, .1 * v); return .12; } },
    craft: { vol: 0.982, min: .1, f(E, t, v) { nz(E, t, .04, .3 * v, 'highpass', 2500, 2000); nz(E, t + .09, .04, .3 * v, 'highpass', 2200, 1800); osc(E, t + .2, 'sine', 660, 660, .1, .13 * v); osc(E, t + .27, 'sine', 990, 990, .16, .13 * v); return .5; } },
    z_groan: { vol: 1.531, min: .25, pri: 2, f(E, t, v, r) { osc(E, t, 'sawtooth', 95 * r, 62 * r, .7, .2 * v, { lp: 420, vib: 5, att: .08 }); nz(E, t, .6, .06 * v, 'bandpass', 280 * r, 200, 2, .1); return .8; } },
    z_rasp: { vol: 2.308, min: .25, pri: 2, f(E, t, v, r) { nz(E, t, .45, .22 * v, 'bandpass', 1200 * r, 700, 1.5, .06); osc(E, t, 'sawtooth', 175 * r, 120 * r, .4, .07 * v, { lp: 700, att: .06 }); return .5; } },
    z_attack: { vol: 4.502, min: .1, f(E, t, v, r) { osc(E, t, 'sawtooth', 160 * r, 80, .2, .25 * v, { lp: 800 }); nz(E, t, .12, .2 * v, 'bandpass', 800, 500); return .25; } },
    z_hit: { vol: 2.077, min: .03, pri: 2, f(E, t, v, r) { nz(E, t, .08, .35 * v, 'lowpass', 1400 * r, 300); osc(E, t, 'sine', 105 * r, 60, .08, .3 * v); return .12; } },
    z_death: { vol: 2.859, min: .05, pri: 2, f(E, t, v, r) { osc(E, t, 'sawtooth', 115 * r, 36, .6, .28 * v, { lp: 500 }); nz(E, t, .4, .22 * v, 'lowpass', 1200, 200); return .65; } },
    screech: { vol: 2.628, min: .5, f(E, t, v, r) { osc(E, t, 'sawtooth', 700 * r, 1500, .55, .17 * v, { lp: 3000, vib: 14, att: .05 }); return .6; } },
    boss_roar: { vol: 1.269, min: .8, pri: 1, f(E, t, v, r) { osc(E, t, 'sawtooth', 72 * r, 34, 1.15, .42 * v, { lp: 320, vib: 7, att: .1 }); nz(E, t, 1, .3 * v, 'lowpass', 650, 120, .7, .1); return 1.2; } },
    explosion: { vol: 1.826, min: .06, pri: 1, f(E, t, v, r) { nz(E, t, .95, .9 * v, 'lowpass', 2500 * r, 60, .7); osc(E, t, 'sine', 82 * r, 25, .75, .7 * v); return 1; } },
    spit: { vol: 4.100, min: .15, f(E, t, v, r) { nz(E, t, .16, .3 * v, 'bandpass', 1800 * r, 500, 1.2); osc(E, t, 'sine', 700 * r, 300, .12, .14 * v); return .2; } },
    armor_hit: { vol: 1.858, min: .05, f(E, t, v, r) { osc(E, t, 'triangle', 2200 * r, 1800, .09, .25 * v); nz(E, t, .04, .3 * v, 'highpass', 3500, 3000); return .12; } },
    wave: { vol: 1.191, min: .5, f(E, t, v, r) { [220, 330].forEach(f => osc(E, t, 'sawtooth', f * r, f * r * .98, .65, .13 * v, { lp: 1100, att: .08 })); return .7; } },
    amb_creak: { vol: 1.066, min: 1, bus: 'amb', f(E, t, v, r) { osc(E, t, 'sawtooth', 95 * r, 70 * r, 1.6, .07 * v, { lp: 380, vib: 3, att: .4 }); return 1.7; } },
    amb_gust: { vol: 1.218, min: 1, bus: 'amb', f(E, t, v, r) { nz(E, t, 3, .16 * v, 'bandpass', 350 * r, 900, .6, 1); return 3.1; } },
    amb_far: { vol: 1.272, min: 1, bus: 'amb', f(E, t, v, r) { osc(E, t, 'sine', 62 * r, 38, 1.4, .13 * v, { att: .05 }); nz(E, t, 1.2, .08 * v, 'lowpass', 400, 120, .7, .05); return 1.5; } }
  };

  /* ---------- engine ---------- */
  function build() {
    const C = window.AudioContext || window.webkitAudioContext; if (!C) return false;
    ctx = new C();
    master = ctx.createGain(); comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -14; comp.knee.value = 18; comp.ratio.value = 5; comp.attack.value = .003; comp.release.value = .18;
    sfxBus = ctx.createGain(); ambBus = ctx.createGain();
    sfxBus.connect(comp); comp.connect(master); ambBus.connect(master); master.connect(ctx.destination);
    E = { c: ctx, out: sfxBus, nb: noiseBuffer(ctx) };
    applyVol(true); startBed(); return true;
  }
  function applyVol(instant) {
    if (!ctx) return; const t = ctx.currentTime, k = instant ? .001 : .02;
    master.gain.setTargetAtTime(S.mute ? 0 : S.master, t, k);
    sfxBus.gain.setTargetAtTime(S.sfx, t, k); ambBus.gain.setTargetAtTime(S.amb, t, k);
  }
  function startBed() { // continuous wind + low drone on the ambience bus
    const c = ctx, s = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
    s.buffer = E.nb; s.loop = true; f.type = 'bandpass'; f.frequency.value = 420; f.Q.value = .6; g.gain.value = .1;
    const l = c.createOscillator(), lg = c.createGain(); l.frequency.value = .13; lg.gain.value = .06; l.connect(lg); lg.connect(g.gain);
    const l2 = c.createOscillator(), l2g = c.createGain(); l2.frequency.value = .07; l2g.gain.value = 220; l2.connect(l2g); l2g.connect(f.frequency);
    s.connect(f); f.connect(g); g.connect(ambBus);
    const d = c.createOscillator(), dg = c.createGain(); d.frequency.value = 48; dg.gain.value = .045; d.connect(dg); dg.connect(ambBus);
    [s, l, l2, d].forEach(n => n.start());
  }
  function unlock() {
    unlocked = true;
    if (!ctx && !build()) return false;
    if (ctx.state === 'suspended') ctx.resume().catch(() => {});
    return true;
  }
  function play(name, o) {
    o = o || {}; const d = DEF[name]; if (!d) return false;
    const now = performance.now();
    if (d.min && now - (lastPlay[name] || 0) < d.min * 1000) { A.stats.dropped++; return false; }
    lastPlay[name] = now;
    if (A.debug) { log.push({ n: name, t: now | 0, dx: o.dx }); if (log.length > 400) log.shift(); }
    if (!unlocked || !ctx || S.mute || S.master < .001) return true;
    if (ctx.state === 'suspended') ctx.resume().catch(() => {});
    let vol = (o.vol == null ? 1 : o.vol) * d.vol, pan = 0;
    if (o.dx != null) { vol *= 1 / (1 + Math.abs(o.dx) / 380); pan = clamp(o.dx / 520, -1, 1) * .85; if (vol < .02) return true; }
    const t = ctx.currentTime;
    while (ends.length && ends[0] <= t) ends.shift();
    if (ends.length >= 34 && d.pri !== 1) { A.stats.dropped++; return false; }
    let out = d.bus === 'amb' ? ambBus : sfxBus;
    if (pan && ctx.createStereoPanner) { const p = ctx.createStereoPanner(); p.pan.value = pan; p.connect(out); out = p; }
    const r = (o.rate || 1) * (1 + (Math.random() - .5) * (d.var == null ? .07 : d.var));
    const dur = d.f({ c: ctx, out, nb: E.nb }, t + (o.delay || 0) + .002, vol, r, o) || .3;
    ends.push(t + (o.delay || 0) + dur + .05); ends.sort((a, b) => a - b);
    A.stats.played++; return true;
  }
  /* Ambient one-shots (creaks, gusts, distant thuds) on a randomized timer. Driven by the game loop. */
  function tick(dt) {
    if (!ctx) return; ambT -= dt;
    if (ambT <= 0) { ambT = 9 + Math.random() * 12; const n = ['amb_creak', 'amb_gust', 'amb_far'][(Math.random() * 3) | 0]; play(n, { dx: (Math.random() - .5) * 1600 }); }
  }
  /* Offline render used by the automated audio-level test (peak / RMS / silence). */
  async function renderOffline(name) {
    const d = DEF[name]; if (!d) return null;
    const oc = new OfflineAudioContext(1, 44100 * 3, 44100), g = oc.createGain(); g.connect(oc.destination);
    const c = oc.createDynamicsCompressor(); c.threshold.value = -14; c.knee.value = 18; c.ratio.value = 5; c.connect(g);
    const dur = d.f({ c: oc, out: c, nb: noiseBuffer(oc) }, .01, d.vol, 1, {});
    const buf = await oc.startRendering(), ch = buf.getChannelData(0);
    let peak = 0, sum = 0, nonSilent = 0; for (let i = 0; i < ch.length; i++) { const a = Math.abs(ch[i]); if (a > peak) peak = a; sum += a * a; if (a > .002) nonSilent++; }
    return { name, peak, rms: Math.sqrt(sum / ch.length), activeSeconds: nonSilent / 44100, declaredDur: dur };
  }
  Object.assign(A, {
    play, tick, unlock, renderOffline, names: () => Object.keys(DEF),
    ctxState: () => (ctx ? ctx.state : 'none'),
    gains: () => (ctx ? { master: master.gain.value, sfx: sfxBus.gain.value, amb: ambBus.gain.value } : null),
    voices: () => (ctx ? ends.filter(e => e > ctx.currentTime).length : 0),
    set(k, v) { if (!(k in S)) return; S[k] = k === 'mute' ? !!v : clamp(Number(v) || 0, 0, 1); applyVol(); save(); },
    toggleMute() { S.mute = !S.mute; applyVol(); save(); return S.mute; }
  });
  /* First real user gesture unlocks audio (autoplay policy). Listeners remove themselves. */
  const once = () => { unlock(); if (ctx) { removeEventListener('pointerdown', once, true); removeEventListener('keydown', once, true); } };
  addEventListener('pointerdown', once, true); addEventListener('keydown', once, true);
  window.DH_AUDIO = A;
})();
