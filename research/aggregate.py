"""analyze_reports.py 결과(summaries.jsonl)를 모아 디자인 통계와 품질 후보 순위를 만든다.

품질 점수는 '눈으로 볼 후보를 고르기 위한' 거친 휴리스틱이다. 예쁘다는 판단은 스크린샷으로 한다.
- 정렬: 비주얼당 서로 다른 모서리 수가 적을수록 (같은 선에 맞춰 배치)
- 겹침 없음, 사용자 테마 사용, 페이지당 비주얼 5~14개, 캔버스 사용률 55~95%
- 직접 지정 색이 적을수록 (서식을 테마로 관리)

사용법: python aggregate.py summaries.jsonl [--top 40] > design_stats.md
"""
import argparse
import json
import statistics as st
from collections import Counter

import re

# Microsoft 기본 테마: "CY24SU10"처럼 연도·업데이트 번호 형식이거나 Desktop 내장 테마 이름
RE_BASE_THEME = re.compile(r"^CY\d{2}SU\d{2}$")
BUILTIN_THEMES = {None, "", "Default", "CityPark", "City Park", "Classroom", "Colorblind safe", "Electric", "High Contrast",
                  "Sunset", "Twilight", "Executive", "Frontier", "Innovate", "Bloom", "Tidal", "Temperature", "Solar",
                  "Divergent", "Storm", "Accessible default", "Accessible Tidal", "Accessible Neutral",
                  "Accessible Orchid", "Accessible City park", "Highrise", "Fluent 2 (Preview)"}


def is_custom_theme(name) -> bool:
    return name not in BUILTIN_THEMES and not RE_BASE_THEME.match(str(name))


def score(s: dict) -> float:
    pts = 0.0
    e = s.get("edges_per_visual")
    if e is not None:
        pts += max(0.0, 3.2 - e) * 10          # 정렬 (최대 약 20점)
    pts += 15 if s.get("overlaps", 1) == 0 else max(0, 10 - 2 * s["overlaps"])
    pts += 15 if is_custom_theme((s.get("theme") or {}).get("name")) else 0
    vpp = s.get("visuals_per_page") or 0
    pts += 10 if 5 <= vpp <= 14 else 0
    cov = s.get("coverage_med") or 0
    pts += 10 if 0.55 <= cov <= 0.95 else 0
    pts += max(0, 10 - s.get("explicit_colors", 0) / 3)  # 색을 테마로 관리할수록 가산
    pts += 5 if s.get("uses_cardVisual") else 0
    return round(pts, 1)


def pct(values, q):
    values = sorted(v for v in values if v is not None)
    return values[min(len(values) - 1, int(len(values) * q))] if values else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.jsonl, encoding="utf-8") if l.strip()]
    ok = [r for r in rows if "error" not in r and r.get("visuals")]
    print(f"# 수집 리포트 디자인 통계\n\n분석 성공 {len(ok)}개 / 실패·빈 리포트 {len(rows) - len(ok)}개\n")

    print("## 분포 (중앙값, 하위 25% ~ 상위 25%)\n")
    print("| 지표 | 중앙값 | 25% | 75% |\n|---|---:|---:|---:|")
    for key, label in [("pages", "페이지 수"), ("visuals_per_page", "페이지당 비주얼"), ("left_margin_med", "왼쪽 여백(px)"),
                       ("gap_med", "가로 간격(px)"), ("edges_per_visual", "비주얼당 모서리 수(낮을수록 정렬)"),
                       ("coverage_med", "캔버스 사용률"), ("decor_ratio", "장식 요소 비율"), ("explicit_colors", "직접 지정 색 개수")]:
        vals = [r.get(key) for r in ok]
        print(f"| {label} | {pct(vals, .5)} | {pct(vals, .25)} | {pct(vals, .75)} |")

    def top(counter, n=12):
        total = sum(counter.values())
        return ", ".join(f"{k} {v / total:.0%}" for k, v in counter.most_common(n))

    types = Counter()
    for r in ok:
        types.update(r["types"])
    print(f"\n## 비주얼 종류 (전체 비주얼 대비)\n\n{top(types, 15)}\n")
    print(f"## 페이지 크기\n\n{top(Counter(r['page_size'] for r in ok), 6)}\n")
    fonts = Counter()
    for r in ok:
        fonts.update(r.get("fonts", {}))
    tfonts = Counter((r.get("theme") or {}).get("font") for r in ok if (r.get("theme") or {}).get("font"))
    print(f"## 글꼴\n\n- 비주얼에 직접 지정: {top(fonts, 8) or '없음'}\n- 테마 기본: {top(tfonts, 8) or '없음'}\n")
    sizes = Counter()
    for r in ok:
        sizes.update({float(k): v for k, v in r.get("font_sizes", {}).items()})
    print(f"## 직접 지정한 글자 크기\n\n{top(sizes, 12) or '없음'}\n")
    themes = Counter((r.get("theme") or {}).get("name") for r in ok)
    print(f"## 테마\n\n{top(themes, 15)}\n")
    bgs = Counter((r.get("theme") or {}).get("background") for r in ok if (r.get("theme") or {}).get("background"))
    print(f"- 배경색: {top(bgs, 8)}\n- 새 카드(cardVisual) 사용 리포트: "
          f"{sum(r.get('uses_cardVisual', False) for r in ok)}개 / 구형 card 사용: {sum(r.get('uses_legacy_card', False) for r in ok)}개\n")

    print(f"## 품질 후보 상위 {args.top} (휴리스틱 점수 — 스크린샷으로 최종 판단)\n")
    print("| 점수 | 파일 | 페이지 | 비주얼/페이지 | 모서리/비주얼 | 겹침 | 테마 |\n|---:|---|---:|---:|---:|---:|---|")
    for r in sorted(ok, key=score, reverse=True)[: args.top]:
        name = r["file"].replace("\\", "/").split("/collected/")[-1]
        print(f"| {score(r)} | {name[:90]} | {r['pages']} | {r['visuals_per_page']} | {r.get('edges_per_visual')} | "
              f"{r.get('overlaps')} | {(r.get('theme') or {}).get('name')} |")


if __name__ == "__main__":
    main()
