# Example 06 · a report on an ODBC source

Many teams reach their warehouse (Presto, Redshift, Snowflake …) through ODBC. This example checks what changes when the
model behind a pilot reads its tables through ODBC instead of files: the answer is only the partition expressions and a
one-time sign-in choice in Desktop.

It is example 05's dashboard on the same outdoor-shop model, with every table read through the **Microsoft Access Text
Driver**. That driver comes with Microsoft Office (Access Database Engine), so the check runs on the bundled CSV files
without installing anything and without a server.

## What an ODBC model looks like in PBIP

Save a report that uses ODBC as a Power BI project and each table's partition holds an M expression like this:

```m
Source = Odbc.Query("dsn=Sales", "SELECT order_id, order_date, amount FROM sales.orders"),
Typed  = Table.TransformColumnTypes(Source, {{"order_date", type date}, {"amount", type number}})
```

Here the connection string sits in one shared expression ([`expressions.tmdl`](OutdoorShopOdbc.SemanticModel/definition/expressions.tmdl)),
and each table runs `SELECT * FROM [Orders.csv]` against it:

```m
expression OdbcConnection = "driver={Microsoft Access Text Driver (*.txt, *.csv)};dbq=" & DataFolder & ";extensions=asc,csv,tab,txt"
```

**No user name or password is in these files.** Desktop asks how to sign in the first time it refreshes and keeps the answer
in its own settings on your PC. Keep it that way: a DSN, or Desktop's sign-in dialog, never `UID=` or `PWD=` in a connection string.

## The flow for your own ODBC report

1. In Desktop, **File → Save as → Power BI project (.pbip)**.
2. Ask for a report on that model. `new_report.py --model <…>.SemanticModel/definition` reads tables, columns and measures
   from the TMDL. The M expressions (connection and SQL) are copied as they are; the agent doesn't rewrite your SQL.
3. The agent fills `model-map.json` with your column names and DAX, as in [example 05](../05-own-model/README.md).
   Here the map is example 05's, unchanged: switching the source to ODBC didn't change the model's shape.
4. Generate and validate.
5. Open the report and click **Refresh now**. Desktop shows the ODBC sign-in dialog once:
   - **Default or Custom**: the DSN or driver handles sign-in (this example: no credentials at all)
   - **Windows**: integrated security
   - **Database**: a user name and password, stored by Desktop, not in the project

## What was checked (2026-09-17)

| Check | Result |
|---|---|
| Generate the report from the ODBC model | 4 pages, 55 visuals. Microsoft's validator: 0 errors · 0 warnings |
| The same driver, connection string and SQL from PowerShell (`System.Data.Odbc`) | Rows: Orders 13,559 · Stores 12 · Products 24 · Budget 180, as in the CSVs |
| Types the driver returns | Dates as DateTime, amounts as Double, IDs as text, so the model's `Table.TransformColumnTypes` works unchanged |
| Totals through ODBC, January–August 2026 | Sales 634,304 (+0.4% YoY) · profit 308,137 · budget 663,800 · attainment 95.6%, the same as example 05's report |
| Open in Power BI Desktop and refresh | Desktop opened the ODBC sign-in dialog, as it does for a real ODBC source |
| Capture every page in Desktop | **Pending.** The unattended run can't answer the sign-in dialog. After choosing *Default or Custom* once, `render_check` can run on its own |

The unattended run failed, as it should: the data never loaded. `tools/render_check.ps1` now also says that a data source is
probably asking how to sign in, instead of only "did not open".

## Try it

```bash
python tools/generate_pbir.py examples/06-odbc/report.spec.json --local-data --out out/06-odbc
# open out/06-odbc/OutdoorOdbc.pbip → Refresh now → Default or Custom → Connect, then:
powershell -ExecutionPolicy Bypass -File tools\render_check.ps1 -Dir out\06-odbc
```

`--local-data` points `DataFolder` at this clone's `examples/_data/outdoor-shop`. The driver is 64-bit, like Desktop.
Check it's there with PowerShell: `Get-OdbcDriver -Platform 64-bit`.

## Notes for real warehouses

- Each driver has its own SQL dialect. The text driver wants `[Orders.csv]` and `#2026-08-31#`; Presto or Redshift won't.
  The agent leaves SQL alone; if your SQL renames a column, map the new name in `model-map.json`.
- Large tables: filter in the SQL (for example the last three years) rather than in Power Query after the load.
- The report doesn't need to know the source is ODBC. Pilots, themes and the DAX checks behave the same.
