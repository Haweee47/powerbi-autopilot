"""레이아웃 템플릿(design-system/layouts/layouts.json)을 픽셀 좌표로 풀고, 검사하고, 와이어프레임을 그린다.

- 본문 좌표: x = left + (col-1) × (colWidth + gutter), w = span × colWidth + (span-1) × gutter
- 레일 좌표: x = inner, w = rail.width - 2 × inner (full이면 레일 전체)
- 공통 영역(shared)은 모든 페이지에 들어간다. 페이지의 omit으로 뺄 수 있다
- 검사: 8의 배수, 캔버스 안, 영역끼리 겹침 없음(바탕 레이어 제외), 본문 줄 사이 세로 경계선 공유
- 결과: layouts.resolved.json (생성기가 읽는 좌표), <page>.svg (1280×720 와이어프레임)

사용법: python tools/build_layouts.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "design-system" / "layouts" / "layouts.json"
OUT = SRC.parent

ROLE_COLOR = {  # 와이어프레임 색: 레일 위 요소는 어두운 톤, 데이터 비주얼은 파랑 계열
    "pageNavigator": "#23344D", "actionButton": "#C6CDD5", "textbox": "#E4E8ED", "advancedSlicerVisual": "#23344D",
    "headline": "#E4E8ED", "cardVisual": "#CFE0F5", "lineChart": "#DCE8F8", "barChart": "#DCE8F8", "scatterChart": "#DCE8F8",
    "context": "#E4E8ED", "tableEx": "#E8EEF6", "pivotTable": "#E8EEF6", "decompositionTreeVisual": "#DCE8F8", "dropdownSlicer": "#23344D",
}


def resolve(spec: dict) -> dict:
    g, cv, bands, rail = spec["grid"], spec["canvas"], spec["bands"], spec["rail"]
    col_w = (cv["width"] - g["left"] - g["margin"] - (g["columns"] - 1) * g["gutter"]) / g["columns"]
    if col_w != int(col_w):
        sys.exit(f"열 폭이 정수가 아니다: {col_w}")
    col_w = int(col_w)
    out = {"canvas": cv, "grid": {**g, "colWidth": col_w}, "rail": rail, "bands": bands, "pages": []}
    for page in spec["pages"]:
        regions = []
        shared = [r for r in spec.get("shared", []) if r["id"] not in page.get("omit", [])]
        for r in shared + page["regions"]:
            y, h = (bands[r["band"]]["y"], bands[r["band"]]["h"]) if "band" in r else (r["y"], r["h"])
            if r.get("zone") == "rail":
                x, w = (0, rail["width"]) if r.get("full") else (rail["inner"], rail["width"] - 2 * rail["inner"])
            else:
                x = g["left"] + (r["col"] - 1) * (col_w + g["gutter"])
                w = r["span"] * col_w + (r["span"] - 1) * g["gutter"]
            regions.append({**{k: v for k, v in r.items() if k not in ("band", "full")}, "x": x, "y": y, "width": w, "height": h})
        out["pages"].append({**{k: v for k, v in page.items() if k not in ("regions", "omit")}, "regions": regions})
    return out


def check(page: dict, cv: dict, unit: int, body_y: int) -> list[str]:
    problems, rs = [], page["regions"]
    for r in rs:
        for k in ("x", "y", "width", "height"):
            if r[k] % unit:
                problems.append(f"{r['id']}.{k}={r[k]} 가 {unit}의 배수가 아님")
        if r["x"] + r["width"] > cv["width"] or r["y"] + r["height"] > cv["height"]:
            problems.append(f"{r['id']} 가 캔버스를 벗어남")
    fg = [r for r in rs if r.get("layer") != "background"]
    for i, a in enumerate(fg):
        for b in fg[i + 1:]:
            if a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"] and a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"]:
                problems.append(f"{a['id']} 와 {b['id']} 가 겹침")
    # 세로 경계선: 본문 줄마다 열 경계(x 끝)를 모아, 두 줄 이상에 걸친 경계가 하나라도 공유되는지
    rows: dict[int, set] = {}
    for r in fg:
        if r["y"] >= body_y and r.get("zone") != "rail" and r["span"] < 12:
            rows.setdefault(r["y"], set()).add(r["x"] + r["width"])
    edges = list(rows.values())
    if len(edges) >= 2 and not all(any(e & f for f in edges if f is not e) for e in edges):
        problems.append("본문 줄 사이에 공유하는 세로 경계선이 없음")
    return problems


def svg(page: dict, cv: dict) -> str:
    W, H = cv["width"], cv["height"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Segoe UI, Malgun Gothic, sans-serif">',
             f'<rect width="{W}" height="{H}" fill="#F2F4F7"/>']
    for r in page["regions"]:
        on_rail = r.get("zone") == "rail"
        if r.get("layer") == "background":
            parts.append(f'<rect x="{r["x"]}" y="{r["y"]}" width="{r["width"]}" height="{r["height"]}" fill="#0F1A2A"/>')
            continue
        fill = ROLE_COLOR.get(r["role"], "#E4E8ED")
        parts.append(f'<rect x="{r["x"]}" y="{r["y"]}" width="{r["width"]}" height="{r["height"]}" rx="8" fill="{fill}" stroke="{"#3A4B63" if on_rail else "#8E99A6"}" stroke-width="1"/>')
        ink, ink2 = ("#F2F5F9", "#AEB9C7") if on_rail else ("#14202B", "#4A5563")
        size = 13 if r["height"] >= 56 else 11
        parts.append(f'<text x="{r["x"] + 10}" y="{r["y"] + 20}" font-size="{size}" font-weight="600" fill="{ink}">{r["label"]}</text>')
        if r["height"] >= 56:
            parts.append(f'<text x="{r["x"] + 10}" y="{r["y"] + 38}" font-size="11" fill="{ink2}">{r["role"]} · {r["x"]},{r["y"]} · {r["width"]}×{r["height"]}</text>')
    parts.append(f'<text x="{W - 24}" y="{H - 6}" font-size="11" text-anchor="end" fill="#5A6471">{page["name"]} · {page["archetype"]} — {page["question"]}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    spec = json.load(open(SRC, encoding="utf-8"))
    res = resolve(spec)
    total_problems = 0
    for page in res["pages"]:
        problems = check(page, res["canvas"], res["grid"]["unit"], res["bands"]["body"]["y"])
        total_problems += len(problems)
        status = "통과" if not problems else "문제 " + str(len(problems))
        print(f"[{page['id']}] 영역 {len(page['regions'])}개 · {status}")
        for p in problems:
            print("   -", p)
        (OUT / f"{page['id']}.svg").write_text(svg(page, res["canvas"]), encoding="utf-8")
    json.dump(res, open(OUT / "layouts.resolved.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"열 폭 {res['grid']['colWidth']}px · 문제 {total_problems}건 · 결과: layouts.resolved.json, *.svg")
    sys.exit(1 if total_problems else 0)


if __name__ == "__main__":
    main()
