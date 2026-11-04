#!/usr/bin/env python3
"""Bake the Magic Wand burst animations from assets/effects/_wand_source/{ice,fire}.png.

Each source is ONE painted burst. This tool animates it procedurally into a 10-frame strip:
  frames 0-3  ERUPT   every column of the picture slides up out of the ground with its own delay (centre first), so the spikes
                      shoot up one after another; the last eruption frame overshoots slightly
  frames 4-5  HOLD    full burst with a bright pulse
  frames 6-9  FADE    dissolves in pixel blocks from the top down while drifting (fire rises like embers, ice sinks and shatters)
Outputs: assets/effects/wand_ice_burst.png, wand_fire_burst.png (10 frames x 300x212), wand_fx.json
Run from the game folder:  python3 tools/bake_wand_fx.py
"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'assets/effects/_wand_source')
OUT = os.path.join(ROOT, 'assets/effects')
FW, FH, N = 300, 212, 10
GROUND = FH - 6
rng = np.random.RandomState(5)

def clean(path):
    """drop the stray specks far away from the burst and tiny dust"""
    a = np.array(Image.open(path).convert('RGBA'))
    m = a[..., 3] > 10
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    sizes = ndi.sum(m, lab, range(1, n + 1))
    big = np.isin(lab, [i + 1 for i in range(n) if sizes[i] > 2000])
    near = ndi.distance_transform_edt(~big) < 70
    keep = m & near
    for i in range(n):                       # tiny dots go even when near
        if sizes[i] < 6: keep[lab == i + 1] = False
    a[~keep] = 0
    ys, xs = np.where(a[..., 3] > 10)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def fit(a):
    h, w = a.shape[:2]
    k = min((FW - 14) / w, (GROUND - 4) / h)
    im = Image.fromarray(a).resize((round(w * k), round(h * k)), Image.LANCZOS)
    canvas = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((FW - im.width) // 2, GROUND - im.height))
    return np.array(canvas), im.width, im.height

def smooth_noise(n, scale):
    return ndi.zoom(rng.rand(n // scale + 2), scale, order=1)[:n]

def erupt(base, t, bw):
    """slide each column up from below the ground; column delay grows away from the centre"""
    H, W = base.shape[:2]
    out = np.zeros_like(base)
    xc = W / 2
    jitter = smooth_noise(W, 14)
    for x in range(W):
        col = base[:, x]
        if col[:, 3].max() == 0: continue
        delay = .42 * abs(x - xc) / (bw / 2) + .18 * jitter[x]
        f = np.clip((t - delay) / .55, 0, 1)
        f = 1 - (1 - f) ** 2.2
        ys = np.where(col[:, 3] > 0)[0]
        extent = GROUND - ys.min() + 6
        s = int(round((1 - f) * extent))
        if s >= H: continue
        shifted = np.zeros_like(col)
        shifted[s:] = col[:H - s] if s else col
        shifted[GROUND + 1:] = 0               # everything below the ground line is hidden
        out[:, x] = shifted
    return out

def scale_about_bottom(a, sx, sy, dy=0):
    im = Image.fromarray(a)
    w, h = FW, FH
    nw, nh = round(w * sx), round(h * sy)
    r = im.resize((nw, nh), Image.LANCZOS)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.alpha_composite(r, ((w - nw) // 2, GROUND - round(GROUND * sy) + dy))
    return np.array(out)

def brighten(a, amt):
    b = a.astype(float); m = b[..., 3] > 0
    b[..., :3][m] = b[..., :3][m] * (1 - amt) + 255 * amt
    return b.astype(np.uint8)

def dissolve(a, thr, up):
    H, W = a.shape[:2]
    blocks = rng.rand(H // 3 + 1, W // 3 + 1)
    field = np.kron(blocks, np.ones((3, 3)))[:H, :W]
    ygrad = np.clip((GROUND - np.arange(H)) / GROUND, 0, 1)[:, None]      # 0 at ground, 1 at the top
    keep = (.62 * field + .38 * (1 - ygrad)) > thr
    out = a.copy(); out[~keep] = 0
    if up:
        sh = np.zeros_like(out); sh[:H - up] = out[up:]; out = sh
    return out

def build(name, rising):
    base, bw, bh = fit(clean(os.path.join(SRC, name + '.png')))
    frames = []
    for i, t in enumerate([.14, .42, .76, 1.15]):
        f = erupt(base, t, bw)
        if i == 3: f = scale_about_bottom(f, 1.05, 1.07)
        frames.append(f)
    frames.append(brighten(scale_about_bottom(base, 1.03, 1.04), .22))
    frames.append(base)
    for thr, up, fade in [(.2, 4 if rising else -2, 1.0), (.38, 10 if rising else -4, .9), (.56, 18 if rising else -5, .7), (.76, 28 if rising else -6, .5)]:
        d = dissolve(base, thr, abs(up) if up > 0 else 0)
        if not rising: d = scale_about_bottom(d, 1.0, 1.0 + up / 400.0)
        d = d.copy(); d[..., 3] = (d[..., 3] * fade).astype(np.uint8)
        frames.append(d)
    sheet = Image.new('RGBA', (FW * N, FH), (0, 0, 0, 0))
    for i, f in enumerate(frames): sheet.alpha_composite(Image.fromarray(f), (i * FW, 0))
    sheet.save(os.path.join(OUT, f'wand_{name}_burst.png'), optimize=True)
    return bw, bh

bwi, bhi = build('ice', rising=False)
bwf, bhf = build('fire', rising=True)
json.dump(dict(note='Magic Wand burst strips, generated by tools/bake_wand_fx.py. 10 frames: 0-3 erupt, 4-5 hold, 6-9 fade. Bottom-centre of each frame is the ground contact.',
               frameW=FW, frameH=FH, frames=N, groundY=GROUND, ice=dict(w=bwi, h=bhi), fire=dict(w=bwf, h=bhf)),
          open(os.path.join(OUT, 'wand_fx.json'), 'w'), indent=1)
print('ok', FW, FH, N, 'ice', bwi, bhi, 'fire', bwf, bhf)
