#!/usr/bin/env python3
"""Generate a detailed ASCII portrait and animated terminal profile GIF."""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from collections import Counter
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ART = ROOT / "assets/portrait.txt"
OUT = ROOT / "assets/terminal_profile.gif"
USER = "GabrielVanderlinde"
W, H = 1100, 1340
BG, BORDER = (12, 13, 16), (68, 72, 80)
PROMPT, LABEL, VALUE, TEXT = (238, 240, 243), (157, 163, 172), (219, 222, 227), (205, 209, 215)
ACCENT = (226, 229, 233)
CURSOR = "_"
TYPE_STEP, TYPE_MS, BLINKS = 4, 45, 1
CURSOR_MS, PAGE_PAUSE_MS = 70, 1600
RAMP = " .,:;irsXA253hMHGS#9B&@"
TEXT_X, TEXT_Y, TEXT_SIZE, LINE_HEIGHT = 52, 782, 13, 28
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



def get_live_stats() -> tuple[list[str], bool]:
    """Fetch public GitHub profile/repository stats when the GIF is built."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GabrielVanderlinde-terminal-profile-gif",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def fetch_json(url: str):
        request = Request(url, headers=headers)
        with urlopen(request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))

    try:
        profile = fetch_json(f"https://api.github.com/users/{USER}")
        repositories = fetch_json(
            f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated"
        )
        repositories = [
            repo for repo in repositories
            if not repo.get("fork")
            and not repo.get("archived")
            and repo.get("name", "").lower() != USER.lower()
        ]
        stars = sum(int(repo.get("stargazers_count") or 0) for repo in repositories)
        languages = Counter(repo.get("language") for repo in repositories if repo.get("language"))
        top_languages = " / ".join(name for name, _ in languages.most_common(4)) or "not reported yet"
        latest = max(repositories, key=lambda repo: repo.get("pushed_at") or "", default=None)
        latest_name = latest.get("name", "none yet") if latest else "none yet"
        last_push = latest.get("pushed_at", "")[:10] if latest else ""
        lines = [
            f"Public repositories: {int(profile.get('public_repos') or 0)}",
            f"Stars on owned projects: {stars}",
            f"Top languages: {top_languages}",
            f"Latest project: {latest_name}",
        ]
        if last_push:
            lines.append(f"Last push date: {last_push}")
        lines.append("Data source: live GitHub REST API snapshot")
        return lines, True
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"GitHub API unavailable during GIF build: {type(exc).__name__}: {exc}")
        return [
            "Live stats temporarily unavailable",
            "The next scheduled build will retry the API",
            "Profile: github.com/GabrielVanderlinde",
        ], False


def load_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()

def load_ascii_portrait() -> list[str]:
    """Load the human-readable character map derived from the supplied portrait."""
    if not ART.exists():
        raise SystemExit(f"Portrait character map not found: {ART}")
    lines = ART.read_text(encoding="utf-8").splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    max_columns = max((len(line) for line in lines), default=0)
    if len(lines) != 100 or max_columns < 150:
        raise SystemExit(
            f"Unexpected portrait map dimensions: {len(lines)} rows, {max_columns} columns"
        )
    invalid = set("".join(lines)) - set(RAMP)
    if invalid:
        raise SystemExit(f"Portrait map has unsupported characters: {''.join(sorted(invalid))}")
    return lines

def make_base(art: list[str]) -> Image.Image:
    """Stack the detailed ASCII portrait above a monochrome animated terminal."""
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)

    # Subtle outer frame and soft grayscale scan lines keep the design restrained.
    draw.rounded_rectangle((12, 10, W - 13, H - 10), radius=13, outline=BORDER, width=1)
    for y in range(20, H - 18, 5):
        draw.line((20, y, W - 20, y), fill=(15, 16, 19), width=1)

    # Portrait section: render the supplied high-detail character map centered above the terminal.
    portrait_font = load_font(5)
    cell_w = draw.textlength("M", font=portrait_font)
    row_step = 5.55
    max_columns = max((len(line) for line in art), default=0)
    portrait_width = max_columns * cell_w
    portrait_x = max(18, (W - portrait_width) / 2)
    portrait_y = 27
    ramp_max = len(RAMP) - 1

    for row_index, line in enumerate(art):
        y = portrait_y + row_index * row_step
        for col_index, char in enumerate(line):
            if char == " ":
                continue
            level = RAMP.find(char)
            if level < 0:
                continue
            shade = int(60 + (level / ramp_max) * 190)
            draw.text(
                (portrait_x + col_index * cell_w, y),
                char,
                font=portrait_font,
                fill=(shade, shade, shade),
            )

    draw.text((28, 598), "ASCII PORTRAIT  /  GRAYSCALE RENDER", font=load_font(9), fill=(112, 116, 124))
    draw.line((24, 633, W - 24, 633), fill=(51, 54, 61), width=1)

    # Terminal sits beneath the portrait in its own window frame.
    tx, ty, tr, tb = 28, 657, W - 28, H - 22
    draw.rounded_rectangle((tx, ty, tr, tb), radius=10, outline=(82, 86, 94), width=1)
    draw.rounded_rectangle((tx + 2, ty + 2, tr - 2, ty + 53), radius=8, fill=(23, 25, 30))
    draw.rectangle((tx + 2, ty + 32, tr - 2, ty + 53), fill=(23, 25, 30))

    # Window controls use shades of gray instead of the usual colored dots.
    for x, shade in ((tx + 18, 145), (tx + 35, 180), (tx + 52, 218)):
        draw.ellipse((x, ty + 18, x + 8, ty + 26), fill=(shade, shade, shade))
    draw.text(
        (tx + 72, ty + 13),
        "gabriel@vanderlinde: ~/portfolio — zsh",
        font=load_font(12),
        fill=(210, 213, 218),
    )
    draw.line((tx + 14, ty + 54, tr - 14, ty + 54), fill=(59, 62, 69), width=1)

    # Main terminal content on the left, fixed system panel on the right.
    divider_x = 756
    body_top = 735
    draw.line((divider_x, body_top, divider_x, tb - 16), fill=(54, 57, 64), width=1)

    sx, sw = 773, tr - 795
    panel_bottom = tb - 17
    draw.rounded_rectangle(
        (sx, body_top + 2, sx + sw, panel_bottom),
        radius=8,
        fill=(18, 20, 24),
        outline=(61, 64, 71),
        width=1,
    )

    small = load_font(10)
    medium = load_font(12)
    muted = (139, 144, 153)
    bright = (224, 227, 232)
    rule = (56, 59, 66)

    draw.text((sx + 18, 756), "SYSTEM OVERVIEW", font=small, fill=bright)
    draw.line((sx + 17, 778, sx + sw - 17, 778), fill=rule, width=1)

    draw.text((sx + 18, 795), "STATUS", font=small, fill=muted)
    draw.text((sx + 18, 813), "ONLINE  ●", font=medium, fill=bright)

    draw.text((sx + 18, 849), "CORE STACK", font=small, fill=muted)
    draw.text((sx + 18, 868), "JAVA / SPRING", font=medium, fill=bright)
    draw.text((sx + 18, 891), "TYPESCRIPT / NESTJS", font=medium, fill=bright)
    draw.text((sx + 18, 914), "NODE.JS / SQL", font=medium, fill=bright)

    draw.text((sx + 18, 950), "ENGINEERING FOCUS", font=small, fill=muted)
    draw.text((sx + 18, 969), "REST APIs  •  TESTING", font=medium, fill=bright)
    draw.text((sx + 18, 992), "OBSERVABILITY", font=medium, fill=bright)

    draw.text((sx + 18, 1028), "LOCATION", font=small, fill=muted)
    draw.text((sx + 18, 1047), "BLUMENAU, SC / BR", font=medium, fill=bright)

    draw.line((sx + 17, 1084, sx + sw - 17, 1084), fill=rule, width=1)
    draw.text((sx + 18, 1105), ">_ BUILDING THE FUTURE", font=medium, fill=bright)
    draw.text((sx + 18, 1133), "CONTINUOUS LEARNING", font=small, fill=muted)
    draw.text((sx + 18, 1153), "ALWAYS BUILDING", font=small, fill=muted)

    # Small footer at the bottom of the terminal window.
    footer_y = tb - 39
    draw.line((tx + 14, footer_y - 14, tr - 14, footer_y - 14), fill=(45, 48, 54), width=1)
    draw.text(
        (tx + 18, footer_y),
        "PROFILE STREAM  •  UTF-8  •  LOOP: ON",
        font=load_font(9),
        fill=(112, 117, 126),
    )
    return image
def draw_line(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
              font: ImageFont.ImageFont, count: int | None = None) -> float:
    shown = text if count is None else text[:count]
    draw.text((x, y), "$ ", font=font, fill=PROMPT)
    cursor_x = x + draw.textlength("$ ", font=font)
    if shown.startswith("[ OK ]"):
        label, value = "[ OK ]", shown[6:]
        draw.text((cursor_x, y), label, font=font, fill=ACCENT)
        cursor_x += draw.textlength(label, font=font)
        if value:
            draw.text((cursor_x, y), value, font=font, fill=TEXT)
            cursor_x += draw.textlength(value, font=font)
    elif shown.startswith("[WARN]"):
        label, value = "[WARN]", shown[6:]
        draw.text((cursor_x, y), label, font=font, fill=LABEL)
        cursor_x += draw.textlength(label, font=font)
        draw.text((cursor_x, y), value, font=font, fill=TEXT)
        cursor_x += draw.textlength(value, font=font)
    elif ":" in shown:
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
    stats, stats_available = get_live_stats()
    boot_lines = [
        "[ OK ] terminal runtime initialized",
        "[ OK ] high-detail ASCII portrait loaded",
        "[ OK ] profile modules loaded",
        "[ OK ] GitHub API connected" if stats_available else "[WARN] GitHub API unavailable; stats omitted",
        "SYSTEM ONLINE — READY",
    ]
    screens = [
        ("PROFILE", SCREENS[0][1]),
        ("TECH STACK", SCREENS[1][1]),
        ("FEATURED PROJECTS", SCREENS[2][1] + [
            "GitHub: github.com/GabrielVanderlinde",
        ]),
        ("LIVE GITHUB STATS", stats),
        ("CURRENT MISSION", SCREENS[3][1] + [
            "STATUS: BUILDING THE FUTURE",
        ]),
    ]
    # Startup comes first and is typed like a real shell session.
    screens.insert(0, ("SYSTEM BOOT", boot_lines))
    frames: list[Image.Image] = []
    durations: list[int] = []
    total = len(screens)
    for screen_number, (section, lines) in enumerate(screens, start=1):
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
        add_frame(frames, durations, base, rows, "clear", len("clear"), False, PAGE_PAUSE_MS)
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
            subprocess.run([gifsicle, "-O3", "--careful", str(OUT), "-o", str(temp_path)],
                           check=True, capture_output=True)
            if temp_path.stat().st_size < OUT.stat().st_size:
                temp_path.replace(OUT)
            else:
                temp_path.unlink(missing_ok=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            temp_path.unlink(missing_ok=True)
            print(f"GIF optimization skipped: {exc}")

    with Image.open(OUT) as gif:
        assert gif.size == (W, H), f"Unexpected GIF dimensions: {gif.size}"
        assert gif.n_frames > 300, f"Animation has too few frames: {gif.n_frames}"
        assert gif.info.get("loop", 0) == 0, "GIF is not set to loop forever"
        print(f"GIF generated: {OUT.relative_to(ROOT)} — {W}x{H}, {gif.n_frames} frames, {OUT.stat().st_size:,} bytes")

if __name__ == "__main__":
    generate()
