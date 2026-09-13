# LinkedIn 게시물 초안 (Power BI 커뮤니티)

첨부: `docs/share/media/` — ① 4종 콜라주(표지) ② 대시보드 요약 ③ 행렬 히트맵 ④ 요인 분해 ⑤ 테마 3종 ⑥ 페이지 넘기는 짧은 영상(GIF/MP4).
첫 이미지가 피드에서 멈추게 하는 역할이라 콜라주를 맨 앞에 둔다.

---

## English (post this)

I stopped hand-building Power BI reports and taught an AI agent to do it — on a small token budget.

One request → a finished PBIP report, checked in Power BI Desktop:

• 4 pilots by purpose: executive dashboard, measure table, matrix check, deep dive
• 3 themes (Navy · Paper · Midnight), English by default, Korean built in, more via one locale file
• The agent writes a 1–3K-token spec. Scripts do layout, theme and field validation — about 6% of what they generate
• 0 errors on Microsoft's PBIR validator, and every page is screenshotted in Desktop before it counts as done
• Design rules from 1,800+ public reports and research (Bach et al. 2023, Kim et al. 2021, Borkin et al. 2016)

Open source, MIT: https://github.com/jinseong0407/powerbi-autopilot

What would you add as a 5th pilot?

#PowerBI #DataVisualization #PBIP #AI #MicrosoftFabric

---

## 한국어 (참고용)

Power BI 리포트를 손으로 만들던 걸 멈추고, AI 에이전트가 적은 토큰으로 만들게 했습니다.

요청 한 줄 → Power BI Desktop에서 확인까지 끝난 PBIP 리포트:

• 용도별 파일럿 4종: 경영 대시보드, 지표 테이블, 행렬 확인, 딥다이브
• 테마 3종(네이비·페이퍼·미드나잇), 기본 영어, 한국어 내장, 다른 언어는 로케일 파일 하나로
• 에이전트는 1~3K 토큰짜리 명세만 씁니다. 배치·테마·필드 검증은 스크립트가 — 생성물의 약 6%
• Microsoft 공식 PBIR 검증 오류 0, 모든 페이지를 Desktop에서 캡처해 확인한 뒤에야 완료
• 디자인 규칙은 공개 리포트 1,800여 개와 연구(Bach 2023, Kim 2021, Borkin 2016)에서

오픈소스(MIT): https://github.com/jinseong0407/powerbi-autopilot

다섯 번째 파일럿으로 무엇이 있으면 좋을까요?

#PowerBI #데이터시각화 #PBIP #AI

---

## 올리기 전 체크

- [ ] GitHub 저장소가 공개되어 링크가 열리는지 (`gh auth login` 후 push)
- [ ] 첫 이미지(콜라주)가 1200×1200 또는 1200×627 안에서 글자가 읽히는지
- [ ] 회사명·실데이터가 이미지에 없는지 (전부 가상 데이터)
- [ ] 첫 댓글에 README의 "직접 해 보기" 3줄을 붙이면 클릭률이 오른다
