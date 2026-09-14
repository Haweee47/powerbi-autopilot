"""Review captures from tools/render_check.ps1: one contact sheet, plus a comparison with the committed screenshots.

  python tools/render_report.py [out/render]

- out/render/sheet.png: every captured page on one image, to look at all of them at once
- for navy + English pilot captures, the share of the page that changed against templates/<purpose>/screenshots/.
  The two images are aligned first (captures can sit a few pixels apart), then compared at half size with a light blur,
  so anti-aliasing doesn't count. Measured on the pilots: unchanged pages 0.00-0.01%; four missing KPI comparison
  lines 0.17%; a missing takeaway line 0.51%. Anything above the threshold: open that page and look.

Needs Pillow (pip install pillow).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[1]
# 커밋된 캡처 파일 이름이 페이지 id·레이아웃 id와 다른 경우
ALIAS = {"category": "categories", "deep_tree": "decomposition", "deep_scatter": "discount", "deep_detail": "raw_data"}
THRESHOLD = 0.1  # % of the page


def font(size: int):
    for f in (Path("C:/Windows/Fonts/seguisb.ttf"), Path("C:/Windows/Fonts/segoeui.ttf")):
        if f.exists():
            return ImageFont.truetype(str(f), size)
    return ImageFont.load_default()


def reference_names(purpose: str) -> list[str]:
    spec = json.load(open(ROOT / "templates" / purpose / "pilot.spec.json", encoding="utf-8"))
    return [ALIAS.get(k, k) for k in (p.get("id") or p["layout"] for p in spec["pages"])]


def _prep(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    return im.convert("L").resize(size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(1))


def _diff(a: Image.Image, b: Image.Image, dx: int, dy: int, margin: int) -> Image.Image:
    return ImageChops.difference(a, ImageChops.offset(b, dx, dy)).crop((margin, margin, a.width - margin, a.height - margin))


def changed_share(capture: Image.Image, reference: Image.Image, threshold: int = 48) -> tuple[float, tuple[int, int]]:
    """(% of the page that changed, shift in 1280-px units). Coarse alignment at 160×90, refined at 640×360."""
    ca, cb = _prep(capture, (160, 90)), _prep(reference, (160, 90))
    cx, cy = min(((x, y) for x in range(-4, 5) for y in range(-4, 5)),
                 key=lambda s: ImageStat.Stat(_diff(ca, cb, *s, 4)).mean[0])
    fa, fb = _prep(capture, (640, 360)), _prep(reference, (640, 360))
    best = min(((cx * 4 + x, cy * 4 + y) for x in range(-3, 4) for y in range(-3, 4)),
               key=lambda s: ImageStat.Stat(_diff(fa, fb, *s, 20)).mean[0])
    changed = _diff(fa, fb, *best, 20).point(lambda v: 255 if v > threshold else 0)
    return 100 * ImageStat.Stat(changed).mean[0] / 255, (best[0] * 2, best[1] * 2)


def sheet(shots: list[Path], out: Path) -> None:
    W, cols, pad, head = 900, 2, 16, 34
    h = W * 9 // 16
    rows = (len(shots) + cols - 1) // cols
    im = Image.new("RGB", (pad + cols * (W + pad), pad + rows * (h + head + pad)), "#0F1A2A")
    d = ImageDraw.Draw(im)
    for i, p in enumerate(shots):
        x, y = pad + (i % cols) * (W + pad), pad + (i // cols) * (h + head + pad)
        d.text((x, y + 4), f"{p.parent.name} / {p.stem}", font=font(20), fill="#F2F5F9")
        im.paste(Image.open(p).convert("RGB").resize((W, h), Image.LANCZOS), (x, y + head))
    im.save(out)


def main() -> None:
    sys.stdout.reconfigure(**({} if sys.stdout.isatty() else {"encoding": "utf-8"}), errors="replace")
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out" / "render"
    dirs = sorted(d for d in base.iterdir() if d.is_dir())
    shots = [p for d in dirs for p in sorted(d.glob("*.png"))]
    if not shots:
        sys.exit(f"no captures in {base}")
    sheet(shots, base / "sheet.png")
    print(f"Contact sheet: {base / 'sheet.png'} ({len(shots)} pages)")

    flagged = compared = 0
    for d in dirs:
        purpose, theme, lang = (d.name.split("-", 2) + ["", ""])[:3]
        if (theme, lang) != ("navy", "en") or not (ROOT / "templates" / purpose / "pilot.spec.json").exists():
            continue
        refs = reference_names(purpose)
        for i, p in enumerate(sorted(d.glob("*.png"))):
            ref = ROOT / "templates" / purpose / "screenshots" / f"{refs[i]}.png" if i < len(refs) else None
            if not ref or not ref.exists():
                continue
            share, shift = changed_share(Image.open(p), Image.open(ref))
            status = "CHECK" if share > THRESHOLD else "ok"
            flagged += status == "CHECK"
            compared += 1
            print(f"  {status:<5} {d.name} / {p.stem:<28} {share:5.2f}% changed (shift {shift}) vs {ref.relative_to(ROOT)}")
    if flagged:
        print(f"{flagged} of {compared} page(s) changed by more than {THRESHOLD}%: look at them in sheet.png")
    elif compared:
        print(f"All {compared} compared pages match the committed screenshots")
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
