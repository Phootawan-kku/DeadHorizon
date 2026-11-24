#!/usr/bin/env python3
"""Bakes the loadout-bar panels (game.html -> UX.drawLoadout) from the supplied art sheet tools/ui_sources/hud_sheet.png (1024x434).

The sheet has the checkerboard 'transparency' baked into its pixels, so this script
  1. keys the light-grey checker out of the background (flood by colour, big components only),
  2. crops the consumables box, one weapon slot and the weapon read-out at NATIVE sheet resolution (the game draws them at 0.8x, smoothed),
  3. replaces the slot's dark checker window with a chain-link mesh and erases the baked tab digit (the game draws 1-6 live),
  4. makes a gold 'selected' variant of the slot.
Outputs (assets/ui/): hud_consumables.png 226x151, hud_slot.png / hud_slot_sel.png 93x132, hud_weapon.png 228x134.
Run from the project root:  python3 tools/bake_hotbar_ui.py
"""
import random
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

random.seed(11); np.random.seed(11)
SRC, OUT = 'tools/ui_sources/hud_sheet.png', 'assets/ui/'
a = np.array(Image.open(SRC).convert('RGB')).astype(int)
lum, sat = a.mean(2), a.max(2) - a.min(2)

# --- 1. key the baked light checker ---
cand = (lum >= 108) & (sat < 28)
lab, n = ndi.label(cand)
sizes = ndi.sum(cand, lab, range(1, n + 1))
bg = np.zeros_like(cand)
for i, s in enumerate(sizes, 1):
    if s > 400:
        bg |= lab == i
bg = ndi.binary_closing(bg, iterations=2)
fg = ndi.binary_opening(~bg, iterations=1)
rgba = np.dstack([a.astype(np.uint8), (fg * 255).astype(np.uint8)])


def crop(x0, y0, x1, y1):
    return rgba[y0:y1, x0:x1].copy()


def save(arr, name):
    Image.fromarray(arr, 'RGBA').save(OUT + name)


# --- 2. consumables + weapon read-out ---
save(crop(0, 128, 226, 279), 'hud_consumables.png')
save(crop(796, 145, 1024, 279), 'hud_weapon.png')

# --- 3. slot (slot 2 is the cleanest: its digit is cream, not the orange 'selected' one) ---
SX0, SY0, SX1, SY1 = 323, 145, 416, 277
slot = crop(SX0, SY0, SX1, SY1)                 # 93x132
H, W = slot.shape[:2]
WX0, WY0, WX1, WY1 = 10, 10, 84, 122            # dark checker window (relative)
TX1, TY1 = 28, 35                               # number tab inside the window's top-left corner

# erase digit: flatten the tab interior to its own body colour (sampled from the tab's untouched left/top strip)
ty0, ty1, tx0, tx1 = WY0 + 1, TY1 - 3, WX0 + 1, TX1 - 2
ref = np.concatenate([slot[WY0 + 2:TY1 - 2, WX0 + 1:WX0 + 3, :3].reshape(-1, 3), slot[WY0 + 1:WY0 + 3, WX0 + 1:TX1 - 2, :3].reshape(-1, 3)]).astype(int)
body = np.median(ref, axis=0)
for yy in range(ty0, ty1):
    for xx in range(tx0, tx1):
        slot[yy, xx, :3] = np.clip(body + np.random.randint(-3, 4, 3), 0, 255)


def fill_window(img, selected):
    px = img
    bgc = (30, 25, 12) if selected else (22, 20, 19)
    for y in range(WY0 + 1, WY1 - 1):
        for x in range(WX0 + 1, WX1 - 1):
            if x < TX1 and y < TY1:
                continue                          # keep the tab
            j = random.randint(-3, 3)
            c = [v + j for v in bgc]
            if not selected:
                u, v = x + y, x - y
                if u % 10 == 0 or v % 10 == 0:
                    c = [62, 60, 57]
                elif (u - 1) % 10 == 0 or (v - 1) % 10 == 0:
                    c = [34, 32, 31]
            else:
                c = [86 + j * 2, 70 + j * 2, 22 + j]
            # edge vignette + inner top shadow so icons sit in a recess
            ex = min(x - WX0, WX1 - 1 - x) / ((WX1 - WX0) / 2)
            ey = min(y - WY0, WY1 - 1 - y) / ((WY1 - WY0) / 2)
            k = 0.72 + 0.28 * min(1, min(ex, ey) * 3.2)
            if y < WY0 + 4:
                k *= 0.7 + 0.075 * (y - WY0)
            px[y, x, :3] = np.clip(np.array(c) * k, 0, 255)


normal = slot.copy(); fill_window(normal, False)
sel = slot.copy(); fill_window(sel, True)
# gold-tint the frame + tab of the selected variant (everything outside the window)
mask = np.ones((H, W), bool); mask[WY0:WY1, WX0:WX1] = False
mask |= (np.arange(H)[:, None] < TY1) & (np.arange(W)[None, :] < TX1) & (np.arange(H)[:, None] >= WY0) & (np.arange(W)[None, :] >= WX0)
L = sel[..., :3].astype(float).mean(2, keepdims=True)
gold = np.clip(L * np.array([1.9, 1.45, 0.5]) + np.array([14, 6, 0]), 0, 255)
sel[..., :3] = np.where(mask[..., None], gold, sel[..., :3]).astype(np.uint8)
save(normal, 'hud_slot.png'); save(sel, 'hud_slot_sel.png')
print('baked: consumables 226x151, slot %dx%d (window %d,%d-%d,%d, tab to %d,%d), weapon 228x134' % (W, H, WX0, WY0, WX1, WY1, TX1, TY1))
