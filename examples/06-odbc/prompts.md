# Example 06 · prompts and manual edits

## What the user asked (verbatim, Korean)

Roadmap step 4, from the plan the agent proposed on 2026-09-16:

> 4. 실무 데이터 흐름 (10월 초) — ODBC 연결을 검증하고, 기존 리포트를 학습하는 흐름

and the go-ahead for an overnight run:

> 음 지금 토큰 44% 남았으니까 .지금 하고 그다음에 새벽4시에 다음 단계 작동시켜. 놀지말고~

The scheduled task said: check which ODBC drivers are already installed, install nothing, read the outdoor-shop CSVs through ODBC,
build a pilot and check the numbers in Desktop, and ask the user if a driver would have to be installed.

## What the agent ran

```powershell
Get-OdbcDriver    # 64-bit: Microsoft Access Text Driver (*.txt, *.csv) is present
```

```bash
# copy the example 05 model; switch the four CSV partitions to Odbc.Query over one shared connection string
python <scratch script>          # the edit is shown in README.md
cp examples/05-own-model/model-map.json examples/06-odbc/
# report.spec.json: example 05's spec with name, model path and brand subtitle changed
python tools/generate_pbir.py examples/06-odbc/report.spec.json
python tools/generate_pbir.py examples/06-odbc/report.spec.json --local-data --out out/odbc-test
powerbi-report-author validate out/odbc-test/OutdoorOdbc.Report
powershell -ExecutionPolicy Bypass -File tools\render_check.ps1 -Dir out\odbc-test
```

Then the same connection string and SQL from PowerShell with `System.Data.Odbc` to count rows and total sales, profit and budget.

## Edits by the agent (not generated)

| File | Edit | Why |
|---|---|---|
| `OutdoorShopOdbc.SemanticModel/definition/expressions.tmdl` | Added `OdbcConnection` | One connection string for every table, as a real ODBC report usually has |
| `OutdoorShopOdbc.SemanticModel/definition/tables/*.tmdl` | `Csv.Document(File.Contents(…))` + `Table.PromoteHeaders` → `Odbc.Query(OdbcConnection, "SELECT * FROM [<table>.csv]")` | The point of the example; column types stay as they were |
| `report.spec.json` | Name `OutdoorOdbc`, model path, brand subtitle "Dashboard · ODBC source" | Everything else is example 05's |
| `tools/render_check.ps1` | Say when a sign-in dialog is probably open, and word the failure as "did not open, or the data did not load" | The run failed (as it should, the data never loaded) but only said the report did not open |

## What a person still has to do

Open the report once, click **Refresh now**, choose **Default or Custom** in the ODBC dialog and **Connect**.
The agent tried to answer the dialog at 4 a.m. and couldn't: the dialog exposes no accessibility tree, and clicks sent to it had no
effect (the screen was probably locked). It stopped there rather than work around the sign-in step.
