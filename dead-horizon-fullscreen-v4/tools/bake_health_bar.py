#!/usr/bin/env python3
"""Splits the supplied health-bar art (tools/ui_sources/health_bar.png: frame + biohazard medallion, ~60% red fill, rest cracked 'empty')
into three layers for a live bar (all 1:1 pixels):
  assets/ui/health_frame.png  228x51  frame + medallion with the interior window cut out (drawn LAST, hides the rounded ends)
  assets/ui/health_empty.png  178x26  cracked dark plate extended over the full window (drawn first)
  assets/ui/health_fill.png   178x26  blood-red fill extended over the full window (drawn clipped to current HP)
Interior window = x 42..219, y 12..37 (cropped-frame coords), rounded on the right. game.html (UX.drawHealth) uses origin (42,12), size 178x26.
Red / empty textures are extended by mirrored tiling of clean columns. Run from the project root."""
from PIL import Image
import numpy as np
SRC, OUT = 'tools/ui_sources/health_bar.png', 'assets/ui/'
IX, IY, IW, IH = 42, 12, 178, 26
XL = {12:38,13:38,14:39,15:39,16:40,17:40,**{y:41 for y in range(18,31)},31:40,32:40,33:40,34:39,35:39,36:38,37:38}                 # outline column on the left
XR = {12:210,13:213,14:214,15:215,16:216,17:217,18:217,19:218,**{y:219 for y in range(20,29)},29:218,30:218,31:217,32:217,33:216,34:215,35:214,36:213,37:210}  # last interior column

def pingpong(i, n):                      # 0,1,..n-1,n-2,..1,0,1..
    m = 2 * (n - 1); j = i % m; return j if j < n else m - j

im = Image.open(SRC).convert('RGBA'); im = im.crop(im.getbbox()); a = np.array(im)
def heal_holes(arr, y0, y1, x0, x1):
    """The art has transparent pin-holes inside the window; fill them from opaque neighbours so they don't turn black."""
    for _ in range(4):
        holes = [(y, x) for y in range(y0, y1) for x in range(x0, x1) if arr[y, x, 3] == 0]
        if not holes: break
        for y, x in holes:
            nb = [arr[yy, xx, :3] for yy in range(y-1, y+2) for xx in range(x-1, x+2) if 0 <= yy < arr.shape[0] and 0 <= xx < arr.shape[1] and arr[yy, xx, 3] > 0]
            if nb: arr[y, x, :3] = np.mean(nb, axis=0).astype(np.uint8); arr[y, x, 3] = 255
heal_holes(a, IY, IY + IH, IX, IX + IW)          # window area only (the frame outside keeps its transparency)
# frame with the interior window removed
frame = a.copy()
for y in range(IY, IY + IH): frame[y, XL[y] + 1: XR[y] + 1, 3] = 0
Image.fromarray(frame).save(OUT + 'health_frame.png')
# red fill: clean red columns 44..150 mirrored across the full window width
base = a[IY:IY + IH, 44:151, :3]; n = base.shape[1]
fill = np.stack([base[:, pingpong(i, n)] for i in range(IW)], axis=1)
# empty plate: original cracks for x>=167, mirrored extension of them to the left of x=167
emp = np.zeros((IH, IW, 3), np.uint8); src_n = 34
for i in range(IW):
    x = IX + i
    emp[:, i] = a[IY:IY + IH, x, :3] if x >= 167 else a[IY:IY + IH, 167 + pingpong(167 - x, src_n), :3]
for name, arr in (('health_fill', fill), ('health_empty', emp)):
    Image.fromarray(np.dstack([arr, np.full((IH, IW), 255, np.uint8)])).save(OUT + name + '.png')
# preview: 62% health
prev = Image.new('RGBA', im.size, (0, 0, 0, 0))
prev.paste(Image.open(OUT + 'health_empty.png'), (IX, IY)); f = Image.open(OUT + 'health_fill.png').crop((0, 0, int(IW * .62), IH)); prev.paste(f, (IX, IY))
prev.alpha_composite(Image.open(OUT + 'health_frame.png')); prev.save('/tmp/health_preview.png'); print('baked', im.size)
