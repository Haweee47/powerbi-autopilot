# Example 07 · your own data: CSV, Excel, or a database

The pilots need a semantic model. [Example 05](../05-own-model/README.md) started from a model someone had already built.
This one starts from **data with no model at all** and builds one: a folder of CSVs, an Excel workbook, or a database over ODBC.

![The dashboard on a model built from an Excel workbook](screenshots/summary-excel.png)

## The three sources, same data, same report

| Source | Command | What the tool read |
|---|---|---|
| CSV folder | `new_model.py --csv examples/_data/outdoor-shop` | 4 files → 4 tables, types from the first 2,000 rows |
| Excel workbook | `new_model.py --excel outdoor-shop.xlsx` | 4 sheets → 4 tables, types from the cells themselves |
| Database (ODBC) | `new_model.py --odbc "<connection>" --query "Orders=SELECT * FROM [Orders.csv]" …` | 4 queries → 4 tables, **types as the driver reports them** |

Each run wrote the same shape: **6 tables** (the four above plus `Calendar` and a measure-only `Metrics`), **22 columns**,
**4 key relationships** found from the data (`Orders[Store ID] → Stores`, `Orders[Product ID] → Products`) plus a date
relationship per table, and **8 starter measures** (a SUM per numeric column, and a row count).

## From model to report

```
new_report.py --purpose dashboard --model out/m-xlsx      → 23 blanks (10 columns, 13 measures), a 1.7 KB map
   fill the map                                            → the only part a person writes
generate_pbir.py                                           → 4 pages, 55 visuals
powerbi-report-author validate                             → 0 errors, 0 warnings
```

The other two sources reused that same map with `--reuse-map`: **0 blanks, nothing to fill**. Same pilot, same map,
three different ways of reaching the data.

## Numbers, checked against the CSVs

Desktop capture of the Excel-built model against values computed from the source files with Python (2026, all channels):

| | Report | Source files |
|---|---|---|
| Sales | 634.3K | 634,304 |
| Profit | 308.1K | 308,137 |
| Target attainment | 95.6% | 95.6% |
| AOV | 185.4 | 185 |
| Furthest behind | Camping ▼27.0K | Camping, 27.0K below budget |

## What went wrong, and what it taught

- **The ODBC path first typed every date as text.** Reading sample values and guessing from their shape fails as soon as
  the driver formats dates in the machine's locale. The fix: ask the driver what each column *is* (`GetFieldType`) and only
  fall back to sniffing when it says "string". Types now come from the source wherever the source states them.
- **A column of whole numbers is not always an integer.** Values like `99.0` read from a workbook come back as integers;
  from CSV text they stay decimal. The generated TMDL says which one it chose for every column, so it is one line to fix.
- **Relationships are guessed, and guesses are printed.** A column that repeats in another table and is unique there
  becomes a key. Everything the tool inferred is printed when it runs and written as plain TMDL you can edit.

## Limits

- **Verified in Desktop**: the CSV and Excel paths, end to end, with the numbers above.
- **ODBC**: the model builds, validates and refreshes through a local driver (the Access Text driver that ships with Office).
  A real warehouse (Presto, Redshift, Snowflake) still needs someone with an account to try it — the first refresh also asks
  once how to sign in ([example 06](../06-odbc/README.md)).
- **Native connectors** (`--connector sqlserver|mysql|postgres|redshift|oracle`) write the M for that connector while the
  columns still come from an ODBC profile. Generated and schema-checked here, not refreshed against those servers.
- The starter measures are a starting point, not a model design. Name and shape them for your business before shipping.
