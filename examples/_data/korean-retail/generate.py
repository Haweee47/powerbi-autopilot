"""한국어 가상 소매 판매 데이터 생성기.

세 가지 도구(skills-for-fabric / data-goblin / powerbi-modeling-mcp)가
똑같은 입력으로 리포트를 만들도록 공용 데이터를 만든다.
시드를 고정했으므로 누가 실행해도 같은 CSV가 나온다.

실행: python generate.py
결과: 판매.csv, 제품.csv, 매장.csv, 목표.csv (UTF-8 BOM)
"""
import csv
import datetime as dt
import random
from collections import defaultdict
from pathlib import Path

SEED = 20260911
START = dt.date(2024, 1, 1)
END = dt.date(2026, 8, 31)  # 기준일: 2026-08 말 (전월까지 마감)
OUT = Path(__file__).parent

# 제품코드, 제품명, 카테고리, 하위카테고리, 정가(원), 원가율
PRODUCTS = [
    ("P001", "55형 OLED TV", "가전", "영상가전", 2190000, 0.78),
    ("P002", "무선청소기", "가전", "생활가전", 689000, 0.72),
    ("P003", "공기청정기", "가전", "생활가전", 459000, 0.70),
    ("P004", "전자레인지", "가전", "주방가전", 189000, 0.74),
    ("P005", "에어프라이어", "가전", "주방가전", 149000, 0.68),
    ("P006", "커피머신", "가전", "주방가전", 329000, 0.66),
    ("P007", "무선이어폰", "가전", "음향기기", 219000, 0.64),
    ("P008", "블루투스 스피커", "가전", "음향기기", 129000, 0.62),
    ("P011", "경량 패딩", "패션", "아우터", 129000, 0.45),
    ("P012", "트렌치코트", "패션", "아우터", 189000, 0.42),
    ("P013", "니트 스웨터", "패션", "상의", 59000, 0.40),
    ("P014", "옥스퍼드 셔츠", "패션", "상의", 45000, 0.38),
    ("P015", "와이드 청바지", "패션", "하의", 69000, 0.40),
    ("P016", "러닝화", "패션", "신발", 119000, 0.50),
    ("P017", "가죽 백팩", "패션", "잡화", 89000, 0.44),
    ("P018", "린넨 원피스", "패션", "상의", 79000, 0.41),
    ("P021", "한우 선물세트", "식품", "신선식품", 159000, 0.70),
    ("P022", "제주 감귤 5kg", "식품", "신선식품", 29000, 0.62),
    ("P023", "유기농 쌀 10kg", "식품", "가공식품", 42000, 0.66),
    ("P024", "견과류 믹스", "식품", "가공식품", 19900, 0.55),
    ("P025", "김 선물세트", "식품", "가공식품", 24900, 0.58),
    ("P026", "콜드브루 커피", "식품", "음료", 12900, 0.48),
    ("P027", "그릭요거트", "식품", "신선식품", 8900, 0.52),
    ("P028", "홍삼정", "식품", "건강식품", 89000, 0.50),
    ("P031", "극세사 이불", "생활용품", "침구", 79000, 0.48),
    ("P032", "호텔 수건 세트", "생활용품", "욕실", 29900, 0.45),
    ("P033", "세탁세제", "생활용품", "욕실", 18900, 0.55),
    ("P034", "주방칼 세트", "생활용품", "주방", 69000, 0.46),
    ("P035", "수납박스", "생활용품", "인테리어", 15900, 0.42),
    ("P036", "디퓨저", "생활용품", "인테리어", 32000, 0.35),
    ("P037", "보온 텀블러", "생활용품", "주방", 27000, 0.40),
    ("P038", "캠핑 의자", "생활용품", "레저", 49000, 0.47),
    ("P041", "수분크림", "뷰티", "스킨케어", 38000, 0.30),
    ("P042", "선크림", "뷰티", "스킨케어", 22000, 0.32),
    ("P043", "비타민C 세럼", "뷰티", "스킨케어", 45000, 0.28),
    ("P044", "쿠션 파운데이션", "뷰티", "메이크업", 42000, 0.33),
    ("P045", "립스틱", "뷰티", "메이크업", 29000, 0.30),
    ("P046", "탈모 샴푸", "뷰티", "헤어/바디", 16900, 0.36),
    ("P047", "마스크팩 10매", "뷰티", "스킨케어", 15000, 0.34),
    ("P048", "오드퍼퓸 50ml", "뷰티", "향수", 98000, 0.38),
]

# 매장코드, 매장명, 시도, 권역, 채널, 개점일, 규모 가중치
STORES = [
    ("S01", "강남점", "서울", "수도권", "오프라인", "2015-03-01", 1.6),
    ("S02", "여의도점", "서울", "수도권", "오프라인", "2016-05-01", 1.2),
    ("S03", "홍대점", "서울", "수도권", "오프라인", "2017-09-01", 1.1),
    ("S04", "잠실점", "서울", "수도권", "오프라인", "2014-11-01", 1.5),
    ("S05", "판교점", "경기", "수도권", "오프라인", "2024-09-01", 1.3),
    ("S06", "수원점", "경기", "수도권", "오프라인", "2018-04-01", 1.0),
    ("S07", "일산점", "경기", "수도권", "오프라인", "2013-06-01", 0.9),
    ("S08", "송도점", "인천", "수도권", "오프라인", "2019-10-01", 0.9),
    ("S09", "서면점", "부산", "영남", "오프라인", "2015-08-01", 1.2),
    ("S10", "센텀점", "부산", "영남", "오프라인", "2017-03-01", 1.1),
    ("S11", "동성로점", "대구", "영남", "오프라인", "2016-07-01", 0.9),
    ("S12", "울산점", "울산", "영남", "오프라인", "2019-02-01", 0.7),
    ("S13", "충장로점", "광주", "호남", "오프라인", "2018-11-01", 0.8),
    ("S14", "전주점", "전북", "호남", "오프라인", "2020-05-01", 0.6),
    ("S15", "둔산점", "대전", "충청", "오프라인", "2017-12-01", 0.9),
    ("S16", "청주점", "충북", "충청", "오프라인", "2021-03-01", 0.6),
    ("S17", "제주점", "제주", "제주", "오프라인", "2020-08-01", 0.5),
    ("S18", "강릉점", "강원", "강원", "오프라인", "2022-06-01", 0.4),
    ("ON1", "공식 온라인몰", "전국", "온라인", "온라인", "2012-01-01", 2.4),
    ("ON2", "모바일 앱", "전국", "온라인", "온라인", "2020-01-01", 2.0),
]

# 월별 계절성 (1월 설, 9월 추석, 11월 블랙프라이데이, 12월 연말)
MONTH_SEASON = {1: 1.10, 2: 0.82, 3: 0.90, 4: 0.92, 5: 1.00, 6: 0.94,
                7: 0.97, 8: 0.93, 9: 1.08, 10: 1.00, 11: 1.18, 12: 1.28}

# 카테고리 × 월 추가 계절성
CATEGORY_SEASON = {
    "식품": {1: 1.6, 9: 1.7},              # 명절 선물세트
    "패션": {10: 1.3, 11: 1.4, 12: 1.3, 1: 1.2, 6: 0.8, 7: 0.8},
    "가전": {11: 1.4, 12: 1.3, 3: 1.1},
    "생활용품": {3: 1.2, 4: 1.2, 5: 1.1},  # 이사·캠핑철
    "뷰티": {5: 1.2, 12: 1.2},
}

# 연간 성장률 (카테고리) — 가전은 역성장, 뷰티는 고성장
CATEGORY_GROWTH = {"가전": -0.06, "패션": 0.02, "식품": 0.04,
                   "생활용품": 0.03, "뷰티": 0.16}
CHANNEL_GROWTH = {"오프라인": 0.00, "온라인": 0.20}
STORE_EXTRA_GROWTH = {"S07": -0.12, "S03": 0.08}  # 일산점 부진, 홍대점 호조

# 카테고리별 선택 가중치 (거래 건수 기준)
CATEGORY_WEIGHT = {"가전": 0.12, "패션": 0.24, "식품": 0.26,
                   "생활용품": 0.18, "뷰티": 0.20}

BASE_LINES_PER_DAY = 20.0


def years_since_start(day: dt.date) -> float:
    return (day - START).days / 365.25


def discount_for(day: dt.date, rng: random.Random) -> float:
    options = [0.0, 0.05, 0.10, 0.20, 0.30]
    if day.month in (11, 12):
        weights = [0.35, 0.20, 0.20, 0.15, 0.10]
    else:
        weights = [0.60, 0.18, 0.14, 0.06, 0.02]
    return rng.choices(options, weights)[0]


def quantity_for(category: str, rng: random.Random) -> int:
    if category in ("식품", "뷰티"):
        return rng.choices([1, 2, 3, 4, 5], [0.45, 0.28, 0.14, 0.08, 0.05])[0]
    if category == "가전":
        return rng.choices([1, 2], [0.92, 0.08])[0]
    return rng.choices([1, 2, 3], [0.70, 0.22, 0.08])[0]


def poisson(lam: float, rng: random.Random) -> int:
    # 표준 라이브러리만 쓰기 위한 정규 근사 (lam이 충분히 큼)
    return max(0, round(rng.gauss(lam, lam ** 0.5)))


def main() -> None:
    rng = random.Random(SEED)
    by_cat = defaultdict(list)
    for p in PRODUCTS:
        by_cat[p[2]].append(p)
    categories = list(CATEGORY_WEIGHT)

    sales_rows = []
    monthly_actual = defaultdict(float)  # (YYYY-MM, 카테고리) -> 매출
    seq = 0
    day = START
    while day <= END:
        t = years_since_start(day)
        weekend = day.weekday() >= 5
        for store in STORES:
            code, _, _, _, channel, opened, size = store
            if day < dt.date.fromisoformat(opened):
                continue
            store_growth = (1 + CHANNEL_GROWTH[channel] + STORE_EXTRA_GROWTH.get(code, 0)) ** t
            day_factor = 1.3 if (weekend and channel == "오프라인") else 1.0
            for cat in categories:
                lam = (BASE_LINES_PER_DAY / len(STORES) * size * CATEGORY_WEIGHT[cat]
                       * MONTH_SEASON[day.month]
                       * CATEGORY_SEASON[cat].get(day.month, 1.0)
                       * (1 + CATEGORY_GROWTH[cat]) ** t
                       * store_growth * day_factor)
                # 기대값이 작으므로 확률적 반올림으로 건수 결정
                n = int(lam) + (1 if rng.random() < lam - int(lam) else 0)
                for _ in range(n):
                    prod = rng.choice(by_cat[cat])
                    pcode, _, _, _, price, cost_rate = prod
                    qty = quantity_for(cat, rng)
                    disc = discount_for(day, rng)
                    revenue = round(qty * price * (1 - disc))
                    cost = round(qty * price * cost_rate)
                    seq += 1
                    sales_rows.append([
                        f"O{day:%Y%m%d}-{seq:06d}", day.isoformat(), code, pcode,
                        qty, price, disc, revenue, cost,
                    ])
                    monthly_actual[(f"{day:%Y-%m}", cat)] += revenue
        day += dt.timedelta(days=1)

    # 목표: 2024년은 실적 ±, 2025년 이후는 전년 동월 실적 × 1.06
    target_rows = []
    for (ym, cat), actual in sorted(monthly_actual.items()):
        year, month = int(ym[:4]), int(ym[5:])
        if year == 2024:
            target = actual * rng.uniform(0.94, 1.08)
        else:
            prev = monthly_actual.get((f"{year - 1}-{month:02d}", cat), actual)
            target = prev * 1.06
        target_rows.append([f"{ym}-01", cat, round(target, -6)])  # 백만원 단위 반올림

    def write(name, header, rows):
        with open(OUT / name, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)

    write("판매.csv",
          ["주문번호", "주문일자", "매장코드", "제품코드", "수량", "정가", "할인율", "매출액", "원가"],
          sales_rows)
    write("제품.csv",
          ["제품코드", "제품명", "카테고리", "하위카테고리", "정가", "원가율"],
          [list(p) for p in PRODUCTS])
    write("매장.csv",
          ["매장코드", "매장명", "시도", "권역", "채널", "개점일"],
          [list(s[:6]) for s in STORES])
    write("목표.csv", ["목표월", "카테고리", "목표매출액"], target_rows)

    total = sum(r[7] for r in sales_rows)
    print(f"판매 {len(sales_rows):,}행 / 총매출 {total / 1e8:,.1f}억 원 / 목표 {len(target_rows)}행")


if __name__ == "__main__":
    main()
