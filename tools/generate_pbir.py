"""명세(report.spec.json) → PBIP 프로젝트(.pbip + .Report + .SemanticModel) 생성기.

에이전트는 작은 명세만 쓴다. 나머지는 이 스크립트가 채운다.
- 좌표: design-system/layouts/layouts.resolved.json (페이지 유형별 1280×720 템플릿)
- 서식: design-system/themes/<theme>.json (visual.json에는 서식을 넣지 않는다)
- 모델: 명세의 "model" 폴더(TMDL)를 .SemanticModel/definition 으로 복사

만들기 전에 명세의 필드 이름을 TMDL의 실제 열·측정값과 대조한다. 오타는 여기서 막는다 (토큰 0).
비주얼·페이지 ID는 이름에서 해시로 만든다 → 다시 생성해도 파일이 같다 (git diff가 깔끔).

PBIR 구조는 Microsoft skills-for-fabric 작성 스킬 문서와 공개 PBIR 예시에서 확인한 형식을 따르고,
결과는 `powerbi-report-author validate`로 검증한다.

사용법: python tools/generate_pbir.py examples/04-autopilot/report.spec.json [--local-data]
  --local-data  M 매개변수 '데이터폴더'를 이 PC의 실제 경로로 바꾼다 (커밋용 산출물에는 쓰지 말 것)
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


def hid(*parts: str, n: int = 20) -> str:
    return hashlib.md5("/".join(parts).encode("utf-8")).hexdigest()[:n]


def lit(value) -> dict:
    """PBIR 식 표기: 문자열은 작은따옴표로 감싸고 안의 작은따옴표는 두 번 쓴다."""
    if isinstance(value, bool):
        return {"expr": {"Literal": {"Value": "true" if value else "false"}}}
    if isinstance(value, (int, float)):
        return {"expr": {"Literal": {"Value": f"{value}D"}}}
    return {"expr": {"Literal": {"Value": "'" + str(value).replace("'", "''") + "'"}}}


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- 모델 읽기 · 필드 해석
def read_model(tmdl_dir: Path) -> dict:
    """TMDL에서 테이블별 열·측정값 이름을 모은다."""
    fields = {}
    for f in (tmdl_dir / "tables").glob("*.tmdl"):
        table, cols, meas = None, set(), set()
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^table\s+(?:'([^']+)'|(\S+))", line)
            if m:
                table = m.group(1) or m.group(2)
            m = re.match(r"^\t(column|measure)\s+(?:'([^']+)'|([^\s=]+))", line)
            if m:
                (cols if m.group(1) == "column" else meas).add(m.group(2) or m.group(3))
        if table:
            fields[table] = {"columns": cols, "measures": meas}
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


# ---------------------------------------------------------------- 비주얼 만들기 (서식 없음: 위치·필드·제목만)
def container(name: str, region: dict, z: int, visual: dict, title: str | None = None) -> dict:
    v = {"$schema": S_VISUAL, "name": name,
         "position": {"x": region["x"], "y": region["y"], "z": z, "height": region["height"], "width": region["width"], "tabOrder": z},
         "visual": visual}
    if title:
        v["visual"]["visualContainerObjects"] = {"title": [{"properties": {"text": lit(title)}}]}
    return v


def projection(resolve, ref: str, display: str | None = None, active: bool = False) -> dict:
    expr, qref, nref = resolve(ref)
    p = {"field": expr, "queryRef": qref, "nativeQueryRef": nref}
    if display:
        p["displayName"] = display
    if active:
        p["active"] = True
    return p


def sort_def(resolve, ref: str, direction: str) -> dict:
    return {"sort": [{"field": resolve(ref)[0], "direction": "Ascending" if direction.startswith("asc") else "Descending"}], "isDefaultSort": False}


def build_visual(role: str, spec: dict, resolve, tokens: dict) -> dict:
    if role == "textbox":
        pt, c = tokens["type"]["pt"], tokens["color"]["light"]
        big = spec.get("sub") is not None
        runs = [{"textRuns": [{"value": spec["text"], "textStyle": {"fontFamily": tokens["font"]["semibold"] if big else tokens["font"]["family"],
                                                                     "fontSize": f"{pt['page'] if big else pt['body']}pt"}}],
                 "horizontalTextAlignment": "left"}]
        if big:
            runs.append({"textRuns": [{"value": spec["sub"], "textStyle": {"fontFamily": tokens["font"]["family"], "fontSize": f"{pt['body']}pt", "color": c["ink3"]}}],
                         "horizontalTextAlignment": "left"})
        return {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": runs}}]}}
    if role == "pageNavigator":
        return {"visualType": "pageNavigator"}
    if role == "actionButton":
        return {"visualType": "actionButton",
                "objects": {"icon": [{"properties": {"shapeType": lit("back")}, "selector": {"id": "default"}}]},
                "visualContainerObjects": {"visualLink": [{"properties": {"show": lit(True), "type": lit(spec.get("action", "Back"))}}]}}
    if role == "advancedSlicerVisual":
        return {"visualType": "advancedSlicerVisual", "query": {"queryState": {"Values": {"projections": [projection(resolve, spec["field"])]}}}}
    if role == "cardVisual":
        return {"visualType": "cardVisual", "query": {"queryState": {"Data": {"projections": [projection(resolve, spec["measure"], spec.get("label"))]}}}}
    if role in ("lineChart", "barChart"):
        qs = {"Category": {"projections": [projection(resolve, spec["x"], active=True)]},
              "Y": {"projections": [projection(resolve, m) for m in spec["y"]]}}
        if spec.get("small"):
            qs["Rows"] = {"projections": [projection(resolve, spec["small"])]}
        q = {"queryState": qs}
        if spec.get("sort"):
            q["sortDefinition"] = sort_def(resolve, spec["y"][0], spec["sort"])
        return {"visualType": role, "query": q}
    if role == "scatterChart":
        return {"visualType": "scatterChart", "query": {"queryState": {
            "Category": {"projections": [projection(resolve, spec["point"], active=True)]},
            "X": {"projections": [projection(resolve, spec["x"])]},
            "Y": {"projections": [projection(resolve, spec["y"])]}}}}
    if role == "tableEx":
        q = {"queryState": {"Values": {"projections": [projection(resolve, c) for c in spec["columns"]]}}}
        if spec.get("sort"):
            q["sortDefinition"] = sort_def(resolve, spec["sort"][0], spec["sort"][1])
        return {"visualType": "tableEx", "query": q}
    raise ValueError(f"지원하지 않는 역할: {role}")


# ---------------------------------------------------------------- 프로젝트 쓰기
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--local-data", action="store_true")
    args = ap.parse_args()
    spec_path = Path(args.spec).resolve()
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = spec_path.parent
    name = spec["name"]
    tmdl = (base / spec["model"]).resolve()
    layouts = {p["id"]: p for p in json.load(open(LAYOUTS, encoding="utf-8"))["pages"]}
    tokens = json.load(open(TOKENS, encoding="utf-8"))
    resolve = FieldResolver(read_model(tmdl), spec["measureTable"])

    # 1) 페이지·비주얼을 메모리에서 먼저 만든다 (필드 오류가 있으면 아무것도 쓰지 않는다)
    pages, pbir = [], {}
    for page in spec["pages"]:
        lay = layouts[page["layout"]]
        pid = hid(name, page["layout"])
        regions = {r["id"]: r for r in lay["regions"]}
        visuals = {}
        order = sorted(page["visuals"], key=lambda k: (regions[k]["y"], regions[k]["x"]))
        for i, rid in enumerate(order, 1):
            if rid not in regions:
                resolve.errors.append(f"{page['layout']}: 레이아웃에 없는 영역 {rid}")
                continue
            r, vs = regions[rid], page["visuals"][rid]
            vid = hid(name, page["layout"], rid)
            visuals[vid] = container(vid, r, i * 1000, build_visual(r["role"], vs, resolve, tokens), vs.get("title"))
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
    rep, sm = base / f"{name}.Report", base / f"{name}.SemanticModel"
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
    if args.local_data:
        ex = sm / "definition" / "expressions.tmdl"
        data_dir = str((ROOT / "examples" / "_data" / "korean-retail").resolve())
        ex.write_text(re.sub(r'"[^"]*korean-retail"', '"' + data_dir.replace("\\", "\\\\") + '"', ex.read_text(encoding="utf-8")), encoding="utf-8")
    write_json(sm / "definition.pbism", {"$schema": S_PBISM, "version": "4.2", "settings": {}})
    write_json(sm / ".platform", {"$schema": S_PLATFORM, "metadata": {"type": "SemanticModel", "displayName": name},
                                  "config": {"version": "2.0", "logicalId": str(hashlib.md5((name + 'model').encode()).hexdigest())}})
    write_json(base / f"{name}.pbip", {"$schema": S_PBIP, "version": "1.0", "artifacts": [{"report": {"path": f"{name}.Report"}}],
                                       "settings": {"enableAutoRecovery": True}})

    # 3) 토큰 관점의 크기 비교
    vfiles = list(D.rglob("visual.json"))
    rep_bytes = sum(f.stat().st_size for f in rep.rglob("*") if f.is_file() and f.suffix == ".json" and "StaticResources" not in f.parts)
    spec_bytes = spec_path.stat().st_size
    avg = sum(f.stat().st_size for f in vfiles) / len(vfiles)
    print(f"생성: {base.name}/{name}.pbip · 페이지 {len(pages)} · 비주얼 {len(vfiles)}")
    print(f"  명세(에이전트가 쓰는 것)   {spec_bytes / 1024:6.1f}KB  ≈ {spec_bytes // 3:>6,} 토큰")
    print(f"  생성된 리포트 JSON          {rep_bytes / 1024:6.1f}KB  ≈ {rep_bytes // 3:>6,} 토큰 (테마 제외)")
    print(f"  visual.json 평균            {avg / 1024:6.2f}KB  (수집한 PBIR 평균 6.5KB의 {avg / 6656:.0%})")


if __name__ == "__main__":
    main()
