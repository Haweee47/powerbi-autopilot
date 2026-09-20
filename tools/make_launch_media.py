"""Launch media: a short demo loop (request typed in, pages coming out) and square slides for a feed post.

Input: Desktop captures. English pages come from templates/<purpose>/screenshots/ (committed); Korean pages come from
out/render/ful-ko/ if a capture run left them there (tools/render_check.ps1 -Dir out/ful-ko), otherwise the Korean demo is skipped.
Output: docs/share/media/demo-ko.gif, demo-en.gif (and .mp4 beside them), slide-ko-1..4.png

The GIF plays anywhere; the MP4 is what a feed prefers. MP4 needs `pip install imageio imageio-ffmpeg`; without it the
GIF is still written and the MP4 is skipped with a note.

Usage: python tools/make_launch_media.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "templates"
OUT = ROOT / "docs" / "share" / "media"
KO_PAGES = ROOT / "out" / "render" / "dashboard-navy-ko"  # the Korean build of the dashboard pilot
FONTS = Path("C:/Windows/Fonts")

NAVY, PANEL, EDGE = "#0F1A2A", "#16202E", "#2A3A4F"
INK, SOFT, DIM = "#F2F5F9", "#AEB9C7", "#7C8798"
ACCENT, GOOD = "#6EA8FE", "#52D19B"
W, H = 1200, 675  # 16:9, the size a feed plays at


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    """kind: body | bold | mono. Malgun Gothic carries both Korean and ASCII, so one family covers both demos."""
    names = {"body": ["malgun.ttf"], "bold": ["malgunbd.ttf", "malgun.ttf"], "mono": ["consola.ttf", "malgun.ttf"]}[kind]
    for n in names:
        if (FONTS / n).exists():
            return ImageFont.truetype(str(FONTS / n), size)
    return ImageFont.load_default()


def card(img: Image.Image, w: int, radius: int = 12) -> Image.Image:
    """A screenshot as a rounded card with a soft shadow (same treatment as make_media.py)."""
    h = round(img.height * w / img.width)
    shot = img.convert("RGB").resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
    pad = 20
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((pad, pad + 6, pad + w, pad + h + 6), radius, fill=(0, 0, 0, 120))
    out = Image.alpha_composite(out, shadow.filter(ImageFilter.GaussianBlur(10)))
    out.paste(shot, (pad, pad), mask)
    return out


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split(" "):
        probe = f"{line} {word}".strip()
        if draw.textlength(probe, font=f) > width and line:
            lines.append(line)
            line = word
        else:
            line = probe
    return lines + [line] if line else lines


def prompt_frame(lines: list[str], shown: int, caret: bool, steps: list[str], title: str, mono_ok: bool) -> Image.Image:
    """The request being typed into the agent, line by line, with the steps it runs ticking off underneath."""
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((80, 72, W - 80, H - 48), 16, fill=PANEL, outline=EDGE, width=2)
    for i, c in enumerate(("#F2645A", "#F5BF4F", "#52D19B")):
        d.ellipse((112 + i * 26, 104, 124 + i * 26, 116), fill=c)
    d.text((204, 100), title, font=font("body", 20), fill=DIM)
    d.line((80, 140, W - 80, 140), fill=EDGE, width=2)

    # Consolas has no Hangul, so a Korean request is typed in the body face instead
    mono, body = (font("mono", 23) if mono_ok else font("body", 22)), font("body", 22)
    d.text((116, 172), ">", font=font("mono", 23), fill=ACCENT)  # ASCII only: these faces have no prompt-arrow glyph
    y = 172
    for line in lines[:shown]:
        d.text((152, y), line, font=mono, fill=INK if not line.startswith("-") else SOFT)
        y += 34
    if caret:
        last = lines[shown - 1] if shown else ""
        d.rectangle((155 + d.textlength(last, font=mono), y - 32, 167 + d.textlength(last, font=mono), y - 8), fill=ACCENT)

    y = max(y + 30, 410)
    for s in steps:
        d.line((122, y + 14, 130, y + 23), fill=GOOD, width=3)  # a drawn tick, for the same reason
        d.line((130, y + 23, 144, y + 5), fill=GOOD, width=3)
        d.text((156, y), s, font=body, fill=SOFT)
        y += 44
    return im


def page_frame(img: Image.Image, caption: str, index: int, total: int) -> Image.Image:
    """One generated page, with a counter so the run reads as a sequence."""
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    c = card(img, 1040)
    im.paste(c, ((W - c.width) // 2, 78), c)
    d.text((100, 30), caption, font=font("bold", 30), fill=INK)
    counter = f"{index}/{total}"
    d.text((W - 100 - d.textlength(counter, font=font("bold", 26)), 36), counter, font=font("bold", 26), fill=ACCENT)
    return im


def end_frame(lines: list[str]) -> Image.Image:
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((100, 232), "powerbi-autopilot", font=font("bold", 58), fill=INK)
    d.text((100, 312), lines[0], font=font("body", 28), fill=SOFT)
    d.text((100, 372), lines[1], font=font("body", 28), fill=SOFT)
    d.text((100, 452), "github.com/Haweee47/powerbi-autopilot", font=font("bold", 30), fill=ACCENT)
    return im


DEMOS = {
    "ko": {
        "title": "Claude Code · powerbi-autopilot",
        "prompt": ["매장별 매출 대시보드 만들어줘.",
                   "- 보는 사람은 영업 팀장과 매장 담당자, 매주 월요일 회의에서 본다",
                   "- 1순위는 매출. 전년 대비와 목표 달성률을 나란히, 금액은 억·만 단위로",
                   "- 부진한 곳이 바로 보이게: 카테고리별 목표 대비, 하위 매장 3곳은 따로",
                   "- 매장을 누르면 상세 페이지로 넘어가게, 기간은 올해가 기본",
                   "- 테마는 실무용으로 차분하게, 한국어로"],
        "steps": ["명세 작성 · 3.1K 토큰", "PBIR 생성 · 4페이지 · 비주얼 55개",
                  "Microsoft 공식 검증 · 오류 0 · 경고 0", "Power BI Desktop에서 전 페이지 캡처"],
        "end": ["한 줄 요청 → 완성된 Power BI 리포트", "오픈소스 MIT · 가상 데이터"],
    },
    "en": {
        "title": "Claude Code · powerbi-autopilot",
        "prompt": ["Build a store sales dashboard.",
                   "- Read every Monday by the sales lead and the store managers",
                   "- Sales first, with year-on-year and target attainment beside it",
                   "- Make the gap obvious: vs target by category, three weakest stores apart",
                   "- Click a store to drill through to its detail page",
                   "- Default period this year, and a calm, practical theme"],
        "steps": ["Spec written · 3.1K tokens", "PBIR generated · 4 pages · 55 visuals",
                  "Microsoft PBIR validator · 0 errors, 0 warnings", "Every page captured in Power BI Desktop"],
        "end": ["One request → a finished Power BI report", "Open source (MIT) · sample data"],
    },
}
# English pages: the committed captures that carry no Korean from the capture machine's Desktop language
EN_PAGES = [("dashboard/summary", "Sales performance"), ("dashboard/categories", "Categories"),
            ("dashboard/stores", "Stores"), ("dashboard/store_detail", "Store detail (drill-through)")]


def ko_pages() -> list[tuple[Path, str]]:
    if not KO_PAGES.exists():
        return []
    return [(p, p.stem.split("-", 1)[1].replace("_", " ")) for p in sorted(KO_PAGES.glob("*.png"))]


def demo(lang: str) -> tuple[list[Image.Image], list[int]] | None:
    d = DEMOS[lang]
    pages = ko_pages() if lang == "ko" else [(T / f"{a}.png".replace("/", "/screenshots/", 1), b) for a, b in EN_PAGES]
    pages = [(p, c) for p, c in pages if p.exists()]
    if not pages:
        return None
    frames, times = [], []
    lines = d["prompt"]
    ascii_only = all(line.isascii() for line in lines)
    for n in range(1, len(lines) + 1):  # a line at a time: a real request is written in points, not one sentence
        frames.append(prompt_frame(lines, n, True, [], d["title"], ascii_only))
        times.append(900 if n == 1 else 520)
    frames.append(prompt_frame(lines, len(lines), False, [], d["title"], ascii_only))
    times.append(600)
    for i in range(1, len(d["steps"]) + 1):
        frames.append(prompt_frame(lines, len(lines), False, d["steps"][:i], d["title"], ascii_only))
        times.append(600 if i < len(d["steps"]) else 1000)
    for i, (p, caption) in enumerate(pages, 1):
        frames.append(page_frame(Image.open(p), caption, i, len(pages)))
        times.append(1050)
    frames.append(end_frame(d["end"]))
    times.append(2400)
    return frames, times


def slide(body) -> Image.Image:
    """A 1200×1200 square slide: title band on navy, content drawn by `body(draw, image)`."""
    im = Image.new("RGB", (1200, 1200), NAVY)
    body(ImageDraw.Draw(im), im)
    return im


def ko_slides() -> list[Image.Image]:
    pages = {p.stem.split("-", 1)[1]: p for p in sorted(KO_PAGES.glob("*.png"))} if KO_PAGES.exists() else {}
    themes = [T / "_themes" / f"{t}.png" for t in ("navy", "aurora", "coast", "ledger", "contrast", "paper", "midnight")]
    slides = []

    def hero(d, im):
        d.text((80, 104), "요청 한 줄로", font=font("bold", 62), fill=INK)
        d.text((80, 186), "완성된 Power BI 리포트", font=font("bold", 62), fill=INK)
        d.text((80, 286), "데이터 모델 → 디자인 → 검증까지. Desktop에서 손으로 만지지 않는다.", font=font("body", 26), fill=SOFT)
        src = pages.get("요약") or (T / "dashboard" / "screenshots" / "summary.png")
        c = card(Image.open(src), 1000)
        im.paste(c, (80 - 20, 380), c)
        for i, t in enumerate(["대시보드 파일럿 · 4페이지 · 비주얼 55개",
                               "모든 이름과 숫자는 가상 데이터", "github.com/Haweee47/powerbi-autopilot"]):
            d.text((80, 990 + i * 52), t, font=font("bold" if i == 2 else "body", 26), fill=ACCENT if i == 2 else SOFT)
    slides.append(slide(hero))

    def detail(d, im):
        d.text((80, 96), "숫자에서 끝나지 않고", font=font("bold", 56), fill=INK)
        d.text((80, 176), "원인까지 한 페이지 더", font=font("bold", 56), fill=ACCENT)
        d.text((80, 268), "표에서 매장을 누르면 그 매장만 보는 상세 페이지로 넘어간다.", font=font("body", 26), fill=SOFT)
        src = pages.get("매장_상세") or (T / "dashboard" / "screenshots" / "store_detail.png")
        c = card(Image.open(src), 1000)
        im.paste(c, (80 - 20, 380), c)
        for i, t in enumerate(["요약 · 카테고리 · 매장 · 매장 상세(드릴스루)",
                               "용도별 파일럿 5종 중 하나. 지표 테이블·행렬·딥다이브·물류 운영도 같은 방식"]):
            d.text((80, 990 + i * 52), t, font=font("body", 26), fill=SOFT)
    slides.append(slide(detail))

    def theme_grid(d, im):
        d.text((80, 96), "같은 리포트, 테마 7종", font=font("bold", 56), fill=INK)
        d.text((80, 178), "색 팔레트 × 카드 모양. 서식은 비주얼이 아니라 테마에 있다.", font=font("body", 26), fill=SOFT)
        x0, y0, cw, gap = 60, 280, 340, 16
        for i, p in enumerate(themes):
            if not p.exists():
                continue
            c = card(Image.open(p), cw, 8)
            centre = (3 - len(themes) % 3) * (cw + gap) // 2 if i // 3 == len(themes) // 3 else 0  # last row sits centred
            im.paste(c, (x0 + (i % 3) * (cw + gap) + centre, y0 + (i // 3) * 210), c)
        d.text((80, 940), "기본 · 쇼케이스 · 실무 세 묶음, 색각 이상 검사를 통과한 계열 색", font=font("body", 26), fill=SOFT)
        d.text((80, 992), "브랜드 색 하나로 새 테마를 만드는 도구도 함께", font=font("body", 26), fill=SOFT)
        d.text((80, 1094), "github.com/Haweee47/powerbi-autopilot", font=font("bold", 30), fill=ACCENT)
    slides.append(slide(theme_grid))

    def numbers(d, im):
        d.text((80, 104), "숫자로", font=font("bold", 62), fill=INK)
        rows = [("$0.6~4", "리포트 하나당 API 비용 (약 800~5,500원)"), ("2~10분", "요청부터 전 페이지 캡처까지"),
                ("0", "Microsoft 공식 PBIR 검증 오류 · 80개 빌드"), ("6%", "에이전트가 쓰는 양 (나머지는 스크립트)"),
                ("1,800+", "디자인 규칙의 근거가 된 공개 리포트")]
        y = 250
        for big, small in rows:
            d.text((80, y), big, font=font("bold", 64), fill=ACCENT)
            d.text((420, y + 22), small, font=font("body", 27), fill=SOFT)
            y += 160
        d.text((80, 1094), "github.com/Haweee47/powerbi-autopilot", font=font("bold", 30), fill=INK)
    slides.append(slide(numbers))
    return slides


FPS = 25  # a feed wants a real frame rate, so each still is repeated for as long as it should be on screen


def write_mp4(frames: list[Image.Image], times: list[int], path: Path) -> str:
    """The same still frames as H.264, which autoplays in a feed where a GIF may not."""
    try:
        import imageio.v2 as imageio
        import numpy as np
    except ImportError:
        return f"{path.name} skipped (pip install imageio imageio-ffmpeg)"
    even = [f.resize((f.width // 2 * 2, f.height // 2 * 2)) for f in frames]  # H.264 wants even dimensions
    with imageio.get_writer(path, fps=FPS, codec="libx264", quality=8,
                            macro_block_size=None, pixelformat="yuv420p") as w:
        for frame, ms in zip(even, times):
            arr = np.asarray(frame.convert("RGB"))
            for _ in range(max(1, round(ms / 1000 * FPS))):
                w.append_data(arr)
    seconds = sum(times) / 1000
    return f"{path.name} ({seconds:.0f}s, {path.stat().st_size / 1e6:.1f} MB)"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for lang in ("ko", "en"):
        got = demo(lang)
        if not got:
            print(f"skipped demo-{lang}.gif: no captures for it")
            continue
        frames, times = got
        pal = [f.quantize(colors=160, method=Image.MEDIANCUT) for f in frames]
        path = OUT / f"demo-{lang}.gif"
        pal[0].save(path, save_all=True, append_images=pal[1:], duration=times, loop=0, optimize=True)
        made.append(f"{path.name} ({len(frames)} frames, {path.stat().st_size / 1e6:.1f} MB)")
        mp4 = write_mp4(frames, times, OUT / f"demo-{lang}.mp4")
        made.append(mp4)
    for i, s in enumerate(ko_slides(), 1):
        s.save(OUT / f"slide-ko-{i}.png", optimize=True)
        made.append(f"slide-ko-{i}.png")
    for m in made:
        print("made:", m)


if __name__ == "__main__":
    main()
