---
name: new-report
description: Start a new Power BI report in this repo from a pre-built pilot. Always asks first — purpose (dashboard, measure table, metric-check matrix, deep dive, fulfillment ops), design theme (ten presets), language and page layout — showing a wireframe and palette for each choice, then copies the matching pilot spec, remaps only the missing fields, generates and validates the PBIP. Use whenever the user asks for a new report, dashboard or table, however casually they phrase it.
---

# New report from a pilot

The point is token economy: a finished pilot already encodes layout, theme, formatting and page flow.
You only choose it and change what differs. Never rebuild a report from scratch when a pilot fits.

## 0. Ask before you build — this is not optional

**A request in plain words is not a complete brief.** "매출 대시보드 만들어줘" or "make me a sales report" says
nothing about who reads it, where it is shown, or in what language. Those choices change the output more than
anything you would infer, and they cost the user one click each.

So: **do not run any generator until the user has chosen.** No "I'll start with navy and we can change it later" —
changing it later means regenerating and re-capturing everything. Ask once, build once.

The only exceptions: the request already names the option (then don't ask that one), or the user explicitly says
to pick for them (then state every default you chose in your reply, so they can correct one).

## 1. Ask once — a single AskUserQuestion call, up to four questions

Read `templates/catalog.json`. Every option there carries a **`preview`** — a wireframe for purposes and layouts,
the palette and card shape for themes. Put it in the option's `preview` field so the user sees what they are
choosing. Use `name[lang]` for the label and `when[lang]` for the description, in the user's language.

Ask in this order; it is the order of how much each one changes the result:

| # | Question | Options |
|---|---|---|
| 1 | **Purpose** | 5 in `purposes`. A question holds 4, so offer the best fit first plus the three closest, and name the fifth in the question text. Warehouse, logistics or fulfillment-centre requests → `fulfillment` (it brings its own model and sample data) |
| 2 | **Theme** | 10 in `themes`, grouped `classic` · `showcase` · `practical`. Offer the recommended one first and the three closest by `when`; list the rest in the question text so the user can type one under Other |
| 3 | **Language** | `languages` in the catalog — English (default), 한국어, 日本語, 简体中文 |
| 4 | **Page layout** | 2 in `frames`: left rail (default) or top bar. Suggest the top bar for wide tables and wall screens |

Judge the recommendation from the request before you ask, and put it first. A board deck leans `navy` or
`broadsheet`; a wall screen leans `midnight` or `carbon`; print and month-end lean `ledger`; accessibility,
projectors and colour-vision deficiency lean `universal` or `contrast`.

**A brand colour.** If the user names one, build the preset before asking the theme question, then offer it as the
first option: `python tools/brand_theme.py --id <id> --accent "#RRGGBB" --base <closest preset>` then
`python tools/build_themes.py`.

## 2. Copy the pilot (zero reading)

```bash
python tools/new_report.py --purpose <id> --theme <id> --lang <code> [--frame top] --name <Name> [--model <TMDL folder>]
```

Read only what it prints: the new spec path, a one-screen model summary, and the list of pilot fields missing in the target model.
Do **not** open the pilot's generated `.Report`, the theme JSON, or TMDL files.

**The user's own model (`--model`).** The pilot's DAX is written for the reference model, so the tool also lists every column and
measure the pilot needs that the model lacks, including those used inside its DAX, and writes `model-map.json` next to the spec:
empty values plus `_hints` with the reference definition, the English name, where it's used, and RULE notes. Fill it in:

- `columns`: the user's `'Table.Column'`. `measures`: DAX in the user's model; keep the `format` the skeleton suggests.
- Follow the RULE notes: last-year and target measures stop at the last data date (a naive `SAMEPERIODLASTYEAR` or a full-year budget gives wrong YoY and attainment).
- If a missing column is only used inside one display measure (e.g. `Orders PY`), map that measure name instead of the column.
- The generator stops if a value is still empty. Worked example: `examples/05-own-model/`.
- **A second report on the same model:** add `--reuse-map <the filled model-map.json>`. Known values are prefilled and hints are
  written only for what's still empty (example 05: the other three pilots needed 5, 1 and 8 new values). Read only those.

**No model yet?** A folder of CSVs, a workbook or a database comes first: `python tools/new_model.py --csv <folder>`
(also `--excel`, `--odbc`). It prints every relationship and dimension it inferred. Then come back with `--model`.

## 3. Edit only the new spec

- Replace each field the tool listed as missing with the closest field from the model summary.
- Rewrite headline sentences (`measures` → `Headline …`) for the new subject. Keep the "item + number" pattern so no grammar depends on the value.
- Change titles and subtitles. Keep one language unless the user wants several (`{"en": …, "ko": …}`).
- Number units live in `templates/_shared/measures.<lang>.json`; don't hard-code units in titles.
- A short list in a small card ("weakest stores"): keep `"top": N` next to `"sort"` so only the rows that fit are shown.
- Keep rail text short (brand name and subtitle about 25 Latin or 12 CJK characters). The generator warns when a line may wrap.
- Layout, colors, fonts and visual formatting: don't touch. If something truly needs a new layout, add it to `design-system/layouts/layouts.json` and run `python tools/build_layouts.py`.

## 4. Build and check

```bash
python tools/design_check.py examples/<Name>/report.spec.json
python tools/generate_pbir.py examples/<Name>/report.spec.json
powerbi-report-author validate examples/<Name>/<Name>.Report
```

`design_check.py` applies the rubric items a script can settle (a KPI without a comparison, a chart with no title, a
bar with no order, a table asked to show more rows than fit) and stops before anything is generated.
The generator then stops before writing if a field doesn't exist. Fix the spec, rerun.

If Power BI Desktop is available, capture every page before calling it done:
`powershell -ExecutionPolicy Bypass -File tools\render_check.ps1 -Dir examples\<Name>` opens it in the Store Desktop, refreshes and saves each page to `out/render/`.
Build with `--local-data` when the report uses the bundled sample model, or Desktop finds no data. **Validation passing does not mean the screen is right** — this repo has had reports that validated with 0 errors and rendered blank.

## 5. Report back

Say which pilot, theme, language and layout you used, what you changed in the spec, the validator result, and whether
you looked at the rendered pages. If you chose any option instead of asking, say which and why, so it can be corrected.
