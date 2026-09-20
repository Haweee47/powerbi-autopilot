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
| 5 | (선택) **X** | 짧은 글 + `demo-en.mp4` | 비용이 거의 없다 |

**하루에 한 곳.** 올린 뒤 몇 시간 안에 댓글에 답하는 것이 글 자체보다 중요하다. 링크는 저장소 하나만 건다.

## 첨부 파일 (`docs/share/media/`, `tools/make_launch_media.py`로 생성)

| 파일 | 쓰는 곳 |
|---|---|
| `demo-ko.mp4` · `demo-en.mp4` | **LinkedIn·X에는 이걸 올린다.** 요청을 입력하면 페이지가 나오는 15~17초 영상 (1200×674, H.264) |
| `demo-ko.gif` · `demo-en.gif` | 같은 내용의 GIF. 영상 업로드가 안 되는 곳(일부 커뮤니티·이슈·README)에 쓴다 |
| `slide-ko-1..4.png` | LinkedIn 이미지 여러 장으로 올릴 때 (1200×1200): 표지 · DPU 페이지 · 테마 7종 · 숫자 |
| `carousel.pdf` | LinkedIn 문서(슬라이드)로 올릴 때 |

LinkedIn은 한 게시물에 **영상 하나 / 이미지 여러 장 / 문서 하나** 중 하나만 붙는다. 1차는 **영상(`demo-ko.mp4`)**을 권한다.
움직이는 결과물이 가장 빨리 이해되고, 같은 내용이라도 GIF보다 영상 쪽이 피드에서 더 멀리 간다.

---

## 1. LinkedIn (한국어) — `demo-ko.mp4` 첨부

🤖 필요한 리포트를 말로 적어 주면 Power BI 리포트가 끝까지 나옵니다. Desktop에서 클릭한 곳은 없습니다.

💬 입력한 요청 (짧게 써도 되고, 자세히 쓰면 더 정확해집니다)
"매장별 매출 대시보드 만들어줘.
 - 보는 사람은 영업 팀장과 매장 담당자, 매주 월요일 회의에서 본다
 - 1순위는 매출. 전년 대비와 목표 달성률을 나란히, 금액은 억·만 단위로
 - 부진한 곳이 바로 보이게: 카테고리별 목표 대비, 하위 매장 3곳은 따로
 - 매장을 누르면 상세 페이지로 넘어가게, 기간은 올해가 기본
 - 테마는 실무용으로 차분하게, 한국어로"

⚙️ 나온 결과
• 4페이지 · 비주얼 55개
• 에이전트가 직접 쓴 건 명세 3.1K 토큰뿐, 나머지는 스크립트가 생성
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
• 용도별 파일럿 5종: 경영 대시보드 · 지표 테이블 · 행렬 확인 · 딥다이브 · 물류 운영
• 테마 7종 + 브랜드 색 하나로 새 테마를 만드는 도구
• 배치 2종(왼쪽 레일 · 상단 메뉴), 한국어 내장

✍️ 요청은 이렇게 적으면 됩니다
한 줄만 써도 만들어집니다. 다만 **구체적일수록 고쳐 쓸 일이 줄어듭니다.**
• 짧게: "매장별 매출 대시보드 만들어줘"
• 보통: "매장별 매출 대시보드. 전년 대비랑 목표 달성률 같이 보이게, 하위 매장 3곳은 따로"
• 자세히: 위 요청처럼 — 보는 사람 / 1순위 지표 / 지표 정의(기준·단위) / 쪼개서 볼 축 / 이동(드릴스루) / 기본 기간 / 테마
무엇을 넣을지 모르겠다면 "누가, 언제, 무엇을 결정하려고 보는지" 한 줄만 더 적어도 결과가 달라집니다.

🔌 데이터 연결
CSV 폴더, 엑셀 파일, ODBC로 붙는 DB에서 시맨틱 모델을 만들어 줍니다. 이미 Power BI로 보고 있는 데이터라면 그 리포트를 PBIP로 저장하면 연결과 SQL을 그대로 물려받습니다.
다만 **실제 데이터 웨어하우스(Presto·Redshift·Snowflake 등) 연결은 아직 테스트하지 못했습니다.** 회사 계정이 필요해서요.
CSV·엑셀은 Desktop에서 숫자까지 대조해 확인했고, ODBC는 로컬 드라이버까지만 확인했습니다.
👉 **실무에서 웨어하우스에 붙여 쓸 수 있는 분이 계시면 꼭 피드백 부탁드립니다.** 어디서 막히는지가 지금 가장 궁금한 부분입니다.

🙋 세 가지가 궁금합니다
1️⃣ 이 화면, 실무에서 그대로 쓰시겠습니까? 어디가 제일 걸리나요?
2️⃣ 어떤 용도의 파일럿이 더 필요할까요?
3️⃣ 실제 DB(웨어하우스)에 붙여 보신다면, 되는지 안 되는지 알려주세요.

🔗 오픈소스(MIT), quickstart.cmd 더블클릭으로 실행됩니다
github.com/Haweee47/powerbi-autopilot

모든 이름과 숫자는 가상 데이터입니다. Windows + Power BI Desktop 2.157 이상이 필요하고, 일본어·중국어 화면 글자는 아직 진행 중입니다.

#PowerBI #데이터분석 #BI #오픈소스 #ClaudeCode

---

## 2. 국내 커뮤니티 (짧은 버전)

필요한 리포트를 말로 적으면 Power BI 리포트를 끝까지 만들어 주는 워크플로를 오픈소스로 공개했습니다(MIT).

요청 한 줄 → 데이터 모델 → 페이지·테마 → 공식 PBIR 검증 → Desktop에서 전 페이지 캡처까지 한 번에 돕니다. 리포트 하나에 2~10분, API 비용 약 $0.6~4로 실측했습니다. 용도별 파일럿 5종(경영 대시보드·지표 테이블·행렬·딥다이브·물류 운영), 테마 7종, 한국어 내장입니다.

요청은 한 줄로도 되고, "보는 사람 / 1순위 지표 / 지표 정의 / 원인 분해 축 / 필터 / 기본 기간 / 테마"까지 적으면 그대로 반영됩니다. 구체적일수록 고쳐 쓸 일이 줄어듭니다.

데이터는 CSV 폴더·엑셀·ODBC DB에서 모델을 만들어 주고, 이미 Power BI로 보고 있다면 PBIP로 저장해 연결을 그대로 씁니다.
다만 **실제 웨어하우스(Presto·Redshift·Snowflake) 연결은 아직 테스트를 못 했습니다**(회사 계정 필요). 실무에서 붙여 보실 수 있는 분이 있으면 피드백 부탁드립니다.

**디자인 의견도 듣고 싶습니다.** 실무에서 그대로 쓰기 어려운 부분이 있으면 그게 제일 듣고 싶은 이야기입니다. 이슈 양식에 1~5점 평가란이 있습니다.

github.com/Haweee47/powerbi-autopilot (전부 가상 데이터, Windows + Desktop 2.157+)

---

## 3. GitHub Discussions → Show and tell (영어) — `demo-en.gif` 첨부

**Title:** One request in, a checked Power BI report out — and I'd like your eyes on the design

I've been building an agent workflow that takes a one-line request and produces a finished PBIP: semantic model, pages, theme, navigation, then Microsoft's PBIR validator, then a Desktop pass that screenshots every page.

What's in it today:
- **5 pilots**: executive dashboard, measure table, metric-check matrix, deep dive, and one domain pilot for warehouse operations
- **7 themes** (a color palette plus a card shape) and two frames: a left rail or a top bar
- **Low token cost**: the agent writes a 1–9K-token spec; scripts generate the rest, about 6% of the output
- **Measured**: about $0.6–4 and 2–10 minutes per report ([how](https://github.com/Haweee47/powerbi-autopilot/blob/main/docs/cost-per-report.md)); 80 build combinations pass the validator with 0 errors and 0 warnings

The thing I keep relearning: a file that passes validation can still be wrong on screen. 25+ issues only showed up in the Desktop captures — doubled units, clipped KPI cards, a slicer default silently ignored, a translated value breaking a relationship so a page came up empty.

**What I'd like feedback on**
1. Would you put these pages in front of your stakeholders as they are? What breaks first?
2. Which purpose is missing from the pilots?
3. **If you run Power BI on a real warehouse (Presto, Redshift, Snowflake), please try it and tell me where it breaks.** `new_model.py` builds a model from a CSV folder, an Excel workbook or a database over ODBC, and an existing .pbip keeps your own connection and SQL untouched - no credentials are ever written. But a live warehouse is exactly the case I cannot test myself, so that gap stays open until someone with an account tries it.

Design feedback has its own issue form with a 1–5 rating against the published rubric — that rating is the data I use to decide what to change.

**Writing the request**: one line is enough to get a report, but the more you say the less you redo. The request above names the audience, the first-priority flow, how the headline measure is defined, the axes to break the cause down by, the filters, the default period and the theme - and all of it lands in the output.

Limits, up front: Windows only (Desktop), 2.157+, Japanese and Chinese UI strings are partial, all sample data is synthetic, and no live warehouse has been tested yet.

https://github.com/Haweee47/powerbi-autopilot

---

## 4. LinkedIn (영어) — 2~3일 뒤, `demo-en.mp4` 첨부

One line of plain language in, a finished Power BI report out. No clicks in Desktop.

> "Build a store sales dashboard.
>  - Read every Monday by the sales lead and the store managers
>  - Sales first, with year-on-year and target attainment beside it
>  - Make the gap obvious: vs target by category, three weakest stores apart
>  - Click a store to drill through to its detail page
>  - Default period this year, and a calm, practical theme"

One line works too, but the more specific the request, the less there is to redo afterwards. That request produces 4 pages and 55 visuals. The agent writes only a spec (3.1K tokens); scripts generate the rest. Microsoft's PBIR validator runs, then Power BI Desktop opens the report and every page is captured and checked. **2–10 minutes and about $0.60–4 per report — measured, not estimated.**

Why I built it: at a previous job I shipped an LLM workflow that wrote Power BI reports from existing PBIP files. It worked, but it burned tokens and the output looked like everything else. Across 1,800+ public reports, 67% of visual.json bytes are formatting, repeated in every visual. Move formatting into the theme and the agent's share of the output drops to about 6%.

The lesson that stuck: **a file that passes the validator can still be wrong on screen.** 25+ times — doubled units, clipped KPI cards, an ignored slicer default. So "open it in Desktop and look at every page" became the core of the workflow, not an afterthought.

On data: it builds the semantic model from a CSV folder, an Excel workbook or a database over ODBC, and if your data is already in Power BI it inherits your connection and SQL from the .pbip. **A live warehouse (Presto, Redshift, Snowflake) is the one thing I have not been able to test** - I don't have an account for one. CSV and Excel are checked in Desktop down to the numbers; ODBC only through a local driver.
**If you can point this at a real warehouse at work, I'd really like to hear where it breaks.**

Three questions for the Power BI people here:
1. Would you show these pages to stakeholders as they are? What breaks first?
2. Which report purpose is missing?
3. If you try it on a real database, does it hold up?

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
