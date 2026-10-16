#!/usr/bin/env python3
"""Bakes the scene backdrop: tools/ui_sources/dead_horizon_bg.png (1376x768) -> assets/environment/dead_horizon_bg.png (960x540).
The game's logical canvas is 960x540, so the image is centre-cropped to exactly 16:9 and resampled ONCE here (no runtime scaling).
game.html tiles it horizontally with alternate tiles mirrored (seamless) and scrolls it at a slow parallax speed. Run from the project root."""
from PIL import Image
im = Image.open('tools/ui_sources/dead_horizon_bg.png').convert('RGB')
w, h = im.size; cw = round(h * 16 / 9); x0 = (w - cw) // 2
im = im.crop((x0, 0, x0 + cw, h)).resize((960, 540), Image.LANCZOS)
im.save('assets/environment/dead_horizon_bg.png', optimize=True); print('baked', im.size)
