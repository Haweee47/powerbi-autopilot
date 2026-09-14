"""공유용 이미지 만들기: 파일럿 캡처(1280×720) → LinkedIn·README용 표지, 테마 비교, 페이지 GIF, PDF 캐러셀.

입력: templates/<용도>/screenshots/*.png, templates/_themes/<테마>.png (Desktop에서 잘라 낸 캔버스)
결과: docs/share/media/cover.png (1200×1500), themes.png (1200×630), pages.gif, carousel.pdf

사용법: python tools/make_media.py
"""
import glob
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "templates"
OUT = ROOT / "docs" / "share" / "media"
FONTS = Path("C:/Windows/Fonts")

NAVY, INK, SOFT, ACCENT, WHITE = "#0F1A2A", "#F2F5F9", "#AEB9C7", "#6EA8FE", "#FFFFFF"
PURPOSES = [("dashboard", "Dashboard"), ("table", "Measure table"), ("matrix", "Matrix check"), ("deepdive", "Deep dive")]
THEMES = [("navy", "Navy"), ("paper", "Paper"), ("midnight", "Midnight")]


def font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    for name in (["seguisb.ttf", "segoeuib.ttf"] if bold else ["segoeui.ttf"]) + ["malgun.ttf"]:
        if (FONTS / name).exists():
            return ImageFont.truetype(str(FONTS / name), size)
    return ImageFont.load_default()


def card(img: Image.Image, w: int, radius: int = 14) -> Image.Image:
    """스크린샷을 폭 w로 줄이고 둥근 모서리 + 부드러운 그림자를 입힌다."""
    h = round(img.height * w / img.width)
    shot = img.convert("RGB").resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
    pad = 24
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((pad, pad + 6, pad + w, pad + h + 6), radius, fill=(0, 0, 0, 110))
    out = Image.alpha_composite(out, shadow.filter(ImageFilter.GaussianBlur(12)))
    out.paste(shot, (pad, pad), mask)
    return out


COVER_PAGE = {"dashboard": "summary", "table": "stores", "matrix": "heatmap", "deepdive": "decomposition"}  # 용도마다 대표 페이지


def first_shot(purpose: str) -> Path | None:
    p = T / purpose / "screenshots" / f"{COVER_PAGE.get(purpose, '')}.png"
    if p.exists():
        return p
    files = sorted((T / purpose / "screenshots").glob("*.png"))
    return files[0] if files else None


def cover() -> Image.Image:
    # 높이는 내용에 맞춘다: 제목 300 + 카드 두 줄 + 설명 세 줄 (빈 띠가 생기지 않게)
    W, H = 1200, 1340
    im = Image.new("RGBA", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((72, 72), "One request →", font=font(True, 58), fill=INK)
    d.text((72, 140), "a finished Power BI report", font=font(True, 58), fill=INK)
    d.text((72, 222), "AI agent + pilots + theme-first generator · checked in Power BI Desktop", font=font(False, 26), fill=SOFT)
    cw, gap, top = 516, 24, 300
    for i, (pid, label) in enumerate(PURPOSES):
        p = first_shot(pid)
        if not p:
            continue
        c = card(Image.open(p), cw)
        x = 72 - 24 + (i % 2) * (cw + gap + 24)
        y = top + (i // 2) * (c.height + 40)
        im.alpha_composite(c, (x, y))
        d.text((x + 24, y + c.height - 14), label, font=font(True, 28), fill=INK)
    facts = ["4 pilots by purpose  ·  3 themes  ·  English default, Korean built in",
             "Agent writes a 1–3K-token spec  ·  0 errors on Microsoft's PBIR validator",
             "github.com/Haweee47/powerbi-autopilot"]
    for i, f in enumerate(facts):
        d.text((72, H - 190 + i * 44), f, font=font(i == 2, 26), fill=ACCENT if i == 2 else SOFT)
    return im


def themes_strip() -> Image.Image | None:
    shots = [(label, T / "_themes" / f"{tid}.png") for tid, label in THEMES]
    if not all(p.exists() for _, p in shots):
        return None
    W, H = 1200, 630
    im = Image.new("RGBA", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((56, 44), "Same report, three themes", font=font(True, 40), fill=INK)
    d.text((56, 100), "One token file → schema-valid Power BI themes", font=font(False, 24), fill=SOFT)
    cw = 344
    for i, (label, p) in enumerate(shots):
        c = card(Image.open(p), cw, 10)
        x = 56 - 24 + i * (cw + 28)
        im.alpha_composite(c, (x, 170))
        d.text((x + 24, 170 + c.height + 4), label, font=font(True, 26), fill=INK)
    return im


def all_pages() -> list[tuple[str, Image.Image]]:
    pages = []
    for pid, label in PURPOSES:
        for p in sorted((T / pid / "screenshots").glob("*.png")):
            pages.append((f"{label} · {p.stem.replace('_', ' ')}", Image.open(p).convert("RGB")))
    return pages


def social_preview() -> Image.Image:
    """GitHub 소셜 미리보기(Settings → Social preview, 1280×640). 저장소 링크를 공유하면 이 이미지가 카드로 뜬다."""
    W, H = 1280, 640
    im = Image.new("RGBA", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((64, 56), "powerbi-autopilot", font=font(True, 30), fill=ACCENT)
    d.text((64, 104), "One request →", font=font(True, 56), fill=INK)
    d.text((64, 172), "a finished Power BI report", font=font(True, 56), fill=INK)
    d.text((64, 256), "AI agent · 4 pilots · 3 themes · checked in Power BI Desktop · open source", font=font(False, 24), fill=SOFT)
    x = 64 - 24
    for pid in ("dashboard", "matrix", "table"):
        p = first_shot(pid)
        if p:
            c = card(Image.open(p), 368, 10)
            im.alpha_composite(c, (x, 322))
            x += 368 + 20
    return im


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cv = cover()
    cv.convert("RGB").save(OUT / "cover.png", optimize=True)
    made = ["cover.png"]
    social_preview().convert("RGB").save(OUT / "social-preview.png", optimize=True)
    made.append("social-preview.png")
    ts = themes_strip()
    if ts:
        ts.convert("RGB").save(OUT / "themes.png", optimize=True)
        made.append("themes.png")
    pages = all_pages()
    if pages:
        frames = [img.resize((960, 540), Image.LANCZOS).quantize(colors=128, method=Image.MEDIANCUT) for _, img in pages]
        frames[0].save(OUT / "pages.gif", save_all=True, append_images=frames[1:], duration=1800, loop=0, optimize=True)
        made.append(f"pages.gif ({len(frames)} frames)")
        # PDF 캐러셀: 표지 → 페이지마다 한 장 (정사각 1200, 위에 설명 한 줄)
        slides = [cv.convert("RGB").resize((1200, 1500))]
        for label, img in pages:
            s = Image.new("RGB", (1200, 1500), NAVY)
            ImageDraw.Draw(s).text((64, 72), label, font=font(True, 44), fill=INK)
            c = card(img, 1072, 12)
            s.paste(c, (64 - 24, 180), c)
            slides.append(s)
        if ts:
            slides.append(ts.convert("RGB").resize((1200, 630)))
        slides[0].save(OUT / "carousel.pdf", save_all=True, append_images=slides[1:], resolution=150)
        made.append(f"carousel.pdf ({len(slides)} slides)")
    for m in made:
        print("만듦:", (OUT / m.split(" ")[0]).relative_to(ROOT), m[len(m.split(" ")[0]):])


if __name__ == "__main__":
    main()
