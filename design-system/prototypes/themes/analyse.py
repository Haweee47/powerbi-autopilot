"""시안이 쓰는 분석 수치를 원본 CSV에서 계산한다.

왜 스크립트인가: 처음에는 집계 파일(retail-data.json)에서 눈대중으로 꺼내 썼다가 두 열을 틀렸다.
`ytd2026[1]`을 이익으로 읽었는데 **원가**였고(마진율이 59%로 나왔다, 실제 41%), 전년 대비는
2026년 8개월을 2025년 **12개월**과 비교해 부호까지 뒤집혔다(−37.7%, 실제 +8.8%).

둘 다 리포트가 쓰는 정의와 어긋난 값이었고, 그 위에서 상관 행렬을 그려 공개까지 했다.
그래서 이제 정의를 한곳에 적고 원본에서 계산한다. 리포트의 측정값과 같은 뜻이어야 한다:

- 이익률  = (매출 − 원가) / 매출
- 전년 대비 = 올해 ÷ **같은 달까지의** 작년 − 1   (8개월 대 12개월을 비교하지 않는다)
- 업력    = 마지막 주문일 − 개점일

    python design-system/prototypes/themes/analyse.py
"""
from __future__ import annotations

import collections
import csv
import datetime
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA = ROOT / "examples" / "_data" / "korean-retail" / "en"
OUT = Path(__file__).resolve().parent
YEAR, PY = 2026, 2025
EN = {"가전": "Electronics", "패션": "Fashion", "식품": "Food", "생활용품": "Home", "뷰티": "Beauty"}


def rows(name: str) -> list[dict]:
    return list(csv.DictReader((DATA / name).open(encoding="utf-8-sig")))


def main() -> None:
    stores = {r["매장코드"]: r for r in rows("매장.csv")}
    prod = {r["제품코드"]: r["카테고리"] for r in rows("제품.csv")}
    sales = rows("판매.csv")

    last = max(datetime.date.fromisoformat(r["주문일자"][:10]) for r in sales
               if r["주문일자"][:4] == str(YEAR))

    s, c, n, s_py = (collections.Counter() for _ in range(4))      # 매장별
    cs, cs_py, cc = (collections.Counter() for _ in range(3))      # 카테고리별
    monthly, monthly_cat = collections.Counter(), collections.Counter()
    for r in sales:
        d = datetime.date.fromisoformat(r["주문일자"][:10])
        k, cat, amt = r["매장코드"], prod[r["제품코드"]], float(r["매출액"])
        if d.year == YEAR:
            s[k] += amt; c[k] += float(r["원가"]); n[k] += 1
            cs[cat] += amt; cc[cat] += float(r["원가"])
            monthly[d.month] += amt
            monthly_cat[(cat, d.month)] += amt
        elif d.year == PY and d.month <= last.month:   # 같은 달까지만 — 리포트와 같은 규칙
            s_py[k] += amt
            cs_py[cat] += amt

    store_rows = []
    for k in sorted(s, key=lambda k: -s[k]):
        store_rows.append(dict(
            name=stores[k]["매장명"],
            sales=s[k], profit=s[k] - c[k],
            margin=(s[k] - c[k]) / s[k] * 100,
            yoy=(s[k] / s_py[k] - 1) * 100 if s_py.get(k) else 0.0,
            orders=n[k], aov=s[k] / n[k],
            age=(last - datetime.date.fromisoformat(stores[k]["개점일"][:10])).days / 365.25))

    VARS = [("Sales", "sales"), ("Profit", "profit"), ("Margin %", "margin"), ("YoY %", "yoy"),
            ("Orders", "orders"), ("Avg order", "aov"), ("Store age", "age")]

    def corr(a: list[float], b: list[float]) -> float:
        m = len(a); ma, mb = sum(a) / m, sum(b) / m
        va = math.sqrt(sum((x - ma) ** 2 for x in a)); vb = math.sqrt(sum((x - mb) ** 2 for x in b))
        return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) if va and vb else 0.0

    M = [[corr([r[x] for r in store_rows], [r[y] for r in store_rows]) for _, y in VARS] for _, x in VARS]
    (OUT / "_analysis.json").write_text(json.dumps(
        {"$comment": "analyse.py 가 원본 CSV에서 계산한다. 손으로 고치지 않는다.",
         "vars": [v for v, _ in VARS], "m": M,
         "rows": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()} for r in store_rows]},
        ensure_ascii=False), encoding="utf-8")

    # 카테고리 × 월 달성률, 작년→올해 다리, 분포, 레이더
    budget = collections.Counter()
    for r in rows("목표.csv"):
        d = datetime.date.fromisoformat(r["목표월"][:10])
        if d.year == YEAR:
            budget[(r["카테고리"], d.month)] += float(r["목표매출액"])
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"][:last.month]
    heat = {cat: [round(monthly_cat[(cat, m)] / budget[(cat, m)] * 100, 1) if budget.get((cat, m)) else None
                  for m in range(1, last.month + 1)] for cat in EN.values()}
    wf = [(cat, round((cs[cat] - cs_py[cat]) / 1e6, 1)) for cat in EN.values()]

    vals = sorted(r["sales"] / 1e6 for r in store_rows)

    def pct(p: float) -> float:
        i = (len(vals) - 1) * p; lo = int(i)
        return vals[lo] + (vals[min(lo + 1, len(vals) - 1)] - vals[lo]) * (i - lo)

    q1, med, q3 = pct(.25), pct(.5), pct(.75)
    iqr = q3 - q1
    out = [(r["name"], round(r["sales"] / 1e6, 1)) for r in store_rows
           if not (q1 - 1.5 * iqr <= r["sales"] / 1e6 <= q3 + 1.5 * iqr)]

    dims = [("Sales", "sales"), ("Margin %", "margin"), ("YoY %", "yoy"),
            ("Orders", "orders"), ("Avg order", "aov"), ("Store age", "age")]
    mx = {k: max(r[k] for r in store_rows) for _, k in dims}
    mn = {k: min(r[k] for r in store_rows) for _, k in dims}
    (OUT / "_analysis2.json").write_text(json.dumps(
        {"$comment": "analyse.py 가 원본 CSV에서 계산한다. 손으로 고치지 않는다.",
         "heat": heat, "months": months, "wf": wf,
         "box": {"min": round(vals[0], 1), "q1": round(q1, 1), "med": round(med, 1),
                 "q3": round(q3, 1), "max": round(vals[-1], 1), "out": out,
                 "all": [round(v, 1) for v in vals],
                 "mean": round(sum(vals) / len(vals), 1)},
         "radar": {"dims": [d for d, _ in dims],
                   "series": [{"name": r["name"],
                               "v": [round((r[k] - mn[k]) / (mx[k] - mn[k]) * 100) for _, k in dims]}
                              for r in store_rows[:3]]}},
        ensure_ascii=False), encoding="utf-8")

    print(f"last order {last} · {len(store_rows)} stores · {len(months)} months")
    print("\nPearson r (upper pairs, strongest first):")
    pairs = sorted(((abs(M[i][j]), VARS[i][0], VARS[j][0], M[i][j])
                    for i in range(len(VARS)) for j in range(i + 1, len(VARS))), reverse=True)
    for _, x, y, v in pairs[:6]:
        print(f"  {x} ~ {y}: r = {v:+.2f}")
    print(f"\nspread (M): min {vals[0]:.1f} Q1 {q1:.1f} median {med:.1f} "
          f"mean {sum(vals)/len(vals):.1f} Q3 {q3:.1f} max {vals[-1]:.1f} | outliers {out}")
    print("radar top 3:", [(x["name"], x["v"]) for x in json.loads((OUT / "_analysis2.json").read_text(encoding="utf-8"))["radar"]["series"]])


if __name__ == "__main__":
    main()
