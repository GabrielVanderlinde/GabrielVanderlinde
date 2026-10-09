#!/usr/bin/env python3
"""Generate an animated terminal-style GitHub profile GIF using assets/perfil.png.

Requirements: Python 3.10+ and Pillow (pip install Pillow).
Run from the repository root: python gerar_gif.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
PHOTO = ROOT / "assets" / "perfil.png"
OUTPUT = ROOT / "assets" / "terminal_profile.gif"
WIDTH, HEIGHT = 800, 434
PHOTO_WIDTH = 325
BG = (7, 14, 12)
GREEN = (72, 220, 145)
WHITE = (226, 240, 230)
FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    "C:/Windows/Fonts/consola.ttf",
    "/System/Library/Fonts/Menlo.ttc",
)

def load_font(size: int):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()

def make_background() -> Image.Image:
    if not PHOTO.exists():
        raise SystemExit(
            "Photo not found: assets/perfil.png. Add your own photo there, then rerun."
        )
    photo = Image.open(PHOTO).convert("RGB")
    left = ImageOps.fit(
        photo, (PHOTO_WIDTH, HEIGHT), method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.35),
    )
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    image.paste(left, (0, 0))
    fade = Image.new("RGBA", (100, HEIGHT), (0, 0, 0, 0))
    fade_draw = ImageDraw.Draw(fade)
    for x in range(100):
        fade_draw.line((x, 0, x, HEIGHT), fill=(*BG, int(235 * x / 99)))
    image.paste(fade, (PHOTO_WIDTH - 100, 0), fade)

    draw = ImageDraw.Draw(image)
    x0, y0, x1, y1 = 250, 24, 775, 412
    draw.rounded_rectangle((x0, y0, x1, y1), radius=16, fill=(8, 17, 14),
                           outline=(32, 80, 61), width=2)
    draw.rounded_rectangle((x0 + 1, y0 + 1, x1 - 1, y0 + 47), radius=15,
                           fill=(15, 31, 24))
    draw.rectangle((x0 + 1, y0 + 30, x1 - 1, y0 + 47), fill=(15, 31, 24))
    for index, color in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        xx = x0 + 18 + index * 21
        draw.ellipse((xx, y0 + 17, xx + 11, y0 + 28), fill=color)
    draw.text((x0 + 105, y0 + 13), "gabriel@dev-profile: ~",
              font=load_font(13), fill=(179, 201, 187))
    return image

LINES = [
    ("$ whoami", GREEN),
    ("Gabriel Vanderlinde", WHITE),
    ("$ role", GREEN),
    ("Software Developer", WHITE),
    ("$ location", GREEN),
    ("Blumenau, SC, Brazil", WHITE),
    ("$ stack", GREEN),
    ("Java · Spring Boot · TypeScript", WHITE),
    ("NestJS · SQL · Docker", WHITE),
    ("$ status", GREEN),
    ("Building useful software.", WHITE),
]

def main():
    base = make_background()
    frames = []
    x0, y0 = 250, 24
    for index, (line, color) in enumerate(LINES):
        previous = LINES[:index]
        for count in range(1, len(line) + 1, 2):
            if count == len(line) - 1:
                count = len(line)
            frame = base.copy()
            draw = ImageDraw.Draw(frame)
            y = y0 + 72
            for old_line, old_color in previous:
                draw.text((x0 + 25, y), old_line, font=load_font(13), fill=old_color)
                y += 31
            visible = line[:count]
            draw.text((x0 + 25, y), visible, font=load_font(13), fill=color)
            if count < len(line) and (count // 2) % 2 == 0:
                width = draw.textlength(visible, font=load_font(13))
                draw.rectangle((x0 + 25 + int(width) + 1, y + 3,
                                x0 + 25 + int(width) + 8, y + 18), fill=GREEN)
            frames.append(frame)
            if count == len(line):
                break

    for blink in range(8):
        frame = base.copy()
        draw = ImageDraw.Draw(frame)
        y = y0 + 72
        for line, color in LINES:
            shown = line + (" █" if blink % 2 == 0 and line == LINES[-1][0] else "")
            draw.text((x0 + 25, y), shown, font=load_font(13), fill=color)
            y += 31
        frames.append(frame)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    paletted = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=64)
                for frame in frames]
    paletted[0].save(
        OUTPUT, save_all=True, append_images=paletted[1:], duration=80,
        loop=0, optimize=True, disposal=2,
    )
    print(f"GIF created: {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()
