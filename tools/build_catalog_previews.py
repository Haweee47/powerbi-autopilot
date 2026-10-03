"""카탈로그의 선택지마다 '미리보기'를 채운다.

왜 있나: 새 리포트를 만들 때 에이전트는 용도·테마·언어·배치를 먼저 묻는다. 그런데 글자만 주면
"navy 와 coast 중 뭐가 다른지" 알 수 없어서, 결국 만들어 본 뒤에야 고르게 된다.
선택지마다 실제 모양과 색을 함께 보여 주면 묻는 자리에서 바로 고를 수 있다.

지어내지 않는다: 와이어프레임은 `layouts.resolved.json`의 실제 좌표에서, 색은 `tokens.json`에서 읽는다.
레이아웃이나 테마가 바뀌면 이 스크립트를 다시 돌려야 하고, CI(check.py)가 안 맞으면 실패시킨다.

    python tools/build_catalog_previews.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CAT = ROOT / "templates" / "catalog.json"

# 화면 틀은 본문 비주얼이 아니다 (레일 바탕·제목·이동·버튼·슬라이서)
CHROME = {"shape", "textbox", "pageNavigator", "actionButton", "headline", "context",
          "advancedSlicerVisual", "dropdownSlicer"}
SHORT = {"cardVisual": "KPI", "lineChart": "line", "barChart": "bars", "columnChart": "cols",
         "scatterChart": "dots", "tableEx": "table", "pivotTable": "matrix",
         "decompositionTreeVisual": "tree"}
COLS = 46   # 와이어프레임 한 줄 글자 수. 터미널 선택지 안에 들어가는 폭


def wireframe(page: dict, rail: bool = True) -> str:
    """영역 좌표를 글자 격자로 줄여 그린다. 칸 안의 글자는 그 자리에 실제로 오는 비주얼이다.

    글자는 ASCII만 쓴다. 윈도우 기본 콘솔(cp949)에서 괘선 문자가 깨지기 때문이다.
    """
    body = [r for r in page["regions"]
            if r.get("zone") != "rail" and r.get("layer") != "background" and r["role"] not in CHROME]
    if not body:
        return ""
    rails = 4 if rail else 0
    inner = COLS - 2 - rails - (1 if rail else 0)
    x0 = min(r["x"] for r in body)
    x1 = max(r["x"] + r["width"] for r in body)
    rows: dict[int, list] = {}
    for r in sorted(body, key=lambda r: (r["y"], r["x"])):
        rows.setdefault(r["y"], []).append(r)

    out = ["+" + ("-" * rails + "+" if rail else "") + "-" * inner + "+"]
    for y in sorted(rows):
        cells = []
        for r in rows[y]:
            w = max(round((r["width"]) / (x1 - x0) * inner), 5)
            lab = SHORT.get(r["role"], r["role"][:5])
            cells.append(lab.center(w - 1)[:w - 1] + "|")
        line = "".join(cells)
        line = (line[:inner - 1] + "|") if len(line) > inner else line + " " * (inner - len(line))
        out.append("|" + ("::: |" if rail else "") + line[:inner] + "|")
    out.append("+" + ("-" * rails + "+" if rail else "") + "-" * inner + "+")
    return "\n".join(out)


def main() -> None:
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    tok = json.loads((DS / "tokens.json").read_text(encoding="utf-8"))
    res = json.loads((DS / "layouts" / "layouts.resolved.json").read_text(encoding="utf-8"))
    pages = {p["id"]: p for p in res["pages"]}
    specs = {p["id"]: json.loads((ROOT / "templates" / p["id"] / "pilot.spec.json").read_text(encoding="utf-8"))
             for p in cat["purposes"] if (ROOT / "templates" / p["id"] / "pilot.spec.json").exists()}

    for p in cat["purposes"]:
        spec = specs.get(p["id"])
        if not spec:
            continue
        first = spec["pages"][0]["layout"]
        shown = [pg for pg in spec["pages"] if not pg.get("hidden")]
        hidden = len(spec["pages"]) - len(shown)
        # 비주얼 수는 적지 않는다. 명세에 적힌 수와 화면에 뜨는 수(레일까지 더해진 것)가 달라 오해를 부른다
        p["preview"] = (wireframe(pages[first]) + "\n"
                        + f"{len(shown)} pages"
                        + (f" (+{hidden} drillthrough)" if hidden else "")
                        + f", first page: {first}")

    styles = tok["styles"]
    for t in cat["themes"]:
        th = tok["themes"][t["id"]]
        c = th["color"]
        st = th.get("style", "soft")
        shape = {"soft": "soft: 12px corners, hairline, faint shadow",
                 "bold": "bold: 16px corners, no border, deeper shadow",
                 "flat": "flat: square corners, hairlines, no shadow"}.get(st, st)
        face = tok.get("typefaces", {}).get(th.get("typeface", ""), {}).get("name", "Segoe")
        t["preview"] = (f"rail {c['rail']}   page {c['page']}   accent {c['accent']}\n"
                        f"cards  {shape}\n"
                        f"type   {face}\n"
                        f"fits   {t['when']['en']}")

    summary = pages["summary"]
    for f in cat["frames"]:
        f["preview"] = (wireframe(summary, rail=(f["id"] == "rail")) + "\n"
                        + ("left rail 192px · body 1040px" if f["id"] == "rail"
                           else "top bar 48px · body full width 1088px"))

    CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{CAT.relative_to(ROOT)}: previews for "
          f"{len(cat['purposes'])} purposes, {len(cat['themes'])} themes, {len(cat['frames'])} frames")


if __name__ == "__main__":
    main()
