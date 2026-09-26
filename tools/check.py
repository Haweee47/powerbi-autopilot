"""Everything a change must pass, in one command. CI runs exactly this.

  python tools/check.py                      # regenerate, build every combination, validate
  python tools/check.py --require-validator  # CI: fail if Microsoft's validator isn't installed

1. Rebuild layouts, themes and the four pilots. Fail if git then shows a change under design-system/ or
   templates/: a source was edited without regenerating, or a generated file was edited by hand.
2. Build every pilot × theme × language (en, ko) into out/check/.
3. Run Microsoft's PBIR validator on each report: 0 errors and 0 warnings required.

Needs Python 3.10+ and `pip install jsonschema` (theme schema check).
Validator: `npm install -g @microsoft/powerbi-report-authoring-cli`
Visual check in Power BI Desktop is separate (Windows only): tools/render_check.ps1
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "check"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
PILOTS = ["dashboard", "table", "matrix", "deepdive", "fulfillment"]
LANGS = ["en", "ko"]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)


def regenerate() -> list[str]:
    problems = []
    steps = [["tools/build_layouts.py"], ["tools/build_themes.py"], ["tools/design_check.py"]] + [
        ["tools/generate_pbir.py", f"templates/{p}/pilot.spec.json"] for p in PILOTS]
    for step in steps:
        r = run([sys.executable, *step])
        print(f"  {'OK ' if r.returncode == 0 else 'ERR'} {' '.join(step)}")
        if r.returncode:
            problems.append(f"{' '.join(step)} failed:\n{r.stdout[-1500:]}{r.stderr[-1500:]}")
    if shutil.which("git"):
        changed = [line for line in run(["git", "status", "--porcelain", "--", "design-system", "templates"]).stdout.splitlines() if line.strip()]
        if changed:
            problems.append("files under design-system/ or templates/ differ from the last commit after regenerating.\n"
                            "  If you edited a source (tokens, layouts, specs), commit the regenerated files too:\n    "
                            + "\n    ".join(changed[:20]))
    return problems


def model_smoke() -> list[str]:
    """new_model.py on the sample CSVs: the tables, the key relationships and the calendar have to come out every time.
    Only the CSV source runs here - Excel and ODBC need a workbook and a driver, so they are checked by hand (example 07)."""
    dest = OUT / "_model"
    r = run([sys.executable, "tools/new_model.py", "--name", "Check", "--out", str(dest),
             "--csv", "examples/_data/outdoor-shop"])
    if r.returncode:
        return ["new_model.py failed:" + r.stdout[-800:] + r.stderr[-800:]]
    want = {"Orders", "Stores", "Products", "Budget", "Calendar", "Metrics"}
    have = {p.stem for p in (dest / "tables").glob("*.tmdl")}
    rels = (dest / "relationships.tmdl").read_text(encoding="utf-8")
    problems = [f"new_model.py: missing tables {sorted(want - have)}"] if want - have else []
    for key in ("Stores.'Store ID'", "Products.'Product ID'", "Calendar.Date"):
        if key not in rels:
            problems.append(f"new_model.py: no relationship to {key}")
    return problems


def validate(validator: str, report: Path) -> tuple[int | str, int | str]:
    r = run([validator, "validate", str(report)])
    for line in reversed(r.stdout.splitlines()):
        if line.startswith("{"):
            try:
                data = json.loads(line)["data"]
                return data["errorCount"], data["warningCount"]
            except (ValueError, KeyError):
                break
    return "?", "?"


def build_all(validator: str | None, themes: list[str]) -> tuple[list[str], list[tuple]]:
    problems, rows = [], []
    # every theme in the rail layout, and the top-bar layout in the first theme (layout and theme are independent)
    combos = [(theme, "rail") for theme in themes] + [(themes[0], "top")]
    for theme, frame in combos:
        for lang in LANGS:
            for p in PILOTS:
                dest = OUT / (f"{p}-{theme}-{lang}" + ("" if frame == "rail" else f"-{frame}"))
                r = run([sys.executable, "tools/generate_pbir.py", f"templates/{p}/pilot.spec.json",
                         "--lang", lang, "--theme", theme, "--frame", frame, "--out", str(dest)])
                if r.returncode:
                    problems.append(f"{p}-{theme}-{lang}: generator failed\n{r.stdout[-1000:]}{r.stderr[-1000:]}")
                    rows.append((p, theme, lang, "gen failed", ""))
                    continue
                errors, warnings = validate(validator, next(dest.glob("*.Report"))) if validator else ("-", "-")
                rows.append((p, theme, lang, errors, warnings))
                if errors not in (0, "-") or warnings not in (0, "-"):
                    problems.append(f"{p}-{theme}-{lang}: validator {errors} errors, {warnings} warnings "
                                    f"(details: powerbi-report-author validate {dest.relative_to(ROOT)})")
    return problems, rows


def main() -> None:
    sys.stdout.reconfigure(**({} if sys.stdout.isatty() else {"encoding": "utf-8"}), errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--require-validator", action="store_true", help="fail when powerbi-report-author is missing")
    a = ap.parse_args()
    validator = shutil.which("powerbi-report-author")
    if not validator:
        msg = "powerbi-report-author not found (npm install -g @microsoft/powerbi-report-authoring-cli)"
        if a.require_validator:
            sys.exit(msg)
        print(f"! {msg}: building without validation")
    themes = list(json.load(open(ROOT / "design-system" / "tokens.json", encoding="utf-8"))["themes"])

    print("1. Regenerate committed files")
    problems = regenerate()
    print("1b. Build a model from sample CSVs (tools/new_model.py)")
    problems += model_smoke()
    print(f"2-3. Build and validate {len(PILOTS)} pilots × {len(themes)} themes × {len(LANGS)} languages")
    more, rows = build_all(validator, themes)
    problems += more
    for p, theme, lang, e, w in rows:
        print(f"  {p:<10} {theme:<9} {lang:<3} errors {e!s:>3}  warnings {w!s:>3}")
    if problems:
        print(f"\nFAILED ({len(problems)})")
        for x in problems:
            print(" -", x)
        sys.exit(1)
    print(f"\nPASSED: {len(rows)} reports, committed files up to date")


if __name__ == "__main__":
    main()
