# Prompts and exact inputs · example 01

The request, given to both runs unchanged:

> Build a sales dashboard page on this model: Sales, Profit, target attainment and AOV as KPIs; monthly sales against
> last year and target; sales vs target by category; a store table. English, 1280×720.

## The shared model

```bash
python tools/new_model.py --name OutdoorShared --out out/shared-model --csv examples/_data/outdoor-shop
```

Then these measures were added to `out/shared-model/tables/Metrics.tmdl`, once, for both runs:

| Measure | DAX | Format |
|---|---|---|
| Sales | `[Total Net Sales]` | `#,0` |
| Profit | `[Total Net Sales] - [Total COGS]` | `#,0` |
| Margin % | `DIVIDE ( [Profit], [Sales] )` | `0.0%` |
| Orders | `[Orders Rows]` | `#,0` |
| AOV | `DIVIDE ( [Sales], [Orders] )` | `#,0` |
| Sales LY | `VAR lastDay = CALCULATE ( MAX ( Orders[Order Date] ), REMOVEFILTERS () ) RETURN CALCULATE ( [Sales], CALCULATETABLE ( SAMEPERIODLASTYEAR ( Calendar[Date] ), KEEPFILTERS ( Calendar[Date] <= lastDay ) ) )` | `#,0` |
| YoY % | `IF ( NOT ISBLANK ( [Sales] ), DIVIDE ( [Sales] - [Sales LY], [Sales LY] ) )` | `+0.0%;-0.0%;0.0%` |
| Target | `VAR lastDay = … RETURN IF ( ISFILTERED ( Products[Product] ) \|\| ISCROSSFILTERED ( Stores ), BLANK (), CALCULATE ( [Total Amount], TREATAS ( VALUES ( Products[Category] ), Budget[Category] ), KEEPFILTERS ( Calendar[Date] <= lastDay ) ) )` | `#,0` |
| Attainment % | `DIVIDE ( [Sales], [Target] )` | `0.0%` |
| vs Target | `IF ( NOT ISBLANK ( [Target] ), [Sales] - [Target] )` | `+#,0;-#,0;0` |

## Run A — following the Microsoft skill

Read: `SKILL.md` (12.9 KB) → `references/authoring.md` (36.6 KB, the mode this request routes to). Looked up capabilities with
`powerbi-report-author catalog describe cardVisual`. Then wrote by hand: the PBIP scaffold, `report.json`, `pages.json`,
`page.json` and eight `visual.json` files (13.7 KB).

Corrections needed on the way:

1. `validate` → 1 error: `/themeCollection/baseTheme/reportVersionAtImport must be object`. A string had been written there.
2. Desktop would not open the project: the semantic-model item was missing `.platform` and `definition.pbism`. The report
   validator does not look at the model item, so it reported success both before and after that fix.

## Run B — this repo

```bash
python tools/new_report.py --purpose dashboard --theme navy --lang en --name ApDashboard --model out/shared-model --out out/ap-run
```

23 blanks in `model-map.json`, filled with the model's own names:

```json
{ "columns": { "날짜.연도": "Calendar.Year", "날짜.월": "Calendar.Month", "날짜.월번호": "Calendar.Month No",
               "매장.권역": "Stores.Region", "매장.매장명": "Stores.Store", "매장.채널": "Stores.Channel",
               "카테고리.카테고리": "Products.Category", "판매.주문일자": "Orders.Order Date" },
  "measures": { "매출": "[Sales]", "이익": "[Profit]", "이익률": "[Margin %]", "주문건수": "[Orders]", "객단가": "[AOV]",
                "전년 매출": "[Sales LY]", "전년 대비 증감률": "[YoY %]", "목표매출": "[Target]",
                "목표 달성률": "[Attainment %]", "목표 대비 차이": "[vs Target]" } }
```

Then `generate_pbir.py`: 4 pages, 55 visuals, validator 0 errors · 0 warnings, first Desktop capture correct.

Edited by hand in run B: nothing in the generated files.
