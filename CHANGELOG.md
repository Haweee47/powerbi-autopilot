# Changelog

What changed, newest first. Issues fixed by a release are linked by number.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · versions: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- `tools/check.py`: one command that regenerates the committed files, builds all 24 pilot × theme × language combinations
  and runs Microsoft's validator. CI runs it on every push and pull request
- `tools/render_check.ps1` + `tools/render_report.py`: open each pilot in Power BI Desktop, refresh, capture every page and
  compare with the committed screenshots. Works in any Desktop display language

### Fixed
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

[Unreleased]: https://github.com/Haweee47/powerbi-autopilot/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Haweee47/powerbi-autopilot/releases/tag/v0.1.0
