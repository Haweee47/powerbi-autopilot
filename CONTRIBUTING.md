# Contributing

Thanks for looking. The most useful thing you can do is **try a pilot and tell me what you see**.
Issues, discussions and pull requests are welcome in English, 한국어, 日本語 or 中文.

## Ways to help

| You want to… | Go to |
|---|---|
| Report something that renders wrong | [Issue: Something looks wrong](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=1-render-bug.yml) |
| Say what looks good or bad (a 1-5 rating is enough) | [Issue: Design feedback](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=2-design-feedback.yml) |
| Ask for a report type or feature | [Issue: New pilot or feature](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=3-pilot-request.yml) |
| Add or fix a language | [Issue: Language support](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=4-language-request.yml) |
| Ask a question or show what you built | [Discussions](https://github.com/Haweee47/powerbi-autopilot/discussions) |

**Never attach real company data.** Screenshots of the bundled sample data are all I need.

## How feedback becomes changes

```
issue form ─▶ needs-triage ─▶ triage ─▶ accepted / roadmap / wontfix ─▶ fix + before/after capture ─▶ CHANGELOG + release ─▶ issue closed with the version
```

- Every issue is triaged and logged in [docs/feedback-log.md](docs/feedback-log.md), so feedback is counted, not just remembered.
- Design feedback is mapped to the [review rubric](design-system/review-rubric.md). When three or more people point at the same thing,
  the design rule itself is revisited, with the issues cited as evidence.
- Design ratings are also a check on my own judgment: the pilots were designed from research and public reports, and your ratings show whether that worked.
- Triage is partly done by an AI agent (the [`triage-feedback`](.claude/skills/triage-feedback/SKILL.md) skill). Decisions and replies are reviewed by me before they're posted.

### Labels

| Label | Meaning |
|---|---|
| `needs-triage` | New, not looked at yet |
| `render` · `design` · `pilot-request` · `i18n` | What the issue is about |
| `accepted` | Will be fixed soon |
| `roadmap` | Good idea, planned for later |
| `wontfix` | Declined, with the reason in a comment |

## Working on the code

Python 3.10+. The generator itself uses only the standard library; the checks need `pip install jsonschema pillow`
and Microsoft's validator (`npm install -g @microsoft/powerbi-report-authoring-cli`).

```bash
python tools/check.py                                            # what CI runs: regenerate, build 24 reports, validate
powershell -ExecutionPolicy Bypass -File tools\render_check.ps1  # Windows: open every pilot in Desktop, capture, compare
```

Before opening a pull request:

1. `python tools/check.py` passes: committed files are up to date and every report shows **0 errors · 0 warnings**. CI runs the same check on your PR.
2. For anything visual, `tools/render_check.ps1` shows no unexpected change and you attach before/after captures. The validator can pass while the screen is wrong.
3. Formatting goes in the theme (`design-system/tokens.json` → `tools/build_themes.py`), not in individual visuals.
4. No confidential data, personal data or local paths. Sample data must be synthetic or public.
5. If you change `README.md`, change `README.ko.md` too, and add a line to `CHANGELOG.md` under "Unreleased".

## License

MIT. By contributing you agree your contribution is released under the same license.
Please don't paste code from GPL projects (for example data-goblin's plugins). Link to them instead.
