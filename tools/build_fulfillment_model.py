"""Write the fulfillment pilot's semantic model (TMDL) from one compact definition.

Why a script: the model has ten tables and ~40 measures; writing TMDL by hand invites indentation and type slips.
The CSVs come from examples/_data/fulfillment/generate.py. Output: templates/fulfillment/model/ (a TMDL folder).

Usage: python tools/build_fulfillment_model.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "templates" / "fulfillment" / "model"
M_TYPE = {"string": "type text", "int64": "Int64.Type", "double": "type number", "dateTime": "type date", "boolean": "type logical"}

# table: (csv file, [(column, dataType, extra lines)])
CSV_TABLES = {
    "Processes": ("Processes.csv", [("Process ID", "string", ["isHidden"]), ("Process", "string", ["sortByColumn: 'Process Order'"]),
                                     ("Flow", "string", []), ("Standard UPH", "int64", ["summarizeBy: none"]),
                                     ("Counts Toward Flow", "boolean", ["isHidden"]), ("Process Order", "int64", ["isHidden"])]),
    "Zones": ("Zones.csv", [("Zone ID", "string", ["isHidden"]), ("Zone", "string", []), ("Kind", "string", [])]),
    "Teams": ("Teams.csv", [("Team ID", "string", ["isHidden"]), ("Team", "string", []), ("Process ID", "string", ["isHidden"]),
                            ("Zone ID", "string", ["isHidden"]), ("Shift", "string", []), ("Headcount", "int64", ["summarizeBy: none"])]),
    "Labor": ("Labor.csv", [("Date", "dateTime", ["formatString: yyyy-mm-dd", "isHidden"]), ("Hour", "int64", ["isHidden"]),
                            ("Team ID", "string", ["isHidden"]), ("Units", "int64", ["isHidden"]),
                            ("Direct Hours", "double", ["isHidden"]), ("Indirect Hours", "double", ["isHidden"]),
                            ("Idle Hours", "double", ["isHidden"]), ("Standard Hours", "double", ["isHidden"]),
                            ("New Hire Share", "double", ["isHidden"])]),
    "Orders": ("Orders.csv", [("Date", "dateTime", ["formatString: yyyy-mm-dd", "isHidden"]), ("Cutoff", "string", []),
                              ("Carrier", "string", []), ("Orders", "int64", ["isHidden"]), ("Orders Due", "int64", ["isHidden"]),
                              ("Units", "int64", ["isHidden"]), ("Lines", "int64", ["isHidden"]),
                              ("Shipped On Time", "int64", ["isHidden"]), ("Cycle Hours", "double", ["isHidden"]),
                              ("Pick Errors", "int64", ["isHidden"]), ("Delivered On Time", "int64", ["isHidden"]),
                              ("First Attempt Delivered", "int64", ["isHidden"]), ("Delivery Hours", "double", ["isHidden"])]),
    "Receipts": ("Receipts.csv", [("Receipt ID", "string", ["isHidden"]), ("Date", "dateTime", ["formatString: yyyy-mm-dd", "isHidden"]),
                                  ("Supplier ID", "string", ["isHidden"]), ("Supplier", "string", []), ("Arrival Hour", "int64", ["summarizeBy: none"]),
                                  ("Units", "int64", ["isHidden"]), ("Arrived On Time", "int64", ["isHidden"]),
                                  ("Damage Free", "int64", ["isHidden"]), ("Documents Correct", "int64", ["isHidden"]),
                                  ("Dock To Stock Hours", "double", ["isHidden"])]),
    "Counts": ("Counts.csv", [("Date", "dateTime", ["formatString: yyyy-mm-dd", "isHidden"]), ("Zone ID", "string", ["isHidden"]),
                              ("Locations Counted", "int64", ["isHidden"]), ("Locations Accurate", "int64", ["isHidden"]),
                              ("Locations Total", "int64", ["isHidden"]), ("Locations Used", "int64", ["isHidden"])]),
}
DESCRIPTIONS = {
    "Processes": "Warehouse processes with their engineered standard (units per direct hour). Counts Toward Flow marks the one process whose units are the flow's volume (pick for outbound, receive for inbound).",
    "Teams": "Crews: each works one process in one zone on one shift.",
    "Labor": "Team-hours: units handled and hours split into direct, indirect and idle time. Standard Hours = units / standard UPH.",
    "Orders": "Outbound orders by day, cut-off and carrier: shipped, due, on time, and what happened in delivery.",
    "Receipts": "Inbound receipts (one row per delivery at the dock) with arrival and dock-to-stock time.",
    "Counts": "Cycle counts and location use by storage zone and day.",
}
CALC_TABLES = {
    "Calendar": ("ADDCOLUMNS ( CALENDAR ( DATE ( 2026, 1, 1 ), DATE ( 2026, 8, 31 ) ), \"Year\", YEAR ( [Date] ), "
                 "\"Month No\", MONTH ( [Date] ), \"Month\", FORMAT ( [Date], \"MMM\", \"en-US\" ), \"Quarter\", \"Q\" & QUARTER ( [Date] ), "
                 "\"Week Start\", [Date] - WEEKDAY ( [Date], 3 ), \"Weekday No\", WEEKDAY ( [Date], 2 ), "
                 "\"Weekday\", FORMAT ( [Date], \"ddd\", \"en-US\" ) )",
                 [("Date", ["isUnique", "formatString: yyyy-mm-dd", "summarizeBy: none"]), ("Year", ["formatString: 0", "summarizeBy: none"]),
                  ("Month No", ["isHidden", "summarizeBy: none"]), ("Month", ["summarizeBy: none", "sortByColumn: 'Month No'"]),
                  ("Quarter", ["summarizeBy: none"]), ("Week Start", ["formatString: mm-dd", "summarizeBy: none"]),
                  ("Weekday No", ["isHidden", "summarizeBy: none"]), ("Weekday", ["summarizeBy: none", "sortByColumn: 'Weekday No'"])]),
    "Hours": ("DATATABLE ( \"Hour\", INTEGER, \"Hour Label\", STRING, \"Shift\", STRING, \"Hour Order\", INTEGER, { "
              + ", ".join(f"{{ {h}, \"{h:02d}:00\", \"{'Day' if 8 <= h <= 17 else 'Night'}\", {i} }}"
                          for i, h in enumerate(list(range(8, 18)) + [20, 21, 22, 23, 0, 1, 2, 3, 4, 5], 1)) + " } )",
              [("Hour", ["isHidden", "summarizeBy: none"]), ("Hour Label", ["summarizeBy: none", "sortByColumn: 'Hour Order'"]),
               ("Shift", ["summarizeBy: none"]), ("Hour Order", ["isHidden", "summarizeBy: none"])]),
    "Loss Types": ("DATATABLE ( \"Loss Type\", STRING, \"Loss Order\", INTEGER, { { \"Below standard\", 1 }, { \"Indirect work\", 2 }, { \"Idle\", 3 } } )",
                   [("Loss Type", ["summarizeBy: none", "sortByColumn: 'Loss Order'"]), ("Loss Order", ["isHidden", "summarizeBy: none"])]),
}
CALC_COLUMNS = {
    "Receipts": [
        ("Arrival Band", "SWITCH ( TRUE (), Receipts[Arrival Hour] < 12, \"< 12:00\", Receipts[Arrival Hour] < 16, \"12:00-16:00\", \"≥ 16:00\" )",
         "string", ["summarizeBy: none", "sortByColumn: 'Arrival Band Order'"]),
        ("Arrival Band Order", "IF ( Receipts[Arrival Hour] < 12, 1, IF ( Receipts[Arrival Hour] < 16, 2, 3 ) )", "int64", ["isHidden", "summarizeBy: none"]),
    ],
}
# folder, name, DAX, format, description
MEASURES = [
    ("1. Labor", "Units", "SUM ( Labor[Units] )", "#,0", "Units handled by the process in context."),
    ("1. Labor", "Direct Hours", "SUM ( Labor[Direct Hours] )", "#,0", "Hours spent on the work itself."),
    ("1. Labor", "Indirect Hours", "SUM ( Labor[Indirect Hours] )", "#,0", "Paid hours on training, meetings, cleaning and other support work."),
    ("1. Labor", "Idle Hours", "SUM ( Labor[Idle Hours] )", "#,0", "Paid hours with no work to do (volume below capacity, system downtime)."),
    ("1. Labor", "Paid Hours", "[Direct Hours] + [Indirect Hours] + [Idle Hours]", "#,0", "All paid hours."),
    ("1. Labor", "Standard Hours", "SUM ( Labor[Standard Hours] )", "#,0", "Hours the work should take at the engineered standard: units / standard UPH."),
    ("1. Labor", "Flow Units", "CALCULATE ( [Units], KEEPFILTERS ( Processes[Counts Toward Flow] = TRUE () ) )", "#,0",
     "Each flow's volume counted once: pick units for outbound, receive units for inbound, counted units for inventory."),
    ("1. Labor", "Handled Units", "IF ( COUNTROWS ( VALUES ( Teams[Process ID] ) ) = 1, [Units], [Flow Units] )", "#,0",
     "Units of the one process in context, or each flow's volume when several processes are in context."),
    ("2. Productivity", "UPH", "DIVIDE ( [Handled Units], [Paid Hours] )", "#,0.0", "Units per paid hour (also called HTP)."),
    ("2. Productivity", "Direct UPH", "DIVIDE ( [Handled Units], [Direct Hours] )", "#,0.0", "Units per direct hour."),
    ("2. Productivity", "Target UPH", "DIVIDE ( [Handled Units], [Standard Hours] ) * 0.85", "#,0.0",
     "The standard rate at the planned 85% direct time: the UPH the plan expects."),
    ("2. Productivity", "UPH vs Target", "DIVIDE ( [UPH], [Target UPH] ) - 1", "+0.0%;-0.0%;0.0%", "UPH above (+) or below (-) the plan."),
    ("2. Productivity", "% of Standard", "DIVIDE ( [Standard Hours], [Direct Hours] )", "0.0%",
     "Performance to standard: standard hours earned per direct hour worked."),
    ("2. Productivity", "Hours Lost", "[Paid Hours] - [Standard Hours]", "#,0",
     "Paid hours the standard did not need: below-standard work + indirect work + idle time."),
    ("2. Productivity", "Hours Below Standard", "[Direct Hours] - [Standard Hours]", "#,0", "Direct hours beyond what the standard needed."),
    ("2. Productivity", "Hours by Loss Type",
     "SWITCH ( SELECTEDVALUE ( 'Loss Types'[Loss Type] ), \"Below standard\", [Hours Below Standard], \"Indirect work\", [Indirect Hours], \"Idle\", [Idle Hours] )",
     "#,0", "Hours Lost split by cause (use with Loss Types)."),
    ("2. Productivity", "Direct Share", "DIVIDE ( [Direct Hours], [Paid Hours] )", "0.0%", "Share of paid hours spent on direct work."),
    ("2. Productivity", "Idle Share", "DIVIDE ( [Idle Hours], [Paid Hours] )", "0.0%", "Share of paid hours with no work."),
    ("2. Productivity", "Indirect Share", "DIVIDE ( [Indirect Hours], [Paid Hours] )", "0.0%", "Share of paid hours on support work."),
    ("2. Productivity", "New Hire Share",
     "DIVIDE ( SUMX ( Labor, Labor[New Hire Share] * ( Labor[Direct Hours] + Labor[Indirect Hours] + Labor[Idle Hours] ) ), [Paid Hours] )",
     "0%", "Share of paid hours worked by people in their first 30 days."),
    ("2. Productivity", "Outbound UPH", "CALCULATE ( [UPH], Processes[Flow] = \"Outbound\" )", "#,0.0", "Units shipped per outbound paid hour (pick, pack, ship)."),
    ("2. Productivity", "Outbound Target UPH", "CALCULATE ( [Target UPH], Processes[Flow] = \"Outbound\" )", "#,0.0", "The outbound plan rate."),
    ("2. Productivity", "Inbound UPH", "CALCULATE ( [UPH], Processes[Flow] = \"Inbound\" )", "#,0.0", "Units received per inbound paid hour (receive, putaway)."),
    ("2. Productivity", "Inbound Target UPH", "CALCULATE ( [Target UPH], Processes[Flow] = \"Inbound\" )", "#,0.0", "The inbound plan rate."),
    ("3. Outbound", "Orders Shipped", "SUM ( Orders[Orders] )", "#,0", "Orders shipped."),
    ("3. Outbound", "Units Shipped", "SUM ( Orders[Units] )", "#,0", "Units shipped."),
    ("3. Outbound", "On-time Ship %", "DIVIDE ( SUM ( Orders[Shipped On Time] ), SUM ( Orders[Orders Due] ) )", "0.0%",
     "Orders shipped by their cut-off / orders due (including carried backlog)."),
    ("3. Outbound", "On-time Ship Target", "0.98", "0%", "Plan: 98% of orders out by cut-off."),
    ("3. Outbound", "Missed Cut-off", "SUM ( Orders[Orders Due] ) - SUM ( Orders[Shipped On Time] )", "#,0", "Orders due that did not leave by their cut-off."),
    ("3. Outbound", "Units per Order", "DIVIDE ( [Units Shipped], [Orders Shipped] )", "0.00", "Average units in an order."),
    ("3. Outbound", "Order Cycle Hours", "DIVIDE ( SUM ( Orders[Cycle Hours] ), [Orders Shipped] )", "0.0", "Hours from order release to ship."),
    ("3. Outbound", "Pick Accuracy", "1 - DIVIDE ( SUM ( Orders[Pick Errors] ), [Orders Shipped] )", "0.00%", "Orders picked without an error."),
    ("4. Inbound and inventory", "Receipts", "COUNTROWS ( Receipts )", "#,0", "Deliveries received."),
    ("4. Inbound and inventory", "Units Received", "SUM ( Receipts[Units] )", "#,0", "Units received."),
    ("4. Inbound and inventory", "Dock-to-Stock Hours", "AVERAGE ( Receipts[Dock To Stock Hours] )", "0.0", "Hours from arrival to putaway."),
    ("4. Inbound and inventory", "Dock-to-Stock Target", "4", "0.0", "Plan: stocked within 4 hours."),
    ("4. Inbound and inventory", "On-time Receipts %", "AVERAGE ( Receipts[Arrived On Time] )", "0.0%", "Deliveries that arrived in their slot."),
    ("4. Inbound and inventory", "Damage-free %", "AVERAGE ( Receipts[Damage Free] )", "0.0%", "Deliveries received without damage."),
    ("4. Inbound and inventory", "Documents Correct %", "AVERAGE ( Receipts[Documents Correct] )", "0.0%", "Deliveries with correct paperwork."),
    ("4. Inbound and inventory", "Inventory Accuracy", "DIVIDE ( SUM ( Counts[Locations Accurate] ), SUM ( Counts[Locations Counted] ) )", "0.00%",
     "Counted locations whose quantity matched the system."),
    ("4. Inbound and inventory", "Capacity Used", "DIVIDE ( SUM ( Counts[Locations Used] ), SUM ( Counts[Locations Total] ) )", "0.0%",
     "Occupied share of storage locations (day-weighted)."),
    ("5. Delivery", "On-time Delivery %", "DIVIDE ( SUM ( Orders[Delivered On Time] ), [Orders Shipped] )", "0.0%", "Orders delivered by the promised date."),
    ("5. Delivery", "First-attempt %", "DIVIDE ( SUM ( Orders[First Attempt Delivered] ), [Orders Shipped] )", "0.0%", "Orders delivered on the first attempt."),
    ("5. Delivery", "Delivery Hours", "DIVIDE ( SUM ( Orders[Delivery Hours] ), [Orders Shipped] )", "0.0", "Hours from ship to delivery."),
    ("6. Info", "Last Data Date", "CALCULATE ( MAX ( Labor[Date] ), REMOVEFILTERS () )", "yyyy-mm-dd", "The last day in the data."),
]
RELATIONSHIPS = [
    ("Labor_Calendar", "Labor.Date", "Calendar.Date"), ("Labor_Hours", "Labor.Hour", "Hours.Hour"),
    ("Labor_Teams", "Labor.'Team ID'", "Teams.'Team ID'"), ("Teams_Processes", "Teams.'Process ID'", "Processes.'Process ID'"),
    ("Teams_Zones", "Teams.'Zone ID'", "Zones.'Zone ID'"), ("Orders_Calendar", "Orders.Date", "Calendar.Date"),
    ("Receipts_Calendar", "Receipts.Date", "Calendar.Date"), ("Counts_Calendar", "Counts.Date", "Calendar.Date"),
    ("Counts_Zones", "Counts.'Zone ID'", "Zones.'Zone ID'"),
]


def q(name: str) -> str:
    return f"'{name}'" if any(c in name for c in " -.%") else name


def csv_table(table: str, file: str, cols: list) -> str:
    lines = []
    if table in DESCRIPTIONS:
        lines.append(f"/// {DESCRIPTIONS[table]}")
    lines.append(f"table {q(table)}\n")
    for col, dtype, extra in cols:
        lines.append(f"\tcolumn {q(col)}\n\t\tdataType: {dtype}")
        if not any(e.startswith("summarizeBy") for e in extra):
            lines.append(f"\t\tsummarizeBy: {'sum' if dtype in ('int64', 'double') else 'none'}")
        lines += [f"\t\t{e}" for e in extra] + [f"\t\tsourceColumn: {col}\n"]
    for name, expr, dtype, extra in CALC_COLUMNS.get(table, []):
        lines.append(f"\tcolumn {q(name)} = {expr}\n\t\tdataType: {dtype}")
        lines += [f"\t\t{e}" for e in extra] + [""]
    types = ", ".join(f'{{"{c}", {M_TYPE[t]}}}' for c, t, _ in cols)
    lines.append(f"""\tpartition {q(table)} = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents(DataFolder & "\\{file}"), [Delimiter = ",", Columns = {len(cols)}, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
\t\t\t\t    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t    Typed = Table.TransformColumnTypes(Promoted, {{{types}}}, "en-US")
\t\t\t\tin
\t\t\t\t    Typed
""")
    return "\n".join(lines)


def calc_table(table: str, dax: str, cols: list) -> str:
    lines = [f"table {q(table)}" + ("\n\tdataCategory: Time" if table == "Calendar" else "") + "\n"]
    for col, extra in cols:
        lines.append(f"\tcolumn {q(col)}")
        lines += [f"\t\t{e}" for e in extra] + ["\t\tisNameInferred", f"\t\tsourceColumn: [{col}]\n"]
    lines.append(f"\tpartition {q(table)} = calculated\n\t\tmode: import\n\t\tsource = {dax}\n")
    return "\n".join(lines)


def measure_table() -> str:
    lines = ["/// Measure-only table: every metric lives here.", "table Metrics\n"]
    for folder, name, dax, fmt, desc in MEASURES:
        lines += [f"\t/// {desc}", f"\tmeasure {q(name)} = {dax}", f"\t\tformatString: {fmt}", f"\t\tdisplayFolder: {folder}", ""]
    lines += ["\tcolumn _\n\t\tisHidden\n\t\tisNameInferred\n\t\tsourceColumn: [_]\n",
              "\tpartition Metrics = calculated\n\t\tmode: import\n\t\tsource = ROW ( \"_\", BLANK () )\n"]
    return "\n".join(lines)


def main() -> None:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    for f in (OUT / "tables").glob("*.tmdl"):
        f.unlink()
    (OUT / "database.tmdl").write_text("database 3b8d7a52-1f6e-4c0a-9e27-5a4f1d2c8b61\n\tcompatibilityLevel: 1550\n"
                                       "\tcompatibilityMode: powerBI\n\tlanguage: 1033\n", encoding="utf-8")
    tables = list(CSV_TABLES) + list(CALC_TABLES) + ["Metrics"]
    (OUT / "model.tmdl").write_text(
        "/// Fulfillment center sample (January to August 2026): labor by team-hour, outbound orders, inbound receipts,\n"
        "/// cycle counts. Synthetic data from examples/_data/fulfillment/generate.py.\n"
        "model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tdiscourageImplicitMeasures\n"
        "\tsourceQueryCulture: en-US\n\tdataAccessOptions\n\t\tlegacyRedirects\n\t\treturnErrorValuesAsNull\n\n"
        "annotation __PBI_TimeIntelligenceEnabled = 0\n\n" + "".join(f"ref table {q(t)}\n" for t in tables), encoding="utf-8")
    (OUT / "expressions.tmdl").write_text(
        "/// Folder with the CSV files. On another PC, change only this value.\n"
        'expression DataFolder = "C:\\path\\to\\powerbi-autopilot\\examples\\_data\\fulfillment" '
        'meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n', encoding="utf-8")
    (OUT / "relationships.tmdl").write_text("".join(
        f"relationship {n}\n\tfromColumn: {a}\n\ttoColumn: {b}\n\n" for n, a, b in RELATIONSHIPS), encoding="utf-8")
    for t, (file, cols) in CSV_TABLES.items():
        (OUT / "tables" / f"{t}.tmdl").write_text(csv_table(t, file, cols), encoding="utf-8")
    for t, (dax, cols) in CALC_TABLES.items():
        (OUT / "tables" / f"{t}.tmdl").write_text(calc_table(t, dax, cols), encoding="utf-8")
    (OUT / "tables" / "Metrics.tmdl").write_text(measure_table(), encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(tables)} tables, {len(MEASURES)} measures, {len(RELATIONSHIPS)} relationships")


if __name__ == "__main__":
    main()
