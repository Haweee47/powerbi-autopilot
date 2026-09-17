---
name: new-report
description: Start a new Power BI report in this repo from a pre-built pilot. Asks the purpose (dashboard, measure table, metric-check matrix, deep dive), the design theme (seven presets: navy, paper, midnight, aurora, coast, ledger, contrast) and the language (English by default), copies the matching pilot spec, remaps only the missing fields, then generates and validates the PBIP. Use whenever the user asks for a new report, dashboard or table.
---

# New report from a pilot

The point is token economy: a finished pilot already encodes layout, theme, formatting and page flow.
You only choose it and change what differs. Never rebuild a report from scratch when a pilot fits.

## 1. Ask once (single AskUserQuestion call, up to four questions)

Read `templates/catalog.json` for the option texts (use the user's language; English if unknown).

| Question | Options (label → description) |
|---|---|
| Purpose | Dashboard · Measure table · Metric check (matrix) · Deep dive · Fulfillment ops — use `purposes[].when`. Five options: offer the recommended one and the three closest. Warehouse, logistics or fulfillment-center requests → Fulfillment ops (its own model and data) |
| Theme | Seven presets in three groups (`themes[].group`: classic · showcase · practical). A question takes at most 4 options: offer the recommended theme first and the three closest by `themes[].when`, and name the rest in the question text so the user can type one under Other |
| Language | English (default) · 한국어 · 日本語 · 简体中文 — from `design-system/i18n/locales.json` |
| Layout | Left rail (default) · Top bar — `frames[].when`. Suggest the top bar for wide tables and wall screens |

If the user names a brand color, make a preset first: `python tools/brand_theme.py --id <id> --accent "#RRGGBB" --base <closest preset>`,
then `python tools/build_themes.py`, and use that id as the theme.

If the request already answers a question, don't ask it. Put the recommended option first.

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
python tools/generate_pbir.py examples/<Name>/report.spec.json
powerbi-report-author validate examples/<Name>/<Name>.Report
```

The generator stops before writing anything if a field doesn't exist. Fix the spec, rerun.
If Power BI Desktop is available, capture every page before calling it done:
`powershell -ExecutionPolicy Bypass -File tools\render_check.ps1 -Dir examples\<Name>` opens it in the Store Desktop, refreshes and saves each page to `out/render/`.
Build with `--local-data` when the report uses the bundled sample model, or Desktop finds no data. Validation passing does not mean the screen is right.

## 5. Report back

Say which pilot, theme and language you used, what you changed in the spec, the validator result, and whether you looked at the rendered pages.
