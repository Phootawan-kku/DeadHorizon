#!/usr/bin/env python3
"""Bake the art for the rust/hazard inventory + crafting panel from assets/ui/_panel_mockup.png (the supplied mock-up).

Outputs (assets/ui/):
  panel_frame.png        border-image: the mock-up's frame, with the right rail + right corners mirrored from the clean left side
                         (the mock-up's own right rail has a scroll bar baked into it). Slice: top 18, right 14, bottom 19, left 14.
  panel_vines_{tl,tr,bl,br}.png   pixel-art foliage that overlaps the frame corners (drawn by this script, transparent background)
  panel_rust.png         tileable rust-brown texture (inventory rows)
  panel_card.png         tileable near-black rusty metal (crafting cards)
  panel_steel.png        tileable brushed steel (Profile/Armory plate, scroll bar thumb)
Run from the game folder:  python3 tools/bake_panel_ui.py
"""
import os
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
UI = os.path.join(ROOT, 'assets/ui')
src = Image.open(os.path.join(UI, '_panel_mockup.png')).convert('RGB')
W, H = src.size                       # 377 x 1024
T, R, B, L = 18, 14, 19, 14           # frame thickness (px) top/right/bottom/left

# ---------------------------------------------------------------- frame (border-image source)
frame = Image.new('RGBA', (W, H), (0, 0, 0, 0))
def paste(img, box, pos): frame.paste(img.crop(box), pos)
# left rail + left corners straight from the mock-up
paste(src, (0, 0, L, H), (0, 0))                                        # whole left column incl. corners
# right rail + right corners = mirrored left column
frame.paste(src.crop((0, 0, R, H)).transpose(Image.FLIP_LEFT_RIGHT), (W - R, 0))
# top and bottom bars between the corners
paste(src, (L, 0, W - R, T), (L, 0))
paste(src, (L, H - B, W - R, H), (L, H - B))
frame.save(os.path.join(UI, 'panel_frame.png'), optimize=True)

# ---------------------------------------------------------------- vine overlays (pixel-art, drawn here; colours sampled from the mock-up's foliage)
import math
from PIL import ImageDraw
STEM = (26, 33, 19, 255); LEAF = [(33, 46, 25, 255), (45, 60, 34, 255), (58, 78, 42, 255)]; HI = (88, 112, 62, 255)
def vine(name, w, h, corner, seed, branches):
    """corner: 'tl'|'tr'|'bl'|'br' = where the vine is rooted; branches: list of (start angle in degrees, steps)"""
    rng = np.random.RandomState(seed)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rx = w - 2 if corner[1] == 'r' else 1; ry = h - 2 if corner[0] == 'b' else 1
    def leaf(x, y, ang):
        L = rng.randint(4, 7); wd = 2.2
        c, sn = math.cos(ang), math.sin(ang)
        pts = [(x, y), (x + c * L * .5 - sn * wd, y + sn * L * .5 + c * wd), (x + c * L, y + sn * L), (x + c * L * .5 + sn * wd, y + sn * L * .5 - c * wd)]
        d.polygon(pts, fill=LEAF[rng.randint(3)])
        d.point((int(x + c * L * .6), int(y + sn * L * .6)), fill=HI if rng.rand() < .5 else LEAF[2])
    def branch(x, y, ang, steps, depth):
        for i in range(steps):
            ang += rng.uniform(-.28, .28); x += math.cos(ang) * 1.7; y += math.sin(ang) * 1.7
            if not (0 <= x < w and 0 <= y < h): return
            d.point((int(x), int(y)), fill=STEM)
            if i % 3 == 0 and rng.rand() < .6: leaf(x, y, ang + rng.choice([-1.15, 1.15]) + rng.uniform(-.3, .3))
            if depth < 2 and i > 4 and rng.rand() < .07: branch(x, y, ang + rng.choice([-.8, .8]), steps // 2, depth + 1)
    for deg, steps in branches: branch(rx, ry, math.radians(deg), steps, 0)
    img.save(os.path.join(UI, f'panel_vines_{name}.png'), optimize=True)
vine('br', 110, 150, 'br', 3, [(-95, 78), (-120, 55), (180, 52), (-70, 40)])     # grows up the right edge and along the bottom
vine('bl', 100, 60, 'bl', 5, [(-5, 50), (-40, 36)])
vine('tr', 50, 110, 'tr', 11, [(95, 58), (120, 36)])
vine('tl', 56, 40, 'tl', 8, [(10, 34), (50, 22)])

# ---------------------------------------------------------------- tileable textures (FFT noise is periodic by construction)
rng = np.random.RandomState(7)
def fnoise(w, h, beta=1.6, sx=1.0, sy=1.0):
    n = rng.randn(h, w)
    fx = np.fft.fftfreq(w)[None, :] * sx; fy = np.fft.fftfreq(h)[:, None] * sy
    f = np.sqrt(fx ** 2 + fy ** 2); f[0, 0] = 1
    n = np.real(np.fft.ifft2(np.fft.fft2(n) / f ** beta)); n -= n.mean(); n /= (n.std() + 1e-9)
    return n
def tex(w, h, base, amp, streak=0.0, spots=0.0, grain=2.0, rustc=(104, 58, 34), scratch=0):
    n1 = fnoise(w, h, 1.5); n2 = fnoise(w, h, 1.0)
    v = n1 * .6 + n2 * .25
    st = fnoise(w, h, 1.3, sx=.35, sy=3.0) * streak           # vertical drips: stretched along y
    img = np.zeros((h, w, 3)) + np.array(base, float)
    img += (v[..., None] * amp) + st[..., None] * (amp * .8)
    img += rng.randn(h, w, 1) * grain
    if spots:
        m = np.clip((fnoise(w, h, 1.2) - 1.6) * 1.5, 0, 1)[..., None] * spots
        img = img * (1 - m) + np.array(rustc, float) * m
    for _ in range(scratch):                                   # thin horizontal scratches
        y = rng.randint(h); x0 = rng.randint(w); ln = rng.randint(10, w // 2)
        for x in range(x0, x0 + ln): img[y, x % w] += rng.uniform(8, 16)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
tex(128, 64, (50, 38, 35), 5.5, streak=2.5, spots=.55, grain=1.6).save(os.path.join(UI, 'panel_rust.png'), optimize=True)
tex(128, 128, (35, 31, 30), 3.0, streak=1.2, spots=.25, grain=1.4, rustc=(62, 36, 28)).save(os.path.join(UI, 'panel_card.png'), optimize=True)
tex(128, 64, (80, 76, 72), 4.5, streak=1.5, spots=.35, grain=2.0, rustc=(96, 62, 44), scratch=26).save(os.path.join(UI, 'panel_steel.png'), optimize=True)
print('baked', sorted(f for f in os.listdir(UI) if f.startswith('panel_')))
