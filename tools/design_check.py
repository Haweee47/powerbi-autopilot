"""명세를 채점표(design-system/review-rubric.md)의 기계 검사 가능한 항목으로 검사한다.

왜 있나: 채점표 31개 항목은 지금까지 사람이 캡처를 보고 매겼다. 그런데 2026-09-26에 대비 검사를 자동화하자마자
**이미 배포된 테마 2종**(paper 4.42:1, midnight 3.64:1)이 걸렸다. 눈으로 7종을 검토하고 내보냈는데 둘이 틀려 있었다.
눈은 일관되지 않고, 파일럿 밖의 명세(에이전트·사용자가 새로 쓰는 것)는 아무도 검토하지 않는다.

무엇을 보나: 생성 전 **명세**만 본다. 생성된 PBIR을 읽지 않으므로 토큰이 들지 않고, Desktop을 열기 전에 멈춘다.
역할(role)은 명세가 아니라 레이아웃 영역에서 오므로 layouts.resolved.json에서 읽는다.

무엇을 보지 않나: 캡처를 봐야 아는 항목(잘림, 실제 렌더링, 숫자 정합)은 여기서 검사하지 않는다.
그것은 render_check.ps1과 사람의 몫이다. 이 스크립트가 통과했다고 "완성"이 아니다.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# 검사에서 빼는 역할: 화면 틀(레일 바탕·제목·이동·버튼·슬라이서)은 본문 시각이 아니다
CHROME = {"shape", "textbox", "pageNavigator", "actionButton", "headline", "context",
          "advancedSlicerVisual", "dropdownSlicer"}
CHARTS = {"lineChart", "barChart", "columnChart", "scatterChart"}
BARS = {"barChart", "columnChart"}
TABLES = {"tableEx", "pivotTable"}


def lum(h: str) -> float:
    v = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    v = [(x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4) for x in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def ratio(a: str, b: str) -> float:
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def ordered_columns(model_dir: Path) -> set[str]:
    """모델이 정렬 순서를 정해 둔 열(`sortByColumn`)의 집합. "테이블.열" 꼴.

    시간대·도착 시간대·공정처럼 순서가 있는 축은 값 순으로 정렬하면 오히려 틀린다. 모델이 이미 순서를 정했으면
    막대에 sort가 없는 것이 정상이다. 이 검사의 첫 판이 파일럿에서 4건을 올렸는데 전부 이 경우였다.
    """
    out: set[str] = set()
    if not model_dir.is_dir():
        return out
    for f in model_dir.rglob("*.tmdl"):
        table, col = f.stem, None
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            t = line.strip()
            if t.startswith("column "):
                # 계산 열은 `column '이름' = 식` 꼴이라 등호 앞까지가 이름이다
                col = t[len("column "):].split(" = ", 1)[0].strip().strip("'")
            elif t.startswith("sortByColumn:") and col:
                out.add(f"{table}.{col}")
    return out


def roles_of(resolved: dict) -> dict[str, dict]:
    """레이아웃 id → {regions: {영역 id: 영역}, purpose}. 역할은 명세가 아니라 레이아웃이 정한다."""
    return {p["id"]: {"regions": {r["id"]: r for r in p["regions"]}, "purpose": p.get("purpose")}
            for p in resolved["pages"]}


def check_spec(spec: dict, layouts: dict, tokens: dict, theme_id: str | None,
               ordered: set[str] | None = None) -> list[str]:
    out: list[str] = []
    ordered = ordered or set()
    theme_id = theme_id or spec.get("theme") or "navy"
    theme = tokens["themes"].get(theme_id)
    pages = spec.get("pages", [])

    visible = [p for p in pages if not p.get("hidden")]
    # G1: 보이는 탭 5~7개. 드릴스루 같은 숨은 페이지는 세지 않는다
    if len(visible) > 7:
        out.append(f"G1 보이는 페이지가 {len(visible)}개다 (채점표: 5~7). 묶거나 드릴스루로 내린다")

    for page in pages:
        lay = page.get("layout")
        entry = layouts.get(lay)
        where = f"{lay}"
        if entry is None:
            continue  # 없는 레이아웃은 생성기가 이미 오류로 잡는다
        regions = entry["regions"]
        for rid, vs in (page.get("visuals") or {}).items():
            reg = regions.get(rid)
            if reg is None or not isinstance(vs, dict):
                continue
            role = vs.get("type") if vs.get("type") in BARS and reg["role"] in BARS else reg["role"]
            if reg.get("zone") == "rail" or reg.get("layer") == "background" or role in CHROME:
                continue
            # A4 / H5: KPI 카드에는 비교 기준(전년·목표)이 반드시 붙는다. 숫자만 덩그러니 있는 카드 금지
            if role == "cardVisual" and not vs.get("ref"):
                out.append(f"A4 {where}/{rid}: KPI에 비교 기준이 없다 (ref: 전년·목표 측정값을 단다)")

            # D3: 제목이 비어 있으면 Power BI가 "Sum of X by Y"를 쓴다
            if role in CHARTS | TABLES and not vs.get("title"):
                out.append(f"D3 {where}/{rid}: 제목이 없다 (기본 제목 'Sum of X by Y'가 나온다)")

            # C3: 막대는 의도한 순서로. 정렬을 안 적으면 이름 순으로 나와 1위가 안 보인다.
            # 단, 모델이 그 열의 순서를 이미 정했으면(sortByColumn) 그대로 두는 것이 맞다
            if role in BARS and not vs.get("sort") and str(vs.get("x", "")) not in ordered:
                out.append(f"C3 {where}/{rid}: 막대에 sort가 없다 (값 순서가 아니라 이름 순으로 나온다)")

            # E3(마크): 계열이 늘어나면 팔레트 뒤쪽 색까지 쓴다. 카드 바탕과 3:1 미만이면 막대가 잘 안 보인다
            ys = vs.get("y")
            if theme and isinstance(ys, list) and role in CHARTS:
                surface = theme["color"]["surface"]
                for i, col in enumerate(theme["categorical"][:len(ys)]):
                    r = ratio(col, surface)
                    if r < 3.0:
                        out.append(f"E3 {where}/{rid}: 계열 {i + 1} 색 {col}이 카드 바탕과 {r:.2f}:1 "
                                   f"(채점표: 막대·선 3:1). 계열을 줄이거나 팔레트 앞쪽 색을 쓴다")

        # 채점표 A3(한 화면의 묶음 수)은 여기서 보지 않는다. 명세는 레이아웃에 있는 영역보다 많이 놓을 수 없으므로
        # 이 검사는 절대 실패할 수 없다. 그 항목은 레이아웃 템플릿을 만들 때 본다 (build_layouts.check)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="명세를 채점표의 기계 검사 항목으로 검사한다")
    ap.add_argument("specs", nargs="*", help="pilot.spec.json 경로 (없으면 templates/*/pilot.spec.json 전부)")
    ap.add_argument("--theme", help="이 테마로 색 대비를 검사한다 (없으면 명세의 theme)")
    args = ap.parse_args()

    resolved = json.loads((DS / "layouts" / "layouts.resolved.json").read_text(encoding="utf-8"))
    tokens = json.loads((DS / "tokens.json").read_text(encoding="utf-8"))
    layouts = roles_of(resolved)

    paths = [Path(p) for p in args.specs] or sorted(ROOT.glob("templates/*/pilot.spec.json"))
    total = 0
    for p in paths:
        spec = json.loads(p.read_text(encoding="utf-8"))
        ordered = ordered_columns((p.parent / spec.get("model", "model")).resolve())
        problems = check_spec(spec, layouts, tokens, args.theme, ordered)
        name = p.parent.name
        if problems:
            total += len(problems)
            print(f"{name}: {len(problems)}건")
            for m in problems:
                print(f"   ! {m}")
        else:
            print(f"{name}: 통과")
    print(f"\n{'문제 ' + str(total) + '건' if total else '검사한 항목 모두 통과'} "
          f"(명세 {len(paths)}개). 캡처로만 알 수 있는 항목은 여기서 검사하지 않는다.")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
