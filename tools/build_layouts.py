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


SLICERS = ("advancedSlicerVisual", "dropdownSlicer")


def to_top(page: dict, res: dict, top: dict) -> dict:
    """The same page in the top-bar frame. Rail regions move into the bar, grid regions get the wider columns,
    the first body row starts 8px lower (and is 8px shorter), and every later row keeps its rail position and height."""
    cv, g, rb, tb = res["canvas"], res["grid"], res["bands"], top["bands"]
    unit, gut = g["unit"], g["gutter"]
    col_w = (cv["width"] - top["left"] - g["margin"] - (g["columns"] - 1) * gut) // g["columns"]
    bar_h, pad = top["bar"]["h"], top["bar"]["inner"]
    inner_h = bar_h - 2 * pad
    rail = [r for r in page["regions"] if r.get("zone") == "rail"]
    placed, labels, x = {}, [], cv["width"] - g["margin"]
    for r in sorted((r for r in rail if r["role"] in SLICERS), key=lambda r: r["y"], reverse=True):
        w = top["slicerWidth"].get(r["id"], top["slicerWidth"]["default"])
        x -= w
        # the validator wants a dropdown slicer at least 48px tall (selector 32 + padding), so it takes the bar's full height
        placed[r["id"]] = (x, 0, w, bar_h) if r["role"] == "dropdownSlicer" else (x, pad, w, inner_h)
        if r["role"] == "dropdownSlicer":  # a dropdown shows only its value ("All"), so it gets a name on its left
            x -= top["labelWidth"]
            labels.append({"id": f"{r['id']}_label", "role": "textbox", "zone": "rail", "bar": True, "labelFor": r["id"],
                           "label": "slicer name", "x": x, "y": pad, "width": top["labelWidth"] - unit, "height": inner_h - unit})
        x -= gut
    nav_x = top["brand"]["x"] + top["brand"]["w"] + 3 * unit
    nav_w = (x - nav_x) // unit * unit
    first_row = min(r["y"] for r in page["regions"] if r.get("zone") != "rail" and r["y"] >= rb["body"]["y"])
    regions = []
    for r in page["regions"]:
        r = dict(r)
        if r.get("zone") == "rail":
            if r["id"] == "asof":
                continue  # the generator puts the as-of date under the report name
            if r["id"] in placed:
                box = placed[r["id"]]
            elif r["role"] == "shape":
                box = (0, 0, cv["width"], bar_h)
            elif r["id"] == "brand":
                box = (top["brand"]["x"], pad, top["brand"]["w"], bar_h - pad)
            elif r["role"] == "pageNavigator":
                box = (nav_x, pad, nav_w, top["nav"]["h"])
            else:
                sys.exit(f"{page['id']}: no place in the top bar for rail region {r['id']}")
            r.update(bar=True)
        else:
            bx = top["left"] + (r["col"] - 1) * (col_w + gut)
            bw = r["span"] * col_w + (r["span"] - 1) * gut
            if r["y"] == rb["title"]["y"]:
                by, bh = tb["title"]["y"], tb["title"]["h"]
            elif r["y"] == rb["headline"]["y"]:
                by, bh = tb["headline"]["y"], tb["headline"]["h"]
            elif r["y"] == first_row:
                by, bh = r["y"] + tb["firstRow"], r["height"] - tb["firstRow"]
            else:
                by, bh = r["y"], r["height"]
            box = (bx, by, bw, bh)
        r.update(x=box[0], y=box[1], width=box[2], height=box[3])
        regions.append(r)
    return {**page, "frame": "top", "regions": regions + labels}


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
    res["frames"] = {"rail": res["pages"], "top": [to_top(p, res, spec["top"]) for p in res["pages"]]}
    for frame, pages in res["frames"].items():
        body_y = res["bands"]["body"]["y"]
        for page in pages:
            problems = check(page, res["canvas"], res["grid"]["unit"], body_y)
            total_problems += len(problems)
            status = "통과" if not problems else "문제 " + str(len(problems))
            print(f"[{frame}/{page['id']}] 영역 {len(page['regions'])}개 · {status}")
            for p in problems:
                print("   -", p)
            suffix = "" if frame == "rail" else f".{frame}"
            (OUT / f"{page['id']}{suffix}.svg").write_text(svg(page, res["canvas"]), encoding="utf-8")
    json.dump(res, open(OUT / "layouts.resolved.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"열 폭 {res['grid']['colWidth']}px · 문제 {total_problems}건 · 결과: layouts.resolved.json, *.svg")
    sys.exit(1 if total_problems else 0)


if __name__ == "__main__":
    main()
