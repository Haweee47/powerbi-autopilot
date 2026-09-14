"""English sample data for a model that is *not* the reference model: an outdoor gear retailer.

Example 05 uses it to test "bring your own model". The model differs from the reference model on purpose, the way
real models do: English names, measures on the fact table, a budget linked to the calendar only, and a naive
last-year measure.

Run: python generate.py  ->  Orders.csv, Stores.csv, Products.csv, Budget.csv (UTF-8). Seed fixed: same files for everyone.
Planted story (Jan-Aug 2026 vs Jan-Aug 2025): Camping down, Footwear up, online stores growing, Burlington falling.
"""
import csv
import datetime as dt
import random
from collections import defaultdict
from pathlib import Path

SEED = 20260914
START, END = dt.date(2024, 1, 1), dt.date(2026, 8, 31)
OUT = Path(__file__).parent

# id, product, category, subcategory, list price (USD), cost ratio
PRODUCTS = [
    ("TG01", "Trail 2P Tent", "Camping", "Tents", 349.0, 0.58), ("TG02", "Ultralight 1P Tent", "Camping", "Tents", 429.0, 0.55),
    ("SB01", "Down Sleeping Bag", "Camping", "Sleep", 279.0, 0.52), ("SB02", "Sleeping Pad", "Camping", "Sleep", 119.0, 0.48),
    ("CK01", "Camp Stove", "Camping", "Kitchen", 89.0, 0.50), ("CK02", "Cookset", "Camping", "Kitchen", 59.0, 0.45),
    ("CL01", "Climbing Harness", "Climbing", "Hardware", 79.0, 0.50), ("CL02", "Dynamic Rope 60m", "Climbing", "Ropes", 229.0, 0.55),
    ("CL03", "Belay Device", "Climbing", "Hardware", 39.0, 0.42), ("CL04", "Chalk Bag", "Climbing", "Accessories", 24.0, 0.35),
    ("FW01", "Trail Runner", "Footwear", "Running", 149.0, 0.48), ("FW02", "Hiking Boot", "Footwear", "Hiking", 219.0, 0.50),
    ("FW03", "Approach Shoe", "Footwear", "Hiking", 169.0, 0.49), ("FW04", "Camp Sandal", "Footwear", "Casual", 69.0, 0.40),
    ("AP01", "Rain Shell", "Apparel", "Outerwear", 249.0, 0.44), ("AP02", "Insulated Jacket", "Apparel", "Outerwear", 299.0, 0.46),
    ("AP03", "Fleece Pullover", "Apparel", "Midlayer", 99.0, 0.40), ("AP04", "Merino Base Layer", "Apparel", "Base layer", 89.0, 0.42),
    ("AP05", "Hiking Pants", "Apparel", "Bottoms", 89.0, 0.38),
    ("AC01", "Headlamp", "Accessories", "Lighting", 49.0, 0.40), ("AC02", "Water Filter", "Accessories", "Hydration", 45.0, 0.38),
    ("AC03", "Trekking Poles", "Accessories", "Trekking", 129.0, 0.47), ("AC04", "Daypack 24L", "Accessories", "Packs", 139.0, 0.45),
    ("AC05", "Insulated Bottle", "Accessories", "Hydration", 35.0, 0.33),
]
# id, store, city, region, channel, size weight
STORES = [
    ("ST01", "Denver Flagship", "Denver", "West", "Retail", 1.6), ("ST02", "Boulder", "Boulder", "West", "Retail", 1.0),
    ("ST03", "Seattle", "Seattle", "West", "Retail", 1.3), ("ST04", "Portland", "Portland", "West", "Retail", 1.1),
    ("ST05", "Chicago", "Chicago", "Midwest", "Retail", 1.2), ("ST06", "Minneapolis", "Minneapolis", "Midwest", "Retail", 0.9),
    ("ST07", "Boston", "Boston", "Northeast", "Retail", 1.1), ("ST08", "Burlington", "Burlington", "Northeast", "Retail", 0.8),
    ("ST09", "Atlanta", "Atlanta", "South", "Retail", 1.0), ("ST10", "Austin", "Austin", "South", "Retail", 1.2),
    ("ST11", "Web Store", "Online", "Online", "Online", 2.0), ("ST12", "Marketplace", "Online", "Online", "Online", 0.9),
]
CATEGORY_GROWTH = {"Camping": -0.10, "Climbing": 0.04, "Footwear": 0.16, "Apparel": 0.03, "Accessories": 0.06}  # per year
STORE_GROWTH = {"ST08": -0.34, "ST11": 0.22, "ST12": 0.12}
SEASON = {  # month 1..12
    "Camping": [0.5, 0.5, 0.7, 0.9, 1.2, 1.5, 1.7, 1.6, 1.1, 0.8, 0.6, 0.6],
    "Apparel": [1.5, 1.3, 1.1, 0.9, 0.7, 0.6, 0.6, 0.7, 0.9, 1.2, 1.5, 1.8],
    "Climbing": [0.8, 0.8, 1.0, 1.1, 1.2, 1.1, 1.0, 1.0, 1.1, 1.1, 0.9, 0.8],
    "Footwear": [0.8, 0.8, 1.0, 1.1, 1.2, 1.2, 1.1, 1.1, 1.0, 1.0, 0.9, 1.0],
    "Accessories": [0.8, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.2, 1.0, 0.9, 1.0, 1.2],
}
CATEGORY_SHARE = {"Camping": 1.2, "Climbing": 0.7, "Footwear": 1.0, "Apparel": 1.1, "Accessories": 1.3}


def write(name: str, header: list[str], rows: list) -> None:
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    orders, n = [], 0
    actual = defaultdict(float)  # (year, month, category) -> net sales
    day = START
    while day <= END:
        years = (day - START).days / 365.25
        stores_w = [s[5] * (1 + STORE_GROWTH.get(s[0], 0.0)) ** years for s in STORES]
        prod_w = [CATEGORY_SHARE[p[2]] * SEASON[p[2]][day.month - 1] * (1 + CATEGORY_GROWTH[p[2]]) ** years for p in PRODUCTS]
        count = int(rng.gauss(18 if day.weekday() >= 5 else 13, 3))
        for _ in range(max(count, 3)):
            s = rng.choices(STORES, stores_w)[0]
            p = rng.choices(PRODUCTS, prod_w)[0]
            qty = rng.choices([1, 2, 3], [0.7, 0.22, 0.08])[0]
            disc = rng.choices([0.0, 0.1, 0.2], [0.6, 0.25, 0.15])[0]
            net = round(qty * p[4] * (1 - disc), 2)
            n += 1
            orders.append((f"O{n:06d}", day.isoformat(), s[0], p[0], qty, p[4], disc, net, round(qty * p[4] * p[5], 2)))
            actual[(day.year, day.month, p[2])] += net
        day += dt.timedelta(days=1)

    budget = []  # last year's month x 1.05; 2024 has no last year, so it is its own actual x 1.02
    for year in (2024, 2025, 2026):
        for month in range(1, 13):
            for cat in CATEGORY_SHARE:
                base = actual.get((year - 1, month, cat)) if year > 2024 else actual.get((year, month, cat), 0) * 0.97
                budget.append((dt.date(year, month, 1).isoformat(), cat, round((base or 0) * 1.05, -2)))

    write("Orders.csv", ["Order ID", "Order Date", "Store ID", "Product ID", "Quantity", "Unit Price", "Discount", "Net Sales", "COGS"], orders)
    write("Stores.csv", ["Store ID", "Store", "City", "Region", "Channel"], [s[:5] for s in STORES])
    write("Products.csv", ["Product ID", "Product", "Category", "Subcategory", "List Price"], [p[:5] for p in PRODUCTS])
    write("Budget.csv", ["Month", "Category", "Amount"], budget)

    def ytd(year, pred):
        return sum(o[7] for o in orders if o[1].startswith(str(year)) and int(o[1][5:7]) <= 8 and pred(o))
    total26, total25 = ytd(2026, lambda o: True), ytd(2025, lambda o: True)
    print(f"Orders.csv {len(orders):,} rows · Jan-Aug 2026 net sales {total26:,.0f} · YoY {total26 / total25 - 1:+.1%}")
    cat_of = {p[0]: p[2] for p in PRODUCTS}
    for cat in CATEGORY_SHARE:
        a, b = ytd(2026, lambda o: cat_of[o[3]] == cat), ytd(2025, lambda o: cat_of[o[3]] == cat)
        print(f"  {cat:<12} {a:>12,.0f}  YoY {a / b - 1:+.1%}")
    for sid in ("ST08", "ST11"):
        a, b = ytd(2026, lambda o: o[2] == sid), ytd(2025, lambda o: o[2] == sid)
        print(f"  {sid}         {a:>12,.0f}  YoY {a / b - 1:+.1%}")


if __name__ == "__main__":
    main()
