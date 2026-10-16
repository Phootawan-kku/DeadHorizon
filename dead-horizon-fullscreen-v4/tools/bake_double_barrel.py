#!/usr/bin/env python3
"""Bakes the Double Barrel art (tools/ui_sources/double_barrel.png, 1678x937 soft-alpha cut-out) into game sprites:
  assets/weapons/double.png       58x20  in-hand sprite (weaponDims('double') is already 58x20 -> drawn 1:1)
  assets/weapons/double_icon.png  64x24  HUD / armory icon (same sprite centred)
Steps: crop to the gun, premultiplied-alpha downscale, mild sharpen + contrast, binarise alpha (crisp pixel silhouette), add a 1px dark outline
(the original's thick outline disappears at this size). Muzzle = right-most opaque column of double.png (measured by game.html). Run from project root."""
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
SRC = 'tools/ui_sources/double_barrel.png'; OUT = 'assets/weapons/'
GUN_W = 54                      # gun width incl. outline in the 58x20 canvas -> 52 px of art + 2 px outline
im = Image.open(SRC).convert('RGBA'); a = np.array(im); al = a[:, :, 3]
ys, xs = np.where(al > 128); im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
w, h = im.size; tw = GUN_W - 2; th = max(1, round(h * tw / w))
arr = np.array(im).astype(np.float32); alpha = arr[:, :, 3:4] / 255.0
pm = Image.fromarray(np.dstack([arr[:, :, :3] * alpha, alpha * 255]).clip(0, 255).astype(np.uint8), 'RGBA')   # premultiplied
chan = [np.array(Image.fromarray(np.array(pm)[:, :, i]).resize((tw, th), Image.LANCZOS)).astype(np.float32) for i in range(4)]
A = chan[3] / 255.0; rgb = np.dstack([chan[i] / np.maximum(A, 1e-3) for i in range(3)]).clip(0, 255)
small = Image.fromarray(rgb.astype(np.uint8), 'RGB')
small = ImageEnhance.Contrast(small).enhance(1.12); small = ImageEnhance.Color(small).enhance(1.08)
small = small.filter(ImageFilter.UnsharpMask(radius=0.7, percent=90, threshold=2))
mask = (A > 0.5)
sp = np.dstack([np.array(small), (mask * 255).astype(np.uint8)])
# 1px dark outline (4-neighbour dilation of the silhouette)
pad = np.pad(mask, 1); dil = pad.copy()
for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): dil |= np.roll(np.roll(pad, dy, 0), dx, 1)
out = np.zeros((th + 2, tw + 2, 4), np.uint8); out[dil & ~pad, :] = (14, 17, 24, 255); inner = np.pad(sp, ((1, 1), (1, 1), (0, 0)))
out[pad] = inner[pad]
gun = Image.fromarray(out, 'RGBA')
canvas = Image.new('RGBA', (58, 20), (0, 0, 0, 0)); canvas.paste(gun, (2, (20 - gun.height) // 2), gun); canvas.save(OUT + 'double.png')
icon = Image.new('RGBA', (64, 24), (0, 0, 0, 0)); icon.paste(canvas, (3, 2), canvas); icon.save(OUT + 'double_icon.png')
print('gun', gun.size, 'canvas', canvas.size, 'bbox', canvas.getbbox())
