"""From a fresh clone to a Power BI report you can open, in one command.

  python tools/quickstart.py                                    # dashboard · navy · English
  python tools/quickstart.py --purpose matrix --theme midnight --lang ja
  python tools/quickstart.py --all                              # all four pilots
  python tools/quickstart.py --open                             # also open it in Power BI Desktop (Windows)

What it does
  1. picks the pilot for the purpose (templates/catalog.json)
  2. generates the PBIP into out/<purpose>-<theme>-<lang>/ with the data folder pointed at this clone
     (the committed pilots carry a placeholder path, so opening them directly finds no data)
  3. prints what to open next

Only the Python standard library is needed. Power BI Desktop runs on Windows.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "templates" / "catalog.json"
LOCALES = ROOT / "design-system" / "i18n" / "locales.json"
DATA = ROOT / "examples" / "_data" / "korean-retail"
OUT = ROOT / "out"
FEEDBACK = "https://github.com/Haweee47/powerbi-autopilot/issues/new/choose"


def load(p: Path) -> dict:
    return json.load(open(p, encoding="utf-8"))


def ensure_data() -> None:
    """Sample CSVs ship with the repo; regenerate them only if someone deleted them."""
    for lang_dir, extra in ((DATA, []), (DATA / "en", ["--lang", "en"])):
        if not any(lang_dir.glob("*.csv")):
            print(f"  sample data missing in {lang_dir.relative_to(ROOT)} - generating it")
            subprocess.run([sys.executable, str(DATA / "generate.py"), *extra], check=True)


def build(purpose: dict, theme: str, lang: str) -> Path | None:
    spec = ROOT / "templates" / purpose["pilot"]
    dest = OUT / f"{purpose['id']}-{theme}-{lang}"
    cmd = [sys.executable, str(ROOT / "tools" / "generate_pbir.py"), str(spec),
           "--lang", lang, "--theme", theme, "--local-data", "--out", str(dest)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        print(f"  FAILED  {purpose['id']}\n{r.stdout}{r.stderr}")
        return None
    return dest / f"{load(spec)['name']}.pbip"


def main() -> None:
    # 콘솔은 유니코드로 출력된다. 파이프·파일로 보낼 때만 UTF-8로 고정한다 (시스템 코드 페이지에서 글자가 깨지지 않게)
    sys.stdout.reconfigure(**({} if sys.stdout.isatty() else {"encoding": "utf-8"}), errors="replace")
    if sys.version_info < (3, 10):
        sys.exit("Python 3.10 or newer is required: https://www.python.org/downloads/")
    cat, loc = load(CATALOG), load(LOCALES)
    purposes = {p["id"]: p for p in cat["purposes"]}
    ap = argparse.ArgumentParser(description="Build a pilot report you can open in Power BI Desktop.")
    ap.add_argument("--purpose", default="dashboard", choices=list(purposes))
    ap.add_argument("--theme", default="navy", choices=[t["id"] for t in cat["themes"]])
    ap.add_argument("--lang", default=loc["default"], choices=list(loc["locales"]))
    ap.add_argument("--all", action="store_true", help="build all four pilots")
    ap.add_argument("--open", action="store_true", help="open the result in Power BI Desktop (Windows)")
    a = ap.parse_args()

    ensure_data()
    chosen = list(purposes.values()) if a.all else [purposes[a.purpose]]
    print(f"Building {len(chosen)} report(s) · theme {a.theme} · language {loc['locales'][a.lang]['name']}")
    built = []
    for p in chosen:
        pbip = build(p, a.theme, a.lang)
        if pbip:
            pages = p["pages"].get(a.lang) or p["pages"]["en"]
            print(f"  OK  {p['name']['en']:<22} {pbip.relative_to(ROOT)}\n      pages: {pages}")
            built.append(pbip)
    if not built:
        sys.exit(1)

    print("\nNext")
    print("  1. Open the .pbip file above in Power BI Desktop (double-click it).")
    print("  2. If the visuals are empty, click Home > Refresh once. The data is bundled sample data.")
    print("  3. To build your own report by asking in plain language, see docs/guide/ (Claude Code section).")
    print(f"\nSomething looks off? Tell me: {FEEDBACK}")
    if a.open:
        if os.name == "nt":
            os.startfile(built[0])  # noqa: S606 - opens the file with its associated app (Power BI Desktop)
            print(f"\nOpening {built[0].name} in Power BI Desktop ...")
        else:
            print("\n--open works on Windows only (Power BI Desktop is Windows-only).")


if __name__ == "__main__":
    main()
