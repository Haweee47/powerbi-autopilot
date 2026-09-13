# powerbi-autopilot

요청 한 줄로 Power BI 리포트를 **데이터 모델 → 디자인 → 검증**까지 만드는 AI 에이전트 워크플로우.
목표는 두 가지다. **보기 좋은 리포트**, 그리고 **적은 토큰**.

> **TL;DR (EN)** — An AI-agent workflow that turns a one-line request into a finished Power BI report (PBIP).
> Four purpose-built pilots (dashboard, measure table, matrix check, deep dive) × three themes (Navy, Paper, Midnight),
> English by default with Korean built in. The agent writes a 1–3K-token spec; scripts generate the rest
> (about 6% of the output), it passes Microsoft's PBIR validator with zero errors, and every page is checked in
> Power BI Desktop. Design rules come from 1,800+ public reports and visualization research.

![파일럿 4종](docs/share/media/cover.png)

---

## 왜 만들었나

이전 직장에서 기존 Power BI 리포트를 PBIP(텍스트 형식)로 바꿔 LLM에게 읽히고, 템플릿을 참고해 새 리포트를 만들게 하는 방식을 직접 설계해 팀에 배포했다.
리포트는 만들어졌다. 하지만 실무에서 계속 쓰기에는 두 가지가 걸렸다.

1. **토큰이 너무 많이 들었다.** 리포트 몇 개를 "학습"시키려면 매번 수십만 토큰을 읽어야 했다.
2. **결과물이 예쁘지 않았다.** 기존 리포트를 따라 하니 기존 리포트 수준의 디자인이 그대로 나왔다.

그래서 이 문제를 공개 데이터로 처음부터 다시 풀고 있다. 모든 과정은 [진행 기록](docs/progress-log.md)에 남긴다. 결정한 것, 틀린 가설, 실패까지 전부다.

## 어떻게 쓰나

새 리포트를 부탁하면 에이전트가 세 가지만 묻는다. **용도, 테마, 언어.**
그다음 미리 만들어 둔 파일럿을 복사해 필드와 문장만 바꾸고, 생성·검증·Desktop 캡처까지 한다 ([스킬](.claude/skills/new-report/SKILL.md)).

```bash
python tools/new_report.py --purpose table --theme paper --lang ko --name StoreKPI   # 파일럿 복사 (명세 1.6K 토큰)
python tools/generate_pbir.py examples/StoreKPI/report.spec.json                      # PBIP 생성
powerbi-report-author validate examples/StoreKPI/StoreKPI.Report                       # 공식 검증
```

## 용도별 파일럿 4종

| 대시보드 — 경영 요약 | 지표 테이블 — 측정값 입력 매트릭스 |
|---|---|
| ![대시보드](templates/dashboard/screenshots/summary.png) | ![지표 테이블](templates/table/screenshots/stores.png) |
| KPI · 추이 · 결론 한 줄 → 드릴스루 상세 | 행 = 항목, 열 = 측정값. 열마다 `bar`·`heat`·`sign` 한 단어로 조건부 서식 |
| **지표 확인 — 행렬** | **딥다이브 — 분석** |
| ![행렬](templates/matrix/screenshots/heatmap.png) | ![딥다이브](templates/deepdive/screenshots/decomposition.png) |
| 계층 행 × 월 히트맵, 권역 > 매장 성적표 (펼친 채로 열림) | 요인 분해 트리 · 할인과 이익 산점도 · 원천 행 |

전체 목록과 선택 기준: [templates/catalog.json](templates/catalog.json)

## 테마 3종 · 언어

![테마 3종](docs/share/media/themes.png)

- **테마**: 네이비 · 페이퍼 · 미드나잇. 토큰 파일 하나에서 생성하고 셋 다 Power BI 공식 테마 스키마(2.157)를 통과한다.
- **언어**: 기본 영어, 한국어 내장. 화면 글자·필드 이름·숫자 단위(M·K ↔ 만·억)·결론 문장·데이터 값까지 언어별로 바뀐다.
  다른 언어는 [locales.json](design-system/i18n/locales.json) 한 줄과 측정값 파일 하나로 더한다.

## 지금까지 한 것

| 영역 | 결과 |
|---|---|
| 공개 리포트 분석 | GitHub 저장소 1,737곳을 훑어 **PBIX·PBIT 1,830개 + PBIP 폴더 271개** 분석 ([research](research/README.md)) |
| 서식 실태 조사 | `visual.json` 11,323개. **파일 용량의 67%가 서식이고, 대부분 테마가 아니라 비주얼마다 따로 박혀 있다** |
| 디자인 근거 | 수집 데이터 + 연구 11편([literature.md](design-system/literature.md)) → [원칙](design-system/principles.md) → [채점표](design-system/review-rubric.md) |
| 데이터 모델 | Power BI Modeling MCP로 테이블 7 · 관계 6 · 측정값 29. **DAX 쿼리 결과가 Python 기대값과 전부 일치** ([예제 03](examples/03-modeling-mcp/model-doc.md)) |
| 생성기 | 명세 → PBIP. 파일럿 4종 + 한국어 예제 모두 **공식 검증(`powerbi-report-author validate`) 오류 0 · 경고 0** |
| 렌더링 검증 | 생성한 파일을 Desktop으로 열어 전 페이지를 캡처하는 루프. 검증기는 통과했지만 화면이 틀린 문제를 **25개 넘게** 찾아 고쳤다 |

## 토큰을 어떻게 줄였나

| 파일럿 | 에이전트가 쓰는 명세 | 생성되는 리포트 JSON |
|---|---:|---:|
| 지표 확인 (행렬) | 1.3K 토큰 | 22K 토큰 |
| 지표 테이블 | 1.9K | 25K |
| 딥다이브 | 2.0K | 38K |
| 대시보드 | 3.5K | 57K |

좌표는 레이아웃 템플릿이, 서식은 테마가, 단위·문장은 공용 측정값 파일이, 필드 대조와 파일 구조는 스크립트가 맡는다.
새 리포트는 파일럿을 복사하면서 한 언어만 남기므로 더 작다. 없는 필드는 TMDL과 대조해 Desktop을 열기 전에 멈춘다(토큰 0).

## 디자인 근거

감이 아니라 데이터와 연구에서 정했다. 몇 가지만:

- **결론은 글로, 그리고 차트에서도 같은 것을 강조한다.** 글과 차트가 같은 특징을 말할 때 그것이 핵심으로 남는다 (Kim et al., CHI 2021).
  그래서 페이지마다 DAX가 쓰는 결론 한 줄이 있고, 그 항목은 차트에서 빨강·맨 윗줄로 다시 보인다.
- **지금 무엇을 보고 있는지 늘 보인다.** 제목 오른쪽에 "2026 · Jan–Aug · All channels" (Bach et al., IEEE TVCG 2023 메타 정보 패턴).
- **질서가 적음만큼 중요하다.** 핵심 차트를 왼쪽 가운데에 두면 시선 이동이 가장 짧다 (시선 추적 연구, Sensors 2024).
- **좋은 리포트는 덜 채운다.** 전문가·공식 리포트는 포트폴리오 리포트보다 페이지당 비주얼이 적고(5.8개 대 10개) 간격이 넓었다(32px 대 18px, 수집 데이터).
- **숫자는 3~4자리 + 단위.** "841.8M", "8.4억" (Microsoft 가이드).

## 일하는 방식

AI 에이전트(Claude Code)가 파일을 만들고 고친다. 나는 문제를 정의하고, 설계를 정하고, 검증 기준을 세우고, 결과를 판단한다.

1. **원본을 통째로 읽히지 않는다.** 스크립트가 필요한 것만 뽑고 에이전트는 요약만 본다.
2. **숫자는 쿼리로 확인한다.** 결론 문장까지 DAX로 대조한다.
3. **화면은 캡처로 확인한다.** 검증기를 통과한 파일에서도 전 기간 합계가 보이거나("35.8억"), 단위가 두 번 붙거나("40천만"), 영어 숫자가 "110,558,285.0,,M"로 나왔다.
4. **속성 이름은 도구로 확인한다.** 공식 CLI와 공개 PBIR 수백 개에서 실제 저장 형식을 대조한다.
5. **실패도 기록한다.**

## 저장소 구성

```
powerbi-autopilot/
├── templates/         용도별 파일럿 4종, 공용 측정값(언어별)·용어집, 선택 카탈로그
├── design-system/     원칙·채점표·연구 정리, 토큰 → 테마 3종, 레이아웃 템플릿, 언어 등록부, HTML 시안
├── tools/             생성기(명세 → PBIR), 새 리포트 시작, 테마·레이아웃 빌드, 공유 이미지, 토큰 측정
├── examples/          공용 가상 데이터(한·영), 예제 03(Modeling MCP), 예제 04(생성기 첫 버전)
├── research/          공개 리포트 수집·분석 스크립트와 결과 (원본은 재배포하지 않음)
├── docs/              환경 세팅, 진행 기록, 공유 초안
└── .claude/skills/    new-report: 용도·테마·언어를 묻고 파일럿으로 시작하는 에이전트 절차
```

## 직접 해 보기

```bash
python examples/_data/korean-retail/generate.py              # 가상 판매 데이터 (시드 고정)
python examples/_data/korean-retail/generate.py --lang en    # 같은 데이터, 영어 값
python tools/build_layouts.py && python tools/build_themes.py
python tools/generate_pbir.py templates/dashboard/pilot.spec.json               # 영어 · 네이비
python tools/generate_pbir.py templates/dashboard/pilot.spec.json --lang ko --theme midnight --out <폴더>
```

## 다음 계획

- [x] 디자인 토큰 → 테마, 레이아웃 템플릿, 명세 → PBIR 생성기
- [x] 용도별 파일럿 4종 · 테마 3종 · 다국어
- [ ] 표 안의 미니 추이선(SVG 측정값)
- [ ] Presto·Redshift 쿼리 → 모델 → 파일럿으로 이어지는 실데이터 흐름
- [ ] 같은 요청문으로 도구 3종 비교(Microsoft 공식 스킬 / 커뮤니티 스킬 / Modeling MCP), 토큰과 채점표 점수로

## 기술

Power BI (PBIP · PBIR · TMDL · DAX) · Python (생성기·분석 스크립트) · JavaScript/SVG (반응형 시안) ·
Claude Code + MCP (Power BI Modeling MCP) · Windows UI Automation (Desktop 캡처) · Git

---

만든 사람: [Haweee47](https://github.com/Haweee47) · 라이선스: [MIT](LICENSE)
