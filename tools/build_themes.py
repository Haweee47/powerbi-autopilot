"""디자인 토큰(design-system/tokens.json) 하나로 Power BI 테마(밝은·어두운)와 CSS 변수를 만들고, 공식 스키마로 검증한다.

왜: 색·글자·간격을 테마 JSON, HTML 시안, 문서에 따로 적으면 반드시 어긋난다. 원본을 하나로 두고 나머지는 생성한다.
또 서식을 테마에 모아 두면 visual.json에는 위치와 필드만 남는다 (토큰 절약).

v3 (앱형): 페이지 선택기·슬라이서는 모두 왼쪽 어두운 레일 위에 있다고 보고 레일 색으로 칠한다.
본문 카드는 흰 바탕 + 머리카락 두께 테두리 + 거의 안 보이는 그림자.

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


def bare() -> dict:
    """바탕·테두리·그림자·제목·여백이 없는 컨테이너 (레일 위 요소, 글상자)."""
    return {"background": [{"show": False}], "border": [{"show": False}], "dropShadow": [{"show": False}],
            "padding": zero_padding(), "title": [{"show": False}]}


def build(tok: dict, mode: str) -> dict:
    c, T, S, SH = tok["color"][mode], tok["type"]["pt"], tok["space"], tok["shadow"]
    F, FS = tok["font"]["family"], tok["font"]["semibold"]
    ink, ink2, ink3 = solid(c["ink"]), solid(c["ink2"]), solid(c["ink3"])

    axis_common = {"fontFamily": F, "fontSize": T["caption"], "labelColor": ink3, "showAxisTitle": False}
    # labelDisplayUnits 1 = 자동 단위 끄기. 단위(억·만)는 측정값 서식이 붙이므로, 켜 두면 "40천만"처럼 두 번 붙는다 (Desktop 캡처로 확인)
    value_axis = {**axis_common, "gridlineShow": True, "gridlineStyle": "solid", "gridlineColor": solid(c["grid"]), "gridlineThickness": 1,
                  "labelDisplayUnits": 1}
    category_axis = {**axis_common, "gridlineShow": False}
    legend_top = {"show": True, "position": "Top", "fontFamily": F, "fontSize": T["caption"], "labelColor": ink2, "showTitle": False}

    # 막대: 값은 막대 끝 레이블로 읽고 값 축은 숨긴다. innerPadding을 넓혀 막대를 얇게 (dataviz: 두꺼운 덩어리 금지)
    bar_like = {
        # preferredCategoryWidth: 기본 최소 폭이면 항목 7개가 카드 높이를 넘어 스크롤바가 생긴다 (Desktop 캡처로 확인)
        "categoryAxis": [{**category_axis, "fontSize": T["body"], "labelColor": ink2, "innerPadding": 45, "preferredCategoryWidth": 16}],
        "valueAxis": [{"show": False, "gridlineShow": False, "showAxisTitle": False}],
        "labels": [{"show": True, "fontSize": T["caption"], "color": ink2, "fontFamily": F, "labelDisplayUnits": 1}],
        "dataPoint": [{"borderShow": False}],
        "legend": [{"show": False}],
    }
    # 표: 가로 줄만, 줄무늬 없음, 머리글은 흐린 글자 (principles 5절)
    table = {
        "grid": [{"gridVertical": False, "gridHorizontal": True, "gridHorizontalColor": solid(c["grid"]), "gridHorizontalWeight": 1,
                  "rowPadding": 8, "outlineColor": solid(c["grid"])}],
        "columnHeaders": [{"fontFamily": FS, "fontSize": T["caption"], "bold": False, "fontColor": ink3, "backColor": solid(c["surface"]),
                           "autoSizeColumnWidth": True, "columnAdjustment": "growToFit", "wordWrap": False}],
        "values": [{"fontFamily": F, "fontSize": T["body"], "fontColorPrimary": ink, "backColorPrimary": solid(c["surface"]),
                    "fontColorSecondary": ink, "backColorSecondary": solid(c["surface"])}],
        "total": [{"fontFamily": FS, "fontSize": T["body"], "bold": False, "fontColor": ink, "backColor": solid(c["surface"])}],
    }
    nav_states = lambda d, h, s: [{"$id": "default", **d}, {"$id": "hover", **h}, {"$id": "selected", **s}]
    # 주의: 슬라이서 선택 상태 이름이 PBIR(CLI)은 "selected", 테마 스키마는 "selection:selected"다
    seg_states = lambda d, h, s: [{"$id": "default", **d}, {"$id": "hover", **h}, {"$id": "selection:selected", **s}]

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
            "callout": {"fontSize": T["kpi"], "fontFace": FS, "color": c["ink"]},
            "title": {"fontSize": T["title"], "fontFace": FS, "color": c["ink"]},
            "header": {"fontSize": T["body"], "fontFace": FS, "color": c["ink"]},
            "label": {"fontSize": T["caption"], "fontFace": F, "color": c["ink"]},
        },
        "visualStyles": {
            "*": {"*": {
                # 흰 카드 + 머리카락 두께 테두리 + 거의 안 보이는 그림자: "종이 한 장" 정도의 깊이
                "background": [{"show": True, "color": solid(c["surface"]), "transparency": 0}],
                "border": [{"show": True, "color": solid(c["border"]), "radius": S["radius"], "width": 1}],
                "dropShadow": [{"show": True, "preset": "Custom", "position": "Outer", "color": solid(c["ink"]),
                                "transparency": SH["transparency"], "shadowBlur": SH["blur"], "shadowDistance": SH["distance"],
                                "shadowSpread": SH["spread"], "angle": 90}],
                "padding": [{"top": S["padding"], "bottom": S["padding"], "left": S["padding"] + 4, "right": S["padding"] + 4}],
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
            # 글상자: 페이지 바탕이나 레일 위에 바로 놓인다 (글자색은 생성기가 자리에 맞춰 넣는다)
            "textbox": {"*": bare()},
            # 도형은 레일 바탕 한 곳에만 쓴다
            "shape": {"*": {
                **bare(),
                "fill": [{"$id": "default", "show": True, "fillColor": solid(c["rail"]), "transparency": 0}],
                "outline": [{"$id": "default", "show": False}],
            }},
            "cardVisual": {"*": {
                # KPI: 왼쪽 정렬, 작은 이름 → 큰 숫자 → 비교 문구. 단위는 측정값 서식이 붙인다 (자동 단위를 끄지 않으면 1,234건이 "1.2천")
                "value": [{"$id": "default", "fontFamily": FS, "fontSize": T["kpi"], "bold": False, "fontColor": ink,
                           "labelDisplayUnits": 1, "horizontalAlignment": "left"}],  # CLI는 문자열 열거형으로 보여 주지만 테마 스키마는 정수
                # 이름·숫자·비교 문구 세 줄이 카드 안(높이 − 여백 32)에 들어가야 한다. 104px 카드에서 숫자 위가 잘려 112px + 9pt로 맞췄다
                "label": [{"$id": "default", "show": True, "position": "aboveValue", "fontFamily": F, "fontSize": T["caption"], "fontColor": ink3}],
                # 비교 문구("전년 대비 ▲12.3%")는 측정값이 통째로 만든다 → 제목은 숨긴다. 색은 생성기가 부호에 맞춰 넣는다
                "referenceLabelTitle": [{"$id": "default", "show": False}],
                "referenceLabelValue": [{"$id": "default", "valueFontFamily": FS, "valueFontSize": T["body"], "valueFontColor": ink2}],
                "referenceLabelLayout": [{"position": "below", "horizontalAlignment": "left"}],
                # 기본값은 회색 상자 + 안쪽 여백이라 카드에서 값이 위로 밀려 잘렸다 (Desktop 캡처로 확인)
                # $id 없이 두면 적용되지 않았다 (Desktop이 쓰는 형식도 selector id "default")
                "referenceLabel": [{"$id": "default", "backgroundShow": False, "paddingUniform": 0}],
                "divider": [{"$id": "default", "show": False}],
                "title": [{"show": False}],
                # 카드 안쪽 기본 윤곽선: 흰 카드 안에 상자가 하나 더 보여 끈다 (Desktop 캡처로 확인)
                "outline": [{"$id": "default", "show": False}],
                # MS 디자인 스킬 base.json의 카드 안전장치 (값 잘림 방지).
                # 같은 파일의 spacing.customizeSpacing은 공식 CLI 검증에서 모르는 속성이라 뺐다
                "cardCalloutArea": [{"paddingUniform": 0}],
            }},
            "lineChart": {"*": {
                "lineStyles": [{"strokeWidth": 2, "lineChartType": "linear", "showMarker": False, "areaShow": False}],
                "labels": [{"show": False}],
                # 작은 여러 차트 칸이 좁으면 월 축에 가로 스크롤이 생겼다 → 최소 항목 폭을 줄인다 (Desktop 캡처로 확인)
                "valueAxis": [value_axis], "categoryAxis": [{**category_axis, "preferredCategoryWidth": 12}], "legend": [legend_top],
                "smallMultiplesLayout": [{"gridLineShow": False}],
                "subheader": [{"fontFamily": FS, "fontSize": T["body"], "fontColor": ink2}],  # 작은 여러 차트 칸 제목 (기본값은 너무 크다)
            }},
            "barChart": {"*": bar_like},
            "columnChart": {"*": bar_like},
            "clusteredBarChart": {"*": {**bar_like, "legend": [legend_top]}},
            "clusteredColumnChart": {"*": {**bar_like, "legend": [legend_top]}},
            "scatterChart": {"*": {"valueAxis": [value_axis], "categoryAxis": [{**value_axis}], "legend": [legend_top]}},
            "tableEx": {"*": table},
            "pivotTable": {"*": table},
            # 페이지 선택기 (레일): 세로 목록. 선택된 페이지만 밝은 바탕 + 왼쪽 강조 막대
            "pageNavigator": {"*": {
                **bare(),
                # 기본 상태를 show False로 두면 흰 칸이 그대로 남았다 → 레일과 같은 색으로 칠해 보이지 않게
                "fill": nav_states({"show": True, "fillColor": solid(c["rail"]), "transparency": 0},
                                   {"show": True, "fillColor": solid(c["railHover"]), "transparency": 0},
                                   {"show": True, "fillColor": solid(c["railOn"]), "transparency": 0}),
                "text": nav_states({"show": True, "fontFamily": F, "fontSize": T["body"], "fontColor": solid(c["railInk2"]),
                                    "horizontalAlignment": "left", "leftMargin": 14},
                                   {"fontColor": solid(c["railInk"])}, {"fontFamily": FS, "fontColor": solid(c["railInk"])}),
                "accentBar": nav_states({"show": False}, {"show": False},
                                        {"show": True, "position": "Left", "width": 3, "color": solid(c["railAccent"]), "transparency": 0}),
                "outline": nav_states({"show": False}, {"show": False}, {"show": False}),
                "shape": [{"tileShape": "rectangleRounded", "rectangleRoundedCurve": 6}],
                "layout": [{"orientation": 1, "cellPadding": 4}],
                "pages": [{"showHiddenPages": False}],  # 드릴스루 전용 숨김 페이지는 선택기에 넣지 않는다
            }},
            # 버튼 슬라이서 (레일): 어두운 칸 안에서 선택된 값만 흰색. 위에 작은 제목("기간", "채널")
            "advancedSlicerVisual": {"*": {
                # 버튼 칠은 fillCustom이다. background(상태별)는 글자 상자 바탕이라 끈다
                # (background로 칠했더니 흰 버튼 안에 어두운 글자 상자가 생겼다 — 공개 PBIR 예시와 대조해 확인)
                "fillCustom": seg_states({"show": True, "fillColor": solid(c["segBg"]), "transparency": 0},
                                         {"show": True, "fillColor": solid(c["railHover"]), "transparency": 0},
                                         {"show": True, "fillColor": solid(c["segOn"]), "transparency": 0}),
                "background": seg_states({"show": False}, {"show": False}, {"show": False}),
                "value": seg_states({"fontFamily": F, "fontSize": T["body"], "fontColor": solid(c["railInk2"])},
                                    {"fontColor": solid(c["railInk"])}, {"fontFamily": FS, "fontColor": solid(c["segOnInk"])}),
                "outline": seg_states({"show": False}, {"show": False}, {"show": False}),
                "shapeCustomRectangle": [{"tileShape": "rectangleRounded", "rectangleRoundedCurve": 6}],
                "title": [{"show": True, "fontFamily": F, "fontSize": T["caption"], "bold": False, "fontColor": solid(c["railInk3"]), "alignment": "left"}],
                "border": [{"show": False}], "dropShadow": [{"show": False}],
                "layout": [{"rowCount": 1, "cellPadding": 4}],
            }},
            # 뒤로 가기 버튼: 본문 위의 작은 알약
            "actionButton": {"*": {
                **bare(),
                # 켜고 끄기(show)는 상태 없는 첫 항목에 둔다. 상태 항목 안의 show는 버튼에서 무시됐다 (Desktop 캡처 + 공개 PBIR 대조)
                "fill": [{"show": True}] + nav_states({"fillColor": solid(c["surface"]), "transparency": 0},
                                                      {"fillColor": solid(c["hover"]), "transparency": 0},
                                                      {"fillColor": solid(c["hover"]), "transparency": 0}),
                "outline": [{"show": True}] + nav_states({"lineColor": solid(c["border"]), "weight": 1},
                                                         {"lineColor": solid(c["axis"]), "weight": 1}, {"lineColor": solid(c["axis"]), "weight": 1}),
                "text": [{"show": True}] + nav_states({"fontFamily": FS, "fontSize": T["body"], "fontColor": ink2}, {"fontColor": ink}, {"fontColor": ink}),
                "icon": [{"show": False}],  # 화살표는 글자("← 매장 목록")에 넣는다
                "shape": [{"tileShape": "rectangleRounded", "rectangleRoundedCurve": 16}],
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
