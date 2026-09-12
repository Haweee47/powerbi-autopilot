"""레이아웃 템플릿(design-system/layouts/layouts.json)을 픽셀 좌표로 풀고, 검사하고, 와이어프레임을 그린다.

- 좌표 계산: x = margin + (col-1) × (colWidth + gutter), w = span × colWidth + (span-1) × gutter
- 검사: 8의 배수, 캔버스 안, 영역끼리 겹침 없음, 세로 경계선 연속성(페이지 안 줄마다 공유하는 열 경계)
- 결과: layouts.resolved.json (생성기가 읽는 좌표), <page>.svg (1280×720 와이어프레임)

사용법: python tools/build_layouts.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "design-system" / "layouts" / "layouts.json"
OUT = SRC.parent

ROLE_COLOR = {  # 와이어프레임 색: 이동·헤더는 회색, 데이터 비주얼은 파랑 계열
    "pageNavigator": "#C6CDD5", "actionButton": "#C6CDD5", "textbox": "#E4E8ED", "advancedSlicerVisual": "#D5DCE4",
    "cardVisual": "#CFE0F5", "lineChart": "#DCE8F8", "barChart": "#DCE8F8", "scatterChart": "#DCE8F8", "tableEx": "#E8EEF6",
}


def resolve(spec: dict) -> dict:
    g, cv, bands = spec["grid"], spec["canvas"], spec["bands"]
    col_w = (cv["width"] - 2 * g["margin"] - (g["columns"] - 1) * g["gutter"]) / g["columns"]
    if col_w != int(col_w):
        sys.exit(f"열 폭이 정수가 아니다: {col_w}")
    col_w = int(col_w)
    out = {"canvas": cv, "grid": {**g, "colWidth": col_w}, "pages": []}
    for page in spec["pages"]:
        regions = []
        for r in page["regions"]:
            y, h = (bands[r["band"]]["y"], bands[r["band"]]["h"]) if "band" in r else (r["y"], r["h"])
            x = g["margin"] + (r["col"] - 1) * (col_w + g["gutter"])
            w = r["span"] * col_w + (r["span"] - 1) * g["gutter"]
            regions.append({**{k: v for k, v in r.items() if k not in ("band",)}, "x": x, "y": y, "width": w, "height": h})
        out["pages"].append({**{k: v for k, v in page.items() if k != "regions"}, "regions": regions})
    return out


def check(page: dict, cv: dict, unit: int) -> list[str]:
    problems, rs = [], page["regions"]
    for r in rs:
        for k in ("x", "y", "width", "height"):
            if r[k] % unit:
                problems.append(f"{r['id']}.{k}={r[k]} 가 {unit}의 배수가 아님")
        if r["x"] + r["width"] > cv["width"] or r["y"] + r["height"] > cv["height"]:
            problems.append(f"{r['id']} 가 캔버스를 벗어남")
    for i, a in enumerate(rs):
        for b in rs[i + 1:]:
            if a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"] and a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"]:
                problems.append(f"{a['id']} 와 {b['id']} 가 겹침")
    # 세로 경계선: 본문(y ≥ 144)의 줄마다 열 경계(x 끝)를 모아, 두 줄 이상에 걸친 경계가 하나라도 공유되는지
    rows: dict[int, set] = {}
    for r in rs:
        if r["y"] >= 144 and r["width"] < cv["width"] - 48:
            rows.setdefault(r["y"], set()).add(r["x"] + r["width"])
    edges = list(rows.values())
    if len(edges) >= 2 and not all(e & edges[0] or any(e & f for f in edges if f is not e) for e in edges):
        problems.append("본문 줄 사이에 공유하는 세로 경계선이 없음")
    return problems


def svg(page: dict, cv: dict) -> str:
    W, H = cv["width"], cv["height"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Segoe UI, Malgun Gothic, sans-serif">',
             f'<rect width="{W}" height="{H}" fill="#EEF1F5"/>']
    for r in page["regions"]:
        fill = ROLE_COLOR.get(r["role"], "#E4E8ED")
        parts.append(f'<rect x="{r["x"]}" y="{r["y"]}" width="{r["width"]}" height="{r["height"]}" rx="8" fill="{fill}" stroke="#8E99A6" stroke-width="1"/>')
        size = 13 if r["height"] >= 56 else 11
        parts.append(f'<text x="{r["x"] + 10}" y="{r["y"] + 20}" font-size="{size}" font-weight="600" fill="#14202B">{r["label"]}</text>')
        if r["height"] >= 56:
            parts.append(f'<text x="{r["x"] + 10}" y="{r["y"] + 38}" font-size="11" fill="#4A5563">{r["role"]} · {r["x"]},{r["y"]} · {r["width"]}×{r["height"]}</text>')
    parts.append(f'<text x="{W - 24}" y="{H - 6}" font-size="11" text-anchor="end" fill="#5A6471">{page["name"]} · {page["archetype"]} — {page["question"]}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    spec = json.load(open(SRC, encoding="utf-8"))
    res = resolve(spec)
    total_problems = 0
    for page in res["pages"]:
        problems = check(page, res["canvas"], res["grid"]["unit"])
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
