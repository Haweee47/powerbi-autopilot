# Example 05 · prompts and manual edits

## What the user asked (verbatim, Korean)

Improvement plan item 3, approved with "ㅇㅇ 그렇게 해줘." ("yes, do that"):

> 3. "내 데이터로" 흐름을 다른 모델로 끝까지 해 보기 — 영어 이름으로 된 두 번째 공개 데이터 모델을 만들고, 거기서 "대시보드 만들어 줘"를 끝까지 해 볼게요. 깨지는 곳을 고치고 예제 05로 남기면 돼요.

## What the agent ran

```bash
python examples/_data/outdoor-shop/generate.py
python tools/new_report.py --purpose dashboard --theme paper --lang en --name OutdoorDashboard \
    --model examples/05-own-model/OutdoorShop.SemanticModel/definition --out examples/05-own-model
# fill model-map.json (below), then
python tools/generate_pbir.py examples/05-own-model/report.spec.json
python tools/generate_pbir.py examples/05-own-model/report.spec.json --local-data --out out/05-own-model
powerbi-report-author validate out/05-own-model/OutdoorDashboard.Report
powershell -ExecutionPolicy Bypass -File tools\render_check.ps1 -Dir out\05-own-model
```

## Edits by the agent (not generated)

| File | Edit | Why |
|---|---|---|
| `model-map.json` | Filled 8 columns and 14 measures from the hints | The pilot's DAX is written for the reference model |
| `model-map.json` | Mapped the display measure `Orders PY` instead of the columns `날짜.날짜` and `날짜.실적기간` | This model has no period flag column |
| `model-map.json` | Last-year measures stop at `[Last Order Date]` | The model's `Revenue LY` compares Jan–Aug 2026 with all of 2025 |
| `model-map.json` | Target stops at `[Last Order Date]` (second pass, after the first capture showed 64.5% attainment) | The budget covers whole years |
| `report.spec.json` | Brand text "Outdoor Shop" | The pilot's name is "Sales Report" |

## The other three pilots (2026-09-15)

Next-steps item 2, approved with "ㅇㅇ 진행해." ("yes, go ahead"): run the remaining pilots on the same model.

```bash
python tools/new_report.py --purpose table --theme paper --lang en --name OutdoorTable \
    --model examples/05-own-model/OutdoorShop.SemanticModel/definition --out examples/05-own-model/table \
    --reuse-map examples/05-own-model/model-map.json      # same for matrix (OutdoorMatrix) and deepdive (OutdoorDeepdive)
```

`--reuse-map` prefilled everything the dashboard map already knew. What the agent still filled:

| Pilot | Prefilled | Filled by the agent |
|---|---:|---|
| table | 19 | `제품.제품명`, `제품.카테고리`, `제품.하위카테고리` → Products columns; `판매수량` = `SUM ( Orders[Quantity] )`; `평균할인율` = `1 - DIVIDE ( [Revenue], SUMX ( Orders, Orders[Quantity] * Orders[Unit Price] ) )` |
| matrix | 20 | `제품.하위카테고리` → `Products.Subcategory` |
| deepdive | 19 | Products columns as above; `판매.매출액`, `판매.수량`, `판매.정가`, `판매.주문번호`, `판매.할인율` → Orders columns; `평균할인율` as above |

Each spec: brand text "Outdoor Shop". No PBIR, TMDL or theme file was edited by hand. The sample model itself (`OutdoorShop.SemanticModel`) was written by a script to
stand in for a model a user brings; its measures and their names are deliberately different from the reference model.
