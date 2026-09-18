"""Synthetic operations data for a fulfillment center (January to August 2026).

Built for the fulfillment pilot: outbound first, inbound and inventory second, delivery third, and productivity (UPH,
units per paid hour) across all of them. Generic, public concepts only; every name and number is made up.

Run: python generate.py  ->  Teams.csv, Processes.csv, Zones.csv, Labor.csv, Orders.csv, Receipts.csv, Counts.csv
Seed fixed: the same files for everyone. Expected values for checking a report are printed at the end.

How the numbers are made
- Every team works one process in one zone, on the day shift (08-17) or the night shift (20-05, dated by the shift start).
- A team-hour has paid hours (people x 1h, plus overtime on backlog days), indirect hours (training, meetings, cleaning)
  and direct hours. Units = direct hours x standard UPH x performance. When the volume is lower than the team could
  handle, the rest of the direct time becomes idle time.
- Performance = zone x tenure x hour-of-day effects, so the drivers can be found again in the report.

Planted story
- Zone C (bulky items) picks and puts away at about 82% of standard; zone A at about 106%.
- New hires work at about 70% of standard. Night pick team PCK-C-N is rebuilt in June with 60% new hires,
  so its performance drops in June and recovers through August (learning curve).
- 02:00-04:00 on the night shift and the first hour of each shift are slower.
- February is quiet: idle time goes up. A promotion (Aug 8-15) raises outbound volume by 30%: backlog, overtime and
  late shipments follow.
- A system outage on the night of May 12 (01:00-03:00) turns direct time into idle time for every night team.
- Receipts that arrive after 16:00 wait for the night putaway team: dock-to-stock is roughly twice as long.
  Supplier "Harbor Home" arrives damage-free less often than the others.
- Zone C counts are less accurate. Carrier "Parcel B" succeeds on the first delivery attempt less often.
- Travel: metres walked per unit (DPU) follow the zone (A 9.5 m, B 14 m, C 26 m) and the order mix - a day with more
  single-unit orders walks more per unit. The promotion shifts the mix to multi-unit and bulk orders, so DPU drops.
"""
import csv
import datetime as dt
import math
import random
from collections import defaultdict
from pathlib import Path

SEED = 20260917
START, END = dt.date(2026, 1, 1), dt.date(2026, 8, 31)
OUT = Path(__file__).parent
rng = random.Random(SEED)

# id, process, flow, standard UPH, counts toward the flow's volume
PROCESSES = [
    ("PCK", "Pick", "Outbound", 120, True), ("PAK", "Pack", "Outbound", 150, False), ("SHP", "Sort & ship", "Outbound", 420, False),
    ("RCV", "Receive", "Inbound", 190, True), ("PUT", "Putaway", "Inbound", 130, False), ("CNT", "Cycle count", "Inventory", 360, True),
]
STD = {p[0]: p[3] for p in PROCESSES}
# id, zone, kind, performance effect on travel-heavy work (pick, putaway, count)
ZONES = [("A", "Zone A", "Small items", 1.06), ("B", "Zone B", "Medium items", 1.00), ("C", "Zone C", "Bulky items", 0.82),
         ("D", "Dock", "Pack and dock", 1.00)]
ZONE_EFFECT = {z[0]: z[3] for z in ZONES}
TRAVEL = {"PCK", "PUT", "CNT"}
# id, process, zone, shift, new-hire share, share of the process volume. Headcount is sized from the average volume below.
TEAM_PLAN = [
    ("PCK-A-D", "PCK", "A", "Day", 0.10, 0.26), ("PCK-A-N", "PCK", "A", "Night", 0.15, 0.20),
    ("PCK-B-D", "PCK", "B", "Day", 0.12, 0.17), ("PCK-B-N", "PCK", "B", "Night", 0.20, 0.13),
    ("PCK-C-D", "PCK", "C", "Day", 0.10, 0.14), ("PCK-C-N", "PCK", "C", "Night", 0.15, 0.10),
    ("PAK-D-1", "PAK", "D", "Day", 0.10, 0.36), ("PAK-D-2", "PAK", "D", "Day", 0.25, 0.24), ("PAK-N-1", "PAK", "D", "Night", 0.18, 0.40),
    ("SHP-D", "SHP", "D", "Day", 0.10, 0.58), ("SHP-N", "SHP", "D", "Night", 0.10, 0.42),
    ("RCV-D", "RCV", "D", "Day", 0.12, 0.70), ("RCV-N", "RCV", "D", "Night", 0.20, 0.30),
    ("PUT-AB-D", "PUT", "A", "Day", 0.10, 0.62), ("PUT-C-N", "PUT", "C", "Night", 0.20, 0.38),
    ("CNT-B-D", "CNT", "B", "Day", 0.05, 1.00),
]
AVG_VOLUME = {"PCK": 52000, "PAK": 52000, "SHP": 52000, "RCV": 47000, "PUT": 47000, "CNT": 3200}
HEADROOM = 1.18  # teams can handle 18% more than an average day


def sized(plan: tuple) -> tuple:
    tid, proc, zone, shift, new_share, share = plan
    perf = (ZONE_EFFECT[zone] if proc in TRAVEL else 1.0) * (1 - 0.30 * new_share) * (0.98 if shift == "Day" else 0.91)
    people = AVG_VOLUME[proc] * share * HEADROOM / (STD[proc] * perf * 9.0 * 0.885)  # 9 effective hours, 88.5% direct
    return (tid, proc, zone, shift, max(2, round(people)), new_share, share)


TEAMS = [sized(t) for t in TEAM_PLAN]
DAY_HOURS = list(range(8, 18))
NIGHT_HOURS = [20, 21, 22, 23, 0, 1, 2, 3, 4, 5]
SUPPLIERS = [("SUP01", "Alder Foods", 1.0), ("SUP02", "Brightline Beauty", 0.8), ("SUP03", "Cobalt Electronics", 0.9),
             ("SUP04", "Delta Apparel", 1.1), ("SUP05", "Evergreen Pet", 0.6), ("SUP06", "Fjord Outdoor", 0.7),
             ("SUP07", "Granite Tools", 0.5), ("SUP08", "Harbor Home", 1.0), ("SUP09", "Iris Kids", 0.6),
             ("SUP10", "Juniper Kitchen", 0.8)]
CARRIERS = [("Parcel A", 0.45, 0.955), ("Parcel B", 0.35, 0.905), ("Own fleet", 0.20, 0.975)]  # share, first-attempt rate
# order type: share of orders, units per order, travel per unit factor (single-unit orders walk the most per unit)
ORDER_TYPES = [("Single unit", 0.52, 1.0, 1.22), ("Multi unit", 0.38, 2.3, 0.88), ("Bulk", 0.10, 6.4, 0.62)]
DPU_BASE = {"A": 9.5, "B": 14.0, "C": 26.0, "D": 0.0}  # metres walked per unit, by zone (picking, putaway, counting)
CUTOFFS = [("12:00", 0.30), ("18:00", 0.45), ("23:00", 0.25)]
PROMO = (dt.date(2026, 8, 8), dt.date(2026, 8, 15))
OUTAGE = (dt.date(2026, 5, 12), {1, 2, 3})


def days():
    d = START
    while d <= END:
        yield d
        d += dt.timedelta(days=1)


def outbound_volume(d: dt.date) -> float:
    """Units to ship: weekly shape, a quiet February, growth, and the August promotion."""
    base = 52000 * (1 + 0.012 * (d.month - 1))
    base *= {0: 1.12, 1: 1.05, 2: 1.0, 3: 0.98, 4: 1.02, 5: 0.86, 6: 0.80}[d.weekday()]
    if d.month == 2:
        base *= 0.78
    if PROMO[0] <= d <= PROMO[1]:
        base *= 1.30
    return base * rng.uniform(0.94, 1.06)


def tenure_effect(team: tuple, d: dt.date) -> tuple[float, float]:
    new_share = team[5]
    if team[0] == "PCK-C-N" and d >= dt.date(2026, 6, 1):  # rebuilt team: 60% new hires, learning through the summer
        weeks = (d - dt.date(2026, 6, 1)).days / 7
        new_share = 0.60 * math.exp(-weeks / 7)
    return 1 - 0.30 * new_share, new_share


def hour_effect(shift: str, hour: int) -> float:
    first = 8 if shift == "Day" else 20
    e = 0.93 if hour == first else 1.0
    if shift == "Night":
        e *= 0.97
        if hour in (2, 3, 4):
            e *= 0.88
    return e


def main() -> None:
    labor, orders, receipts, counts = [], [], [], []
    backlog = 0.0
    team_by_proc = defaultdict(list)
    for t in TEAMS:
        team_by_proc[t[1]].append(t)
    rid = 0
    for d in days():
        # ---- the day's order mix: a promotion pulls orders towards multi-unit and bulk
        shift_mix = (-0.12, 0.07, 0.05) if PROMO[0] <= d <= PROMO[1] else (0.0, 0.0, 0.0)
        shares = [max(0.02, t[1] + m + rng.uniform(-0.02, 0.02)) for t, m in zip(ORDER_TYPES, shift_mix)]
        shares = [x / sum(shares) for x in shares]
        upo = sum(sh * t[2] for sh, t in zip(shares, ORDER_TYPES))
        base_travel = sum(t[1] * t[3] for t in ORDER_TYPES)
        travel_factor = sum(sh * t[3] for sh, t in zip(shares, ORDER_TYPES)) / base_travel
        # ---- outbound demand and what gets shipped
        demand = outbound_volume(d) + backlog
        overtime = 1.0 if backlog > 4000 else 0.0  # an extra hour per person on backlog days
        # ---- inbound receipts for the day
        n_receipts = int(rng.uniform(52, 64) * (1.35 if PROMO[0] - dt.timedelta(days=6) <= d <= PROMO[1] else 1.0)
                         * (0.8 if d.weekday() == 6 else 1.0))
        inbound_units = 0.0
        day_receipts = []
        for _ in range(n_receipts):
            rid += 1
            sup = rng.choices(SUPPLIERS, weights=[s[2] for s in SUPPLIERS])[0]
            hour = rng.choices(range(6, 22), weights=[2, 4, 6, 7, 7, 6, 5, 5, 5, 5, 4, 3, 3, 2, 2, 1])[0]
            units = rng.randint(250, 1400)
            on_time = rng.random() < (0.90 if sup[0] != "SUP06" else 0.78)
            damage_free = rng.random() < (0.93 if sup[0] == "SUP08" else 0.99)
            docs_ok = rng.random() < 0.97
            d2s = rng.uniform(2.0, 4.2) * (2.1 if hour >= 16 else 1.0) * (1.25 if d.month == 8 and d.day >= 3 else 1.0)
            inbound_units += units
            day_receipts.append((f"R{rid:06d}", d.isoformat(), sup[0], sup[1], hour, units, int(on_time), int(damage_free),
                                 int(docs_ok), round(d2s, 2)))
        receipts += day_receipts
        count_units = 3200 * rng.uniform(0.9, 1.1)
        volume = {"PCK": demand, "PAK": demand, "SHP": demand, "RCV": inbound_units, "PUT": inbound_units, "CNT": count_units}
        shipped_by_proc = {}
        for proc, teams in team_by_proc.items():
            done = 0.0
            for t in teams:
                tid, _, zone, shift, heads, _, share = t
                hours = DAY_HOURS if shift == "Day" else NIGHT_HOURS
                ten, new_share = tenure_effect(t, d)
                need = volume[proc] * share
                weights = [0.9 if h in (8, 20) else (0.5 if h in (12, 0) else 1.0) for h in hours]
                wsum = sum(weights)
                for h, w in zip(hours, weights):
                    crew = heads * (0.85 if d.weekday() >= 5 else 1.0)  # lighter weekend rosters
                    paid = crew * (1.0 if w != 0.5 else 0.5) + (crew * overtime / len(hours) if shift == "Night" else 0)
                    indirect = paid * rng.uniform(0.09, 0.14)
                    perf = ten * hour_effect(shift, h) * (ZONE_EFFECT[zone] if proc in TRAVEL else 1.0) * rng.uniform(0.96, 1.04)
                    available = paid - indirect
                    if d == OUTAGE[0] and shift == "Night" and h in OUTAGE[1]:
                        available *= 0.15
                    capacity = available * STD[proc] * perf
                    want = need * w / wsum
                    units = min(want, capacity)
                    direct = units / (STD[proc] * perf)
                    idle = paid - indirect - direct
                    done += units
                    dpu = DPU_BASE[zone] * (travel_factor if proc == "PCK" else 1.0) * rng.uniform(0.97, 1.03) if proc in TRAVEL else 0.0
                    labor.append((d.isoformat(), h, tid, round(units), round(direct, 3), round(indirect, 3), round(idle, 3),
                                  round(units / STD[proc], 3), round(new_share, 3), round(units * dpu)))
            shipped_by_proc[proc] = done
        shipped = min(shipped_by_proc["PCK"], shipped_by_proc["PAK"], shipped_by_proc["SHP"])
        backlog = max(0.0, demand - shipped)
        # ---- orders by cutoff and carrier
        late_share = min(0.35, backlog / max(demand, 1) * 1.6) + 0.012
        n_total = shipped / upo
        for cutoff, cshare in CUTOFFS:
            for carrier, kshare, first_rate in CARRIERS:
                for (otype, _, t_upo, _), oshare in zip(ORDER_TYPES, shares):
                    n = max(1, round(n_total * cshare * kshare * oshare))
                    units = n * t_upo
                    due = round(n + backlog / upo * cshare * kshare * oshare)
                    on_time = round(n * (1 - late_share * (1.3 if cutoff == "12:00" else 1.0)))
                    lines = round(n * (1.0 + 0.28 * min(t_upo, 4)))
                    cycle = n * rng.uniform(5.0, 6.4) * (1.4 if backlog > 4000 else 1.0)
                    errors = sum(1 for _ in range(n) if rng.random() < 0.0011)
                    delivered_on_time = round(n * min(0.99, (0.965 if carrier != "Parcel B" else 0.935) - late_share * 0.5))
                    first = round(n * first_rate * rng.uniform(0.985, 1.01))
                    orders.append((d.isoformat(), cutoff, carrier, otype, n, due, round(units), lines, on_time, round(cycle, 1),
                                   errors, delivered_on_time, min(first, n), round(n * rng.uniform(26, 34) *
                                                                                  (1.15 if carrier == "Parcel B" else 1.0), 1)))
        # ---- cycle counts by storage zone
        for zid, zname, _, _ in ZONES[:3]:
            counted = rng.randint(380, 460)
            acc_rate = {"A": 0.996, "B": 0.995, "C": 0.978}[zid]
            accurate = sum(1 for _ in range(counted) if rng.random() < acc_rate)
            total = {"A": 12000, "B": 16000, "C": 6000}[zid]
            growth = (d - START).days / (END - START).days
            used = total * ({"A": 0.80, "B": 0.83, "C": 0.76}[zid] + 0.08 * growth + (0.03 if d.month == 8 else 0)) * rng.uniform(0.99, 1.01)
            counts.append((d.isoformat(), zid, counted, accurate, total, round(min(used, total))))

    def write(name, header, rows):
        with open(OUT / name, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)

    write("Processes.csv", ["Process ID", "Process", "Flow", "Standard UPH", "Counts Toward Flow", "Process Order"],
          [(p[0], p[1], p[2], p[3], "TRUE" if p[4] else "FALSE", i) for i, p in enumerate(PROCESSES, 1)])
    write("Zones.csv", ["Zone ID", "Zone", "Kind"], [(z[0], z[1], z[2]) for z in ZONES])
    write("Teams.csv", ["Team ID", "Team", "Process ID", "Zone ID", "Shift", "Headcount"],
          [(t[0], t[0], t[1], t[2], t[3], t[4]) for t in TEAMS])
    write("Labor.csv", ["Date", "Hour", "Team ID", "Units", "Direct Hours", "Indirect Hours", "Idle Hours", "Standard Hours",
                        "New Hire Share", "Travel Distance"], labor)
    write("Orders.csv", ["Date", "Cutoff", "Carrier", "Order Type", "Orders", "Orders Due", "Units", "Lines", "Shipped On Time",
                         "Cycle Hours", "Pick Errors", "Delivered On Time", "First Attempt Delivered", "Delivery Hours"], orders)
    write("Receipts.csv", ["Receipt ID", "Date", "Supplier ID", "Supplier", "Arrival Hour", "Units", "Arrived On Time",
                           "Damage Free", "Documents Correct", "Dock To Stock Hours"], receipts)
    write("Counts.csv", ["Date", "Zone ID", "Locations Counted", "Locations Accurate", "Locations Total", "Locations Used"], counts)

    # ---- expected values for checking a report: Q3 (July and August 2026, the default view), all shifts
    aug = lambda r: r[0][:7] in ("2026-07", "2026-08")
    proc_of = {t[0]: t[1] for t in TEAMS}
    team_zone = {t[0]: t[2] for t in TEAMS}
    L = [r for r in labor if aug(r)]
    paid = lambda rows: sum(r[4] + r[5] + r[6] for r in rows)
    out_rows = [r for r in L if proc_of[r[2]] in ("PCK", "PAK", "SHP")]
    pick_units = sum(r[3] for r in L if proc_of[r[2]] == "PCK")
    O = [r for r in orders if aug(r)]
    R = [r for r in receipts if r[1][:7] in ("2026-07", "2026-08")]
    C = [r for r in counts if aug(r)]
    print(f"rows: labor {len(labor):,} · orders {len(orders):,} · receipts {len(receipts):,} · counts {len(counts):,}")
    print("Q3 2026 (July-August), all shifts")
    print(f"  outbound units (pick) {pick_units:,.0f} · outbound UPH {pick_units / paid(out_rows):.1f} "
          f"· % of standard {sum(r[7] for r in out_rows) / sum(r[4] for r in out_rows):.1%}")
    print(f"  units shipped {sum(r[6] for r in O):,} · on-time ship {sum(r[8] for r in O) / sum(r[5] for r in O):.1%} "
          f"· missed cut-off {sum(r[5] - r[8] for r in O):,} · orders {sum(r[4] for r in O):,} · units per order {sum(r[6] for r in O) / sum(r[4] for r in O):.2f}")
    pick = [r for r in L if proc_of[r[2]] == "PCK"]
    dpu = lambda rows: sum(r[9] for r in rows) / sum(r[3] for r in rows)
    walks = [r for r in L if proc_of[r[2]] in TRAVEL]  # the report's DPU covers every process that walks
    print(f"  single-unit orders {sum(r[4] for r in O if r[3] == 'Single unit') / sum(r[4] for r in O):.0%} "
          f"· pick DPU {dpu(pick):.1f} m/unit · DPU by zone " +
          " · ".join(f"{z} {dpu([r for r in walks if team_zone[r[2]] == z]):.1f}" for z in "ABC"))
    lost = sum(r[4] + r[5] + r[6] - r[7] for r in L)
    print(f"  hours lost vs standard {lost:,.0f} (indirect {sum(r[5] for r in L) / lost:.0%}, idle {sum(r[6] for r in L) / lost:.0%})")
    by_team = defaultdict(lambda: [0.0, 0.0])
    for r in L:
        by_team[r[2]][0] += r[7]
        by_team[r[2]][1] += r[4]
    worst = sorted(by_team.items(), key=lambda kv: kv[1][0] / kv[1][1])[:3]
    print("  lowest teams (% of standard): " + ", ".join(f"{k} {v[0] / v[1]:.1%}" for k, v in worst))
    print(f"  received units {sum(r[5] for r in R):,} · dock-to-stock {sum(r[9] for r in R) / len(R):.1f}h "
          f"· damage-free {sum(r[7] for r in R) / len(R):.1%}")
    print(f"  inventory accuracy {sum(r[3] for r in C) / sum(r[2] for r in C):.2%} "
          f"· zone C {sum(r[3] for r in C if r[1] == 'C') / sum(r[2] for r in C if r[1] == 'C'):.2%}")
    print(f"  on-time delivery {sum(r[11] for r in O) / sum(r[4] for r in O):.1%} · first attempt "
          + ", ".join(f"{c} {sum(r[12] for r in O if r[2] == c) / sum(r[4] for r in O if r[2] == c):.1%}" for c, _, _ in CARRIERS))


if __name__ == "__main__":
    main()
