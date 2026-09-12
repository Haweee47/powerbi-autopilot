"""수집한 Power BI 리포트에서 디자인 지표를 뽑는다 (원본을 AI가 통째로 읽지 않기 위해).

지원 형식
- .pbix / .pbit : zip 안의 Report/Layout (구형, UTF-16 JSON) 또는 Report/definition/ (PBIR)
- .Report 폴더  : definition/ (PBIR) 또는 report.json (구형)

뽑는 지표 (리포트당 한 줄 요약)
- 페이지 수·크기, 페이지당 비주얼 수, 비주얼 종류
- 레이아웃: 왼쪽 여백, 가로 간격, 정렬도(서로 다른 x·y 모서리 개수), 겹침 수, 캔버스 사용률
- 서식: 글꼴·글자 크기, 직접 지정한 색 개수, 테마 이름·팔레트·배경색
- 장식 요소: 도형·이미지·텍스트 상자 비율

사용법: python analyze_reports.py <파일 또는 폴더>... [--out summaries.jsonl]
"""
import argparse
import json
import re
import statistics as st
import sys
import zipfile
from collections import Counter
from pathlib import Path

RE_COLOR = re.compile(r"#[0-9A-Fa-f]{6}\b")
RE_FONT_SIZE = re.compile(r'"fontSize"\s*:\s*\{\s*"expr"\s*:\s*\{\s*"Literal"\s*:\s*\{\s*"Value"\s*:\s*"(\d+(?:\.\d+)?)D"')
RE_FONT_FAMILY = re.compile(r'"fontFamily"\s*:\s*\{\s*"expr"\s*:\s*\{\s*"Literal"\s*:\s*\{\s*"Value"\s*:\s*"\'([^\']+)\'')
DECOR = {"shape", "basicShape", "image", "textbox", "actionButton"}


def decode(raw: bytes) -> str:
    # 구형 Report/Layout은 UTF-16LE다. BOM이 없는 파일도 있는데, 이때 UTF-8로 읽어도 오류가 나지 않고
    # NUL 문자가 섞인 엉터리 문자열이 된다. 그래서 앞부분에 0 바이트가 있으면 UTF-16으로 본다.
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")) or b"\x00" in raw[:64]:
        return raw.decode("utf-16", errors="ignore").lstrip("﻿")
    return raw.decode("utf-8-sig", errors="ignore")


# ---------- 형식별 읽기: 결과는 공통 구조 [{"w","h","name","visuals":[{"type","x","y","w","h","raw"}]}] ----------

def pages_from_legacy(layout: dict) -> list:
    pages = []
    for sec in layout.get("sections", []):
        visuals = []
        for vc in sec.get("visualContainers", []):
            try:
                cfg = json.loads(vc.get("config", "{}"))
            except json.JSONDecodeError:
                cfg = {}
            sv = cfg.get("singleVisual") or {}
            vtype = sv.get("visualType") or ("group" if "singleVisualGroup" in cfg else "unknown")
            if vtype == "group":
                continue
            visuals.append({"type": vtype, "x": vc.get("x", 0), "y": vc.get("y", 0),
                            "w": vc.get("width", 0), "h": vc.get("height", 0), "raw": vc.get("config", "")})
        pages.append({"name": sec.get("displayName", ""), "w": sec.get("width", 1280), "h": sec.get("height", 720),
                      "visuals": visuals, "raw": sec.get("config", "")})
    return pages


def pages_from_pbir(files: dict) -> list:
    """files: {상대경로(definition/...): 텍스트}"""
    pages = {}
    for path, text in files.items():
        m = re.match(r"definition/pages/([^/]+)/page\.json$", path)
        if m:
            p = json.loads(text)
            pages.setdefault(m.group(1), {"visuals": []}).update(
                {"name": p.get("displayName", ""), "w": p.get("width", 1280), "h": p.get("height", 720), "raw": text})
    for path, text in files.items():
        m = re.match(r"definition/pages/([^/]+)/visuals/[^/]+/visual\.json$", path)
        if not m:
            continue
        v = json.loads(text)
        if "visualGroup" in v:
            continue
        pos = v.get("position", {})
        pages.setdefault(m.group(1), {"visuals": [], "w": 1280, "h": 720, "name": "", "raw": ""})["visuals"].append(
            {"type": (v.get("visual") or {}).get("visualType", "unknown"), "x": pos.get("x", 0), "y": pos.get("y", 0),
             "w": pos.get("width", 0), "h": pos.get("height", 0), "raw": text})
    return list(pages.values())


def load(path: Path) -> tuple[list, list, str]:
    """(pages, themes, format) — themes: 테마 JSON 텍스트 목록"""
    if path.suffix.lower() in (".pbix", ".pbit"):
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            # 사용자 테마(RegisteredResources)를 뒤에 두어 기본 테마를 덮어쓰게 한다
            themes = [decode(z.read(n)) for n in sorted(
                (n for n in names if n.startswith("Report/StaticResources/") and n.lower().endswith(".json")),
                key=lambda n: "RegisteredResources" in n)]
            if "Report/Layout" in names:
                return pages_from_legacy(json.loads(decode(z.read("Report/Layout")))), themes, "pbix-legacy"
            defs = {n[len("Report/"):]: decode(z.read(n)) for n in names if n.startswith("Report/definition/")}
            return pages_from_pbir(defs), themes, "pbix-pbir"
    root = path
    themes = [p.read_text(encoding="utf-8-sig", errors="ignore")
              for p in sorted((root / "StaticResources").rglob("*.json"),
                              key=lambda p: "RegisteredResources" in p.as_posix())
              ] if (root / "StaticResources").exists() else []
    if (root / "definition").exists():
        defs = {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8-sig", errors="ignore")
                for p in (root / "definition").rglob("*.json")}
        return pages_from_pbir(defs), themes, "pbir"
    if (root / "report.json").exists():
        return pages_from_legacy(json.loads((root / "report.json").read_text(encoding="utf-8-sig"))), themes, "pbip-legacy"
    raise ValueError("알 수 없는 형식")


# ---------- 지표 ----------

def layout_metrics(page: dict) -> dict:
    vs = [v for v in page["visuals"] if v["w"] > 0 and v["h"] > 0]
    if not vs:
        return {}
    W, H = page["w"] or 1280, page["h"] or 720
    xs = sorted({round(v["x"]) for v in vs} | {round(v["x"] + v["w"]) for v in vs})
    ys = sorted({round(v["y"]) for v in vs} | {round(v["y"] + v["h"]) for v in vs})
    overlaps = 0
    for i, a in enumerate(vs):
        for b in vs[i + 1:]:
            if a["type"] in DECOR or b["type"] in DECOR:
                continue  # 배경 도형 위에 올린 것은 의도된 겹침
            if min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]) > 2 and \
               min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]) > 2:
                overlaps += 1
    gaps = []  # 같은 줄(세로 겹침)에 있는 이웃 비주얼 사이 가로 간격
    data_vs = sorted([v for v in vs if v["type"] not in DECOR], key=lambda v: v["x"])
    for i, a in enumerate(data_vs):
        for b in data_vs[i + 1:]:
            if min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]) > 0 and b["x"] >= a["x"] + a["w"] - 1:
                gaps.append(round(b["x"] - (a["x"] + a["w"])))
                break
    area = sum(v["w"] * v["h"] for v in vs if v["type"] not in DECOR)
    return {"n": len(vs), "left": round(min(v["x"] for v in vs)), "edges": len(xs) + len(ys),
            "overlaps": overlaps, "gap_med": st.median(gaps) if gaps else None,
            "coverage": round(min(area / (W * H), 1.5), 2)}


def theme_info(themes: list) -> dict:
    info = {}
    for text in themes:
        try:
            t = json.loads(text)
        except json.JSONDecodeError:
            continue
        if not isinstance(t, dict) or "dataColors" not in t:
            continue
        # 사용자 테마(RegisteredResources)가 기본 테마보다 우선 — 뒤에 오는 것이 덮어씀
        info = {"name": t.get("name"), "palette": t.get("dataColors", [])[:8],
                "background": t.get("background"), "foreground": t.get("foreground"),
                "font": ((t.get("textClasses") or {}).get("label") or {}).get("fontFace")}
    return info


def summarize(path: Path) -> dict:
    pages, themes, fmt = load(path)
    allv = [v for p in pages for v in p["visuals"]]
    raw = "".join(v["raw"] for v in allv) + "".join(p.get("raw", "") for p in pages)
    types = Counter(v["type"] for v in allv)
    per_page = [layout_metrics(p) for p in pages]
    per_page = [m for m in per_page if m]
    sizes = Counter(f'{round(p["w"])}x{round(p["h"])}' for p in pages)
    fs = Counter(float(x) for x in RE_FONT_SIZE.findall(raw))
    return {
        "file": str(path), "format": fmt, "pages": len(pages), "page_size": sizes.most_common(1)[0][0] if sizes else None,
        "visuals": len(allv), "visuals_per_page": round(len(allv) / max(len(pages), 1), 1),
        "types": dict(types.most_common(12)),
        "decor_ratio": round(sum(types[t] for t in DECOR) / max(len(allv), 1), 2),
        "left_margin_med": st.median([m["left"] for m in per_page]) if per_page else None,
        "gap_med": st.median([m["gap_med"] for m in per_page if m["gap_med"] is not None]) if any(m["gap_med"] is not None for m in per_page) else None,
        "edges_per_visual": round(st.mean([m["edges"] / m["n"] for m in per_page]), 2) if per_page else None,
        "overlaps": sum(m["overlaps"] for m in per_page),
        "coverage_med": st.median([m["coverage"] for m in per_page]) if per_page else None,
        "font_sizes": dict(sorted(fs.items())), "fonts": dict(Counter(RE_FONT_FAMILY.findall(raw)).most_common(5)),
        "explicit_colors": len(set(c.upper() for c in RE_COLOR.findall(raw))),
        "top_colors": [c for c, _ in Counter(c.upper() for c in RE_COLOR.findall(raw)).most_common(8)],
        "theme": theme_info(themes),
        "uses_cardVisual": "cardVisual" in types, "uses_legacy_card": "card" in types,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out", default=None, help="결과를 JSON Lines로 저장")
    args = ap.parse_args()
    targets = []
    for p in map(Path, args.paths):
        if p.is_dir() and not p.name.endswith(".Report"):
            targets += [q for q in p.rglob("*") if q.suffix.lower() in (".pbix", ".pbit") or
                        (q.is_dir() and q.name.endswith(".Report"))]
        else:
            targets.append(p)
    out = open(args.out, "w", encoding="utf-8") if args.out else None
    ok = fail = 0
    for t in targets:
        try:
            s = summarize(t)
            ok += 1
        except Exception as e:  # 손상·암호화·알 수 없는 형식
            s = {"file": str(t), "error": f"{type(e).__name__}: {e}"[:200]}
            fail += 1
        line = json.dumps(s, ensure_ascii=False)
        print(line) if out is None else out.write(line + "\n")
    print(f"분석 {ok}개 성공, {fail}개 실패", file=sys.stderr)


if __name__ == "__main__":
    main()
