# Prompts · example 07

What I typed, unedited. The agent ran the commands; I only filled the model map.

---

> 내 데이터로 리포트 만들고 싶은데, Power BI 모델이 아직 없어. CSV 폴더랑 엑셀 파일, DB 전부 되게 해줘.

Result: `tools/new_model.py`, then the same dashboard pilot on all three sources.

```bash
# 1. a folder of CSVs
python tools/new_model.py --name OutdoorCsv --out out/m-csv --csv examples/_data/outdoor-shop

# 2. one Excel workbook, a sheet per table
python examples/_data/outdoor-shop/make_xlsx.py            # builds outdoor-shop.xlsx from the CSVs
python tools/new_model.py --name OutdoorXlsx --out out/m-xlsx --excel examples/_data/outdoor-shop/outdoor-shop.xlsx

# 3. a database over ODBC (here: the Access Text driver that comes with Office, reading the same CSVs)
python tools/new_model.py --name OutdoorOdbc --out out/m-odbc \
  --odbc "Driver={Microsoft Access Text Driver (*.txt, *.csv)};DBQ=<...>\examples\_data\outdoor-shop;Extensions=asc,csv,tab,txt;" \
  --query "Orders=SELECT * FROM [Orders.csv]" --query "Stores=SELECT * FROM [Stores.csv]" \
  --query "Products=SELECT * FROM [Products.csv]" --query "Budget=SELECT * FROM [Budget.csv]"

# then the same pilot on each model
python tools/new_report.py --purpose dashboard --theme navy --lang en --name OutdoorXlsx --model out/m-xlsx --out out/r-xlsx
#   fill out/r-xlsx/model-map.json (23 blanks), then:
python tools/generate_pbir.py out/r-xlsx/report.spec.json
python tools/new_report.py ... --model out/m-csv --out out/r-csv --reuse-map out/r-xlsx/model-map.json   # 0 blanks
```

Edited by hand: nothing in the generated files. The model map (`model-map.json`) is the only thing a person writes,
and it is written once and reused for the other two sources.
