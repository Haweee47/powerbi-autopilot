# Getting started

**English** · [한국어](ko.md) · [日本語](ja.md) · [简体中文](zh-CN.md)

From download to an open Power BI report in about five minutes, then how to build your own by asking in plain language.

## What you need

| | Needed for | Where |
|---|---|---|
| Windows 10/11 + Power BI Desktop **2.157 or newer** | Everything | Microsoft Store (free, keeps itself up to date). Older versions cut off some labels ([#1](https://github.com/Haweee47/powerbi-autopilot/issues/1)) |
| Python 3.10 or newer | Everything | [python.org](https://www.python.org/downloads/). Tick **Add python.exe to PATH** during setup |
| Claude Code | Building reports by asking | [claude.com/claude-code](https://claude.com/claude-code) |
| Microsoft's PBIR validator | Optional checks | `npm install -g @microsoft/powerbi-report-authoring-cli` |

There's nothing else to install. The scripts use only Python's standard library.

## 1. Download

Green **Code** button → **Download ZIP**, then unzip. Or:

```bash
git clone https://github.com/Haweee47/powerbi-autopilot.git
```

## 2. Open a finished report (no AI needed)

Double-click **`quickstart.cmd`** in the folder. It builds the dashboard pilot with the bundled sample data and opens it in Power BI Desktop.

The first time the report opens:

1. A yellow bar says some tables have no data → click **Refresh now**.
2. If a bar then says there are pending changes → click **Apply changes**.

To try another pilot, theme or language, run it from a terminal in the folder:

```bash
python tools/quickstart.py --purpose matrix --theme midnight
python tools/quickstart.py --all --lang ko
```

| Option | Values |
|---|---|
| `--purpose` | `dashboard` · `table` · `matrix` · `deepdive` |
| `--theme` | `navy` · `paper` · `midnight` |
| `--lang` | `en` · `ko` · `ja` · `zh-CN` |

Reports are written to `out/`, which git ignores. Collapse the Filters, Visualizations and Data panes (») to see the page at full size.

## 3. Build a report by asking (Claude Code)

```bash
cd powerbi-autopilot
claude
```

Then say what you want, for example:

> Make a store KPI table in the Paper theme, in Korean.

The agent asks only what you left out (purpose, theme, language), copies the closest pilot, changes fields and titles,
generates the PBIP and validates it. The procedure it follows is in [`.claude/skills/new-report/SKILL.md`](../../.claude/skills/new-report/SKILL.md).

## 4. Use your own data

1. Open your existing report in Power BI Desktop and choose **File → Save as → Power BI project (.pbip)**.
   On older versions, first turn on **Options → Preview features → Power BI project (.pbip) save option**.
2. Tell the agent where the model is:
   > Build a dashboard from the model in C:\Reports\Sales\Sales.SemanticModel\definition
3. The agent reads a one-screen summary of your model, not the whole files. `new_report.py` lists everything the pilot needs that your model
   doesn't have (measures used inside its DAX too) and writes a `model-map.json` with the reference definitions as hints.
   The agent fills in that map with your column names and your DAX. Worked example: [example 05](../../examples/05-own-model/README.md).

Your data connection (SQL Server, files, ODBC …) is copied with the model and stays on your PC.
**ODBC hasn't been fully tested yet.** If you use ODBC, save one existing report as PBIP and let the agent read its design and connection first. The result will fit your setup better.

Keep real data out of commits and issues. `out/` is ignored by git; a report you build under `examples/` is not.

## Languages

| Language | Report text | Numbers | Sample data values |
|---|---|---|---|
| English | Complete | K · M | English |
| 한국어 | Complete | 만 · 억 | Korean |
| 日本語 | Mostly English for now | K · M | English |
| 简体中文 | Mostly English for now | K · M | English |

Want your language finished? Open a [Language support](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=4-language-request.yml) issue. Native speakers who can review are especially welcome.

## Troubleshooting

| What you see | What to do |
|---|---|
| Visuals are empty | Click **Refresh now** on the yellow bar, or **Home → Refresh** |
| "Couldn't find file" or a data-folder error | Open the report from `out/` (built by quickstart), not from `templates/`: the pilots there carry a placeholder path. Or set **Transform data → Edit parameters → 데이터폴더** to the full path of `examples\_data\korean-retail\en` |
| `python` is not recognized | Reinstall Python with **Add python.exe to PATH**, or run `py tools\quickstart.py` |
| Desktop won't open the `.pbip` | Update Power BI Desktop |
| Table and column names in the Data pane are Korean | The sample model is a Korean retail dataset. Labels on the page are translated; your own model keeps its own names |
| KPI comparison lines missing, text cut off | Your Power BI Desktop is older than 2.157 (**Help → About**). With two copies installed (installer and Store), double-clicking opens the older one: run `python tools/quickstart.py --open`, or start Desktop from the Start menu and use **File → Open** ([#1](https://github.com/Haweee47/powerbi-autopilot/issues/1)) |
| Anything else looks wrong | [Report it](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=1-render-bug.yml) with a full-window screenshot |

## Feedback

Every issue is read, logged and answered. See [how feedback becomes changes](../../CONTRIBUTING.md#how-feedback-becomes-changes).

- [Something looks wrong](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=1-render-bug.yml)
- [Design feedback](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=2-design-feedback.yml) (a 1-5 rating is enough)
- [New pilot or feature](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=3-pilot-request.yml)
- [Questions and show-and-tell](https://github.com/Haweee47/powerbi-autopilot/discussions)
