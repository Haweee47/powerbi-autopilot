# Changelog

What changed, newest first. Issues fixed by a release are linked by number.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · versions: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- A domain pilot for fulfillment-center operations (`--purpose fulfillment`), with its own model (11 tables, 45 measures) and seeded
  sample data: outbound, lost hours vs standard, productivity by hour, teams and their drivers, inbound and inventory, and a team
  drill-through, in English and Korean (data values too). Concepts and formulas: `design-system/domains/fulfillment.md`
- Matrix specs take `"columnTotals": false`; the top-bar layout packs only the slicers a page uses and keeps tab widths equal
  across the report; the rail's page selector grows for more than four pages
- A second layout for every page: `--frame top` puts the report name, page tabs and slicers in a bar across the top and gives
  the body the full width (columns 72 → 88 px). Built from the same layout templates, so specs don't change
- Table specs take `"top": N`: a Top N visual filter by the table's sort measure, in the shape Desktop saves. The dashboard's
  "weakest stores" card now shows the three weakest instead of a scrolling list, and the watch list the five weakest
- The generator warns when rail text (report name, subtitle) is likely to wrap and be cut off
- Example 06: example 05's dashboard on the same model read through ODBC (the Access Text driver that comes with Office).
  The report builds and validates unchanged, and totals queried through the driver match the CSVs. The Desktop capture waits for the
  one-time sign-in choice; guides in four languages describe the ODBC flow
- Four more themes, seven in all, in three groups: classic (Navy, Paper, Midnight), showcase (Aurora, Coast) and practical
  (Ledger, Contrast). A theme is now a color palette plus a card shape (`soft`, `bold`, `flat`), so shape changes without touching
  layouts or specs. Every series palette passes the color-vision check; Navy, Paper and Midnight render exactly as before
- `tools/brand_theme.py`: a preset from one brand color. Blue, teal and violet brands also become the data accent; other hues only
  tint the rail and selections, so red keeps meaning "below target"
- `docs/cost-per-report.md`: two reports built end to end and priced. About $0.6–4 per report on Claude Opus 5 API pricing,
  2–10 minutes from the request to every page captured in Desktop

### Changed
- A report with one visible page leaves out the page selector and moves the rail slicers up
- The README opens with the page-by-page GIF of the four pilots
- `render_check.ps1 -Theme` accepts any preset in the tokens file; the `new-report` skill offers four themes at a time and names the rest

### Fixed
- `render_check.ps1` says when a data source is probably asking how to sign in, and reports "did not open, or the data did not
  load" instead of only "did not open"
- `render_check.ps1` clicks a second bar ("pending changes") after the refresh and fails a report when a bar is still showing;
  a capture under that bar came out empty but was reported as captured
- `new_report.py` listed names a measure creates inside its own DAX (`SalesV` in the sparkline) as missing measures, which left a
  model-map blank no value could fill. It now shares the generator's rule

## [0.3.0] - 2026-09-15

All four pilots on your own model, sparklines in tables, and a DAX check that catches broken references before Desktop does.

### Added
- `new_report.py --reuse-map`: start another report on the same model from a map already filled. In example 05 the three
  other pilots needed only 5, 1 and 8 new values; hints are written only for what's still empty
- Example 05 covers all four pilots, every headline checked against the CSVs
- Sparklines in tables: a `Sales Trend` measure draws each row's monthly sales as a small SVG line with an end dot that is blue
  when the row grew year over year and red when it shrank. Added to the measure table, the matrix scorecard and the dashboard's
  store ranking; the theme sets the image size once
- The generator checks the DAX of display and adapter measures before writing anything: a column or measure the model doesn't have
  stops the build with the measure's name, instead of a visual that only breaks in Desktop

### Changed
- Korean money measures pick the unit from the size of the selection: charts and tables use 만 (억 from 1조), KPIs use 억
  (만 below 1억). A smaller model shows 63만 instead of 0.0억; the bundled Korean pilots render as before

### Fixed
- The decomposition tree listed its first level alphabetically and only a few bars fit, so the top item could be off screen
  (example 05 hid West, the top region; the bundled pilot hid the 2nd and 3rd). It now sorts by value, as most saved trees do

## [0.2.0] - 2026-09-15

Bring your own model, and checks anyone can run. Reports that use the new unit measures need model compatibility level 1601,
which the generator sets; Power BI Desktop 2.157 or newer is still required.

### Added
- `tools/check.py`: one command that regenerates the committed files, builds all 24 pilot × theme × language combinations
  and runs Microsoft's validator. CI runs it on every push and pull request
- `tools/render_check.ps1` + `tools/render_report.py`: open each pilot in Power BI Desktop, refresh, capture every page and
  compare with the committed screenshots. Works in any Desktop display language. `-Dir` captures any report folder
- Bring your own model: `new_report.py --model` finds every column and measure a pilot needs, inside its DAX too, and writes a
  `model-map.json` skeleton with reference definitions and time rules as hints. The generator applies the map: renames fields and
  DAX columns, adds hidden adapter measures, and finds measures that live on a fact table
- Example 05: the dashboard pilot on a differently shaped English model (outdoor shop), numbers checked against the CSVs

### Changed
- English money measures pick K, M or B from the size of the current selection (dynamic format strings) instead of always M,
  so a smaller model shows 634.3K instead of 0.6M. The reference pilots render exactly as before
- Last-year orders moved into a display measure (`Orders PY`) so other models can replace it without a period flag column

### Fixed
- `new_report.py` split a single field written as text (`"y": "…"`) into characters and missed the measures used inside the pilot's DAX
- `render_check` reported "match" from old captures when a report failed to open. It now clears captures first, fails when a
  report doesn't open, and `render_report` flags missing pages
- Reports that use the unit measures get compatibility level 1601 (required for format string expressions; Desktop refused to
  open 1550), and `formatStringDefinition` is written after the other measure properties
- The generator crashed on Windows when its output was redirected and the console code page lacked a character (≈)
- Theme file names hash line-ending-normalized content, so Windows and Linux generate identical pilot files

## [0.1.0] - 2026-09-14

First public release. Requires **Power BI Desktop 2.157 or newer**: every pilot page was captured in 2.157.1354 before release.

### Added
- Four pilots by purpose: dashboard, measure table, metric check (matrix), deep dive
- Three themes generated from one token file: Navy, Paper, Midnight
- Report languages: English (default) and Korean complete; Japanese and Simplified Chinese registered, mostly English for now
- Spec → PBIP generator with field checks against the model; every pilot passes Microsoft's PBIR validator with 0 errors · 0 warnings
- `new-report` agent skill: asks purpose, theme and language, then starts from a pilot
- One-command start: `tools/quickstart.py` and a double-click `quickstart.cmd`
- Getting-started guides in English, Korean, Japanese and Simplified Chinese (`docs/guide/`)
- Feedback loop: issue forms, Discussions, triage labels, `triage-feedback` agent skill and `docs/feedback-log.md`

### Changed
- Japanese and Chinese reports use English sample data values when no data translation exists (previously Korean)

### Fixed
- Pilots looked broken when the `.pbip` opened in an older Power BI Desktop (2.147): KPI comparison lines missing, takeaway clipped,
  table columns narrow, slicer buttons truncated. `quickstart` now opens the Microsoft Store version when it's installed and warns
  when only an older Desktop is found; the guides state the minimum version. ([#1](https://github.com/Haweee47/powerbi-autopilot/issues/1))

[Unreleased]: https://github.com/Haweee47/powerbi-autopilot/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Haweee47/powerbi-autopilot/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Haweee47/powerbi-autopilot/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Haweee47/powerbi-autopilot/releases/tag/v0.1.0
