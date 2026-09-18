# Fulfillment center sample data

Synthetic operations data for the [fulfillment pilot](../../../templates/fulfillment/): one fulfillment center,
January to August 2026. Every name and number is made up; the concepts are the public ones described in
[design-system/domains/fulfillment.md](../../../design-system/domains/fulfillment.md).

```bash
python generate.py   # rewrites the CSVs below (seeded: the same files every time) and prints the expected values
```

| File | Rows | Grain |
|---|---:|---|
| `Labor.csv` | 38,880 | team × hour × day: units, direct / indirect / idle hours, standard hours, new-hire share, travel distance (m) |
| `Orders.csv` | 6,561 | day × cut-off × carrier × order type: orders, orders due, units, lines, shipped on time, cycle hours, pick errors, delivery results |
| `Receipts.csv` | 13,927 | one inbound delivery: supplier, arrival hour, units, on time, damage-free, documents, dock-to-stock hours |
| `Counts.csv` | 729 | storage zone × day: locations counted and accurate, locations used and total |
| `Teams.csv` · `Processes.csv` · `Zones.csv` | 16 · 6 · 4 | 16 crews (process, zone, shift, headcount); processes with their standard UPH |

## How the numbers are made

Each team works one process in one zone, on the day shift (08–17) or the night shift (20–05, dated by the shift start).
Paid hours split into indirect work (9–14%), direct work and idle time. Units = direct hours × standard UPH × performance;
when there is less work than the team could do, the rest of the time is idle. Teams are sized to handle 18% more than an
average day, with lighter weekend rosters.

Performance = zone × tenure × hour of day, so these drivers can be found again in the report:

| Driver | Effect |
|---|---|
| Zone C (bulky items) | pick, putaway and counting at 82% of standard; zone A at 106% |
| New hires (first 30 days) | 70% of standard. Night pick team PCK-C-N is rebuilt on June 1 with 60% new hires, then learns |
| Hour | the first hour of a shift at 93%; the night shift at 97%, and 88% of that from 02:00 to 04:59 |
| Volume | February is quiet (more idle time). A promotion on Aug 8–15 adds 30% volume: backlog, overtime, late shipments |
| Outage | May 12, 01:00–03:59: night teams lose most of their direct time to idle |
| Inbound | arrivals after 16:00 wait for the night putaway team (about twice the dock-to-stock time); Harbor Home arrives damaged more often |
| Inventory and delivery | zone C counts are less accurate; Parcel B succeeds on the first delivery attempt less often |
| Travel | metres per unit (DPU) follow the zone (A 9.5, B 14, C 26) and the order mix: single-unit orders walk the most per unit, bulk the least. The promotion shifts the mix to multi-unit and bulk, so DPU falls that week |

## Expected values

The pilot opens on Q3 (July–August 2026), all shifts. These are the numbers the report should show:

| Measure | Value |
|---|---|
| Units shipped · orders · units per order | 3,512,125 · 1,678,062 · 2.09 |
| Outbound UPH (pick units per outbound paid hour) · % of standard | 41.2 · 91.0% |
| On-time ship · missed cut-off | 84.3% · 286,069 orders |
| Single-unit orders · pick DPU · DPU by zone | 50% · 14.7 m/unit · A 9.5, B 13.9, C 25.9 |
| Hours lost vs standard | 43,848 (idle 38%, indirect 38%) |
| Lowest teams, % of standard | PUT-C-N 71.3%, PCK-C-N 71.6%, PCK-C-D 79.0% |
| Units received · dock-to-stock · damage-free | 3,113,636 · 4.3 h · 98.6% |
| Inventory accuracy · zone C | 99.00% · 97.90% |
| On-time delivery · first attempt | 91.6% · Parcel A 95.2%, Parcel B 90.2%, Own fleet 97.2% |
