"""디자인 토큰(design-system/tokens.json) 하나로 Power BI 테마(밝은·어두운)와 CSS 변수를 만들고, 공식 스키마로 검증한다.

왜: 색·글자·간격을 테마 JSON, HTML 시안, 문서에 따로 적으면 반드시 어긋난다. 원본을 하나로 두고 나머지는 생성한다.
또 서식을 테마에 모아 두면 visual.json에는 위치와 필드만 남는다 (토큰 절약).

속성 이름·허용값은 기억이 아니라 `powerbi-report-author formatting describe-object/describe-property`로 확인한 것만 쓴다.
검증 스키마: microsoft/powerbi-desktop-samples 의 reportThemeSchema-2.157.json (Desktop 2.157과 같은 버전)

사용법: python tools/build_themes.py [--schema <로컬 스키마 경로>]
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DS = ROOT / "design-system"
SCHEMA_VERSION = "2.157"
SCHEMA_URL = ("https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/"
              f"Report%20Theme%20JSON%20Schema/reportThemeSchema-{SCHEMA_VERSION}.json")
CACHE = ROOT / "research" / "collected" / "_cache" / f"reportThemeSchema-{SCHEMA_VERSION}.json"


def solid(hex_color: str) -> dict:
    return {"solid": {"color": hex_color}}


def zero_padding() -> list:
    return [{"top": 0, "bottom": 0, "left": 0, "right": 0}]


def build(tok: dict, mode: str) -> dict:
    c, T, S = tok["color"][mode], tok["type"]["pt"], tok["space"]
    F, FS = tok["font"]["family"], tok["font"]["semibold"]
    ink, ink2, ink3 = solid(c["ink"]), solid(c["ink2"]), solid(c["ink3"])

    axis_common = {"fontFamily": F, "fontSize": T["caption"], "labelColor": ink3, "showAxisTitle": False}
    value_axis = {**axis_common, "gridlineShow": True, "gridlineStyle": "solid", "gridlineColor": solid(c["grid"]), "gridlineThickness": 1}
    category_axis = {**axis_common, "gridlineShow": False}
    legend_top = {"show": True, "position": "Top", "fontFamily": F, "fontSize": T["caption"], "labelColor": ink2, "showTitle": False}

    # 막대: 값은 막대 끝 레이블로 읽고 값 축은 숨긴다. innerPadding을 넓혀 막대를 얇게 (dataviz: 두꺼운 덩어리 금지)
    bar_like = {
        "categoryAxis": [{**category_axis, "fontSize": T["body"], "labelColor": ink2, "innerPadding": 40}],
        "valueAxis": [{"show": False, "gridlineShow": False, "showAxisTitle": False}],
        "labels": [{"show": True, "fontSize": T["caption"], "color": ink2, "fontFamily": F}],
        "dataPoint": [{"borderShow": False}],
        "legend": [{"show": False}],
    }
    # 표: 가로 줄만, 줄무늬 없음, 머리글은 흐린 글자 (principles 5절)
    table = {
        "grid": [{"gridVertical": False, "gridHorizontal": True, "gridHorizontalColor": solid(c["grid"]), "gridHorizontalWeight": 1,
                  "rowPadding": 6, "outlineColor": solid(c["grid"])}],
        "columnHeaders": [{"fontFamily": F, "fontSize": T["caption"], "bold": True, "fontColor": ink3, "backColor": solid(c["surface"]),
                           "autoSizeColumnWidth": True, "columnAdjustment": "growToFit", "wordWrap": False}],
        "values": [{"fontFamily": F, "fontSize": T["body"], "fontColorPrimary": ink, "backColorPrimary": solid(c["surface"]),
                    "fontColorSecondary": ink, "backColorSecondary": solid(c["surface"])}],
        "total": [{"fontFamily": F, "fontSize": T["body"], "bold": True, "fontColor": ink, "backColor": solid(c["surface"])}],
    }
    states = lambda default, hover, selected: [{"$id": "default", **default}, {"$id": "hover", **hover}, {"$id": "selected", **selected}]
    slicer_states = lambda default, hover, selected: [{"$id": "default", **default}, {"$id": "hover", **hover}, {"$id": "selection:selected", **selected}]

    return {
        "$schema": SCHEMA_URL,
        "name": f"Autopilot {mode.title()}",
        "dataColors": tok["categorical"][mode],
        "good": c["pos"], "neutral": c["context"], "bad": c["neg"],
        "maximum": c["pos"], "center": c["mid"], "minimum": c["neg"], "null": c["context"],
        # 구조 색은 어두운 테마에서 한꺼번에 바꿔야 글자가 사라지지 않는다 (MS theming 문서)
        "foreground": c["ink"], "firstLevelElements": c["ink"],
        "secondLevelElements": c["ink2"], "foregroundNeutralSecondary": c["ink2"],
        "thirdLevelElements": c["grid"], "backgroundLight": c["grid"],
        "fourthLevelElements": c["ink3"], "foregroundNeutralTertiary": c["ink3"],
        "background": c["surface"], "secondaryBackground": c["axis"], "backgroundNeutral": c["axis"],
        "tableAccent": c["axis"], "hyperlink": c["posInk"], "visitedHyperlink": c["posInk"],
        "textClasses": {
            "callout": {"fontSize": T["kpi"], "fontFace": F, "color": c["ink"]},
            "title": {"fontSize": T["title"], "fontFace": F, "color": c["ink"]},
            "header": {"fontSize": T["body"], "fontFace": FS, "color": c["ink"]},
            "label": {"fontSize": T["caption"], "fontFace": F, "color": c["ink"]},
        },
        "visualStyles": {
            "*": {"*": {
                # 흰 카드 + 둥근 모서리 + 테두리·그림자 없음. 카드와 같은 색의 테두리로 모서리만 둥글게 한다
                "background": [{"show": True, "color": solid(c["surface"]), "transparency": 0}],
                "border": [{"show": True, "color": solid(c["surface"]), "radius": S["radius"], "width": 1}],
                "dropShadow": [{"show": False}],
                "padding": [{"top": S["padding"], "bottom": S["padding"], "left": S["padding"], "right": S["padding"]}],
                "title": [{"show": True, "fontFamily": FS, "fontSize": T["title"], "bold": False, "fontColor": ink, "alignment": "left", "titleWrap": True}],
                "subTitle": [{"fontFamily": F, "fontSize": T["caption"], "fontColor": ink3, "alignment": "left"}],
                "valueAxis": [value_axis],
                "categoryAxis": [category_axis],
                "legend": [legend_top],
            }},
            # 필터 창은 구조 색을 따르지 않으므로 직접 지정한다.
            # MS 문서 예시는 "*"에 두지만 공식 CLI 검증은 "*"의 outspacePane·filterCard를 모르는 객체로 거부해서 페이지 쪽에 둔다
            "page": {"*": {
                "background": [{"color": solid(c["page"]), "transparency": 0}],
                "outspace": [{"color": solid(c["page"]), "transparency": 0}],
                "outspacePane": [{"backgroundColor": solid(c["surface"]), "foregroundColor": ink, "titleSize": T["title"], "border": True,
                                  "borderColor": solid(c["grid"]), "checkboxAndApplyColor": solid(c["accent"]), "inputBoxColor": solid(c["surface"])}],
                "filterCard": [
                    {"$id": "Applied", "backgroundColor": solid(c["page"]), "foregroundColor": ink, "border": True, "borderColor": solid(c["grid"])},
                    {"$id": "Available", "backgroundColor": solid(c["surface"]), "foregroundColor": ink, "border": True, "borderColor": solid(c["grid"])},
                ],
            }},
            # 헤더 글은 페이지 바탕 위에 바로 놓인다
            "textbox": {"*": {"background": [{"show": False}], "border": [{"show": False}], "padding": zero_padding(), "title": [{"show": False}]}},
            "cardVisual": {"*": {
                "value": [{"$id": "default", "fontFamily": F, "fontSize": T["kpi"], "bold": True, "fontColor": ink}],
                "label": [{"$id": "default", "show": True, "position": "aboveValue", "fontFamily": F, "fontSize": T["body"], "fontColor": ink2}],
                "title": [{"show": False}],
                # MS 디자인 스킬 base.json의 카드 안전장치 (값 잘림 방지).
                # 같은 파일의 spacing.customizeSpacing은 공식 CLI 검증에서 모르는 속성이라 뺐다
                "cardCalloutArea": [{"paddingUniform": 0}],
            }},
            "lineChart": {"*": {
                "lineStyles": [{"strokeWidth": 2, "lineChartType": "linear", "showMarker": False, "areaShow": False}],
                "labels": [{"show": False}],
                "valueAxis": [value_axis], "categoryAxis": [category_axis], "legend": [legend_top],
            }},
            "barChart": {"*": bar_like},
            "columnChart": {"*": bar_like},
            "clusteredBarChart": {"*": {**bar_like, "legend": [legend_top]}},
            "clusteredColumnChart": {"*": {**bar_like, "legend": [legend_top]}},
            "scatterChart": {"*": {"valueAxis": [value_axis], "categoryAxis": [{**value_axis}], "legend": [legend_top]}},
            "tableEx": {"*": table},
            "pivotTable": {"*": table},
            # 페이지 선택기: 선택된 탭만 흰 카드, 나머지는 페이지 바탕 (HTML 시안의 상단 탭)
            "pageNavigator": {"*": {
                "fill": states({"show": True, "fillColor": solid(c["page"]), "transparency": 0},
                               {"show": True, "fillColor": solid(c["hover"]), "transparency": 0},
                               {"show": True, "fillColor": solid(c["surface"]), "transparency": 0}),
                "text": states({"show": True, "fontFamily": FS, "fontSize": T["body"], "fontColor": ink2},
                               {"fontColor": ink}, {"fontColor": ink}),
                "outline": states({"show": False}, {"show": False}, {"show": False}),
                "background": [{"show": False}], "border": [{"show": False}], "padding": zero_padding(), "title": [{"show": False}],
            }},
            # 버튼 슬라이서: 회색 틀 안에서 선택된 값만 흰색 (HTML 시안의 기간·채널 버튼)
            # 주의: 선택 상태 이름이 PBIR(CLI)은 "selected", 테마 스키마는 "selection:selected"다
            "advancedSlicerVisual": {"*": {
                "background": slicer_states({"show": True, "color": solid(c["segBg"]), "transparency": 0},
                                            {"show": True, "color": solid(c["hover"]), "transparency": 0},
                                            {"show": True, "color": solid(c["segOn"]), "transparency": 0}),
                "label": slicer_states({"fontFamily": FS, "fontSize": T["body"], "fontColor": ink2}, {"fontColor": ink}, {"fontColor": ink}),
                "outline": slicer_states({"show": False}, {"show": False}, {"show": False}),
            }},
        },
    }


def css(tok: dict) -> str:
    def block(mode):
        c = tok["color"][mode]
        return "\n".join(f"  --{k}: {v};" for k, v in c.items())
    px = tok["type"]["px"]
    fs = "\n".join(f"  --fs-{k}: {v}px;" for k, v in px.items())
    return (f"/* tools/build_themes.py가 design-system/tokens.json에서 생성. 직접 고치지 말 것 */\n"
            f":root {{\n  color-scheme: light;\n{block('light')}\n{fs}\n  --radius: {tok['space']['radius']}px;\n}}\n"
            f"@media (prefers-color-scheme: dark) {{\n  :root:not([data-theme=\"light\"]) {{\n  color-scheme: dark;\n{block('dark')}\n  }}\n}}\n"
            f":root[data-theme=\"dark\"] {{\n  color-scheme: dark;\n{block('dark')}\n}}\n")


def load_schema(path: str | None) -> dict:
    p = Path(path) if path else CACHE
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        print(f"스키마 내려받는 중: {SCHEMA_URL}")
        urllib.request.urlretrieve(SCHEMA_URL, p)
    return json.load(open(p, encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", help="로컬 reportThemeSchema 경로 (없으면 내려받아 캐시)")
    args = ap.parse_args()
    tok = json.load(open(DS / "tokens.json", encoding="utf-8"))
    import jsonschema
    schema = load_schema(args.schema)
    validator = jsonschema.validators.validator_for(schema)(schema)
    out_dir = DS / "themes"
    out_dir.mkdir(exist_ok=True)
    failed = 0
    for mode in ("light", "dark"):
        theme = build(tok, mode)
        errors = sorted(validator.iter_errors(theme), key=lambda e: list(e.absolute_path))
        path = out_dir / f"autopilot-{mode}.json"
        path.write_text(json.dumps(theme, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        size = path.stat().st_size
        print(f"[{mode}] {path.relative_to(ROOT)} · {size / 1024:.1f}KB · 스키마 {SCHEMA_VERSION} 검증: {'통과' if not errors else f'오류 {len(errors)}건'}")
        for e in errors[:15]:
            print(f"   - {'/'.join(map(str, e.absolute_path))}: {e.message[:160]}")
        failed += len(errors)
    (DS / "tokens.css").write_text(css(tok), encoding="utf-8")
    print("CSS 변수: design-system/tokens.css")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
