# Changelog

What changed, newest first. Issues fixed by a release are linked by number.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · versions: [SemVer](https://semver.org/).

## [Unreleased]

The first release (v0.1.0) goes out once the known issue below is fixed.

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

### Known issues
- **Power BI Desktop 2.157.1354.0** (a Microsoft Store auto-update, September 2026) renders the pilots differently from 2.157.879.0, where they were checked:
  KPI cards drop the comparison line ("YoY ▲1.5%"), the one-line takeaway is clipped at the top, table columns no longer stretch to the visual's width,
  and the channel slicer buttons truncate ("Offli…"). The generated files are unchanged; a fix is in progress.
