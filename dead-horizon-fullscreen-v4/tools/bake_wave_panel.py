#!/usr/bin/env python3
"""Bakes the wave / hostiles HUD panel (assets/ui/wave_panel.png) from tools/ui_sources/wave_frame.png.

The source is a full 213x135 frame with a busy art scene inside. For a short HUD banner we keep the frame at native pixel size
(no stretching) and CUT a horizontal band out of the middle (CUT_A..CUT_B, in cropped-frame rows), then replace the busy interior
with a darkened, tiled piece of the calm metal plate so text stays readable. A 3px inner lip of the original is kept.
Output also prints the interior rectangle (INNER) that game.html uses for layout. Run from the project root.
"""
import sys
from PIL import Image
import numpy as np

SRC = 'tools/ui_sources/wave_frame.png'
OUT = 'assets/ui/wave_panel.png'
CUT_A, CUT_B = int(sys.argv[1]) if len(sys.argv) > 1 else 52, int(sys.argv[2]) if len(sys.argv) > 2 else 100
IN_X0, IN_X1, IN_Y0, IN_Y1 = 22, 191, 24, 110          # interior window of the original (cropped coords)
LIP = 3
PATCH = (90, 30, 130, 75)                              # calm dark plate with rivets/seam (x0,y0,x1,y1)
DARK = 0.5

im = Image.open(SRC).convert('RGBA'); im = im.crop(im.getbbox())          # 213x135
top = im.crop((0, 0, im.width, CUT_A)); bot = im.crop((0, CUT_B, im.width, im.height))
out = Image.new('RGBA', (im.width, top.height + bot.height), (0, 0, 0, 0))
out.paste(top, (0, 0)); out.paste(bot, (0, top.height))
cut = CUT_B - CUT_A
iy1 = IN_Y1 - cut                                                          # interior bottom after the cut
ih, iw = iy1 - IN_Y0, IN_X1 - IN_X0

# calm plate, darkened + slightly desaturated, tiled across the interior
patch = np.array(im.crop(PATCH).convert('RGB')).astype(float)
g = patch.mean(axis=2, keepdims=True); patch = (patch * 0.6 + g * 0.4) * DARK
tile = np.tile(patch, (1, iw // patch.shape[1] + 2, 1))[:ih, :iw]
if tile.shape[0] < ih: tile = np.tile(tile, (ih // tile.shape[0] + 1, 1, 1))[:ih]
# depth: darker toward the top edge, faint vignette at the sides
yy = np.linspace(0, 1, ih)[:, None, None]; xx = np.linspace(-1, 1, iw)[None, :, None]
shade = (0.62 + 0.38 * np.clip(yy * 3.2, 0, 1)) * (1 - 0.18 * xx ** 2)
tile = np.clip(tile * shade, 0, 255).astype(np.uint8)
a = np.array(out)
y0, x0 = IN_Y0 + LIP, IN_X0 + LIP
a[y0:iy1 - LIP, x0:IN_X1 - LIP, :3] = tile[LIP:ih - LIP, LIP:iw - LIP]
a[y0:iy1 - LIP, x0:IN_X1 - LIP, 3] = 255
Image.fromarray(a).save(OUT)
print('size', out.size, 'INNER x', IN_X0 + LIP, IN_X1 - LIP, 'y', y0, iy1 - LIP)
