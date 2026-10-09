#!/usr/bin/env python3
"""Generate a detailed ASCII portrait and animated terminal profile GIF."""
from __future__ import annotations
import base64
import gzip
import html
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
ART = ROOT / "assets/portrait_ascii.gz.b64"
OUT = ROOT / "assets/terminal_profile.gif"
USER = "GabrielVanderlinde"
W, H = 1100, 560
BG, BORDER = (22, 25, 31), (57, 64, 77)
PROMPT, LABEL, VALUE, TEXT = (201, 209, 217), (242, 141, 53), (141, 231, 241), (220, 226, 233)
GREEN = (105, 230, 158)
CURSOR = "_"
TYPE_STEP, TYPE_MS, BLINKS = 4, 45, 1
CURSOR_MS, PAGE_PAUSE_MS = 70, 1600
RAMP = " .,:;irsXA253hMHGS#9B&@"
TEXT_X, TEXT_Y, TEXT_SIZE, LINE_HEIGHT = 34, 84, 12, 22
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
    if not ART.exists():
        raise SystemExit(f"ASCII portrait map not found: {ART}")
    try:
        encoded = ART.read_text(encoding="ascii").strip()
        raw = gzip.decompress(base64.b64decode(encoded, validate=True))
        lines = raw.decode("utf-8").splitlines()
    except (ValueError, OSError, gzip.BadGzipFile, UnicodeError) as exc:
        raise SystemExit(f"Cannot decode portrait map: {exc}") from exc
    if len(lines) != 100 or max((len(line) for line in lines), default=0) < 150:
        raise SystemExit(f"Unexpected portrait map dimensions: {len(lines)} rows")
    invalid = set("".join(lines)) - set(RAMP)
    if invalid:
        raise SystemExit(f"Portrait map has unsupported characters: {''.join(sorted(invalid))}")
    return lines

def write_portrait_svg(art: list[str]) -> None:
    """Render the supplied portrait map as a detailed standalone SVG for README."""
    width, height = 1240, 800
    rows = []
    for index, line in enumerate(art):
        y = 14 + index * 7.8
        rows.append(
            f'<text x="20" y="{y:.1f}">{html.escape(line, quote=False)}</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
      viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
      <title id="title">Gabriel Vanderlinde — ASCII portrait</title>
      <desc id="desc">A detailed portrait rendered with terminal characters on a dark background.</desc>
      <defs>
        <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#070b09"/>
          <stop offset="100%" stop-color="#111a15"/>
        </linearGradient>
        <linearGradient id="ink" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="#bfcfc5"/>
          <stop offset="55%" stop-color="#f0f4f1"/>
          <stop offset="100%" stop-color="#9fe8bd"/>
        </linearGradient>
        <pattern id="scanlines" width="4" height="6" patternUnits="userSpaceOnUse">
          <path d="M0 5.5 H4" stroke="#6de6a0" stroke-opacity=".05" stroke-width=".5"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" rx="18" fill="url(#background)"/>
      <rect x="12" y="12" width="{width-24}" height="{height-24}" rx="14"
        fill="none" stroke="#1a6e46" stroke-opacity=".65"/>
      <path d="M26 54 V26 H54 M{width-54} 26 H{width-26} V54 M26 {height-54} V{height-26} H54 M{width-54} {height-26} H{width-26} V{height-54}"
        stroke="#36e88d" stroke-width="1.5" fill="none" opacity=".8"/>
      <g font-family="DejaVu Sans Mono, Liberation Mono, monospace" font-size="8"
         letter-spacing="1.2" fill="url(#ink)" opacity=".96">
        {''.join(rows)}
      </g>
      <rect width="100%" height="100%" rx="18" fill="url(#scanlines)"/>
      <text x="30" y="{height-26}" font-family="monospace" font-size="10"
        fill="#36e88d" opacity=".7">ASCII / PORTRAIT</text>
    </svg>'''
    (ROOT / "assets" / "readme_ascii_portrait.svg").write_text(svg + "\n", encoding="utf-8")


def make_base() -> Image.Image:
    """Build the terminal window; the standalone portrait lives above it in the README."""
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((12, 9, W - 13, H - 9), radius=14, outline=BORDER, width=1)
    draw.rounded_rectangle((14, 11, W - 15, 61), radius=12, fill=(15, 22, 19))
    draw.rectangle((14, 43, W - 15, 61), fill=(15, 22, 19))
    for x, color in ((31, (255, 95, 86)), (48, (255, 189, 46)), (65, (39, 201, 63))):
        draw.ellipse((x, 28, x + 8, 36), fill=color)
    draw.text((88, 23), "gabriel@dev-profile: ~/portfolio — zsh", font=load_font(12), fill=(173, 190, 180))
    draw.line((22, 62, W - 22, 62), fill=(37, 58, 46), width=1)
    draw.line((628, 74, 628, H - 23), fill=(37, 58, 46), width=1)

    # Sidebar: persistent system status and the key themes of this profile.
    sx, sw = 653, W - 681
    draw.rounded_rectangle((sx, 80, sx + sw, H - 24), radius=10,
                           fill=(11, 17, 14), outline=(35, 82, 57), width=1)
    small = load_font(10)
    medium = load_font(12)
    draw.text((sx + 18, 96), "SYSTEM OVERVIEW", font=small, fill=GREEN)
    draw.line((sx + 18, 118, sx + sw - 18, 118), fill=(37, 58, 46), width=1)
    draw.text((sx + 18, 134), "STATUS", font=small, fill=(123, 143, 130))
    draw.text((sx + 18, 151), "ONLINE  ●", font=medium, fill=GREEN)
    draw.text((sx + 18, 190), "CORE STACK", font=small, fill=(123, 143, 130))
    draw.text((sx + 18, 210), "JAVA / SPRING", font=medium, fill=TEXT)
    draw.text((sx + 18, 232), "TYPESCRIPT / NESTJS", font=medium, fill=TEXT)
    draw.text((sx + 18, 270), "ENGINEERING FOCUS", font=small, fill=(123, 143, 130))
    draw.text((sx + 18, 290), "APIs  •  TESTING", font=medium, fill=VALUE)
    draw.text((sx + 18, 312), "OBSERVABILITY", font=medium, fill=VALUE)
    draw.text((sx + 18, 350), "LOCATION", font=small, fill=(123, 143, 130))
    draw.text((sx + 18, 370), "BLUMENAU, SC / BR", font=medium, fill=TEXT)
    draw.text((sx + 18, H - 60), ">_  ALWAYS BUILDING", font=medium, fill=GREEN)
    return image
def draw_line(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
              font: ImageFont.ImageFont, count: int | None = None) -> float:
    shown = text if count is None else text[:count]
    draw.text((x, y), "$ ", font=font, fill=PROMPT)
    cursor_x = x + draw.textlength("$ ", font=font)
    if shown.startswith("[ OK ]"):
        label, value = "[ OK ]", shown[6:]
        draw.text((cursor_x, y), label, font=font, fill=GREEN)
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
    write_portrait_svg(art)
    base = make_base()
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
