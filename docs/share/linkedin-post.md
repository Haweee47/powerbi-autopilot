# LinkedIn 게시물 초안 (Power BI 커뮤니티)

첨부: `docs/share/media/`. LinkedIn은 한 게시물에 **이미지 여러 장 · 문서(PDF) 하나 · 영상 하나** 중 하나만 붙일 수 있다.

- 추천: `carousel.pdf`를 문서로 올린다 (13장: 표지 → 페이지 11장 → 테마 비교). 피드에서 넘겨 보는 형식이라 체류 시간이 길다.
- 이미지로 올릴 때: `cover.png`(4종 콜라주)를 첫 장, `themes.png`(테마 7종)를 두 번째 장, `cost-run-b.png`(처음 보는 모델로 만든 대시보드)를 세 번째 장. `pages.gif`는 11페이지를 넘기는 짧은 움직임.

---

## English (post this)

🤖 I built a Power BI report from start to finish with AI.
No manual clicks. No hand-editing.

💬 One plain-language request goes in.
⚙️ The agent builds the data model, pages, theme and navigation.
✅ It validates the files, opens the report in Power BI Desktop and screenshots every page to check it.
🙋 My only input: purpose, theme, language.
⏱️ 2–10 minutes and about $0.60–4 of Claude Opus 5 API tokens per report. Measured, not estimated.

What's inside 👇

📊 4 pilots by purpose: executive dashboard, measure table, matrix check, deep dive
🎨 7 themes, from showcase looks to print-ready finance packs, or one made from your brand color
🧩 Works on your own semantic model: a model map covers the fields a pilot needs
🌍 English by default, Korean built in, more languages via locale files
🪙 Low token cost: the agent writes a 1–3K-token spec, scripts generate the rest (about 6% of the output)
🧪 0 errors on Microsoft's PBIR validator, every page checked in Desktop
📚 Design rules from 1,800+ public reports and visualization research

🔌 A note on data sources
ODBC works: I read the sample model through a local ODBC driver, and the report built unchanged with the same totals. A live warehouse (Presto, Redshift) is next.
If you already run a Power BI report on ODBC, save it as PBIP. The agent keeps your connection and SQL as they are, and no password goes into the files.

🚧 This is a work in progress. I'll keep improving it and share what I learn along the way.

🔗 Open source (MIT): https://github.com/Haweee47/powerbi-autopilot

#PowerBI #DataVisualization #PBIP #AI #MicrosoftFabric

---

## 한국어 (참고용)

Power BI 리포트를 처음부터 끝까지 AI로 만들었습니다. 손으로 클릭하거나 고친 곳은 없습니다.

자연어 요청 한 줄이 들어가면 에이전트가 데이터 모델, 페이지, 테마, 페이지 이동까지 만들고, 파일을 검증한 뒤 Power BI Desktop에서 열어 모든 페이지를 캡처해 확인합니다. 제가 하는 일은 용도·테마·언어를 고르는 것뿐입니다. 리포트 하나에 2~10분, Claude Opus 5 API 요금으로 약 $0.6~4(약 800~5,500원)가 들었습니다. 추정이 아니라 실측입니다.

• 용도별 파일럿 4종: 경영 대시보드, 지표 테이블, 행렬 확인, 딥다이브
• 테마 7종: 발표용 쇼케이스부터 인쇄용 재무 보고까지, 또는 회사 브랜드 색으로 한 벌 더
• 내 시맨틱 모델에서도 동작: 파일럿에 필요한 필드를 모델 대응표로 연결
• 기본 영어, 한국어 내장, 다른 언어는 로케일 파일로 추가
• 적은 토큰: 에이전트는 1~3K 토큰짜리 명세만 쓰고 나머지는 스크립트가 생성 (생성물의 약 6%)
• Microsoft 공식 PBIR 검증 오류 0, 모든 페이지를 Desktop에서 렌더링해 확인한 뒤에야 완료
• 디자인 규칙은 공개 리포트 1,800여 개와 시각화 연구에서

데이터 연결 참고: ODBC도 됩니다. 예제 모델을 로컬 ODBC 드라이버로 읽어도 리포트가 그대로 만들어지고 합계도 같았습니다. 실제 데이터 웨어하우스(Presto, Redshift)는 다음 순서입니다. 지금 ODBC로 쓰는 리포트가 있다면 PBIP로 저장하세요. 에이전트는 연결 방식과 SQL을 그대로 두고, 비밀번호는 파일에 들어가지 않습니다.

계속 개선하면서 배운 것을 공유하겠습니다.

오픈소스(MIT): https://github.com/Haweee47/powerbi-autopilot

#PowerBI #데이터시각화 #PBIP #AI

---

## 올리기 전 체크

- [x] GitHub 저장소가 공개되어 링크가 열리는지
- [ ] 첨부 이미지·PDF에 회사명·실데이터가 없는지 (전부 가상 데이터)
- [ ] 첫 댓글에 README의 "직접 해 보기" 3줄을 붙이면 클릭률이 오른다
