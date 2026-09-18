# 1차 홍보(작게) 초안 — 피드백을 받는 것이 목적

큰 홍보(r/PowerBI · Hacker News · awesome 목록)는 [launch-posts.md](launch-posts.md)에 있고, **예제 01·02(기존 도구와의 토큰·디자인 비교)가 끝난 뒤**에 한다.
그전까지는 "왜 Microsoft 공식 스킬 대신 이걸 쓰나"에 숫자로 답할 수 없다. 한 번뿐인 기회를 거기에 쓴다.

이 단계의 목적은 **스타가 아니라 외부 의견**이다. 지금까지 디자인을 평가한 사람은 나 혼자고, 이슈 양식·Discussions·채점표를 만들어 뒀는데 들어온 평가가 0건이다.

## 어디에, 어떤 순서로

| 순서 | 채널 | 무엇을 | 왜 |
|---|---|---|---|
| 1 | **LinkedIn (한국어)** | `demo-ko.gif` 한 장 + 아래 한국어 글 | 실무자 도달과 포트폴리오가 같은 글에서 해결된다. 댓글로 의견이 남는다 |
| 2 | **국내 Power BI·데이터 분석 커뮤니티** (본인이 이미 속한 오픈채팅·디스코드·페이스북 그룹) | 짧은 버전 + 링크 | 피드백 밀도가 가장 높다. 모르는 커뮤니티에 새로 가입해 홍보부터 하지 않는다 |
| 3 | **GitHub Discussions → Show and tell** | 영어 글 + `demo-en.gif` | 저장소에 들어온 사람이 읽을 고정 글. 이후 모든 링크의 착지점 |
| 4 | **LinkedIn (영어)** | 같은 영상 + 영어 글 | 1과 같은 날 올리지 않는다. 2~3일 뒤 |
| 5 | (선택) **X** | 짧은 글 + `demo-en.gif` | 비용이 거의 없다 |

**하루에 한 곳.** 올린 뒤 몇 시간 안에 댓글에 답하는 것이 글 자체보다 중요하다. 링크는 저장소 하나만 건다.

## 첨부 파일 (`docs/share/media/`, `tools/make_launch_media.py`로 생성)

| 파일 | 쓰는 곳 |
|---|---|
| `demo-ko.gif` · `demo-en.gif` | 요청을 입력하면 페이지가 나오는 20초 루프 (1200×675) |
| `slide-ko-1..4.png` | LinkedIn 이미지 여러 장으로 올릴 때 (1200×1200): 표지 · DPU 페이지 · 테마 7종 · 숫자 |
| `carousel.pdf` | LinkedIn 문서(슬라이드)로 올릴 때 |

LinkedIn은 한 게시물에 **영상 하나 / 이미지 여러 장 / 문서 하나** 중 하나만 붙는다. 1차는 **영상(GIF) 한 장**을 권한다. 움직이는 결과물이 가장 빨리 이해된다.

---

## 1. LinkedIn (한국어) — `demo-ko.gif` 첨부

🤖 자연어 한 줄로 Power BI 리포트를 끝까지 만들었습니다. Desktop에서 클릭한 곳은 없습니다.

💬 입력한 요청
"풀필먼트센터 운영 리포트 만들어줘. 출고가 1순위, 생산성(UPH)이랑 그 원인까지 보이게."

⚙️ 나온 결과
• 7페이지 · 비주얼 96개
• 에이전트가 직접 쓴 건 명세 8.9K 토큰뿐, 나머지는 스크립트가 생성
• Microsoft 공식 PBIR 검증 오류 0 · 경고 0
• Power BI Desktop에서 전 페이지를 캡처해 눈으로 확인하는 것까지 한 번의 실행

⏱️ 리포트 하나에 2~10분, 약 $0.6~4 (800~5,500원)
추정이 아니라 리포트 두 개를 처음부터 끝까지 만들어 잰 값입니다.

🔍 왜 만들었나
이전 직장에서 PBIP와 LLM으로 리포트를 만드는 방식을 팀에 배포한 적이 있습니다. 동작은 했지만 두 가지가 발목을 잡았습니다. 토큰이 너무 많이 들었고, 결과물이 예쁘지 않았습니다.
공개 리포트 1,800여 개를 뜯어 보니 visual.json 용량의 67%가 서식이었고, 그게 비주얼마다 반복되고 있었습니다. 서식을 테마로 옮기니 에이전트가 쓰는 양이 생성물의 6%가 됐습니다.

⚠️ 가장 많이 배운 지점
검증을 통과한 파일이 화면에서는 틀린 경우가 25번 넘게 있었습니다. 단위가 두 번 붙고, KPI 카드 글자가 잘리고, 슬라이서 기본값이 조용히 무시됐습니다.
그래서 "Desktop에서 캡처해 눈으로 본다"가 이 워크플로의 핵심이 됐습니다.

📊 지금 들어 있는 것
• 용도별 파일럿 5종: 대시보드 · 지표 테이블 · 행렬 확인 · 딥다이브 · 풀필먼트센터 운영
• 테마 7종 + 브랜드 색 하나로 새 테마를 만드는 도구
• 배치 2종(왼쪽 레일 · 상단 메뉴), 한국어 내장
• 내 시맨틱 모델에도 적용 — 쓰던 리포트를 PBIP로 저장하면 연결과 SQL은 그대로 두고 필드만 대응표로 잇습니다

🙋 두 가지가 궁금합니다
1️⃣ 이 화면, 실무에서 그대로 쓰시겠습니까? 어디가 제일 걸리나요?
2️⃣ 어떤 용도의 파일럿이 더 필요할까요?

🔗 오픈소스(MIT), quickstart.cmd 더블클릭으로 실행됩니다
github.com/Haweee47/powerbi-autopilot

모든 이름과 숫자는 가상 데이터입니다. Windows + Power BI Desktop 2.157 이상이 필요하고, 일본어·중국어 화면 글자는 아직 진행 중입니다.

#PowerBI #데이터분석 #BI #오픈소스 #물류 #ClaudeCode

---

## 2. 국내 커뮤니티 (짧은 버전)

Power BI 리포트를 자연어 한 줄로 끝까지 만드는 워크플로를 오픈소스로 공개했습니다(MIT).

요청 한 줄 → 데이터 모델 → 페이지·테마 → 공식 PBIR 검증 → Desktop에서 전 페이지 캡처까지 한 번에 돕니다. 리포트 하나에 2~10분, API 비용 약 $0.6~4로 실측했습니다. 용도별 파일럿 5종(대시보드·지표 테이블·행렬·딥다이브·풀필먼트 운영), 테마 7종, 한국어 내장입니다.

**디자인 의견을 듣고 싶어서 올립니다.** 실무에서 그대로 쓰기 어려운 부분이 있으면 그게 제일 듣고 싶은 이야기입니다. 이슈 양식에 1~5점 평가란이 있습니다.

github.com/Haweee47/powerbi-autopilot (전부 가상 데이터, Windows + Desktop 2.157+)

---

## 3. GitHub Discussions → Show and tell (영어) — `demo-en.gif` 첨부

**Title:** One request in, a checked Power BI report out — and I'd like your eyes on the design

I've been building an agent workflow that takes a one-line request and produces a finished PBIP: semantic model, pages, theme, navigation, then Microsoft's PBIR validator, then a Desktop pass that screenshots every page.

What's in it today:
- **5 pilots**: executive dashboard, measure table, metric-check matrix, deep dive, and a fulfillment-operations pilot (outbound → lost hours vs standard → productivity by hour → teams → travel per unit → inbound and inventory)
- **7 themes** (a color palette plus a card shape) and two frames: a left rail or a top bar
- **Low token cost**: the agent writes a 1–9K-token spec; scripts generate the rest, about 6% of the output
- **Measured**: about $0.6–4 and 2–10 minutes per report ([how](https://github.com/Haweee47/powerbi-autopilot/blob/main/docs/cost-per-report.md)); 80 build combinations pass the validator with 0 errors and 0 warnings

The thing I keep relearning: a file that passes validation can still be wrong on screen. 25+ issues only showed up in the Desktop captures — doubled units, clipped KPI cards, a slicer default silently ignored, a translated value breaking a relationship so a page came up empty.

**What I'd like feedback on**
1. Would you put these pages in front of your stakeholders as they are? What breaks first?
2. Which purpose is missing from the pilots?
3. If you run Power BI on a real warehouse (Presto, Redshift, Snowflake): the generator copies your M expressions and never touches credentials, but I've only tested through a local ODBC driver. I'd like to hear how it goes.

Design feedback has its own issue form with a 1–5 rating against the published rubric — that rating is the data I use to decide what to change.

Limits, up front: Windows only (Desktop), 2.157+, Japanese and Chinese UI strings are partial, all sample data is synthetic.

https://github.com/Haweee47/powerbi-autopilot

---

## 4. LinkedIn (영어) — 2~3일 뒤, 같은 영상

One line of plain language in, a finished Power BI report out. No clicks in Desktop.

> "Build a fulfillment operations report: outbound first, then productivity (UPH) and what moves it."

That request produces 7 pages and 96 visuals. The agent writes only a spec (8.9K tokens); scripts generate the rest. Microsoft's PBIR validator runs, then Power BI Desktop opens the report and every page is captured and checked. **2–10 minutes and about $0.60–4 per report — measured, not estimated.**

Why I built it: at a previous job I shipped an LLM workflow that wrote Power BI reports from existing PBIP files. It worked, but it burned tokens and the output looked like everything else. Across 1,800+ public reports, 67% of visual.json bytes are formatting, repeated in every visual. Move formatting into the theme and the agent's share of the output drops to about 6%.

The lesson that stuck: **a file that passes the validator can still be wrong on screen.** 25+ times — doubled units, clipped KPI cards, an ignored slicer default. So "open it in Desktop and look at every page" became the core of the workflow, not an afterthought.

Two questions for the Power BI people here:
1. Would you show these pages to stakeholders as they are? What breaks first?
2. Which report purpose is missing?

Open source (MIT), double-click to run: github.com/Haweee47/powerbi-autopilot
All sample data is synthetic. Windows + Power BI Desktop 2.157+; Japanese and Chinese are still partial.

#PowerBI #DataVisualization #PBIP #AI #MicrosoftFabric

---

## 5. X (선택)

One request → a finished Power BI report: model, pages, theme, Microsoft's PBIR validator, then a Desktop pass that screenshots every page.

~$0.6–4 and 2–10 min per report, measured. 5 pilots, 7 themes, MIT.

github.com/Haweee47/powerbi-autopilot

---

## 올리기 전 확인

- [ ] 첨부한 GIF·이미지에 회사명·실데이터·로컬 경로가 없다 (전부 가상 데이터)
- [ ] 저장소 링크가 열리고 README 첫 화면이 깨지지 않는다
- [ ] Discussions의 Show and tell 글을 먼저 올려 두고, 다른 채널에서 그 글이 아니라 저장소를 링크한다
- [ ] 댓글 알림을 켜 둔다. 첫 24시간 안에 답하는 것이 글보다 중요하다
- [ ] 들어온 의견은 `docs/feedback-log.md`에 날짜·채널·요지로 남긴다 (칭찬도 포함, 나중에 무엇이 통했는지 알기 위해)
