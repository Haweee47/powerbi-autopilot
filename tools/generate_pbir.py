"""명세(report.spec.json) → PBIP 프로젝트(.pbip + .Report + .SemanticModel) 생성기.

에이전트는 작은 명세만 쓴다. 나머지는 이 스크립트가 채운다.
- 좌표: design-system/layouts/layouts.resolved.json (페이지 유형별 1280×720 템플릿, 왼쪽 내비 레일 포함)
- 서식: design-system/themes/autopilot-<테마>.json (네이비·페이퍼·미드나잇; visual.json에는 서식을 넣지 않는다)
- 언어: design-system/i18n/locales.json (기본 영어). 명세의 글자는 {"en": ..., "ko": ...}, 없는 언어는 영어로
- 모델: 명세의 "model" 폴더(TMDL)를 복사하고, 표시용 측정값(include·measures)을 더하고,
        데이터 로케일이 있으면 모델의 글자 값(월 이름 등)과 데이터 폴더를 그 언어로 바꾼다

만들기 전에 명세의 필드 이름을 TMDL의 실제 열·측정값과 대조한다. 오타는 여기서 막는다 (토큰 0).
비주얼·페이지 ID는 이름에서 해시로 만든다 → 다시 생성해도 파일이 같다 (git diff가 깔끔).

visual.json에 서식을 넣는 예외는 두 가지뿐이다.
1) 데이터에 따라 달라지는 것: 슬라이서 기본 선택, 카드 비교 문구와 부호 색, 목표 계열 점선, 표·행렬 조건부 서식
2) 역할 서식: 같은 비주얼 종류라도 역할이 다른 것 (결론 문장 카드, 레일 위 슬라이서의 투명 바탕)

표·행렬 조건부 서식은 열마다 한 단어로 적는다: bar(데이터 막대) · heat(색 척도) · sign(감소만 빨강 — 색 측정값 자동 생성)

결과는 `powerbi-report-author validate`로 검증한다.

사용법: python tools/generate_pbir.py <명세> [--lang en|ko|…] [--theme navy|paper|midnight] [--local-data] [--out <폴더>]
  --local-data  M 매개변수 '데이터폴더'를 이 PC의 실제 경로로 바꾼다 (커밋용 산출물에는 쓰지 말 것)
  --out         산출물을 다른 폴더에 쓴다 (Desktop 렌더링 확인용 사본, 테마·언어 변형)
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
LOCALES = ROOT / "design-system" / "i18n" / "locales.json"

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

UNIT_SUFFIX = re.compile(r"\s*\((만|억)\)$")  # 용어집이 없을 때만: '매출 (만)' → '매출'
AUTO_ROLES = ("pageNavigator", "shape")       # 명세에 없어도 레이아웃에 있으면 자동으로 놓는다 (페이지 선택기, 레일 바탕)
BAR_FAMILY = ("barChart", "columnChart")
EACH_POINT = {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}


class Lang:
    """명세 글자 고르기: {"en": .., "ko": ..} → 현재 언어, 없으면 대체 언어, 그것도 없으면 첫 값."""

    def __init__(self, code: str, fallback: str, codes: set[str]):
        self.code, self.fallback, self.codes, self.missing = code, fallback, codes, set()

    def is_text_map(self, v) -> bool:
        return isinstance(v, dict) and bool(v) and set(v) <= self.codes

    def __call__(self, v):
        if not self.is_text_map(v):
            return v
        if self.code in v:
            return v[self.code]
        self.missing.add(next(iter(v.values()))[:24])
        return v.get(self.fallback, next(iter(v.values())))


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

    def is_column(self, ref: str) -> bool:
        return "." in ref and ref.split(".", 1)[0] in self.model

    def __call__(self, ref: str) -> tuple[dict, str, str]:
        """'테이블.열' → Column, 그 밖 → Measure. (식, queryRef, nativeQueryRef)
        측정값은 측정값 테이블에서 먼저 찾고, 없으면 그 측정값이 있는 테이블을 쓴다 (측정값을 사실 테이블에 두는 모델)."""
        if self.is_column(ref):
            table, col = ref.split(".", 1)
            if col not in self.model[table]["columns"]:
                self.errors.append(f"열 없음: {ref}")
            expr = {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": col}}
            return expr, f"{table}.{col}", col
        home = self.mt if ref in self.model.get(self.mt, {}).get("measures", set()) else \
            next((t for t, info in self.model.items() if ref in info["measures"]), None)
        if home is None:
            self.errors.append(f"측정값 없음: {ref}")
            home = self.mt
        expr = {"Measure": {"Expression": {"SourceRef": {"Entity": home}}, "Property": ref}}
        return expr, f"{home}.{ref}", ref

    def dtype(self, ref: str) -> str | None:
        table, col = ref.split(".", 1)
        return self.model.get(table, {}).get("types", {}).get(col)


# ---------------------------------------------------------------- 표시용 측정값 → TMDL
def normalize_measure(m, t: Lang) -> dict:
    """측정값 표기 세 가지: "DAX" · {"expr": .., "format": ..} · {"en": "DAX", "ko": "DAX"} (값마다 언어 사전도 된다)."""
    if isinstance(m, str):
        return {"expr": m}
    if "expr" in m:  # formatExpr: 동적 서식 문자열(DAX). 데이터 크기에 따라 K·M·B를 고를 때
        # category: data category such as ImageUrl, so a measure that returns an SVG data URI renders as a picture
        return {"expr": t(m["expr"]), "format": t(m.get("format")), "formatExpr": t(m.get("formatExpr")), "category": m.get("category")}
    return {"expr": t(m)}


def measure_tmdl(measures: dict, palette: dict) -> list[str]:
    """측정값을 TMDL 줄로. 식 안의 @pos·@neg 같은 이름은 디자인 토큰 색으로 바꾼다.
    모델 대응표로 넣는 연결 측정값(adapter)은 숨기고 폴더를 따로 둔다."""
    out = []
    keys = sorted(palette, key=len, reverse=True)  # @negInk가 @neg보다 먼저 바뀌어야 한다
    for name, m in measures.items():
        expr = m["expr"]
        for k in keys:
            expr = expr.replace("@" + k, palette[k])
        adapter = m.get("adapter", False)
        out.append("\t/// " + ("Model map: a measure the pilot expects, in this model's terms" if adapter else "리포트 표시용 (명세에서 생성)"))
        out.append(f"\tmeasure '{name.replace(chr(39), chr(39) * 2)}' = {expr}")
        if m.get("format") and not m.get("formatExpr"):  # 동적 서식이 있으면 고정 서식은 쓰지 않는다
            out.append(f"\t\tformatString: {m['format']}")
        if adapter:
            out.append("\t\tisHidden")
        out.append(f"\t\tdisplayFolder: {'9. Model map (autopilot)' if adapter else '9. 리포트 표시용'}")
        if m.get("category"):
            out.append(f"\t\tdataCategory: {m['category']}")
        # formatStringDefinition은 속성이 아니라 하위 개체라 속성들 뒤, 맨 끝에 와야 한다.
        # 중간에 두면 Desktop이 다음 속성 줄을 "들여쓰기 오류"로 보고 모델을 열지 못한다 (Desktop 오류 창에서 확인)
        if m.get("formatExpr"):
            out.append(f"\t\tformatStringDefinition = {m['formatExpr']}")
        out.append("")
    return out


def inject_measures(def_dir: Path, table: str, measures: dict, palette: dict) -> None:
    f = def_dir / "tables" / f"{table}.tmdl"
    lines = f.read_text(encoding="utf-8").split("\n")
    at = next(i for i, l in enumerate(lines) if re.match(r"^\t(column|partition)\s", l))  # 측정값 뒤, 열·파티션 앞
    lines[at:at] = measure_tmdl(measures, palette)
    f.write_text("\n".join(lines), encoding="utf-8")


def patch_model(def_dir: Path, patches: list) -> list[str]:
    """데이터 로케일의 TMDL 치환 (모델 글자 값·데이터 폴더). 찾는 글이 없으면 알린다."""
    misses = []
    for p in patches:
        f = def_dir / p["file"]
        text = f.read_text(encoding="utf-8")
        if p["find"] not in text:
            misses.append(f"{p['file']}: {p['find'][:40]}")
            continue
        f.write_text(text.replace(p["find"], p["replace"]), encoding="utf-8")
    return misses


# ---------------------------------------------------------------- 다른 모델에 맞추기 (모델 대응표)
# 파일럿의 DAX는 기준 모델(예제 03)의 이름으로 적혀 있다. 다른 모델은 대응표(model-map.json) 한 장으로 잇는다.
#   columns      : 기준 열 '테이블.열' → 이 모델의 '테이블.열'. 명세의 필드와 DAX 안의 열을 함께 바꾼다
#   measures     : 기준 측정값 이름 → 이 모델의 DAX. 숨긴 연결 측정값으로 넣고, 공용 측정값과 이름이 같으면 그 식을 바꾼다
#   measureTable : 표시용 측정값을 넣을 테이블
# 대응표 뼈대(없는 것 목록과 기준 식 힌트)는 tools/new_report.py --model 이 만든다.
REF_COL = re.compile(r"(?:'([^']+)'|\b([^\W\d]\w*))\[([^\]]+)\]")   # 'T'[C] · T[C]
REF_MEASURE = re.compile(r"(?<![\w'\]])\[([^\]]+)\]")                 # 테이블 없이 쓴 [M]
DAX_STRING = re.compile(r'("(?:[^"]|"")*")')
DAX_STRING_BODY = re.compile(r'"((?:[^"]|"")*)"')


def dax_refs(expr: str) -> tuple[set[str], set[str]]:
    """DAX 식이 부르는 열('테이블.열')과 측정값 이름. 문자열 리터럴 안은 보지 않는다.
    Names the expression makes itself (ADDCOLUMNS ( …, "SalesV", … ) → [SalesV]) are local, not measures."""
    code = DAX_STRING.sub('""', expr)
    local = {x.replace('""', '"') for x in DAX_STRING_BODY.findall(expr)}
    return {f"{q or u}.{c}" for q, u, c in REF_COL.findall(code)}, set(REF_MEASURE.findall(code)) - local


def rename_columns(expr: str, cmap: dict) -> str:
    """DAX 안의 열 참조를 대응표대로 바꾼다 (문자열 리터럴은 그대로)."""
    if not cmap:
        return expr

    def sub(m: re.Match) -> str:
        key = f"{m.group(1) or m.group(2)}.{m.group(3)}"
        if key not in cmap:
            return m.group(0)
        table, col = cmap[key].split(".", 1)
        return f"'{table}'[{col}]"
    parts = DAX_STRING.split(expr)
    return "".join(p if i % 2 else REF_COL.sub(sub, p) for i, p in enumerate(parts))


def rename_fields(v, cmap: dict):
    """명세 안의 필드 이름('테이블.열')을 대응표대로 바꾼다. format 같은 딕셔너리의 키도 바꾼다."""
    if isinstance(v, str):
        return cmap.get(v, v)
    if isinstance(v, list):
        return [rename_fields(x, cmap) for x in v]
    if isinstance(v, dict):
        return {cmap.get(k, k): rename_fields(x, cmap) for k, x in v.items()}
    return v


def read_measure_defs(tmdl_dir: Path) -> dict[str, dict]:
    """TMDL 측정값 이름 → {"expr": 한 줄로 이은 식, "format": 서식 문자열}. 대응표 뼈대·힌트용."""
    out = {}
    for f in (tmdl_dir / "tables").glob("*.tmdl"):
        cur = None
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\tmeasure\s+(?:'((?:[^']|'')+)'|([^\s=]+))\s*=\s*(.*)$", line)
            if m:
                first = m.group(3).strip()
                cur = out[(m.group(1) or m.group(2)).replace("''", "'")] = {"expr": [first] if first else [], "format": None}
            elif cur is not None and line.startswith("\t\t\t"):   # 여러 줄 식
                cur["expr"].append(line.strip())
            elif cur is not None and line.startswith("\t\tformatString:"):
                cur["format"] = line.split(":", 1)[1].strip()
            elif cur is not None and not line.startswith("\t\t"):
                cur = None
    return {k: {"expr": " ".join(v["expr"]), "format": v["format"]} for k, v in out.items()}


# ---------------------------------------------------------------- 비주얼 만들기 (위치·필드·제목 + 위의 예외만)
class Ctx:
    """비주얼을 만들 때 쓰는 공통 재료: 필드 해석, 언어, 용어집, 색·글자 토큰."""

    def __init__(self, resolve: FieldResolver, t: Lang, glossary: dict, tokens: dict, palette: dict, ui: dict):
        self.resolve, self.t, self.glossary, self.tokens, self.c, self.ui = resolve, t, glossary, tokens, palette, ui

    def label(self, ref: str) -> str | None:
        """화면 이름: 용어집 → (없으면) 단위 꼬리 떼기 → 없음."""
        if ref in self.glossary:
            return self.t(self.glossary[ref])
        nref = ref.split(".", 1)[1] if self.resolve.is_column(ref) else ref
        return UNIT_SUFFIX.sub("", nref) if UNIT_SUFFIX.search(nref) else None

    def proj(self, ref: str, display=None, active: bool = False) -> dict:
        expr, qref, nref = self.resolve(ref)
        p = {"field": expr, "queryRef": qref, "nativeQueryRef": nref}
        display = self.t(display) or self.label(ref)
        if display:
            p["displayName"] = display
        if active:
            p["active"] = True
        return p

    def mcolor(self, ref: str) -> dict:
        """색을 측정값 값(#RRGGBB)으로 — Power BI의 '필드 값' 조건부 서식."""
        return {"solid": {"color": {"expr": self.resolve(ref)[0]}}}


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


def sort_def(resolve, ref: str, direction: str) -> dict:
    return {"sort": [{"field": resolve(ref)[0], "direction": "Ascending" if direction.startswith("asc") else "Descending"}], "isDefaultSort": False}


def paragraph(text: str, font: str, size: int, fg: str) -> dict:
    return {"textRuns": [{"value": text, "textStyle": {"fontFamily": font, "fontSize": f"{size}pt", "color": fg}}], "horizontalTextAlignment": "left"}


def sign_measure(fld: str) -> str:
    return f"{fld} Sign Color"


def cell_formats(spec: dict, x: Ctx) -> dict:
    """표·행렬 열 서식 약속: bar(데이터 막대) · heat(색 척도) · sign(감소만 빨강)."""
    objs, c = {}, x.c
    for fld, kind in spec.get("format", {}).items():
        expr, q, _ = x.resolve(fld)
        if kind == "bar":
            objs.setdefault("columnFormatting", []).append({"properties": {"dataBars": {
                "positiveColor": color(c["barPos"]), "negativeColor": color(c["barNeg"]), "axisColor": color(c["border"]),
                "reverseDirection": lit(False), "hideText": lit(False)}}, "selector": {"metadata": q}})
        elif kind == "heat":
            objs.setdefault("values", []).append({"properties": {"backColor": {"solid": {"color": {"expr": {"FillRule": {
                "Input": expr, "FillRule": {"linearGradient2": {
                    "min": {"color": {"Literal": {"Value": f"'{c['surface']}'"}}},
                    "max": {"color": {"Literal": {"Value": f"'{c['heatMax']}'"}}},
                    "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'asZero'"}}}}}}}}}}},
                "selector": {**EACH_POINT, "metadata": q}})
        elif kind == "sign":
            objs.setdefault("values", []).append({"properties": {"fontColor": x.mcolor(sign_measure(fld))},
                                                  "selector": {**EACH_POINT, "metadata": q}})
    for fld, m in spec.get("colors", {}).items():  # 예전 표기: 열 → 색 측정값
        objs.setdefault("values", []).append({"properties": {"fontColor": x.mcolor(m)}, "selector": {**EACH_POINT, "metadata": x.resolve(fld)[1]}})
    return objs


def build_visual(role: str, spec: dict, x: Ctx, region: dict) -> dict:
    c, t, pt, f = x.c, x.t, x.tokens["type"]["pt"], x.tokens["font"]
    on_rail = region.get("zone") == "rail"
    if role == "shape":  # 레일 바탕. 색·테두리는 테마의 shape 서식
        return {"visualType": "shape", "objects": {"shape": [{"properties": {"tileShape": lit("rectangle")}, "selector": {"id": "default"}}]}}
    if role == "textbox":
        strong_c, soft_c = (c["railInk"], c["railInk3"]) if on_rail else (c["ink"], c["ink3"])
        size = {"title": pt["page"], "brand": pt["title"]}.get(region["id"], pt["caption"] if on_rail else pt["body"])
        strong = region["id"] in ("title", "brand")
        runs = [paragraph(t(spec["text"]), f["semibold"] if strong else f["family"], size, strong_c if strong else soft_c)]
        if spec.get("sub"):
            runs.append(paragraph(t(spec["sub"]), f["family"], pt["caption"] if on_rail else pt["body"], soft_c))
        # 테마에서도 여백 0이지만, 공식 검증은 비주얼 파일만 보고 기본 8px로 계산해 경고한다 → 여기서도 명시
        return {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": runs}}]},
                "visualContainerObjects": {"padding": zero_padding()}}
    if role in ("headline", "context"):
        # 결론 한 줄(headline): 문장을 돌려주는 측정값을 카드로. 제목 다음으로 강한 글자 — 진한 색 세미볼드 (literature.md R1)
        # 지금 보는 범위(context): 제목 줄 오른쪽, 작은 흐린 글자, 오른쪽 정렬 (R4)
        # 카드 테마(큰 숫자)와 달라 역할 서식을 채운다
        head = role == "headline"
        off = lambda k: [{"properties": {k: lit(False)}}, {"properties": {k: lit(False)}, "selector": {"id": "default"}}]
        return {"visualType": "cardVisual",
                "query": {"queryState": {"Data": {"projections": [x.proj(spec["measure"])]}}},
                # 켜고 끄기는 선택자 없는 항목에도 둔다 (selector만 두면 무시됐다). 흰 띠 = 카드 칠 + 배치 바탕
                "objects": {"label": [{"properties": {"show": lit(False)}, "selector": {"id": "default"}}],
                            "fillCustom": off("show"), "layout": off("backgroundShow"),
                            "cardCalloutArea": [{"properties": {"backgroundTransparency": lit(100)}}],
                            "value": [{"properties": {"fontSize": lit(pt["title"] if head else pt["caption"]), "bold": lit(False),
                                                      "fontFamily": lit(f["semibold"] if head else f["family"]),
                                                      "fontColor": color(c["ink"] if head else c["ink3"]),
                                                      "horizontalAlignment": lit("left" if head else "right")}, "selector": {"id": "default"}}]},
                "visualContainerObjects": {**hide("background", "border", "dropShadow", "title"), "padding": zero_padding()}}
    if role == "pageNavigator":
        return {"visualType": "pageNavigator"}
    if role == "actionButton":
        # 켜고 끄기(show)는 선택자 없는 항목에, 글자 내용은 상태(default) 항목에 — 공개 PBIR의 뒤로 버튼과 같은 형식
        return {"visualType": "actionButton",
                "objects": {"icon": [{"properties": {"shapeType": lit("back")}, "selector": {"id": "default"}},
                                     {"properties": {"show": lit(False)}}],
                            "text": [{"properties": {"show": lit(True)}},
                                     {"properties": {"text": lit(t(spec.get("text")) or x.ui["back"])}, "selector": {"id": "default"}}]},
                "visualContainerObjects": {"visualLink": [{"properties": {"show": lit(True), "type": lit(spec.get("action", "Back"))}}]}}
    if role == "advancedSlicerVisual":
        v = {"visualType": "advancedSlicerVisual", "query": {"queryState": {"Values": {"projections": [x.proj(spec["field"])]}}}}
        # 버튼 안쪽 여백: 기본값(Normal)이면 레일 폭 160에서 "2026"이 "2…"로 잘렸다 (Desktop 캡처로 확인)
        objs = {"padding": [{"properties": {"paddingSelection": lit("Custom"), "leftMargin": lit_int(4), "rightMargin": lit_int(4),
                                            "topMargin": lit_int(0), "bottomMargin": lit_int(0)}, "selector": {"id": "default"}}]}
        if "default" in spec:  # 처음 열었을 때 선택된 값 (예: 올해)
            table, col = spec["field"].split(".", 1)
            vals = spec["default"] if isinstance(spec["default"], list) else [spec["default"]]
            dt = x.resolve.dtype(spec["field"])
            objs["general"] = [{"properties": {"filter": {"filter": {
                "Version": 2, "From": [{"Name": "d", "Entity": table, "Type": 0}],
                "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": col}}],
                                                "Values": [[filter_literal(v_, dt)] for v_ in vals]}}}]}}}}]
        if spec.get("single"):
            objs["selection"] = [{"properties": {"singleSelect": lit(True)}}]
        v["objects"] = objs
        # 레일 위에서는 바탕을 비우고 바깥 여백을 없앤다. 테마의 background·padding은 버튼 상태 서식과 이름이 겹쳐 여기서 지정
        v["visualContainerObjects"] = {**hide("background", "border", "dropShadow"), "padding": zero_padding()}
        return v
    if role == "dropdownSlicer":  # 값이 많은 필드용 드롭다운 (레일 색은 테마 slicer 서식)
        return {"visualType": "slicer", "query": {"queryState": {"Values": {"projections": [x.proj(spec["field"])]}}},
                "objects": {"data": [{"properties": {"mode": lit("Dropdown")}}], "header": [{"properties": {"show": lit(False)}}]},
                "visualContainerObjects": {**hide("background", "border", "dropShadow"), "padding": zero_padding()}}
    if role == "cardVisual":
        p = x.proj(spec["measure"], spec.get("label"))
        # 지표 이름은 카드 안 라벨이 아니라 컨테이너 제목으로 둔다. 비교 문구가 있으면 카드 안쪽 배치가 라벨 줄을 눌러
        # 위가 잘렸다 (104·112px, 여백·valueArea를 바꿔도 같음). 제목은 카드 내용 밖이라 눌리지 않는다
        v = {"visualType": "cardVisual", "query": {"queryState": {"Data": {"projections": [p]}}},
             "objects": {"label": [{"properties": {"show": lit(False)}}, {"properties": {"show": lit(False)}, "selector": {"id": "default"}}]},
             "visualContainerObjects": {
                 "padding": [{"properties": {"top": lit(12), "bottom": lit(10), "left": lit(20), "right": lit(20)}}],
                 "title": [{"properties": {"show": lit(True), "text": lit(p.get("displayName", p["nativeQueryRef"])), "fontFamily": lit(f["family"]),
                                           "fontSize": lit(pt["caption"]), "fontColor": color(c["ink3"])}}]}}
        if spec.get("ref"):  # 값 아래 비교 문구 (예: YoY ▲12.3%)
            sel = {"data": [{"dataViewWildcard": {"matchingOption": 0}}], "metadata": p["queryRef"],
                   "id": "field-" + hid(p["queryRef"], spec["ref"], n=32)}
            v["objects"]["referenceLabel"] = [{"properties": {"value": {"expr": x.resolve(spec["ref"])[0]}}, "selector": {**sel, "order": 0}}]
            if spec.get("ref_color"):  # 문구 색을 부호로 (▲ 파랑, ▼ 빨강)
                v["objects"]["referenceLabelValue"] = [{"properties": {"valueFontColor": x.mcolor(spec["ref_color"])}, "selector": sel}]
        return v
    if role in ("lineChart",) + BAR_FAMILY:
        qs = {"Category": {"projections": [x.proj(spec["x"], active=True)]},
              "Y": {"projections": [x.proj(m) for m in spec["y"]]}}
        if spec.get("small"):
            qs["Rows"] = {"projections": [x.proj(spec["small"])]}
        q = {"queryState": qs}
        if spec.get("sort"):
            q["sortDefinition"] = sort_def(x.resolve, spec["y"][0], spec["sort"])
        v, objs, styles = {"visualType": role, "query": q}, {}, []
        if role == "lineChart" and len(spec["y"]) > 1:  # 첫 계열(올해)만 굵게: 나머지는 맥락
            styles.append({"properties": {"strokeWidth": lit(3)}, "selector": {"metadata": x.resolve(spec["y"][0])[1]}})
        if spec.get("target"):  # 목표 계열은 흐린 점선: 실적과 경쟁하지 않는 기준선
            tq = x.resolve(spec["target"])[1]
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
            objs["dataPoint"] = [{"properties": {"fill": x.mcolor(spec["color"])}, "selector": EACH_POINT}]
        if objs:
            v["objects"] = objs
        return v
    if role == "scatterChart":
        qs = {"Category": {"projections": [x.proj(spec["point"], active=True)]},
              "X": {"projections": [x.proj(spec["x"])]}, "Y": {"projections": [x.proj(spec["y"])]}}
        if spec.get("size"):
            qs["Size"] = {"projections": [x.proj(spec["size"])]}
        v, objs = {"visualType": "scatterChart", "query": {"queryState": qs}}, {}
        if spec.get("color"):  # 점 색을 측정값으로 (예: 감소 매장 빨강 — 의미 색, R6)
            objs["dataPoint"] = [{"properties": {"fill": x.mcolor(spec["color"])}, "selector": EACH_POINT}]
        if spec.get("zero"):  # 세로축 0 기준선: 성장과 감소를 가르는 임계값 (Bach 임계값 패턴, R6)
            objs["y1AxisReferenceLine"] = [{"properties": {"show": lit(True), "value": lit(0), "lineColor": color(c["axis"]), "style": lit("dashed"),
                                                           "width": lit(1), "position": lit("back")}, "selector": {"id": "1"}}]
        if objs:
            v["objects"] = objs
        return v
    if role == "tableEx":
        q = {"queryState": {"Values": {"projections": [x.proj(col) for col in spec["columns"]]}}}
        if spec.get("sort"):
            q["sortDefinition"] = sort_def(x.resolve, spec["sort"][0], spec["sort"][1])
        v, objs = {"visualType": "tableEx", "query": q}, cell_formats(spec, x)
        if spec.get("totals") is False:  # 주의 목록처럼 합계가 의미 없는 표: 한 줄이라도 더 보이게
            objs["total"] = [{"properties": {"totals": lit(False)}}]
        else:  # 합계 줄 이름은 Desktop 표시 언어를 따라가서("합계") 리포트 언어로 고정한다
            objs["total"] = [{"properties": {"label": lit(x.ui["total"])}}]
        if objs:
            v["objects"] = objs
        return v
    if role == "pivotTable":
        rows, expand = spec.get("rows", []), spec.get("expand", False)
        qs = {"Values": {"projections": [x.proj(m) for m in spec["values"]]}}
        if rows:
            qs["Rows"] = {"projections": [x.proj(r, active=(expand or i == 0)) for i, r in enumerate(rows)]}
        if spec.get("columns"):
            qs["Columns"] = {"projections": [x.proj(col, active=True) for col in spec["columns"]]}
        v = {"visualType": "pivotTable", "query": {"queryState": qs}}
        if spec.get("sort"):
            v["query"]["sortDefinition"] = sort_def(x.resolve, spec["sort"][0], spec["sort"][1])
        objs = cell_formats(spec, x)
        # 합계 이름을 리포트 언어로 (행렬은 total에 이름 속성이 없고 subTotals에 있다)
        objs["subTotals"] = [{"properties": {"rowSubtotalsLabel": lit(x.ui["total"]), "columnSubtotalsLabel": lit(x.ui["total"])}}]
        v["objects"] = objs
        if expand and len(rows) > 1:  # 모든 행 수준을 펼친 채로 연다 (Desktop의 "모두 확장"과 같은 저장 형식)
            v["expansionStates"] = [{"roles": ["Rows"], "levels": [{"queryRefs": [x.resolve(r)[1]], "isCollapsed": False, "isPinned": True}
                                                                   for r in rows[:-1]], "root": {}}]
        return v
    if role == "decompositionTreeVisual":
        by = spec["by"]
        # 값이 큰 순서로: 정렬이 없으면 알파벳 순이라 한 칸에 보이는 몇 개 밖으로 1위 항목이 밀려난다
        # (예제 05에서 결론 문장은 "1위 권역 West 36%"인데 트리에는 West가 보이지 않았다)
        return {"visualType": "decompositionTreeVisual",
                "query": {"queryState": {"Analyze": {"projections": [x.proj(spec["measure"])]},
                                         "ExplainBy": {"projections": [x.proj(b, active=True) for b in by]}},
                          "sortDefinition": sort_def(x.resolve, spec["measure"], "desc")},
                # 뿌리를 펼쳐 첫 기준(예: 권역)까지 보이게 연다. 그 아래는 사람이 +로 고른다
                "expansionStates": [{"roles": ["ExplainBy"],
                                     "levels": [{"queryRefs": [x.resolve(b)[1]], "isCollapsed": True, "identityKeys": [x.resolve(b)[0]],
                                                 "isPinned": i == 0} for i, b in enumerate(by)],
                                     "root": {"isToggled": True}}]}
    raise ValueError(f"지원하지 않는 역할: {role}")


# ---------------------------------------------------------------- 프로젝트 쓰기
def load_json(p: Path) -> dict:
    return json.load(open(p, encoding="utf-8"))


def main() -> None:
    # 파이프·파일로 출력할 때 시스템 코드 페이지(cp949 등)에 없는 글자(≈)에서 멈추지 않게 UTF-8로 고정한다
    sys.stdout.reconfigure(**({} if sys.stdout.isatty() else {"encoding": "utf-8"}), errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--lang")
    ap.add_argument("--theme")
    ap.add_argument("--local-data", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()
    spec_path = Path(args.spec).resolve()
    spec = load_json(spec_path)
    base = spec_path.parent
    out = Path(args.out).resolve() if args.out else base
    name = spec["name"]
    tmdl = (base / spec["model"]).resolve()
    layouts = {p["id"]: p for p in load_json(LAYOUTS)["pages"]}
    tokens, loc = load_json(TOKENS), load_json(LOCALES)
    lang_code = args.lang or spec.get("lang") or loc["default"]
    theme_id = args.theme or spec.get("theme", "navy")
    if theme_id not in tokens["themes"]:
        sys.exit(f"테마 없음: {theme_id} (가능: {', '.join(tokens['themes'])})")
    t = Lang(lang_code, loc["fallback"], set(loc["locales"]))
    palette = tokens["themes"][theme_id]["color"]
    ui = {**loc["locales"][loc["fallback"]]["ui"], **loc["locales"].get(lang_code, {}).get("ui", {})}

    # 다른 모델이면 대응표(model-map.json)로 먼저 잇는다: 명세의 필드 이름, 표시용 측정값 DAX 안의 열, 연결 측정값
    mmap = load_json((base / spec["modelMap"]).resolve()) if spec.get("modelMap") else {}
    entry = lambda v: v if isinstance(v, dict) else {"expr": v}  # noqa: E731 — 측정값 값은 "DAX" 또는 {"expr", "format"}
    blank = [k for k, v in mmap.get("columns", {}).items() if not v] + [k for k, v in mmap.get("measures", {}).items() if not entry(v).get("expr")]
    if blank:
        sys.exit(f"model map has {len(blank)} empty values; fill them first: {', '.join(blank[:10])}")
    cmap = mmap.get("columns", {})
    if mmap.get("measureTable"):
        spec["measureTable"] = mmap["measureTable"]
    for k in ("pages", "shared"):
        if k in spec:
            spec[k] = rename_fields(spec[k], cmap)

    # 표시용 측정값: 공용 파일({lang} 자리에 언어) → 명세 순서로 덮어쓴다. 언어 파일이 없으면 대체 언어 파일
    raw = {}
    for inc in spec.get("include", []):
        p = (base / inc.replace("{lang}", lang_code)).resolve()
        if not p.exists():
            p = (base / inc.replace("{lang}", loc["fallback"])).resolve()
            print(f"  ! {inc}: '{lang_code}' 파일이 없어 '{loc['fallback']}'로 대신")
        raw.update(load_json(p)["measures"])
    raw.update(spec.get("measures", {}))
    extra = {k: normalize_measure(v, t) for k, v in raw.items()}
    for m in extra.values():
        m["expr"] = rename_columns(m["expr"], cmap)
    model = read_model(tmdl)
    existing = {m for info in model.values() for m in info["measures"]}
    adapters = {}
    for mname, v in mmap.get("measures", {}).items():  # 'name'은 리포트 이름이라 쓰지 않는다
        v = entry(v)
        if mname in extra:  # 공용 표시용 측정값을 이 모델의 식으로 바꿔 쓴다 (예: Orders PY)
            extra[mname]["expr"] = v["expr"]
            extra[mname]["format"] = v.get("format") or extra[mname].get("format")
        elif mname not in existing:
            adapters[mname] = {"expr": v["expr"], "format": v.get("format"), "adapter": True}
    extra = {**adapters, **extra}
    # 부호 글자색 측정값 자동 생성 (format: sign) — 명세에 색 측정값을 따로 적지 않는다
    for page in spec["pages"]:
        for vs in list(page["visuals"].values()) + list(spec.get("shared", {}).values()):
            for fld, kind in vs.get("format", {}).items():
                if kind == "sign":
                    extra.setdefault(sign_measure(fld), {"expr": f"IF ( [{fld}] < 0, \"@negInk\", \"@ink\" )"})
    glossary = load_json((base / spec["glossary"]).resolve())["fields"] if spec.get("glossary") else {}
    glossary = {cmap.get(k, k): v for k, v in glossary.items()}

    model.setdefault(spec["measureTable"], {"columns": set(), "measures": set(), "types": {}})["measures"] |= set(extra)
    resolve = FieldResolver(model, spec["measureTable"])
    # The DAX of display and adapter measures must point at real columns and measures. The validator can't see this and
    # Desktop only shows a broken visual (example 05), so stop here instead. Names made inside the expression ("SalesV") are local (dax_refs skips them).
    known = {m for info in model.values() for m in info["measures"]}
    for mname, m in extra.items():
        cols, meas = dax_refs(m["expr"])
        for c in sorted(cols):
            table, col = c.split(".", 1)
            if col not in model.get(table, {}).get("columns", set()):
                resolve.errors.append(f"DAX of '{mname}': column {c} is not in the model (add it to the model map)")
        for ref in sorted(meas - known):
            resolve.errors.append(f"DAX of '{mname}': measure [{ref}] is not in the model (add it to the model map)")
    x = Ctx(resolve, t, glossary, tokens, palette, ui)

    # 1) 페이지·비주얼을 메모리에서 먼저 만든다 (필드 오류가 있으면 아무것도 쓰지 않는다)
    pages = []
    for page in spec["pages"]:
        lay = layouts[page["layout"]]
        page_key = page.get("id") or page["layout"]  # 같은 레이아웃을 두 번 쓰면 id로 구분
        if any(k == page_key for k, *_ in pages):
            page_key = f"{page_key}-{len(pages)}"
        pid = hid(name, page_key)
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
            vid = hid(name, page_key, rid)
            role = r["role"]
            if vs.get("type") in BAR_FAMILY and role in BAR_FAMILY:  # 막대 방향만은 명세가 바꿀 수 있다 (항목 수에 따라)
                role = vs["type"]
            title = t(vs.get("title"))
            if role in ("advancedSlicerVisual", "dropdownSlicer") and not title:
                title = x.label(vs["field"])  # 슬라이서 제목 기본값 = 용어집 이름
            sub = t(vs.get("sub")) if role != "textbox" else None
            visuals[vid] = container(vid, r, i * 1000, build_visual(role, vs, x, r), title, sub)
        pj = {"$schema": S_PAGE, "name": pid, "displayName": t(page.get("name")) or lay["name"], "displayOption": "FitToPage",
              "height": 720, "width": 1280}
        if page.get("hidden"):
            pj["visibility"] = "HiddenInViewMode"
        if page.get("drillthrough"):
            fexpr = resolve(page["drillthrough"])[0]
            fname = hid(name, pid, "drill")
            pj["filterConfig"] = {"filters": [{"name": fname, "field": fexpr, "type": "Categorical", "howCreated": "Drillthrough"}]}
            pj["pageBinding"] = {"name": hid(name, pid, "binding"), "type": "Drillthrough",
                                 "parameters": [{"name": hid(name, pid, "param"), "boundFilter": fname, "fieldExpr": fexpr}]}
        pages.append((page_key, pid, pj, visuals))
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
    theme_src = THEMES / f"autopilot-{theme_id}.json"
    # 테마가 바뀌면 이름도 바뀐다 (Desktop 캐시 회피). 줄바꿈을 LF로 맞춰 해시해야 Windows와 CI(Linux)가 같은 이름을 만든다
    theme_hash = hashlib.md5(theme_src.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:8]
    theme_file = f"autopilot-{theme_id}-{theme_hash}.json"
    res_dir = rep / "StaticResources" / "RegisteredResources"
    res_dir.mkdir(parents=True, exist_ok=True)
    theme_obj = load_json(theme_src)
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
    write_json(D / "pages" / "pages.json", {"$schema": S_PAGES, "pageOrder": [p[1] for p in pages], "activePageName": pages[0][1]})
    for _, pid, pj, visuals in pages:
        write_json(D / "pages" / pid / "page.json", pj)
        for vid, v in visuals.items():
            write_json(D / "pages" / pid / "visuals" / vid / "visual.json", v)
    write_json(rep / "definition.pbir", {"$schema": S_PBIR, "version": "4.0", "datasetReference": {"byPath": {"path": f"../{name}.SemanticModel"}}})
    write_json(rep / ".platform", {"$schema": S_PLATFORM, "metadata": {"type": "Report", "displayName": name},
                                   "config": {"version": "2.0", "logicalId": str(hashlib.md5((name + 'report').encode()).hexdigest())}})

    shutil.copytree(tmdl, sm / "definition")
    if extra:
        inject_measures(sm / "definition", spec["measureTable"], extra, palette)
    if any(m.get("formatExpr") for m in extra.values()):
        # 동적 서식 문자열(FormatStringDefinition)은 호환성 수준 1601 이상이 필요하다.
        # 1550이면 Desktop이 "필요한 최소 호환성 수준 1601보다 낮습니다"로 모델을 열지 못한다 (복사본만 올린다)
        db = sm / "definition" / "database.tmdl"
        db.write_text(re.sub(r"(compatibilityLevel:\s*)(\d+)", lambda m: m.group(1) + str(max(int(m.group(2)), 1601)),
                             db.read_text(encoding="utf-8")), encoding="utf-8")
    data_note = ""
    if spec.get("dataLocales") and lang_code != spec.get("dataLang", "ko"):
        # 데이터 값 번역이 없는 언어(ja 등)는 화면 글자처럼 대체 언어(영어) 데이터를 쓴다
        data_lang = next((c for c in (lang_code, loc["fallback"]) if (base / spec["dataLocales"] / f"{c}.json").exists()), None)
        if data_lang and data_lang != spec.get("dataLang", "ko"):
            dl = (base / spec["dataLocales"] / f"{data_lang}.json").resolve()
            misses = patch_model(sm / "definition", load_json(dl).get("tmdl", []))
            data_note = f" · 데이터 값 {data_lang}" + (f" (치환 실패 {len(misses)}: {misses})" if misses else "")
        else:
            data_note = f" · 데이터 값은 {spec.get('dataLang', 'ko')} 그대로 ({lang_code} 데이터 로케일 없음)"
    if args.local_data:
        # 자리표시 경로 "C:\path\to\powerbi-autopilot\examples\_data\<데이터>[\en]" → 이 PC의 저장소 경로 (어떤 샘플 데이터든)
        ex = sm / "definition" / "expressions.tmdl"
        ex.write_text(re.sub(r'"[^"]*?(\\examples\\_data\\[^"]+)"', lambda m: '"' + str(ROOT) + m.group(1) + '"',
                             ex.read_text(encoding="utf-8")), encoding="utf-8")
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
    print(f"생성: {out.name}/{name}.pbip · 언어 {lang_code} · 테마 {theme_id} · 페이지 {len(pages)} · 비주얼 {len(vfiles)} · 표시용 측정값 {len(extra)}{data_note}")
    print(f"  명세(에이전트가 쓰는 것)   {spec_bytes / 1024:6.1f}KB  ≈ {spec_bytes // 3:>6,} 토큰")
    print(f"  생성된 리포트 JSON          {rep_bytes / 1024:6.1f}KB  ≈ {rep_bytes // 3:>6,} 토큰 (테마 제외)")
    print(f"  visual.json 평균            {avg / 1024:6.2f}KB  (수집한 PBIR 평균 6.5KB의 {avg / 6656:.0%})")
    if t.missing:
        print(f"  ! '{lang_code}' 번역이 없어 대체 언어로 쓴 글: {len(t.missing)}개 (예: {sorted(t.missing)[:3]})")


if __name__ == "__main__":
    main()
