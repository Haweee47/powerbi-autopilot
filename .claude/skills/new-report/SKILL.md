---
name: new-report
description: Start a new Power BI report in this repo from a pre-built pilot. Asks the purpose (dashboard, measure table, metric-check matrix, deep dive), the design theme (navy, paper, midnight) and the language (English by default), copies the matching pilot spec, remaps only the missing fields, then generates and validates the PBIP. Use whenever the user asks for a new report, dashboard or table.
---

# New report from a pilot

The point is token economy: a finished pilot already encodes layout, theme, formatting and page flow.
You only choose it and change what differs. Never rebuild a report from scratch when a pilot fits.

## 1. Ask once (single AskUserQuestion call, three questions)

Read `templates/catalog.json` for the option texts (use the user's language; English if unknown).

| Question | Options (label → description) |
|---|---|
| Purpose | Dashboard · Measure table · Metric check (matrix) · Deep dive — use `purposes[].when` |
| Theme | Navy · Paper · Midnight — use `themes[].when` |
| Language | English (default) · 한국어 · 日本語 · 简体中文 — from `design-system/i18n/locales.json` |

If the request already answers a question, don't ask it. Put the recommended option first.

## 2. Copy the pilot (zero reading)

```bash
python tools/new_report.py --purpose <id> --theme <id> --lang <code> --name <Name> [--model <TMDL folder>]
```

Read only what it prints: the new spec path, a one-screen model summary, and the list of pilot fields missing in the target model.
Do **not** open the pilot's generated `.Report`, the theme JSON, or TMDL files.

## 3. Edit only the new spec

- Replace each field the tool listed as missing with the closest field from the model summary.
- Rewrite headline sentences (`measures` → `Headline …`) for the new subject. Keep the "item + number" pattern so no grammar depends on the value.
- Change titles and subtitles. Keep one language unless the user wants several (`{"en": …, "ko": …}`).
- Number units live in `templates/_shared/measures.<lang>.json`; don't hard-code units in titles.
- Layout, colors, fonts and visual formatting: don't touch. If something truly needs a new layout, add it to `design-system/layouts/layouts.json` and run `python tools/build_layouts.py`.

## 4. Build and check

```bash
python tools/generate_pbir.py examples/<Name>/report.spec.json
powerbi-report-author validate examples/<Name>/<Name>.Report
```

The generator stops before writing anything if a field doesn't exist. Fix the spec, rerun.
If Power BI Desktop is available, render and capture every page (see `docs/progress-log.md` for the capture loop) before calling it done:
validation passing does not mean the screen is right.

## 5. Report back

Say which pilot, theme and language you used, what you changed in the spec, the validator result, and whether you looked at the rendered pages.
