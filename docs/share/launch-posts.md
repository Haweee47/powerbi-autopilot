# 공개 알림 초안 (오픈소스 공유용)

> **이 파일은 큰 홍보용이다.** 전제 조건이던 예제 01·02(기존 도구와의 비교)는 2026-09-20에 끝났고, 그 숫자가 아래 글에 들어 있다.
> 작은 홍보(LinkedIn·커뮤니티·Discussions)는 [soft-launch.md](soft-launch.md)에 있고 2026-09-20에 LinkedIn부터 시작했다.
> awesome-claude-code 제출은 첫 커밋 +14일인 **2026-09-25**부터 가능하다.

광고가 아니라 "만든 것과 배운 것을 공유하고 의견을 묻는" 글이다. 채널마다 한 번씩, 하루에 한 곳씩 올린다.
첫 몇 시간 안에 댓글에 답하는 것이 글 자체보다 중요하다. 링크는 저장소 하나만 건다.

| 채널 | 언제 | 비고 |
|---|---|---|
| r/PowerBI | 화~목 오전(미국 동부) | 커뮤니티 규칙 확인, 플레어는 공유용(예: Community Share) |
| Hacker News (Show HN) | 화~목 오전(미국 동부) | 기술 이야기 위주, 한계를 먼저 말한다 |
| Fabric Community 포럼 | 아무 때나 | Power BI 커뮤니티 블로그 또는 Desktop 포럼 |
| LinkedIn | 평일 오전 | [linkedin-post.md](linkedin-post.md) |
| awesome-claude-code | **2026-09-25 이후** (첫 커밋 후 14일) | 웹 양식으로 사람이 직접 제출 (CLI·에이전트 제출 금지 규칙) |
| dev.to · Medium | 위 글들 뒤 | 아래 블로그 초안 |

---

## r/PowerBI

**Title:** I made an open-source workflow where an AI agent builds a Power BI report (PBIP) end to end, and checks it in Desktop

**Body:**

I've been working on letting an AI agent build Power BI reports without me touching Desktop, and I'm sharing it in case it's useful (MIT, no signup).

- You ask for a report in one line. The agent picks one of 4 pre-built pilots (dashboard, measure table, matrix check, deep dive), swaps in your fields, generates the PBIP, runs Microsoft's PBIR validator, then opens it in Desktop and screenshots every page.
- Formatting lives in the theme instead of every visual.json, so the agent only writes a 1–3.5K-token spec (about 6% of the generated report).
- I finished the same page with Microsoft's `powerbi-report-cli` and with data-goblin's `pbir` to see whether that is worth anything. Instructions to read: ~1.7k tokens here, ~89 KB of reference files there, ~32.6k tokens for the four data-goblin skills. Microsoft's CLI has no create command, so the agent hand-writes every `visual.json` - 13.7 KB for 8 visuals. Both public runs produced pages their validators called clean that were wrong on screen ([example 01](https://github.com/Haweee47/powerbi-autopilot/tree/main/examples/01-microsoft-skill), [example 02](https://github.com/Haweee47/powerbi-autopilot/tree/main/examples/02-data-goblin)).
- Measured cost: about $0.60–4 of Claude Opus 5 API tokens and 2–10 minutes per report, including the Desktop capture pass ([how it was measured](https://github.com/Haweee47/powerbi-autopilot/blob/main/docs/cost-per-report.md)).
- It works on your own model: a model map lists the fields and measures a pilot needs, with the reference DAX as hints.
- 7 themes (classic, showcase, practical) or one made from your brand color, English and Korean. Japanese and Chinese are in progress, and native speakers are welcome to help.

The part I didn't expect: files that passed the validator still looked wrong on screen more than 25 times (doubled units, clipped KPI cards, a slicer default filter silently ignored). So the Desktop screenshot step became the core of the workflow.

Try it: download, double-click `quickstart.cmd`, click Refresh. https://github.com/Haweee47/powerbi-autopilot

I'd really like to hear which pilot you'd use at work and what's missing. ODBC works through a local driver (example 06), but I haven't tried a live warehouse yet, so feedback from Presto, Redshift or Snowflake users is especially welcome.

---

## Hacker News

**Title:** Show HN: Powerbi-autopilot – an AI agent that builds Power BI reports and checks them in Desktop

**Text:**

Power BI's new text formats (PBIP/PBIR/TMDL) let an agent write reports directly. In practice two things got in the way for me: token cost (formatting is repeated in every visual file; 67% of visual.json bytes across ~11k public files) and quality (validator-clean files that render wrong).

What I built: formatting moves into a generated theme, page coordinates into layout templates, and the agent only writes a small spec (1–3.5K tokens, ~6% of the output). A script checks every field against the model before anything is written. After Microsoft's validator passes, a UI Automation loop opens the report in Power BI Desktop and captures every page. That loop caught 25+ issues the validator couldn't see.

Measured end to end, one report took 2.5–7.5 minutes and $0.57–2.43 of Claude Opus 5 API tokens (normalized to a fresh session), most of it cache reads.

Design rules come from analyzing 1,800+ public reports and a handful of visualization papers (Kim et al. 2021 on chart+text emphasis, Bach et al. 2023 dashboard patterns).

I also finished the same page with the two public toolkits to check the claim. Measured with one instrument (`claude plugin details`): ~1.7k tokens of instructions here, ~4.4k (+14.7k for its model skill) over ~89 KB of reference files for Microsoft's, ~32.6k for data-goblin's four authoring skills. Microsoft's CLI is lookup and validation only - `catalog`, `formatting`, `validate` - so the agent writes every `visual.json` by hand, 13.7 KB for 8 visuals; their own reference recommends a deterministic generator when repetition is the constraint. data-goblin's `pbir` does generate, compactly, but `pbir new report` needs a Fabric sign-in and a published model, so there is no local-only path in. Both runs passed their validators and were wrong on screen - one with auto-units and a three-year sum, the other missing two of seven visuals for a reason I tested four hypotheses for and never found.

Starting from data with no model at all works now too: `new_model.py` reads a CSV folder, an Excel workbook or a database over ODBC and writes the TMDL, with the inferred keys and calendar printed.

Limits: Windows only (Desktop), Desktop 2.157+ (older builds clip labels, found while testing the first-run flow), ODBC tested only through a local driver so far, no live warehouse tested, Japanese/Chinese partial.

https://github.com/Haweee47/powerbi-autopilot

---

## Fabric Community (Power BI 커뮤니티 블로그·포럼)

**Title:** Open-source PBIP pilots: let an AI agent build a themed, multi-page report and verify it in Desktop

**Body:**

I'm sharing an open-source project (MIT) built on PBIP/PBIR/TMDL.

It includes four pilot reports (executive dashboard, measure table, metric-check matrix, deep dive), seven themes generated from one token file (a color palette plus a card shape), and a generator that turns a small JSON spec into a PBIP. Every pilot passes `powerbi-report-author validate` with 0 errors and 0 warnings and was captured in Desktop 2.157.

A few PBIR details I learned the hard way, in case they save someone time:
- On/off toggles (`show`) for buttons and card fills only take effect in selector-less entries.
- The button slicer's button fill is `fillCustom`, not `background`.
- Format-string scaling like `#,0.0,,"M"` was ignored in my tests; dividing in the measure worked.
- Desktop 2.147 drops `cardCalloutArea` on save and clips several card labels; 2.157 renders the same files correctly.

Repo and a quick start (double-click `quickstart.cmd`): https://github.com/Haweee47/powerbi-autopilot
Feedback and questions are very welcome.

---

## awesome-claude-code (웹 양식, 2026-09-25 이후 직접 제출)

양식: https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml

**Description (한 줄, 이모지 없이, 설명체):**
Claude Code skills and scripts that build Power BI reports (PBIP) from pre-built pilots, validate them with Microsoft's PBIR validator, and check every page in Power BI Desktop.

---

## 블로그 초안 (dev.to · Medium)

**Title:** An AI agent writes Power BI reports now. Here's what the validator couldn't catch

1. **The problem.** At a previous job I had an LLM read existing PBIP reports and generate new ones. It worked, but it cost hundreds of thousands of tokens per report and the output looked like the reports it copied.
2. **Where the tokens go.** 1,800+ public reports: 67% of visual.json bytes are formatting, repeated per visual. Move it into the theme, and the agent writes a spec that's about 6% of the final report.
3. **Pilots, not prompts.** Four finished reports by purpose. A new report is a copy with different fields. The agent asks three questions: purpose, theme, language.
4. **What a report costs.** Two reports built end to end: 8 and 28 requests, 2.5 and 7.5 minutes, about $0.6 and $2.4. A long session had cost $262 for the whole build, 96% of it re-reading context.
5. **The validator is not the screen.** 25+ bugs that passed validation: a year filter ignored because it was written as text, "40천만" doubled units, clipped KPI cards, English numbers printed as "110,558,285.0,,M".
6. **A wrong hypothesis, on the record.** I blamed a Desktop auto-update for broken pilots; the window I was testing was an older installer copy that `.pbip` files opened by default.
7. **Design from evidence.** Takeaway sentence under every title, the same item highlighted in the chart, the current filter scope next to the title, 5–8 visuals per page.
8. **Try it / tell me.** Link, quick start, feedback forms.
