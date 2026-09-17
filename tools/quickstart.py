"""From a fresh clone to a Power BI report you can open, in one command.

  python tools/quickstart.py                                    # dashboard · navy · English
  python tools/quickstart.py --purpose matrix --theme midnight --lang ja
  python tools/quickstart.py --all                              # all four pilots
  python tools/quickstart.py --open                             # also open it in Power BI Desktop (Windows)

What it does
  1. picks the pilot for the purpose (templates/catalog.json)
  2. generates the PBIP into out/<purpose>-<theme>-<lang>/ with the data folder pointed at this clone
     (the committed pilots carry a placeholder path, so opening them directly finds no data)
  3. checks which Power BI Desktop will open it: versions older than 2.157 cut off labels in the pilots (#1)
  4. prints what to open next

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
# Microsoft Store 판은 스스로 업데이트된다. 설치 관리자(MSI) 판은 오래된 채로 남아 .pbip 연결을 차지하기도 한다 (#1)
STORE_ALIAS = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "PBIDesktopStore.exe"
MSI_EXE = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Microsoft Power BI Desktop" / "bin" / "PBIDesktop.exe"
MIN_DESKTOP = (2, 157)  # 파일럿을 캡처로 확인한 버전. 2.147은 KPI 비교 줄·결론 줄·표 열 폭·버튼 글자가 틀린다


def load(p: Path) -> dict:
    return json.load(open(p, encoding="utf-8"))


def ensure_data() -> None:
    """Sample CSVs ship with the repo; regenerate them only if someone deleted them."""
    for lang_dir, extra in ((DATA, []), (DATA / "en", ["--lang", "en"])):
        if not any(lang_dir.glob("*.csv")):
            print(f"  sample data missing in {lang_dir.relative_to(ROOT)} - generating it")
            subprocess.run([sys.executable, str(DATA / "generate.py"), *extra], check=True)
    ops = ROOT / "examples" / "_data" / "fulfillment"
    if not any(ops.glob("*.csv")):
        print(f"  sample data missing in {ops.relative_to(ROOT)} - generating it")
        subprocess.run([sys.executable, str(ops / "generate.py")], check=True)


def build(purpose: dict, theme: str, lang: str, frame: str = "rail") -> Path | None:
    spec = ROOT / "templates" / purpose["pilot"]
    dest = OUT / (f"{purpose['id']}-{theme}-{lang}" + ("" if frame == "rail" else f"-{frame}"))
    cmd = [sys.executable, str(ROOT / "tools" / "generate_pbir.py"), str(spec),
           "--lang", lang, "--theme", theme, "--frame", frame, "--local-data", "--out", str(dest)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        print(f"  FAILED  {purpose['id']}\n{r.stdout}{r.stderr}")
        return None
    return dest / f"{load(spec)['name']}.pbip"


def file_version(exe: Path) -> tuple[int, ...] | None:
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", f"(Get-Item '{exe}').VersionInfo.FileVersion"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return tuple(int(x) for x in out.split(".")) if out else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def desktop_check() -> tuple[bool, str | None]:
    """(Store version available, warning text or None)."""
    if os.name != "nt":
        return False, "Power BI Desktop runs on Windows only."
    msi = file_version(MSI_EXE) if MSI_EXE.exists() else None
    old = msi is not None and msi[:2] < MIN_DESKTOP
    ver = ".".join(map(str, msi)) if msi else ""
    need = f"{MIN_DESKTOP[0]}.{MIN_DESKTOP[1]}"
    if STORE_ALIAS.exists():
        if old:
            return True, (f"Two copies of Power BI Desktop are installed. Double-clicking a .pbip may open the older one ({ver}),\n"
                          f"  which cuts off some labels. Use --open, or start Power BI Desktop from the Start menu and use File > Open.")
        return True, None
    if old:
        return False, (f"Power BI Desktop {ver} is older than {need} and will cut off some labels.\n"
                       f"  Update it, or install the Microsoft Store version (it keeps itself up to date).")
    if msi is None:
        return False, "Power BI Desktop was not found. Install it from the Microsoft Store (free)."
    return False, None


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
    ap.add_argument("--frame", default="rail", choices=[f["id"] for f in cat["frames"]], help="page layout: left rail or top bar")
    ap.add_argument("--all", action="store_true", help="build all four pilots")
    ap.add_argument("--open", action="store_true", help="open the result in Power BI Desktop (Windows)")
    a = ap.parse_args()

    ensure_data()
    chosen = list(purposes.values()) if a.all else [purposes[a.purpose]]
    print(f"Building {len(chosen)} report(s) · theme {a.theme} · layout {a.frame} · language {loc['locales'][a.lang]['name']}")
    built = []
    for p in chosen:
        pbip = build(p, a.theme, a.lang, a.frame)
        if pbip:
            pages = p["pages"].get(a.lang) or p["pages"]["en"]
            print(f"  OK  {p['name']['en']:<22} {pbip.relative_to(ROOT)}\n      pages: {pages}")
            built.append(pbip)
    if not built:
        sys.exit(1)

    store, warning = desktop_check()
    print("\nNext")
    print("  1. Open the .pbip file above in Power BI Desktop 2.157 or newer.")
    print("  2. If the visuals are empty, click Refresh now on the yellow bar (then Apply changes if asked).")
    print("  3. To build your own report by asking in plain language, see docs/guide/ (Claude Code section).")
    if warning:
        print(f"\n! {warning}")
    print(f"\nSomething looks off? Tell me: {FEEDBACK}")
    if a.open and os.name == "nt":
        if store:
            subprocess.Popen([str(STORE_ALIAS), str(built[0])])
            print(f"\nOpening {built[0].name} in Power BI Desktop (Microsoft Store version) ...")
        else:
            os.startfile(built[0])  # noqa: S606 - opens the file with its associated app
            print(f"\nOpening {built[0].name} in Power BI Desktop ...")


if __name__ == "__main__":
    main()
