"""Make a theme preset from one brand color.

The new preset copies a base preset (layout, card shape, text colors) and moves the brand color in:
- Blue, teal and violet brands (hue 165–330°) become the data accent too: this year's series, positive changes, bars.
- Red, orange, yellow and green brands only color the navigation rail and selections. The data keeps the base colors,
  because the reports use red for "below target" and red next to green is the pair color-blind readers confuse most.

Usage:
  python tools/brand_theme.py --id acme --name "Acme" --accent "#0F62FE" [--base navy] [--group brand]
  python tools/build_themes.py
  python tools/quickstart.py --purpose dashboard --theme acme

Writes the preset into design-system/tokens.json and templates/catalog.json. Run it again with the same id to replace it.
"""
import argparse
import colorsys
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "design-system" / "tokens.json"
CATALOG = ROOT / "templates" / "catalog.json"
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
ROWS = [["page", "surface", "hover", "border", "shadow"], ["ink", "ink2", "ink3"], ["grid", "axis", "mid"],
        ["accent", "context", "target"], ["pos", "neg", "posInk", "negInk"], ["barPos", "barNeg", "heatMax"],
        ["rail", "railBorder", "railHover", "railOn", "railAccent"], ["railInk", "railInk2", "railInk3"], ["segBg", "segOn", "segOnInk"]]


def rgb(h: str) -> tuple[float, float, float]:
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


def hexed(c) -> str:
    return "#" + "".join(f"{round(max(0, min(1, x)) * 255):02X}" for x in c)


def mix(a: str, b: str, t: float) -> str:
    """t = 0 → a, t = 1 → b."""
    return hexed([x + (y - x) * t for x, y in zip(rgb(a), rgb(b))])


def luminance(h: str) -> float:
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb(h)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def readable(color: str, ground: str, target: float = 4.5) -> str:
    """Darken (light ground) or lighten (dark ground) until the text contrast reaches the target."""
    toward = "#000000" if luminance(ground) > 0.4 else "#FFFFFF"
    for step in range(21):
        c = mix(color, toward, step * 0.05)
        if contrast(c, ground) >= target:
            return c
    return toward


def is_dark(h: str) -> bool:
    return luminance(h) < 0.2


def brand_palette(base: dict, accent: str) -> tuple[dict, list, bool]:
    c, cat = dict(base["color"]), list(base["categorical"])
    hue, light, sat = colorsys.rgb_to_hls(*rgb(accent))
    data_accent = 165 <= hue * 360 <= 330 and sat > 0.25
    if data_accent:
        c.update(accent=accent, pos=accent, posInk=readable(accent, c["surface"]),
                 barPos=mix(accent, c["surface"], 0.72), heatMax=mix(accent, c["surface"], 0.45))
        cat = [accent] + [x for x in cat[1:] if x.upper() != accent.upper()]
        cat = (cat + base["categorical"])[:len(base["categorical"])]
    if is_dark(c["rail"]):  # dark rail: tint it with the brand, keep light text on it
        c.update(rail=mix(accent, "#000000", 0.80), railBorder=mix(accent, "#000000", 0.80),
                 railHover=mix(accent, "#000000", 0.70), railOn=mix(accent, "#000000", 0.58),
                 segBg=mix(accent, "#000000", 0.70), railAccent=mix(accent, "#FFFFFF", 0.35))
    else:  # light rail: brand on the selected page and the selected slicer button
        on_ink = "#FFFFFF" if contrast("#FFFFFF", accent) >= 4.5 else c["ink"]
        c.update(railOn=mix(accent, c["rail"], 0.86), railAccent=accent, segOn=accent, segOnInk=on_ink)
    return c, cat, data_accent


def color_block(c: dict) -> str:
    return ",\n".join("        " + ", ".join(f'"{k}": "{c[k]}"' for k in row) for row in ROWS)


def write_theme(tid: str, name: str, desc: str, style: str, c: dict, cat: list) -> None:
    text = TOKENS.read_text(encoding="utf-8")
    block = (f'    "{tid}": {{\n      "name": "{name}",\n      "desc": "{desc}",\n      "style": "{style}",\n'
             f'      "color": {{\n{color_block(c)}\n      }},\n      "categorical": {json.dumps(cat)}\n    }}')
    existing = re.search(rf'\n    "{re.escape(tid)}": \{{.*?\n    \}}(?=,?\n)', text, re.S)
    if existing:
        text = text[:existing.start() + 1] + block + text[existing.end():]
    else:
        end = text.index('\n  },\n  "styles"')
        text = text[:end] + ",\n" + block + text[end:]
    json.loads(text)
    TOKENS.write_text(text, encoding="utf-8")


def write_catalog(tid: str, name: str, group: str, when: str) -> None:
    text = CATALOG.read_text(encoding="utf-8")
    line = json.dumps({"id": tid, "group": group, "name": {"en": name, "ko": name}, "when": {"en": when, "ko": when}},
                      ensure_ascii=False).replace("{", "{ ").replace("}", " }")
    pat = re.compile(rf'\n    \{{ "id": "{re.escape(tid)}".*?\}} \}}(?=,?\n)')
    if pat.search(text):
        text = pat.sub(lambda m: "\n    " + line, text)
    else:
        end = text.index('\n  ],\n  "languages"')
        text = text[:end] + ",\n    " + line + text[end:]
    json.loads(text)
    CATALOG.write_text(text, encoding="utf-8")


def main() -> None:
    sys.stdout.reconfigure(**({} if sys.stdout.isatty() else {"encoding": "utf-8"}), errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--id", required=True, help="preset id, lowercase letters and digits")
    ap.add_argument("--name", help="display name (default: the id, capitalized)")
    ap.add_argument("--accent", required=True, help="brand color, #RRGGBB")
    ap.add_argument("--base", default="navy", help="preset to start from (layout, card shape, text colors)")
    ap.add_argument("--group", default="brand")
    a = ap.parse_args()
    tok = json.loads(TOKENS.read_text(encoding="utf-8"))
    if not re.fullmatch(r"[a-z][a-z0-9]{1,23}", a.id):
        sys.exit("--id: lowercase letters and digits, 2–24 characters")
    if not HEX.match(a.accent):
        sys.exit("--accent: a color like #0F62FE")
    if a.base not in tok["themes"]:
        sys.exit(f"--base: one of {', '.join(tok['themes'])}")
    if a.id == a.base:
        sys.exit("--id must differ from --base")
    accent, base = a.accent.upper(), tok["themes"][a.base]
    name = a.name or a.id.title()
    c, cat, data_accent = brand_palette(base, accent)
    role = "rail, selections and data accent" if data_accent else "rail and selections (data keeps the base colors)"
    when = f"{name} brand color on {role}. Based on {a.base.title()}"
    write_theme(a.id, name, when, base.get("style", "soft"), c, cat)
    write_catalog(a.id, name, a.group, when)
    print(f"Preset '{a.id}': {accent} on {role}, from {a.base} ({base.get('style', 'soft')} cards)")
    checks = [("selected page text", c["railInk"], c["railOn"]), ("selected button text", c["segOnInk"], c["segOn"])]
    if data_accent:
        checks.insert(0, ("accent text on cards", c["posInk"], c["surface"]))
    print("  contrast: " + " · ".join(f"{label} {contrast(x, y):.1f}:1" for label, x, y in checks))
    print("Next: python tools/build_themes.py, then build a pilot with --theme " + a.id)


if __name__ == "__main__":
    main()
