#!/usr/bin/env python3
"""Generate the animated terminal profile GIF. Install with: python -m pip install Pillow."""
# Rebuild trigger: keep this generator as the single source of truth for the profile animation.
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ART = ROOT / "assets/portrait.txt"
OUT = ROOT / "assets/terminal_profile.gif"
W, H = 900, 426
BG, BORDER = (22, 25, 31), (57, 64, 77)
PROMPT, LABEL, VALUE = (201, 209, 217), (242, 141, 53), (141, 231, 241)
CURSOR = "_"
STEP, TYPE_MS, BLINKS = 2, 45, 2
CURSOR_MS, LANGUAGE_PAUSE_MS = 100, 1200
RAMP = " .,:;irsXA253hMHGS#9B&@"
FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "C:/Windows/Fonts/consola.ttf",
)
LANGS = [
    ("EN", "English", [
        "Name: ........... Gabriel Vanderlinde", "Role: ........... Software Developer",
        "Location: ....... Blumenau, SC, Brazil", "Focus: .......... Backend APIs & scalable systems",
        "Stack: .......... Java, Spring Boot, TypeScript, NestJS", "Tools: .......... SQL, Docker, Linux, Git",
        "Interests: ...... Quality, observability & architecture", "", "CONTACT",
        "GitHub: ......... GabrielVanderlinde", "LinkedIn: ....... linkedin.com/in/gabrielhenriquevanderlinde"]),
    ("PT", "Português", [
        "Nome: ........... Gabriel Vanderlinde", "Atuação: ........ Desenvolvimento de Software",
        "Localização: .... Blumenau, SC, Brasil", "Foco: ........... APIs e sistemas escaláveis",
        "Stack: .......... Java, Spring Boot, TypeScript, NestJS", "Ferramentas: .... SQL, Docker, Linux, Git",
        "Interesses: ..... Qualidade, observabilidade e arquitetura", "", "CONTATO",
        "GitHub: ......... GabrielVanderlinde", "LinkedIn: ....... linkedin.com/in/gabrielhenriquevanderlinde"]),
    ("ES", "Español", [
        "Nombre: ........ Gabriel Vanderlinde", "Rol: ............ Desarrollador de Software",
        "Ubicación: ..... Blumenau, SC, Brasil", "Enfoque: ....... APIs y sistemas escalables",
        "Stack: ......... Java, Spring Boot, TypeScript, NestJS", "Herramientas: .. SQL, Docker, Linux, Git",
        "Intereses: ..... Calidad, observabilidad y arquitectura", "", "CONTACTO",
        "GitHub: ........ GabrielVanderlinde", "LinkedIn: ...... linkedin.com/in/gabrielhenriquevanderlinde"]),
]

def load_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

def make_palette() -> Image.Image:
    fixed = [BG, BORDER, PROMPT, LABEL, VALUE, (224, 228, 234), (8, 10, 14)]
    colors = [component for color in fixed for component in color]
    for i in range(256 - len(fixed)):
        shade = int(i * 255 / max(1, 255 - len(fixed)))
        colors.extend((shade, shade, shade))
    palette = Image.new("P", (1, 1))
    palette.putpalette((colors + [0] * 768)[:768])
    return palette

PALETTE = make_palette()

def make_base() -> Image.Image:
    if not ART.exists():
        raise SystemExit(f"Portrait character map not found: {ART}")
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    for y in range(H):
        shade = max(0, 5 - int(abs(y - H / 2) / (H / 2) * 5))
        draw.line((0, y, W, y), fill=(BG[0] + shade, BG[1] + shade, BG[2] + shade))
    draw.rounded_rectangle((12, 19, W - 13, H - 19), radius=10, outline=BORDER, width=1)
    mono = load_font(4)
    cell_w = draw.textlength("M", font=mono)
    y = 42
    for row in ART.read_text(encoding="utf-8").splitlines():
        for column, char in enumerate(row):
            if char == " ":
                continue
            level = max(0, RAMP.find(char))
            shade = int(20 + level / (len(RAMP) - 1) * 235)
            draw.text((24 + column * cell_w, y), char, font=mono, fill=(shade, shade, shade))
        y += 5
    return image

def draw_profile_line(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
                      face: ImageFont.ImageFont, count: int | None = None) -> float:
    shown = text if count is None else text[:count]
    draw.text((x, y), "$ ", font=face, fill=PROMPT)
    px = x + draw.textlength("$ ", font=face)
    if ":" in shown:
        label, value = shown.split(":", 1)
        label += ":"
        draw.text((px, y), label, font=face, fill=LABEL)
        px += draw.textlength(label, font=face)
        if value:
            draw.text((px, y), value, font=face, fill=VALUE)
            px += draw.textlength(value, font=face)
    else:
        draw.text((px, y), shown, font=face, fill=VALUE)
        px += draw.textlength(shown, font=face)
    return px

def draw_rows(draw: ImageDraw.ImageDraw, rows: list[tuple[str, str]],
              face: ImageFont.ImageFont, x: int, y: int, line_h: int) -> int:
    for kind, text in rows:
        if kind == "language":
            draw.text((x, y), "$ ", font=face, fill=PROMPT)
            draw.text((x + draw.textlength("$ ", font=face), y), text, font=face, fill=PROMPT)
        else:
            draw_profile_line(draw, x, y, text, face)
        y += line_h
    return y

def add_frame(frames: list[Image.Image], durations: list[int], base: Image.Image,
              rows: list[tuple[str, str]], active: tuple[str, str] | None = None,
              count: int | None = None, cursor: bool = False, duration: int = TYPE_MS) -> None:
    frame = base.copy()
    draw = ImageDraw.Draw(frame)
    face = load_font(10)
    x, y = 285, 98
    y = draw_rows(draw, rows, face, x, y, 19)
    if active is not None:
        kind, text = active
        if kind == "language":
            draw.text((x, y), "$ ", font=face, fill=PROMPT)
            px = x + draw.textlength("$ ", font=face)
            shown = text if count is None else text[:count]
            draw.text((px, y), shown, font=face, fill=PROMPT)
            px += draw.textlength(shown, font=face)
        else:
            px = draw_profile_line(draw, x, y, text, face, count)
        if cursor:
            draw.text((px + 1, y), CURSOR, font=face, fill=PROMPT)
    frames.append(frame.quantize(palette=PALETTE, dither=Image.Dither.NONE))
    durations.append(duration)

def generate() -> None:
    base = make_base()
    frames: list[Image.Image] = []
    durations: list[int] = []
    for code, language, lines in LANGS:
        rows: list[tuple[str, str]] = []
        title = f"[{code}] {language}"
        for _ in range(BLINKS):
            add_frame(frames, durations, base, rows, ("language", title), 0, True, CURSOR_MS)
            add_frame(frames, durations, base, rows, ("language", title), 0, False, CURSOR_MS)
        for index in range(0, len(title) + STEP, STEP):
            add_frame(frames, durations, base, rows, ("language", title), min(index, len(title)),
                      index < len(title))
        rows.append(("language", title))
        for line in lines:
            for _ in range(BLINKS):
                add_frame(frames, durations, base, rows, ("line", line), 0, True, CURSOR_MS)
                add_frame(frames, durations, base, rows, ("line", line), 0, False, CURSOR_MS)
            for index in range(0, len(line) + STEP, STEP):
                add_frame(frames, durations, base, rows, ("line", line), min(index, len(line)),
                          index < len(line))
            rows.append(("line", line))
        frames.append(frames[-1].copy())
        durations.append(LANGUAGE_PAUSE_MS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, optimize=True, disposal=1)
    gifsicle = shutil.which("gifsicle")
    if gifsicle:
        with tempfile.NamedTemporaryFile(suffix=".gif", dir=OUT.parent, delete=False) as temporary:
            temp_path = Path(temporary.name)
        try:
            subprocess.run([gifsicle, "-O3", str(OUT), "-o", str(temp_path)],
                           check=True, capture_output=True)
            if temp_path.stat().st_size < OUT.stat().st_size:
                temp_path.replace(OUT)
            else:
                temp_path.unlink(missing_ok=True)
        except (OSError, subprocess.CalledProcessError):
            temp_path.unlink(missing_ok=True)
    print(f"GIF created: {OUT.relative_to(ROOT)} — {W}x{H}, {len(frames)} frames, {OUT.stat().st_size:,} bytes")

if __name__ == "__main__":
    generate()
