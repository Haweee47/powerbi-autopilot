"""파일럿에서 새 리포트 명세를 만든다 — 에이전트가 읽을 것을 최소로 줄이는 시작점.

1) templates/catalog.json에서 용도에 맞는 파일럿 명세를 찾아 복사한다
2) {"en": .., "ko": ..} 글자는 고른 언어만 남긴다 (명세가 작아지고, 에이전트가 읽는 토큰이 준다)
3) 상대 경로(model·include·glossary·dataLocales)를 새 위치 기준으로 고친다
4) 대상 모델을 한 화면 요약으로 보여 주고, 파일럿이 쓰는 필드 중 대상 모델에 없는 것을 나열한다
   → 에이전트는 이 목록만 보고 명세의 필드 이름을 바꾸면 된다 (TMDL을 통째로 읽지 않는다)

사용법:
  python tools/new_report.py --purpose table --theme paper --lang ko --name StoreKPI [--model <TMDL 폴더>] [--out examples/StoreKPI]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from generate_pbir import read_model  # noqa: E402

TEMPLATES = ROOT / "templates"
LOCALES = ROOT / "design-system" / "i18n" / "locales.json"
REF = re.compile(r"^[^.\s]+\.[^.]+$")


def load(p: Path) -> dict:
    return json.load(open(p, encoding="utf-8"))


def keep_lang(v, lang: str, codes: set, fallback: str):
    """글자 사전은 한 언어만 남긴다. 측정값 식 사전도 같다."""
    if isinstance(v, dict):
        if v and set(v) <= codes:
            return v.get(lang, v.get(fallback, next(iter(v.values()))))
        return {k: keep_lang(x, lang, codes, fallback) for k, x in v.items()}
    if isinstance(v, list):
        return [keep_lang(x, lang, codes, fallback) for x in v]
    return v


def fields_in(v, out: set) -> set:
    """명세 안에서 필드처럼 보이는 문자열('테이블.열' 또는 측정값 이름)을 모은다."""
    if isinstance(v, dict):
        for k, x in v.items():
            if k in ("field", "measure", "x", "point", "size", "small", "target", "color", "ref", "ref_color", "drillthrough"):
                if isinstance(x, str):
                    out.add(x)
            elif k in ("y", "columns", "rows", "values", "by"):
                out.update(s for s in x if isinstance(s, str))
            elif k in ("format", "colors"):
                out.update(x.keys())
            else:
                fields_in(x, out)
    elif isinstance(v, list):
        for x in v:
            fields_in(x, out)
    return out


def rel(target: Path, start: Path) -> str:
    return os.path.relpath(target, start).replace("\\", "/")


def main() -> None:
    sys.stdout.reconfigure(**({} if sys.stdout.isatty() else {"encoding": "utf-8"}), errors="replace")
    cat, loc = load(TEMPLATES / "catalog.json"), load(LOCALES)
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True, choices=[p["id"] for p in cat["purposes"]])
    ap.add_argument("--theme", default="navy", choices=[t["id"] for t in cat["themes"]])
    ap.add_argument("--lang", default=loc["default"])
    ap.add_argument("--name", required=True)
    ap.add_argument("--model", help="대상 모델 TMDL 폴더 (없으면 파일럿 모델 그대로)")
    ap.add_argument("--out", help="새 명세 폴더 (기본 examples/<name>)")
    a = ap.parse_args()

    purpose = next(p for p in cat["purposes"] if p["id"] == a.purpose)
    pilot_path = TEMPLATES / purpose["pilot"]
    pilot_dir = pilot_path.parent
    spec = load(pilot_path)
    out = Path(a.out).resolve() if a.out else ROOT / "examples" / a.name
    out.mkdir(parents=True, exist_ok=True)

    spec = keep_lang(spec, a.lang, set(loc["locales"]), loc["fallback"])
    spec.update({"name": a.name, "theme": a.theme, "lang": a.lang})
    spec["$comment"] = f"{purpose['id']} pilot → {a.name} ({a.lang}, {a.theme}). Change only fields that the tool listed as missing, sentences and titles."
    model_dir = Path(a.model).resolve() if a.model else (pilot_dir / spec["model"]).resolve()
    spec["model"] = rel(model_dir, out)
    for k in ("glossary", "dataLocales"):
        if spec.get(k):
            spec[k] = rel((pilot_dir / spec[k]).resolve(), out)
    spec["include"] = [rel((pilot_dir / i.replace("{lang}", "__LANG__")).resolve(), out).replace("__LANG__", "{lang}") for i in spec.get("include", [])]
    dest = out / "report.spec.json"
    dest.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 대상 모델 요약 (한 화면) + 파일럿 필드 중 없는 것
    model = read_model(model_dir)
    extra = set(spec.get("measures", {}))
    for inc in spec.get("include", []):
        p = (out / inc.replace("{lang}", a.lang))
        if not p.exists():
            p = out / inc.replace("{lang}", loc["fallback"])
        extra |= set(load(p)["measures"])
    measures = model.get(spec["measureTable"], {}).get("measures", set()) | extra
    missing = []
    for f in sorted(fields_in(spec.get("pages", []), set()) | fields_in(spec.get("shared", {}), set())):
        if REF.match(f) and f.split(".", 1)[0] in model:
            if f.split(".", 1)[1] not in model[f.split(".", 1)[0]]["columns"]:
                missing.append(f)
        elif f not in measures and not f.endswith(" Sign Color"):
            missing.append(f)

    size = dest.stat().st_size
    print(f"새 명세: {rel(dest, ROOT)} · {size / 1024:.1f}KB ≈ {size // 3:,} 토큰 · 용도 {purpose['id']} · 테마 {a.theme} · 언어 {a.lang}")
    print(f"모델 요약 ({rel(model_dir, ROOT)}):")
    for tname, info in sorted(model.items()):
        cols = ", ".join(sorted(info["columns"] - {"_"}))
        line = f"  {tname}: {cols}" if cols else f"  {tname}:"
        if info["measures"]:
            line += f" | 측정값 {len(info['measures'])}개: " + ", ".join(sorted(info["measures"]))
        print(line[:400] + (" …" if len(line) > 400 else ""))
    if missing:
        print(f"대상 모델에 없는 필드 {len(missing)}개 — 명세에서 이것만 바꾸면 된다:")
        for m in missing:
            print("  -", m)
    else:
        print("파일럿 필드가 대상 모델에 모두 있다.")
    print("다음: python tools/generate_pbir.py", rel(dest, ROOT), "&& powerbi-report-author validate <만들어진 .Report>")


if __name__ == "__main__":
    main()
