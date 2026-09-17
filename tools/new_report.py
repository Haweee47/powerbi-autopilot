"""파일럿에서 새 리포트 명세를 만든다 — 에이전트가 읽을 것을 최소로 줄이는 시작점.

1) templates/catalog.json에서 용도에 맞는 파일럿 명세를 찾아 복사한다
2) {"en": .., "ko": ..} 글자는 고른 언어만 남긴다 (명세가 작아지고, 에이전트가 읽는 토큰이 준다)
3) 상대 경로(model·include·glossary)를 새 위치 기준으로 고친다
4) 대상 모델을 한 화면 요약으로 보여 주고, 파일럿이 그 모델에 기대는 것 중 없는 것을 전부 찾는다:
   명세의 필드 + 공용·명세 측정값의 DAX가 부르는 기준 측정값과 열.
   다른 모델(--model)이면 없는 것으로 model-map.json 뼈대를 쓴다 (값은 빈칸, 힌트는 기준 모델의 식).
   → 에이전트는 대응표 빈칸만 채우면 된다 (TMDL을 통째로 읽지 않는다)

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
from generate_pbir import dax_refs, read_measure_defs, read_model  # noqa: E402

TEMPLATES = ROOT / "templates"
LOCALES = ROOT / "design-system" / "i18n" / "locales.json"
REF = re.compile(r"^[^.\s]+\.[^.]+$")
FIELD_KEYS = ("field", "measure", "x", "y", "point", "size", "small", "target", "color", "ref", "ref_color", "drillthrough",
              "columns", "rows", "values", "by")


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
    """명세 안에서 필드처럼 쓰인 문자열('테이블.열' 또는 측정값 이름)을 모은다."""
    if isinstance(v, dict):
        for k, x in v.items():
            if k in FIELD_KEYS:
                if isinstance(x, str):  # "y": "전년 대비 증감률"처럼 한 개면 문자열 (글자 단위로 쪼개지 않는다)
                    out.add(x)
                elif isinstance(x, list):
                    out.update(s for s in x if isinstance(s, str))
            elif k in ("format", "colors") and isinstance(x, dict):
                out.update(x.keys())
            else:
                fields_in(x, out)
    elif isinstance(v, list):
        for x in v:
            fields_in(x, out)
    return out


def expr_text(v, lang: str, fallback: str) -> str:
    e = v.get("expr", v) if isinstance(v, dict) else v
    if isinstance(e, dict):
        e = e.get(lang) or e.get(fallback) or next(iter(e.values()))
    return e


def rel(target: Path, start: Path) -> str:
    return os.path.relpath(target, start).replace("\\", "/")


def main() -> None:
    sys.stdout.reconfigure(**({} if sys.stdout.isatty() else {"encoding": "utf-8"}), errors="replace")
    cat, loc = load(TEMPLATES / "catalog.json"), load(LOCALES)
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True, choices=[p["id"] for p in cat["purposes"]])
    ap.add_argument("--theme", default="navy", choices=[t["id"] for t in cat["themes"]])
    ap.add_argument("--lang", default=loc["default"])
    ap.add_argument("--frame", default="rail", choices=[f["id"] for f in cat["frames"]], help="page layout: left rail or top bar")
    ap.add_argument("--name", required=True)
    ap.add_argument("--model", help="target model TMDL folder (default: the pilot's reference model)")
    ap.add_argument("--out", help="folder for the new spec (default examples/<name>)")
    ap.add_argument("--reuse-map", help="a model-map.json already filled for this model: known values are prefilled")
    a = ap.parse_args()

    purpose = next(p for p in cat["purposes"] if p["id"] == a.purpose)
    pilot_path = TEMPLATES / purpose["pilot"]
    pilot_dir = pilot_path.parent
    spec = load(pilot_path)
    out = Path(a.out).resolve() if a.out else ROOT / "examples" / a.name
    out.mkdir(parents=True, exist_ok=True)

    spec = keep_lang(spec, a.lang, set(loc["locales"]), loc["fallback"])
    spec.update({"name": a.name, "theme": a.theme, "lang": a.lang})
    if a.frame != "rail":
        spec["frame"] = a.frame
    spec["$comment"] = f"{purpose['id']} pilot → {a.name} ({a.lang}, {a.theme}). Change only what the tool listed as missing, sentences and titles."
    ref_model = (pilot_dir / spec["model"]).resolve()
    model_dir = Path(a.model).resolve() if a.model else ref_model
    own = model_dir != ref_model
    spec["model"] = rel(model_dir, out)
    for k in ("glossary", "dataLocales"):
        if spec.get(k):
            spec[k] = rel((pilot_dir / spec[k]).resolve(), out)
    spec["include"] = [rel((pilot_dir / i.replace("{lang}", "__LANG__")).resolve(), out).replace("__LANG__", "{lang}") for i in spec.get("include", [])]
    if own:  # 샘플 데이터의 값 번역(월 이름·데이터 폴더)은 다른 모델에 맞지 않는다
        spec.pop("dataLocales", None)
        spec.pop("dataLang", None)

    # 파일럿이 기대하는 것: 명세의 필드 + 표시용 측정값(공용·명세) DAX가 부르는 열과 측정값
    layer = {}
    for inc in spec["include"]:
        p = out / inc.replace("{lang}", a.lang)
        layer.update(load(p if p.exists() else out / inc.replace("{lang}", loc["fallback"]))["measures"])
    layer.update(spec.get("measures", {}))
    # 같은 모델로 이미 채운 대응표가 있으면 가져온다. 거기서 이 모델의 식으로 바꿔 쓴 표시용 측정값(예: Orders PY)은
    # 기준 식이 부르던 열(날짜.실적기간 등)이 더는 필요 없다
    reuse = load(Path(a.reuse_map)) if a.reuse_map else {}
    overridden = {k for k in reuse.get("measures", {}) if k in layer}
    used_by: dict[str, set] = {}
    for name, v in layer.items():
        if name in overridden:
            continue
        cols, meas = dax_refs(expr_text(v, a.lang, loc["fallback"]))
        for r in cols | meas:
            used_by.setdefault(r, set()).add(name)
    refs = fields_in(spec.get("pages", []), set()) | fields_in(spec.get("shared", {}), set())
    for r in refs:
        used_by.setdefault(r, set()).add("visuals")

    model = read_model(model_dir)
    target_measures = {m for info in model.values() for m in info["measures"]}
    missing_cols, missing_meas = [], []
    for r in sorted(used_by):
        if r in layer or r.endswith(" Sign Color"):
            continue
        if REF.match(r):
            t, c = r.split(".", 1)
            if c not in model.get(t, {}).get("columns", set()):
                missing_cols.append(r)
        elif r not in target_measures:
            missing_meas.append(r)

    size_note = ""
    if own and (missing_cols or missing_meas):
        ref_defs = read_measure_defs(ref_model)
        ref_types = read_model(ref_model)
        glossary = load(out / spec["glossary"])["fields"] if spec.get("glossary") else {}

        def label(r):
            g = glossary.get(r)
            return (g.get(a.lang) or g.get("en")) if g else ""

        def where(r):
            names = sorted(used_by[r] - {"visuals"})
            parts = (["visuals"] if "visuals" in used_by[r] else []) + ([f"DAX of {', '.join(names[:4])}" + (" …" if len(names) > 4 else "")] if names else [])
            return "used in " + " and ".join(parts)

        # 기준 모델의 식에 드러나지 않는 규칙: 기준 데이터는 마지막 데이터 달에서 끝나므로 비교가 저절로 같은 기간이 된다.
        # 연간 예산이나 단순한 전년 측정값이 있는 모델에서는 직접 맞춰야 한다 (예제 05에서 달성률 64.5%로 틀려서 알았다)
        notes = {
            "전년 매출": "RULE: compare only through the last data date, so a partial year meets the same months last year",
            "전년 이익": "RULE: compare only through the last data date, so a partial year meets the same months last year",
            "목표매출": "RULE: limit the target to dates up to the last data date; a full-year budget otherwise halves attainment",
            "날짜.실적기간": "flag for dates up to the last data date; instead of mapping it you can map the measure 'Orders PY'",
            "날짜.날짜": "the date key; instead of mapping it you can map the measure 'Orders PY'",
        }
        hints = {}
        for c in missing_cols:
            t, col = c.split(".", 1)
            dtype = ref_types.get(t, {}).get("types", {}).get(col, "")
            hints[c] = " · ".join(x for x in (label(c), dtype, notes.get(c, ""), where(c)) if x)
        for m in missing_meas:
            ref = f"reference: {ref_defs[m]['expr']}" if m in ref_defs else ""
            hints[m] = " · ".join(x for x in (label(m), notes.get(m, ""), ref, where(m)) if x)
        guess = reuse.get("measureTable") or max(model, key=lambda t: len(model[t]["measures"]))
        columns = {c: reuse.get("columns", {}).get(c, "") for c in missing_cols}
        measures = {m: reuse["measures"][m] if reuse.get("measures", {}).get(m) else
                    ({"expr": "", "format": ref_defs[m]["format"]} if ref_defs.get(m, {}).get("format") else "") for m in missing_meas}
        measures.update({m: reuse["measures"][m] for m in sorted(overridden)})
        filled = lambda v: bool(v.get("expr") if isinstance(v, dict) else v)  # noqa: E731
        prefilled = sum(filled(v) for v in list(columns.values()) + list(measures.values()))
        empty = [k for k, v in {**columns, **measures}.items() if not filled(v)]
        hints = {k: v for k, v in hints.items() if k in empty}  # 채운 항목의 힌트는 읽을 필요가 없다
        skeleton = {
            "$comment": ("Model map: the pilot was written for the reference model (examples/03-modeling-mcp). Fill each empty value: "
                         "columns → this model's 'Table.Column'; measures → a DAX expression in this model. Mapped measures are added hidden. "
                         "If a missing column is only used inside one display measure, you can map that measure name instead. "
                         "_hints shows the reference definition and where each item is used."),
            "measureTable": guess,
            "columns": columns,
            "measures": measures,
            "_hints": hints,
        }
        map_path = out / "model-map.json"
        if map_path.exists():
            size_note = f"model-map.json already exists; not overwritten ({len(missing_cols)} columns, {len(missing_meas)} measures still expected)"
        else:
            map_path.write_text(json.dumps(skeleton, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            size_note = (f"wrote {rel(map_path, ROOT)} ({map_path.stat().st_size / 1024:.1f}KB ≈ {map_path.stat().st_size // 3:,} tokens) · "
                         f"{len(empty)} empty, {prefilled} prefilled" + (f" from {a.reuse_map}" if a.reuse_map else ""))
        spec["modelMap"] = "model-map.json"
    dest = out / "report.spec.json"
    dest.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    size = dest.stat().st_size
    print(f"New spec: {rel(dest, ROOT)} · {size / 1024:.1f}KB ≈ {size // 3:,} tokens · {purpose['id']} · {a.theme} · {a.lang}")
    print(f"Model summary ({rel(model_dir, ROOT)}):")
    for tname, info in sorted(model.items()):
        cols = ", ".join(sorted(info["columns"] - {"_"}))
        line = f"  {tname}: {cols}" if cols else f"  {tname}:"
        if info["measures"]:
            line += f" | {len(info['measures'])} measures: " + ", ".join(sorted(info["measures"]))
        print(line[:400] + (" …" if len(line) > 400 else ""))
    if missing_cols or missing_meas:
        print(f"The pilot expects {len(missing_cols)} columns and {len(missing_meas)} measures this model doesn't have "
              f"(in visuals and inside the pilot's DAX):")
        print("  columns:  " + ", ".join(missing_cols))
        print("  measures: " + ", ".join(missing_meas))
        if own:
            print(f"Model map: {size_note}. Fill the empty values, then generate.")
        else:
            print("Fix these names in the spec.")
    else:
        print("Everything the pilot uses exists in the target model.")
    print("Next: python tools/generate_pbir.py", rel(dest, ROOT), "&& powerbi-report-author validate <the .Report folder>")


if __name__ == "__main__":
    main()
