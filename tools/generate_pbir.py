"""명세(report.spec.json) → PBIP 프로젝트(.pbip + .Report + .SemanticModel) 생성기.

에이전트는 작은 명세만 쓴다. 나머지는 이 스크립트가 채운다.
- 좌표: design-system/layouts/layouts.resolved.json (페이지 유형별 1280×720 템플릿, 왼쪽 내비 레일 포함)
- 서식: design-system/themes/<theme>.json (visual.json에는 서식을 넣지 않는다)
- 모델: 명세의 "model" 폴더(TMDL)를 .SemanticModel/definition 으로 복사하고,
        명세의 "measures"(표시용 측정값: 억·만 단위, ▲▼ 문구, 결론 문장, 증감 색)를 측정값 테이블에 더한다

만들기 전에 명세의 필드 이름을 TMDL의 실제 열·측정값과 대조한다. 오타는 여기서 막는다 (토큰 0).
비주얼·페이지 ID는 이름에서 해시로 만든다 → 다시 생성해도 파일이 같다 (git diff가 깔끔).

visual.json에 서식을 넣는 예외는 두 가지뿐이다.
1) 데이터에 따라 달라지는 것: 슬라이서 기본 선택, 카드 비교 문구와 부호 색, 목표 계열 점선, 증감 색
2) 역할 서식: 같은 비주얼 종류라도 역할이 다른 것 (결론 문장 카드, 레일 위 슬라이서의 투명 바탕)
   테마는 비주얼 종류 단위로만 서식을 줄 수 있어서, 역할 차이는 생성기가 채운다. 명세 토큰은 늘지 않는다.

PBIR 구조는 Microsoft skills-for-fabric 작성 스킬 문서와 공개 PBIR 예시에서 확인한 형식을 따르고,
결과는 `powerbi-report-author validate`로 검증한다.

사용법: python tools/generate_pbir.py examples/04-autopilot/report.spec.json [--local-data] [--out <폴더>]
  --local-data  M 매개변수 '데이터폴더'를 이 PC의 실제 경로로 바꾼다 (커밋용 산출물에는 쓰지 말 것)
  --out         산출물을 다른 폴더에 쓴다 (Desktop 렌더링 확인용 사본)
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = ROOT / "design-system" / "layouts" / "layouts.resolved.json"
THEMES = ROOT / "design-system" / "themes"
TOKENS = ROOT / "design-system" / "tokens.json"

SCHEMA = "https://developer.microsoft.com/json-schemas/fabric"
# 2.10.0 이상은 Desktop이 쓰긴 하지만 스키마가 공개돼 있지 않아(404) CLI가 스키마 검증을 건너뛴다 (2026-09-13 확인)
S_VISUAL = f"{SCHEMA}/item/report/definition/visualContainer/2.9.0/schema.json"
S_PAGE = f"{SCHEMA}/item/report/definition/page/2.1.0/schema.json"
S_PAGES = f"{SCHEMA}/item/report/definition/pagesMetadata/1.0.0/schema.json"
S_VERSION = f"{SCHEMA}/item/report/definition/versionMetadata/1.0.0/schema.json"
S_REPORT = f"{SCHEMA}/item/report/definition/report/3.3.0/schema.json"
S_PBIR = f"{SCHEMA}/item/report/definitionProperties/2.0.0/schema.json"
S_PBISM = f"{SCHEMA}/item/semanticModel/definitionProperties/1.0.0/schema.json"
S_PBIP = f"{SCHEMA}/pbip/pbipProperties/1.0.0/schema.json"
S_PLATFORM = f"{SCHEMA}/gitIntegration/platformProperties/2.0.0/schema.json"

UNIT_SUFFIX = re.compile(r"\s*\((만|억)\)$")  # '매출 (만)' → 범례·머리글에는 '매출'로 (단위는 값에 붙어 있다)
AUTO_ROLES = ("pageNavigator", "shape")       # 명세에 없어도 레이아웃에 있으면 자동으로 놓는다 (페이지 선택기, 레일 바탕)
BAR_FAMILY = ("barChart", "columnChart")
EACH_POINT = {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}


def hid(*parts: str, n: int = 20) -> str:
    return hashlib.md5("/".join(parts).encode("utf-8")).hexdigest()[:n]


def lit(value) -> dict:
    """PBIR 식 표기: 문자열은 작은따옴표로 감싸고 안의 작은따옴표는 두 번 쓴다."""
    if isinstance(value, bool):
        return {"expr": {"Literal": {"Value": "true" if value else "false"}}}
    if isinstance(value, (int, float)):
        return {"expr": {"Literal": {"Value": f"{value}D"}}}
    return {"expr": {"Literal": {"Value": "'" + str(value).replace("'", "''") + "'"}}}


def lit_int(n: int) -> dict:
    """정수형 서식 속성(행·열 수 등)은 D가 아니라 L."""
    return {"expr": {"Literal": {"Value": f"{int(n)}L"}}}


def filter_literal(value, dtype: str | None) -> dict:
    """필터 값 표기: 정수 열은 2026L, 실수는 D, 나머지는 문자열.
    계산 테이블(예: CALENDAR로 만든 날짜)은 TMDL에 dataType이 없다 → 명세 값의 JSON 형식으로 판단한다.
    형식이 어긋나면 필터가 조용히 무시된다 (Desktop 캡처에서 전 기간 합계가 보여 알았다)."""
    if dtype is None:
        dtype = "int64" if isinstance(value, int) and not isinstance(value, bool) else "double" if isinstance(value, float) else "string"
    if dtype == "int64":
        return {"Literal": {"Value": f"{int(value)}L"}}
    if dtype in ("double", "decimal"):
        return {"Literal": {"Value": f"{value}D"}}
    return {"Literal": {"Value": "'" + str(value).replace("'", "''") + "'"}}


def color(hex_: str) -> dict:
    return {"solid": {"color": lit(hex_)}}


def hide(*names: str) -> dict:
    return {n: [{"properties": {"show": lit(False)}}] for n in names}


def zero_padding() -> list:
    return [{"properties": {k: lit(0) for k in ("top", "bottom", "left", "right")}}]


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- 모델 읽기 · 필드 해석
def read_model(tmdl_dir: Path) -> dict:
    """TMDL에서 테이블별 열·측정값 이름과 열의 데이터 형식을 모은다."""
    fields = {}
    for f in (tmdl_dir / "tables").glob("*.tmdl"):
        table, cols, meas, types, cur = None, set(), set(), {}, None
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^table\s+(?:'([^']+)'|(\S+))", line)
            if m:
                table = m.group(1) or m.group(2)
            m = re.match(r"^\t(column|measure)\s+(?:'([^']+)'|([^\s=]+))", line)
            if m:
                name = m.group(2) or m.group(3)
                (cols if m.group(1) == "column" else meas).add(name)
                cur = name if m.group(1) == "column" else None
            m = re.match(r"^\t\tdataType:\s*(\w+)", line)
            if m and cur:
                types[cur] = m.group(1)
        if table:
            fields[table] = {"columns": cols, "measures": meas, "types": types}
    return fields


class FieldResolver:
    def __init__(self, model: dict, measure_table: str):
        self.model, self.mt, self.errors = model, measure_table, []

    def __call__(self, ref: str) -> tuple[dict, str, str]:
        """'테이블.열' → Column, 그 밖 → 측정값 테이블의 Measure. (식, queryRef, nativeQueryRef)"""
        if "." in ref and ref.split(".", 1)[0] in self.model:
            table, col = ref.split(".", 1)
            if col not in self.model[table]["columns"]:
                self.errors.append(f"열 없음: {ref}")
            expr = {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": col}}
            return expr, f"{table}.{col}", col
        if ref not in self.model.get(self.mt, {}).get("measures", set()):
            self.errors.append(f"측정값 없음: {ref}")
        expr = {"Measure": {"Expression": {"SourceRef": {"Entity": self.mt}}, "Property": ref}}
        return expr, f"{self.mt}.{ref}", ref

    def dtype(self, ref: str) -> str | None:
        table, col = ref.split(".", 1)
        return self.model.get(table, {}).get("types", {}).get(col)


# ---------------------------------------------------------------- 표시용 측정값 → TMDL
def measure_tmdl(measures: dict, palette: dict) -> list[str]:
    """명세의 measures를 TMDL 줄로. 식 안의 @pos·@neg 같은 이름은 디자인 토큰 색으로 바꾼다."""
    out = []
    keys = sorted(palette, key=len, reverse=True)  # @negInk가 @neg보다 먼저 바뀌어야 한다
    for name, m in measures.items():
        m = m if isinstance(m, dict) else {"expr": m}
        expr = m["expr"]
        for k in keys:
            expr = expr.replace("@" + k, palette[k])
        out.append("\t/// 리포트 표시용 (report.spec.json에서 생성)")
        out.append(f"\tmeasure '{name.replace(chr(39), chr(39) * 2)}' = {expr}")
        if m.get("format"):
            out.append(f"\t\tformatString: {m['format']}")
        out.append("\t\tdisplayFolder: 9. 리포트 표시용")
        out.append("")
    return out


def inject_measures(def_dir: Path, table: str, measures: dict, palette: dict) -> None:
    f = def_dir / "tables" / f"{table}.tmdl"
    lines = f.read_text(encoding="utf-8").split("\n")
    at = next(i for i, l in enumerate(lines) if re.match(r"^\t(column|partition)\s", l))  # 측정값 뒤, 열·파티션 앞
    lines[at:at] = measure_tmdl(measures, palette)
    f.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------- 비주얼 만들기 (위치·필드·제목 + 위의 예외만)
def container(name: str, region: dict, z: int, visual: dict, title: str | None = None, sub: str | None = None) -> dict:
    v = {"$schema": S_VISUAL, "name": name,
         "position": {"x": region["x"], "y": region["y"], "z": z, "height": region["height"], "width": region["width"], "tabOrder": z},
         "visual": visual}
    vco = visual.setdefault("visualContainerObjects", {})
    if title:
        vco["title"] = [{"properties": {"text": lit(title)}}]
    if sub:  # 차트 부제목: 단위·기간·읽는 법
        vco["subTitle"] = [{"properties": {"show": lit(True), "text": lit(sub)}}]
    if not vco:
        del visual["visualContainerObjects"]
    return v


def projection(resolve, ref: str, display: str | None = None, active: bool = False) -> dict:
    expr, qref, nref = resolve(ref)
    p = {"field": expr, "queryRef": qref, "nativeQueryRef": nref}
    display = display or (UNIT_SUFFIX.sub("", nref) if UNIT_SUFFIX.search(nref) else None)
    if display:
        p["displayName"] = display
    if active:
        p["active"] = True
    return p


def sort_def(resolve, ref: str, direction: str) -> dict:
    return {"sort": [{"field": resolve(ref)[0], "direction": "Ascending" if direction.startswith("asc") else "Descending"}], "isDefaultSort": False}


def measure_color(resolve, ref: str) -> dict:
    """색을 측정값 값(#RRGGBB)으로 — Power BI의 '필드 값' 조건부 서식."""
    return {"solid": {"color": {"expr": resolve(ref)[0]}}}


def paragraph(text: str, font: str, size: int, fg: str) -> dict:
    return {"textRuns": [{"value": text, "textStyle": {"fontFamily": font, "fontSize": f"{size}pt", "color": fg}}], "horizontalTextAlignment": "left"}


def build_visual(role: str, spec: dict, resolve, tokens: dict, region: dict) -> dict:
    c, pt, f = tokens["color"]["light"], tokens["type"]["pt"], tokens["font"]
    on_rail = region.get("zone") == "rail"
    if role == "shape":  # 레일 바탕. 색·테두리는 테마의 shape 서식
        return {"visualType": "shape", "objects": {"shape": [{"properties": {"tileShape": lit("rectangle")}, "selector": {"id": "default"}}]}}
    if role == "textbox":
        strong_c, soft_c = (c["railInk"], c["railInk3"]) if on_rail else (c["ink"], c["ink3"])
        size = {"title": pt["page"], "brand": pt["title"]}.get(region["id"], pt["caption"] if on_rail else pt["body"])
        strong = region["id"] in ("title", "brand")
        runs = [paragraph(spec["text"], f["semibold"] if strong else f["family"], size, strong_c if strong else soft_c)]
        if spec.get("sub"):
            runs.append(paragraph(spec["sub"], f["family"], pt["caption"] if on_rail else pt["body"], soft_c))
        # 테마에서도 여백 0이지만, 공식 검증은 비주얼 파일만 보고 기본 8px로 계산해 경고한다 → 여기서도 명시
        return {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": runs}}]},
                "visualContainerObjects": {"padding": zero_padding()}}
    if role == "headline":  # 결론 한 줄: 문장을 돌려주는 측정값을 카드로. 카드 테마(큰 숫자)와 달라 역할 서식을 채운다
        return {"visualType": "cardVisual",
                "query": {"queryState": {"Data": {"projections": [projection(resolve, spec["measure"])]}}},
                "objects": {"label": [{"properties": {"show": lit(False)}, "selector": {"id": "default"}}],
                            "fillCustom": [{"properties": {"show": lit(False)}, "selector": {"id": "default"}}],  # 카드 자체 흰 칠
                            "layout": [{"properties": {"backgroundShow": lit(False)}, "selector": {"id": "default"}}],  # 카드 배치 영역 흰 칠 (이것까지 꺼야 띠가 사라진다)
                            "value": [{"properties": {"fontSize": lit(pt["title"]), "bold": lit(False), "fontColor": color(c["ink2"]),
                                                      "horizontalAlignment": lit("left")}, "selector": {"id": "default"}}]},
                "visualContainerObjects": {**hide("background", "border", "dropShadow", "title"), "padding": zero_padding()}}
    if role == "pageNavigator":
        return {"visualType": "pageNavigator"}
    if role == "actionButton":
        # 켜고 끄기(show)는 선택자 없는 항목에, 글자·아이콘 내용은 상태(default) 항목에 둔다 — 공개 PBIR의 뒤로 버튼과 같은 형식.
        # show를 상태 항목 안에 넣었더니 글자가 끝내 나오지 않았다 (Desktop 캡처로 확인)
        return {"visualType": "actionButton",
                "objects": {"icon": [{"properties": {"shapeType": lit("back")}, "selector": {"id": "default"}},
                                     {"properties": {"show": lit(False)}}],
                            "text": [{"properties": {"show": lit(True)}},
                                     {"properties": {"text": lit(spec.get("text", "← 뒤로"))}, "selector": {"id": "default"}}]},
                "visualContainerObjects": {"visualLink": [{"properties": {"show": lit(True), "type": lit(spec.get("action", "Back"))}}]}}
    if role == "advancedSlicerVisual":
        v = {"visualType": "advancedSlicerVisual", "query": {"queryState": {"Values": {"projections": [projection(resolve, spec["field"])]}}}}
        # 버튼 안쪽 여백: 기본값(Normal)이면 레일 폭 160에서 "2026"이 "2…"로 잘렸다 (Desktop 캡처로 확인)
        objs = {"padding": [{"properties": {"paddingSelection": lit("Custom"), "leftMargin": lit_int(4), "rightMargin": lit_int(4),
                                            "topMargin": lit_int(0), "bottomMargin": lit_int(0)}, "selector": {"id": "default"}}]}
        if "default" in spec:  # 처음 열었을 때 선택된 값 (예: 올해)
            table, col = spec["field"].split(".", 1)
            vals = spec["default"] if isinstance(spec["default"], list) else [spec["default"]]
            dt = resolve.dtype(spec["field"])
            objs["general"] = [{"properties": {"filter": {"filter": {
                "Version": 2, "From": [{"Name": "d", "Entity": table, "Type": 0}],
                "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": col}}],
                                                "Values": [[filter_literal(x, dt)] for x in vals]}}}]}}}}]
        if spec.get("single"):
            objs["selection"] = [{"properties": {"singleSelect": lit(True)}}]
        v["objects"] = objs
        # 레일 위에서는 바탕을 비우고 바깥 여백을 없앤다. 테마의 background·padding은 버튼 상태 서식과 이름이 겹쳐 여기서 지정
        v["visualContainerObjects"] = {**hide("background", "border", "dropShadow"), "padding": zero_padding()}
        return v
    if role == "cardVisual":
        p = projection(resolve, spec["measure"], spec.get("label"))
        v = {"visualType": "cardVisual", "query": {"queryState": {"Data": {"projections": [p]}}}}
        if spec.get("ref"):  # 값 아래 비교 문구 (예: 전년 대비 ▲12.3%)
            sel = {"data": [{"dataViewWildcard": {"matchingOption": 0}}], "metadata": p["queryRef"],
                   "id": "field-" + hid(p["queryRef"], spec["ref"], n=32)}
            v["objects"] = {"referenceLabel": [{"properties": {"value": {"expr": resolve(spec["ref"])[0]}}, "selector": {**sel, "order": 0}}]}
            if spec.get("ref_color"):  # 문구 색을 부호로 (▲ 파랑, ▼ 빨강)
                v["objects"]["referenceLabelValue"] = [{"properties": {"valueFontColor": measure_color(resolve, spec["ref_color"])}, "selector": sel}]
        return v
    if role in ("lineChart",) + BAR_FAMILY:
        qs = {"Category": {"projections": [projection(resolve, spec["x"], active=True)]},
              "Y": {"projections": [projection(resolve, m) for m in spec["y"]]}}
        if spec.get("small"):
            qs["Rows"] = {"projections": [projection(resolve, spec["small"])]}
        q = {"queryState": qs}
        if spec.get("sort"):
            q["sortDefinition"] = sort_def(resolve, spec["y"][0], spec["sort"])
        v, objs, styles = {"visualType": role, "query": q}, {}, []
        if role == "lineChart" and len(spec["y"]) > 1:  # 첫 계열(올해)만 굵게: 나머지는 맥락
            styles.append({"properties": {"strokeWidth": lit(3)}, "selector": {"metadata": resolve(spec["y"][0])[1]}})
        if spec.get("target"):  # 목표 계열은 흐린 점선: 실적과 경쟁하지 않는 기준선
            tq = resolve(spec["target"])[1]
            styles.append({"properties": {"lineStyle": lit("dashed"), "strokeWidth": lit(1.5)}, "selector": {"metadata": tq}})
            objs["dataPoint"] = [{"properties": {"fill": color(c["target"])}, "selector": {"metadata": tq}}]
        if styles:
            objs["lineStyles"] = styles
        if spec.get("continuous"):  # 숫자 축(연속): 좁은 칸에서도 가로 스크롤이 생기지 않는다 (작은 여러 차트에서 확인)
            objs["categoryAxis"] = [{"properties": {"axisType": lit("Scalar"), "start": lit(1)}}]  # 월 번호 축이 0부터 그려졌다
        if spec.get("grid"):  # 작은 여러 차트 배치 [행, 열] — 기본 자동 배치는 2열로 쌓여 스크롤이 생겼다
            objs["smallMultiplesLayout"] = [{"properties": {"layoutType": lit("custom"), "rowCount": lit_int(spec["grid"][0]),
                                                            "columnCount": lit_int(spec["grid"][1])}}]
        if spec.get("color"):  # 막대마다 색을 측정값으로 (예: 목표 미달 빨강)
            objs["dataPoint"] = [{"properties": {"fill": measure_color(resolve, spec["color"])}, "selector": EACH_POINT}]
        if objs:
            v["objects"] = objs
        return v
    if role == "scatterChart":
        return {"visualType": "scatterChart", "query": {"queryState": {
            "Category": {"projections": [projection(resolve, spec["point"], active=True)]},
            "X": {"projections": [projection(resolve, spec["x"])]},
            "Y": {"projections": [projection(resolve, spec["y"])]}}}}
    if role == "tableEx":
        q = {"queryState": {"Values": {"projections": [projection(resolve, col) for col in spec["columns"]]}}}
        if spec.get("sort"):
            q["sortDefinition"] = sort_def(resolve, spec["sort"][0], spec["sort"][1])
        v, objs = {"visualType": "tableEx", "query": q}, {}
        if spec.get("colors"):  # 열 글자색을 측정값으로 (예: 감소만 빨강)
            objs["values"] = [{"properties": {"fontColor": measure_color(resolve, m)},
                               "selector": {**EACH_POINT, "metadata": resolve(fld)[1]}} for fld, m in spec["colors"].items()]
        if spec.get("totals") is False:  # 주의 목록처럼 합계가 의미 없는 표: 한 줄이라도 더 보이게
            objs["total"] = [{"properties": {"totals": lit(False)}}]
        if objs:
            v["objects"] = objs
        return v
    raise ValueError(f"지원하지 않는 역할: {role}")


# ---------------------------------------------------------------- 프로젝트 쓰기
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--local-data", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()
    spec_path = Path(args.spec).resolve()
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = spec_path.parent
    out = Path(args.out).resolve() if args.out else base
    name = spec["name"]
    tmdl = (base / spec["model"]).resolve()
    layouts = {p["id"]: p for p in json.load(open(LAYOUTS, encoding="utf-8"))["pages"]}
    tokens = json.load(open(TOKENS, encoding="utf-8"))
    model = read_model(tmdl)
    extra = spec.get("measures", {})
    model.setdefault(spec["measureTable"], {"columns": set(), "measures": set(), "types": {}})["measures"] |= set(extra)
    resolve = FieldResolver(model, spec["measureTable"])

    # 1) 페이지·비주얼을 메모리에서 먼저 만든다 (필드 오류가 있으면 아무것도 쓰지 않는다)
    pages = []
    for page in spec["pages"]:
        lay = layouts[page["layout"]]
        pid = hid(name, page["layout"])
        regions = {r["id"]: r for r in lay["regions"]}
        shared = {k: v for k, v in spec.get("shared", {}).items() if k in regions}  # 레일의 이름·기준일·슬라이서: 명세에 한 번만
        wanted = {**{r["id"]: {} for r in lay["regions"] if r["role"] in AUTO_ROLES}, **shared, **page["visuals"]}
        for rid in [k for k in wanted if k not in regions]:
            resolve.errors.append(f"{page['layout']}: 레이아웃에 없는 영역 {rid}")
            del wanted[rid]
        visuals = {}
        order = sorted(wanted, key=lambda k: (regions[k].get("layer") != "background", regions[k]["y"], regions[k]["x"]))
        for i, rid in enumerate(order, 1):
            r, vs = regions[rid], wanted[rid]
            vid = hid(name, page["layout"], rid)
            role = r["role"]
            if vs.get("type") in BAR_FAMILY and role in BAR_FAMILY:  # 막대 방향만은 명세가 바꿀 수 있다 (항목 수에 따라)
                role = vs["type"]
            sub = vs.get("sub") if role != "textbox" else None
            visuals[vid] = container(vid, r, i * 1000, build_visual(role, vs, resolve, tokens, r), vs.get("title"), sub)
        pj = {"$schema": S_PAGE, "name": pid, "displayName": lay["name"], "displayOption": "FitToPage", "height": 720, "width": 1280}
        if page.get("hidden"):
            pj["visibility"] = "HiddenInViewMode"
        if page.get("drillthrough"):
            fexpr = resolve(page["drillthrough"])[0]
            fname = hid(name, pid, "drill")
            pj["filterConfig"] = {"filters": [{"name": fname, "field": fexpr, "type": "Categorical", "howCreated": "Drillthrough"}]}
            pj["pageBinding"] = {"name": hid(name, pid, "binding"), "type": "Drillthrough",
                                 "parameters": [{"name": hid(name, pid, "param"), "boundFilter": fname, "fieldExpr": fexpr}]}
        pages.append((pid, pj, visuals))
    if resolve.errors:
        print("명세 오류 — 파일을 쓰지 않았다:")
        for e in resolve.errors:
            print("  -", e)
        sys.exit(1)

    # 2) 쓰기 (이전 산출물은 지운다)
    rep, sm = out / f"{name}.Report", out / f"{name}.SemanticModel"
    for d in (rep, sm):
        if d.exists():
            shutil.rmtree(d)
    theme_src = THEMES / f"{spec['theme']}.json"
    theme_file = f"{spec['theme']}-{hashlib.md5(theme_src.read_bytes()).hexdigest()[:8]}.json"  # 테마가 바뀌면 이름도 바뀐다 (Desktop 캐시 회피)
    res_dir = rep / "StaticResources" / "RegisteredResources"
    res_dir.mkdir(parents=True, exist_ok=True)
    theme_obj = json.load(open(theme_src, encoding="utf-8"))
    # 공식 CLI 규칙: 테마 파일 안의 name = report.json이 부르는 이름(확장자 포함).
    # Desktop이 저장한 실제 리포트는 표시 이름("Sunflower Twilight")을 두지만, 검증 통과를 우선한다
    theme_obj["name"] = theme_file
    write_json(res_dir / theme_file, theme_obj)
    D = rep / "definition"
    write_json(D / "version.json", {"$schema": S_VERSION, "version": "2.0.0"})
    write_json(D / "report.json", {
        "$schema": S_REPORT,
        # reportVersionAtImport는 필수 (CLI 검증). 이 생성기가 쓰는 스키마 버전과 맞춘다
        "themeCollection": {"customTheme": {"name": theme_file, "type": "RegisteredResources",
                                            "reportVersionAtImport": {"visual": "2.9.0", "report": "3.3.0", "page": "2.1.0"}}},
        "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources",
                              "items": [{"name": theme_file, "path": theme_file, "type": "CustomTheme"}]}]})
    write_json(D / "pages" / "pages.json", {"$schema": S_PAGES, "pageOrder": [p[0] for p in pages], "activePageName": pages[0][0]})
    for pid, pj, visuals in pages:
        write_json(D / "pages" / pid / "page.json", pj)
        for vid, v in visuals.items():
            write_json(D / "pages" / pid / "visuals" / vid / "visual.json", v)
    write_json(rep / "definition.pbir", {"$schema": S_PBIR, "version": "4.0", "datasetReference": {"byPath": {"path": f"../{name}.SemanticModel"}}})
    write_json(rep / ".platform", {"$schema": S_PLATFORM, "metadata": {"type": "Report", "displayName": name},
                                   "config": {"version": "2.0", "logicalId": str(hashlib.md5((name + 'report').encode()).hexdigest())}})

    shutil.copytree(tmdl, sm / "definition")
    if extra:
        inject_measures(sm / "definition", spec["measureTable"], extra, tokens["color"]["light"])
    if args.local_data:
        ex = sm / "definition" / "expressions.tmdl"
        data_dir = str((ROOT / "examples" / "_data" / "korean-retail").resolve())
        ex.write_text(re.sub(r'"[^"]*korean-retail"', '"' + data_dir.replace("\\", "\\\\") + '"', ex.read_text(encoding="utf-8")), encoding="utf-8")
    write_json(sm / "definition.pbism", {"$schema": S_PBISM, "version": "4.2", "settings": {}})
    write_json(sm / ".platform", {"$schema": S_PLATFORM, "metadata": {"type": "SemanticModel", "displayName": name},
                                  "config": {"version": "2.0", "logicalId": str(hashlib.md5((name + 'model').encode()).hexdigest())}})
    write_json(out / f"{name}.pbip", {"$schema": S_PBIP, "version": "1.0", "artifacts": [{"report": {"path": f"{name}.Report"}}],
                                      "settings": {"enableAutoRecovery": True}})

    # 3) 토큰 관점의 크기 비교
    vfiles = list(D.rglob("visual.json"))
    rep_bytes = sum(f.stat().st_size for f in rep.rglob("*") if f.is_file() and f.suffix == ".json" and "StaticResources" not in f.parts)
    spec_bytes = spec_path.stat().st_size
    avg = sum(f.stat().st_size for f in vfiles) / len(vfiles)
    print(f"생성: {out.name}/{name}.pbip · 페이지 {len(pages)} · 비주얼 {len(vfiles)} · 표시용 측정값 {len(extra)}")
    print(f"  명세(에이전트가 쓰는 것)   {spec_bytes / 1024:6.1f}KB  ≈ {spec_bytes // 3:>6,} 토큰")
    print(f"  생성된 리포트 JSON          {rep_bytes / 1024:6.1f}KB  ≈ {rep_bytes // 3:>6,} 토큰 (테마 제외)")
    print(f"  visual.json 평균            {avg / 1024:6.2f}KB  (수집한 PBIR 평균 6.5KB의 {avg / 6656:.0%})")


if __name__ == "__main__":
    main()
