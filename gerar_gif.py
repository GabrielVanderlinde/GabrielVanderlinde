#!/usr/bin/env python3
"""Generate a detailed ASCII portrait and animated terminal profile GIF."""
from __future__ import annotations
import base64
import gzip
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ART = ROOT / "assets/portrait_ascii.gz.b64"
OUT = ROOT / "assets/terminal_profile.gif"
W, H = 900, 426
BG, BORDER = (22, 25, 31), (57, 64, 77)
PROMPT, LABEL, VALUE, TEXT = (201, 209, 217), (242, 141, 53), (141, 231, 241), (220, 226, 233)
CURSOR = "_"
TYPE_STEP, TYPE_MS, BLINKS = 2, 55, 2
CURSOR_MS, PAGE_PAUSE_MS = 100, 1500
RAMP = " .,:;irsXA253hMHGS#9B&@"
PORTRAIT_X, PORTRAIT_Y, PORTRAIT_ROW_STEP = 14, 12, 2.85
TEXT_X, TEXT_Y, TEXT_SIZE, LINE_HEIGHT = 430, 62, 9, 17
FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "C:/Windows/Fonts/consola.ttf",
)
SCREENS = [
    ("PROFILE", [
        "Name: ........... Gabriel Vanderlinde",
        "Role: ........... Software Developer",
        "Location: ....... Blumenau, SC, Brazil",
        "Focus: .......... Backend engineering and REST APIs",
        "Stack: .......... Java, Spring Boot, TypeScript, NestJS",
        "Interests: ...... Architecture, code quality, observability",
        "Status: ......... Always learning, always building",
    ]),
    ("TECH STACK", [
        "Frontend: HTML, CSS, JavaScript, TypeScript, React",
        "Backend: Node.js, NestJS, Java, Spring Boot, Python",
        "Database/ORM: MySQL, PostgreSQL, MongoDB, Prisma",
        "Cloud/Containers: Azure, Docker, Podman",
        "Observability: Prometheus, Grafana, Loki, Tempo",
        "IDE/Testing: VS Code, IntelliJ, PyCharm, Postman, Playwright",
        "Tools/OS: Git, GitHub, npm, Linux, Ubuntu, PowerShell",
        "Quality: Clean code, tests, maintainability",
    ]),
    ("FEATURED PROJECTS", [
        "Tasks Management: NestJS, TypeScript, Prisma",
        "Travel Management: Java, Spring Boot, JPA, MySQL",
        "Vollmed API: Medical clinic management backend",
        "Rios Alerta: River information and monitoring web project",
        "Gerenciador de Tarefas v2: Java",
        "More projects: APIs, experiments, learning projects",
    ]),
    ("CURRENT MISSION", [
        "Backend: Reliable, well-structured REST APIs",
        "Software Quality: Clean code, testing, maintainability",
        "Data: Relational and NoSQL databases",
        "DevOps: Containers, metrics, logs, monitoring",
        "Focus: Practice, build projects, improve continuously",
        "GitHub: github.com/GabrielVanderlinde",
        "LinkedIn: linkedin.com/in/gabrielhenriquevanderlinde",
        "Open to collaboration and tech conversations",
    ]),
]

def load_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()

def load_ascii_portrait() -> list[str]:
    if not ART.exists():
        raise SystemExit(f"ASCII portrait map not found: {ART}")
    try:
        encoded = ART.read_text(encoding="ascii").strip()
        raw = gzip.decompress(base64.b64decode(encoded, validate=True))
        lines = raw.decode("utf-8").splitlines()
    except (ValueError, OSError, gzip.BadGzipFile, UnicodeError) as exc:
        raise SystemExit(f"Cannot decode portrait map: {exc}") from exc
    if not lines or not any(any(c != " " for c in line) for line in lines):
        raise SystemExit("ASCII portrait map is empty")
    return lines

def make_base(art: list[str]) -> Image.Image:
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((12, 9, W - 13, H - 9), radius=10, outline=BORDER, width=1)
    portrait_font = load_font(3)
    cell_w = draw.textlength("M", font=portrait_font)
    # Draw characters sampled from the user's supplied transparent portrait.
    # The map uses a denser grid to preserve eyes, teeth, hair and face contours.
    for row, line in enumerate(art):
        for column, char in enumerate(line):
            if char == " ":
                continue
            level = max(1, RAMP.find(char))
            shade = int(45 + level / (len(RAMP) - 1) * 210)
            draw.text(
                (PORTRAIT_X + column * cell_w, PORTRAIT_Y + row * PORTRAIT_ROW_STEP),
                char, font=portrait_font, fill=(shade, shade, shade),
            )
    return image

def draw_line(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
              font: ImageFont.ImageFont, count: int | None = None) -> float:
    shown = text if count is None else text[:count]
    draw.text((x, y), "$ ", font=font, fill=PROMPT)
    cursor_x = x + draw.textlength("$ ", font=font)
    if ":" in shown:
        label, value = shown.split(":", 1)
        label += ":"
        draw.text((cursor_x, y), label, font=font, fill=LABEL)
        cursor_x += draw.textlength(label, font=font)
        if value:
            draw.text((cursor_x, y), value, font=font, fill=VALUE)
            cursor_x += draw.textlength(value, font=font)
    else:
        draw.text((cursor_x, y), shown, font=font, fill=TEXT)
        cursor_x += draw.textlength(shown, font=font)
    return cursor_x

def add_frame(frames: list[Image.Image], durations: list[int], base: Image.Image,
              rows: list[str], active: str | None = None, count: int | None = None,
              cursor: bool = False, duration: int = TYPE_MS) -> None:
    frame = base.copy()
    draw = ImageDraw.Draw(frame)
    font = load_font(TEXT_SIZE)
    y = TEXT_Y
    for row in rows:
        draw_line(draw, TEXT_X, y, row, font)
        y += LINE_HEIGHT
    if active is not None:
        cursor_x = draw_line(draw, TEXT_X, y, active, font, count)
        if cursor:
            draw.text((cursor_x + 1, y), CURSOR, font=font, fill=PROMPT)
    frames.append(frame)
    durations.append(duration)

def generate() -> None:
    art = load_ascii_portrait()
    base = make_base(art)
    frames: list[Image.Image] = []
    durations: list[int] = []
    total = len(SCREENS)
    for screen_number, (section, lines) in enumerate(SCREENS, start=1):
        header = f"[{screen_number:02d}/{total:02d}] {section}"
        rows: list[str] = []
        for _ in range(BLINKS):
            add_frame(frames, durations, base, rows, header, 0, True, CURSOR_MS)
            add_frame(frames, durations, base, rows, header, 0, False, CURSOR_MS)
        for index in range(0, len(header) + TYPE_STEP, TYPE_STEP):
            count = min(index, len(header))
            add_frame(frames, durations, base, rows, header, count, count < len(header))
        rows.append(header)
        for line in lines:
            for _ in range(BLINKS):
                add_frame(frames, durations, base, rows, line, 0, True, CURSOR_MS)
                add_frame(frames, durations, base, rows, line, 0, False, CURSOR_MS)
            for index in range(0, len(line) + TYPE_STEP, TYPE_STEP):
                count = min(index, len(line))
                add_frame(frames, durations, base, rows, line, count, count < len(line))
            rows.append(line)
        add_frame(frames, durations, base, rows, "$ clear", len("$ clear"), False, PAGE_PAUSE_MS)
        frames.append(frames[-1].copy())
        durations.append(PAGE_PAUSE_MS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, optimize=True, disposal=1)
    gifsicle = shutil.which("gifsicle")
    if gifsicle:
        with tempfile.NamedTemporaryFile(suffix=".gif", dir=OUT.parent, delete=False) as temp:
            temp_path = Path(temp.name)
        try:
            subprocess.run([gifsicle, "-O3", str(OUT), "-o", str(temp_path)],
                           check=True, capture_output=True)
            if temp_path.stat().st_size < OUT.stat().st_size:
                temp_path.replace(OUT)
            else:
                temp_path.unlink(missing_ok=True)
        except (OSError, subprocess.CalledProcessError):
            temp_path.unlink(missing_ok=True)
    with Image.open(OUT) as gif:
        assert gif.size == (W, H), f"Unexpected GIF dimensions: {gif.size}"
        assert gif.n_frames > 100, f"Animation has too few frames: {gif.n_frames}"
        assert gif.info.get("loop", 0) == 0, "GIF should loop infinitely"
        print(f"GIF generated: {OUT.relative_to(ROOT)} — {W}x{H}, {gif.n_frames} frames, {OUT.stat().st_size:,} bytes")

if __name__ == "__main__":
    generate()
