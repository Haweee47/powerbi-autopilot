# powerbi-autopilot

[![check](https://github.com/Haweee47/powerbi-autopilot/actions/workflows/check.yml/badge.svg)](https://github.com/Haweee47/powerbi-autopilot/actions/workflows/check.yml)
[![Release](https://img.shields.io/github/v/release/Haweee47/powerbi-autopilot)](https://github.com/Haweee47/powerbi-autopilot/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Power BI Desktop 2.157+](https://img.shields.io/badge/Power%20BI%20Desktop-2.157%2B-F2C811)](docs/guide/en.md)
[![PBIR validator: 0 errors](https://img.shields.io/badge/PBIR%20validator-0%20errors-2ea44f)](CHANGELOG.md)
[![Discussions](https://img.shields.io/github/discussions/Haweee47/powerbi-autopilot)](https://github.com/Haweee47/powerbi-autopilot/discussions)

**English** · [한국어](README.ko.md)

An AI-agent workflow that builds a Power BI report from start to finish (**data model → design → validation**) from a one-line request.
No manual clicks in Power BI Desktop.

**The point: analysts should spend their time on analysis, not on building dashboards.** Data and business analysts lose hours to
placing visuals, formatting and fixing pages. This project cuts that work to one request, so the time goes back into data and business
analysis, where the business impact is. Along the way it holds two bars: **reports that look good**, and **low token cost**.

![Every page of the four pilots, rendered in Power BI Desktop](docs/share/media/pages.gif)

---

## Why not the official skill?

Microsoft and data-goblin both ship a Claude Code plugin for Power BI. I finished **the same page, on the same model**, with each
of them, and measured it instead of asserting it ([example 01](examples/01-microsoft-skill/README.md) · [example 02](examples/02-data-goblin/README.md)):

| | Instructions the agent reads | What the agent writes | Result |
|---|---|---|---|
| **this repo** | **~1.7k tokens** on invoke | a model map, 5.1 KB | 4 pages, 55 visuals, themed |
| Microsoft `powerbi-report-cli` | ~89 KB of reference files (~4.4k + 14.7k tokens) | every `visual.json` — 13.7 KB for 8 visuals | 1 page, validator-clean, defects on screen |
| data-goblin `reports` | five skills, ~32.6k tokens | ~600 bytes of `pbir` commands | 2 of 7 visuals never rendered |

Microsoft's CLI is lookup and validation only, so the agent hand-writes the JSON — their own authoring reference recommends a
deterministic generator when repetition is the constraint. data-goblin's `pbir` does generate, compactly, but creating a report
needs a Fabric sign-in and a published model, so there is no local-only way in.

**Both public runs passed their validators and were still wrong on screen.** That is why every page here is opened in Power BI
Desktop and captured before anything is called finished. The rubric scores in those write-ups come with their bias stated: I wrote
the rubric.

## Why I built this

Every hour spent building a dashboard is an hour not spent on the questions behind it: what changed, why, and what to do next.
Most of that hour isn't analysis. It goes to layout, formatting, fixing visuals that render wrong and keeping reports consistent.
Cutting that time comes first. The analysis is where an analyst creates business impact, so that's where the time should go.

At my previous job I designed and rolled out a workflow for my team: convert existing Power BI reports to PBIP (a text-based format), have an LLM read them, and generate new reports from templates.
It worked. But two things kept it from being practical day to day:

1. **It burned too many tokens.** Teaching it a few reference reports meant reading hundreds of thousands of tokens every time.
2. **The results didn't look good.** Copying existing reports reproduced their design, flaws included.

So I'm solving the same problem again from scratch, with public data. Every step is in the [progress log](docs/progress-log.md) (Korean): decisions, wrong hypotheses, and failures included.

## How it works

Ask for a new report and the agent asks only three things: **purpose, theme, language.**
It then copies a pre-built pilot, swaps in your fields and text, generates the PBIP, runs Microsoft's validator,
and opens the report in Power BI Desktop to screenshot every page ([skill](.claude/skills/new-report/SKILL.md)).

```bash
python tools/new_report.py --purpose table --theme paper --lang en --name StoreKPI   # copy a pilot (~1.6K-token spec)
python tools/generate_pbir.py examples/StoreKPI/report.spec.json                      # generate the PBIP
powerbi-report-author validate examples/StoreKPI/StoreKPI.Report                       # official validation
```

## Quick start

1. **Download**: green **Code** button → **Download ZIP** (or `git clone`). You need Windows, Power BI Desktop and Python 3.10+.
2. **Double-click `quickstart.cmd`**. It builds the dashboard pilot with bundled sample data and opens it in Power BI Desktop.
3. Click **Refresh now** on the yellow bar (and **Apply changes** if asked).

Step-by-step guide, including building reports by asking and using your own data:
[English](docs/guide/en.md) · [한국어](docs/guide/ko.md) · [日本語](docs/guide/ja.md) · [简体中文](docs/guide/zh-CN.md)

> Needs Power BI Desktop **2.157 or newer**. Older versions cut off a few labels ([#1](https://github.com/Haweee47/powerbi-autopilot/issues/1));
> the Microsoft Store version keeps itself up to date, and `quickstart` opens it when it's installed.

## Pilots by purpose

| Dashboard: executive summary | Measure table: measure input matrix |
|---|---|
| ![Dashboard](templates/dashboard/screenshots/summary.png) | ![Measure table](templates/table/screenshots/stores.png) |
| KPIs · trend · one-line takeaway → drillthrough detail | Rows = items, columns = measures. One word per column (`bar` · `heat` · `sign`) sets the conditional formatting |
| **Matrix check** | **Deep dive** |
| ![Matrix](templates/matrix/screenshots/heatmap.png) | ![Deep dive](templates/deepdive/screenshots/decomposition.png) |
| Hierarchical rows × month heatmap, region › store scorecard (opens expanded) | Decomposition tree · discount vs. margin scatter · source rows |

### Domain pilot: fulfillment center operations

![Fulfillment pilot, outbound page](templates/fulfillment/screenshots/outbound.png)

For warehouse and fulfillment analysts: **outbound first** (units shipped, outbound UPH vs plan, on-time ship, missed cut-offs),
then **lost hours** (paid hours the engineered standard didn't need, split into slow work, support work and waiting, by process → shift → zone → team),
**productivity by hour**, **teams and their drivers** (new-hire share vs % of standard), **travel per unit**
(DPU: metres walked per unit, against the share of single-unit orders, filtered by order type), and **inbound and inventory**
(dock-to-stock, damage, count accuracy).
It has its own model and seeded sample data; concepts and formulas are in [design-system/domains/fulfillment.md](design-system/domains/fulfillment.md).
`python tools/quickstart.py --purpose fulfillment`

Full list and how to choose: [templates/catalog.json](templates/catalog.json)

## Ten themes · languages

![Ten themes](docs/share/media/themes.png)

Every theme is a color palette, a card shape and a typeface set, generated from one token file and checked against Power BI's official theme schema (2.157).
Pick by where the report will be read:

| Group | Theme | Card shape | Where it fits |
|---|---|---|---|
| Classic | **Navy** | soft | Board decks and presentations |
| | **Paper** | soft | Light, document-like; prints and PDFs well |
| | **Midnight** | soft, full dark | Wall screens, dim rooms, long monitoring |
| Showcase | **Aurora** | bold: rounder, borderless, deeper shadow | Launches and first impressions |
| | **Coast** | soft | Calm and fresh; operations, retail and service reviews |
| Practical | **Ledger** | flat: square corners, hairlines, no shadow | Finance packs, month-end reviews, print |
| | **Contrast** | flat, darker lines and text | Accessibility, projectors, bright rooms |
| | **Universal** | soft | Okabe-Ito colors: readable with color-vision deficiency, on projectors and in print |
| | **Carbon** | flat, dark rail, DIN numerals | Dense operations screens with many series |
| Showcase | **Broadsheet** | flat, warm paper, serif headings | Board packs and monthly reviews that are read, not watched |

Each series palette passes a color-vision check (adjacent series stay apart for protan, deutan and tritan viewers); the second color is gray on purpose, for last year.
Text is checked too: every label is measured against the fill behind it and the build fails under WCAG 4.5:1.

**Typefaces** are the third axis, limited to the fonts Power BI itself ships - anything else falls back silently on the reader's machine.
`segoe` is the neutral default, `din` is Power BI's signage face (numbers read as instruments), `editorial` sets Georgia headings over Corbel. Every set chains the same CJK fallbacks.

**Two layouts:** every pilot page comes with navigation in a left rail (default) or in a bar across the top with a full-width body (`--frame top`).

**Your brand color:** `python tools/brand_theme.py --id acme --accent "#0F62FE" --base navy` makes an eleventh preset from one color. Blue, teal and violet brands also color the data; red, orange, yellow and green brands color only the rail and selections, because red already means "below target" ([guide](docs/guide/en.md)).

- **Languages**: English by default, Korean built in. UI text, field names, number units (M · K ↔ 만 · 억), takeaway sentences and even data values switch with the language.
  Add another language with one entry in [locales.json](design-system/i18n/locales.json) and one measures file.

## Data sources

The pilots run on a seeded synthetic retail dataset, so anyone can reproduce them exactly.
**ODBC:** a report on ODBC works the same way. Save it as PBIP and the agent keeps its connection and SQL as they are; no password goes into the files.
[Example 06](examples/06-odbc/README.md) reads the sample data through a local ODBC driver: the model builds and validates, and the totals match.
The Desktop capture there waits for the one-time sign-in choice, and a live warehouse (Presto, Redshift …) hasn't been tested yet.

## What's done so far

| Area | Result |
|---|---|
| Public report analysis | Scanned 1,737 GitHub repos and analyzed **1,830 PBIX/PBIT files + 271 PBIP folders** ([research](research/README.md)) |
| Formatting audit | 11,323 `visual.json` files. **67% of file size is formatting, and most of it is hard-coded per visual instead of living in the theme** |
| Design basis | Collected data + 11 research papers ([literature.md](design-system/literature.md)) → [principles](design-system/principles.md) → [review rubric](design-system/review-rubric.md) |
| Data model | Built with Power BI Modeling MCP: 7 tables · 6 relationships · 29 measures. **Every DAX query result matched the Python expected values** ([example 03](examples/03-modeling-mcp/model-doc.md)) |
| Generator | Spec → PBIP. All four pilots and the Korean example pass Microsoft's validator (`powerbi-report-author validate`) with **0 errors · 0 warnings** |
| Render check | A loop that opens each generated file in Desktop and captures every page. It caught and fixed **25+ issues** that passed the validator but looked wrong on screen |
| Your own model | The dashboard pilot on a differently shaped English model: `new_report.py` lists every column and measure the pilot needs, inside its DAX too, and writes a model map the agent fills. Numbers checked against the CSVs ([example 05](examples/05-own-model/README.md)) |
| Your own data, no model yet | `new_model.py` builds the semantic model from a **CSV folder, an Excel workbook or a database over ODBC**: types from the source, key relationships and a calendar inferred, starter measures written. The same pilot and the same model map then run on all three ([example 07](examples/07-own-data/README.md)) |
| ODBC source | The same model read through a local ODBC driver: builds and validates unchanged, totals through the driver match. Desktop capture waits for the one-time sign-in choice ([example 06](examples/06-odbc/README.md)) |

## How tokens were cut

**One report costs about $0.6–4 on Claude Opus 5 API pricing and takes 2–10 minutes**, from the request to every page captured in
Power BI Desktop ([measured runs](docs/cost-per-report.md)). The low end is a pilot on the bundled model; the high end is a first report on a model the agent has never seen.

| Pilot | Spec the agent writes | Generated report JSON |
|---|---:|---:|
| Matrix check | 1.3K tokens | 22K tokens |
| Measure table | 1.9K | 25K |
| Deep dive | 2.0K | 38K |
| Dashboard | 3.5K | 57K |

Layout templates handle coordinates, the theme handles formatting, shared measure files handle units and sentences, and scripts handle field checks and file structure.
A new report keeps only one language when it copies a pilot, so its spec is even smaller. Fields missing from the model are caught against the TMDL before Desktop ever opens (0 tokens).

## Design basis

Decided from data and research, not gut feel. A few examples:

- **Say the takeaway in words, and emphasize the same thing in the chart.** What the text and the chart both point to is what people remember (Kim et al., CHI 2021).
  Every page has a one-line takeaway written by DAX, and that item shows up again in the chart in red, at the top.
- **Always show what you're looking at.** Next to the title: "2026 · Jan–Aug · All channels" (metadata pattern, Bach et al., IEEE TVCG 2023).
- **Order matters as much as restraint.** Putting the key chart center-left keeps eye movement shortest (eye-tracking study, Sensors 2024).
- **Good reports fill less.** Expert and official reports had fewer visuals per page than portfolio reports (5.8 vs. 10) and wider spacing (32px vs. 18px, collected data).
- **Numbers: 3–4 digits plus a unit.** "841.8M", "8.4억" (Microsoft guidance).

## How I work

An AI agent (Claude Code) creates and edits the files. I define the problem, set the design, decide what counts as correct, and judge the results.

1. **Never feed raw files whole.** Scripts extract what's needed; the agent only sees summaries.
2. **Verify numbers with queries.** Even the takeaway sentences are checked against DAX.
3. **Verify the screen with captures.** Files that passed the validator still showed all-time totals, doubled units ("40천만"), or broken English numbers ("110,558,285.0,,M").
4. **Check property names with tools, not memory.** I compared against the official CLI and hundreds of public PBIR files to see how settings are actually stored.
5. **Log the failures too.**

## Repository layout

```
powerbi-autopilot/
├── templates/         Four pilots by purpose and a fulfillment-operations pilot (own model), shared measures, glossary, catalog
├── design-system/     Principles, rubric, research notes, tokens → ten themes (palette × card shape × typeface), layout templates, locales, HTML prototypes
├── tools/             Generator (spec → PBIR), new-report starter, theme/layout builds, design check, share images, token measurement
├── examples/          Shared synthetic data (Korean/English), example 03 (Modeling MCP), example 04 (first generator run)
├── research/          Public report collection and analysis scripts with results (originals are not redistributed)
├── docs/              Setup, progress log, share drafts
└── .claude/skills/    new-report: the agent procedure that asks purpose, theme, language and starts from a pilot
```

## Try it

```bash
python examples/_data/korean-retail/generate.py              # synthetic sales data (fixed seed)
python examples/_data/korean-retail/generate.py --lang en    # same data, English values
python tools/build_layouts.py && python tools/build_themes.py
python tools/generate_pbir.py templates/dashboard/pilot.spec.json               # English · Navy
python tools/generate_pbir.py templates/dashboard/pilot.spec.json --lang ko --theme midnight --out <folder>
```

## Feedback

I read, log and answer every issue. Design feedback comes with a 1–5 rating and is mapped to the review rubric;
when several people point at the same thing, the design rule changes. [How feedback becomes changes](CONTRIBUTING.md#how-feedback-becomes-changes)

[Something looks wrong](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=1-render-bug.yml) ·
[Design feedback](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=2-design-feedback.yml) ·
[New pilot or feature](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=3-pilot-request.yml) ·
[Language support](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=4-language-request.yml) ·
[Discussions](https://github.com/Haweee47/powerbi-autopilot/discussions). Any language is fine. What changed: [CHANGELOG](CHANGELOG.md).

## Roadmap

This is a work in progress. I'll keep improving it and logging what I learn.

- [x] Design tokens → themes, layout templates, spec → PBIR generator
- [x] Four pilots · a fulfillment-operations pilot · ten themes · two layouts · multiple languages
- [ ] Sparklines inside tables (SVG measures)
- [ ] Real-data flow: Presto/Redshift query → model → pilot, including ODBC validation
- [ ] Same request across three tools (Microsoft's official skill / a community skill / Modeling MCP), compared by tokens and rubric score

## Tech

Power BI (PBIP · PBIR · TMDL · DAX) · Python (generator, analysis scripts) · JavaScript/SVG (responsive prototypes) ·
Claude Code + MCP (Power BI Modeling MCP) · Windows UI Automation (Desktop captures) · Git

---

Built by [Haweee47](https://github.com/Haweee47) · License: [MIT](LICENSE)
