# 논문·자료에서 가져온 디자인 규칙

"더 예뻐져야 한다"는 피드백을 감으로 풀지 않으려고, 대시보드·시각화 연구와 공식 가이드를 읽고
**측정 가능한 규칙**으로 바꿔 생성기·테마·레이아웃에 넣었다. 규칙마다 근거와 반영 위치를 적는다.

## 읽은 자료

| 자료 | 핵심 발견 |
|---|---|
| Bach et al., *Dashboard Design Patterns*, IEEE TVCG 2023 ([사이트](https://dashboarddesignpatterns.github.io/patterns.html)) | 대시보드 144개에서 패턴 42개. 메타 정보(업데이트 시각·데이터 설명), 임계값(좋음·나쁨 판단), 추세 화살표, 계층 레이아웃(위→아래 중요도), 의미 색 |
| Sarikaya et al., *What Do We Talk About When We Talk About Dashboards?*, IEEE TVCG 2019 ([논문](https://ieeexplore.ieee.org/document/8443395/)) | 대시보드 유형은 목적(전략·전술·운영·학습)과 상호작용 수준으로 나뉜다 → 용도별 파일럿 4종의 근거 |
| Harrison, Reinecke, Chang, *Infographic Aesthetics: Designing for the First Impression*, CHI 2015 ([논문](https://www.cs.tufts.edu/~remco/publications/2015/CHI2015-Aesthetics.pdf)) | 사람은 0.5초 만에 첫인상을 만들고, 그 인상은 **색 풍부도와 시각 복잡도**로 대부분 설명된다 |
| Kim, Setlur, Agrawala, *Towards Understanding How Readers Integrate Charts and Captions*, CHI 2021 ([논문](https://arxiv.org/abs/2101.08235)) | 글과 차트가 **같은 두드러진 특징**을 말하면 그것이 핵심으로 남는다. 글이 덜 두드러진 것을 말하면 독자는 차트를 믿는다 |
| Borkin et al., *Beyond Memorability*, IEEE TVCG 2016 ([논문](https://ieeexplore.ieee.org/document/7192646/)) | 시선은 글에 많이 머문다. **제목과 보조 글이 메시지를 말해야** 기억과 회상이 좋아진다 |
| Zhan et al., *The Effects of Layout Order on Interface Complexity: An Eye-Tracking Study for Dashboard Design*, Sensors 2024 ([논문](https://pmc.ncbi.nlm.nih.gov/articles/PMC11435723/)) | 질서 있는 배치가 반응 시간·응시 수를 줄이고, 차트가 많을수록 차이가 커진다. 핵심 차트는 **왼쪽 가운데**가 가장 빨랐다 ("less is more"에 더해 "order is more") |
| Coursaris & Kripintris, *Web Aesthetics and Usability: White Space*, IJEBR 2012 ([논문](https://www.igi-global.com/article/web-aesthetics-usability/62277)) | 여백은 매력도를 올리지만 **50%를 넘기면 사용성이 떨어진다** |
| Cawthon & Vande Moere, *The Effect of Aesthetic on the Usability of Data Visualization*, IV 2007 ([논문](https://www.semanticscholar.org/paper/The-Effect-of-Aesthetic-on-the-Usability-of-Data-Cawthon-Moere/d15ca38d2fb1250222132b5bf3fed8d249bcac45)) | 아름답다고 느끼면 **포기하지 않고 더 오래 본다** |
| Quispel, Maes, Schilperoord, *Graph and chart aesthetics for experts and laymen*, Information Visualization 2016 ([논문](https://journals.sagepub.com/doi/10.1177/1473871615606478)) | 매력도는 실제 사용성보다 **익숙함과 쉬워 보임**을 따른다 → 낯선 차트보다 막대·선·표 |
| Microsoft Learn, *Tips for designing a great Power BI dashboard* ([문서](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips)) | 숫자는 3~4자리까지("3.4 million"), 가장 중요한 것은 왼쪽 위, 한 화면, 불필요한 데이터 레이블 제거, 시간 범위를 섞지 않기 |
| Tableau Research 시선 추적 연구 ([블로그](https://www.tableau.com/blog/eye-tracking-study-5-key-learnings-data-designers-everywhere-72395)) | 제목과 큰 숫자를 먼저 본다. 차트에서는 선보다 **레이블과 범례**를 본다 |
| IBM Carbon Design System, *Data visualization — color palettes* ([문서](https://carbondesignsystem.com/data-visualization/color-palettes/)) | 범주형 색은 **정해진 순서대로** 쓴다. 이웃한 색끼리 대비가 최대가 되도록 배열돼 있어 계열 2개일 때도 14개일 때도 구분된다. 그라데이션을 순차 팔레트 대신 쓰지 않는다 |
| Okabe & Ito, *Color Universal Design* (2008) ([설명](https://jfly.uni-koeln.de/color/)) | 세 가지 색각 이상에서 모두 구분되는 8색 세트. 접근성 팔레트의 사실상 표준 |
| Chen et al., *DMiner: Dashboard Design Mining and Recommendation*, IEEE TVCG 2023 ([논문](https://arxiv.org/abs/2209.01599)) | 대시보드 854개에서 **배치(위치·크기)와 뷰 사이 연동**을 규칙으로 뽑았다. 구성은 취향이 아니라 반복되는 규칙이다 |
| Power BI 글꼴 지원 ([Data Mozart](https://data-mozart.com/custom-fonts-in-power-bi-everything-you-wanted-to-know/)) | Desktop이 들고 있는 글꼴(Segoe UI·DIN·Georgia·Corbel·Candara 등) 밖의 글꼴은 **보는 사람 PC에 없으면 조용히 대체**된다. 테마 글꼴은 내장 글꼴로 제한해야 같은 화면이 보장된다 |

## 규칙과 반영

| # | 규칙 | 근거 | 반영 |
|---|---|---|---|
| R1 | 결론 문장은 페이지에서 두 번째로 강한 글자다 (제목 다음) | Kim 2021, Borkin 2016 | 결론 줄을 흐린 회색 → 본문 진한 색 + 세미볼드 |
| R2 | 결론이 가리키는 항목은 차트에서도 두드러진다 (두 번 강조) | Kim 2021 | 결론 "가장 모자란 카테고리 가전" = 막대에서 빨강. 매장 결론 = 표 맨 윗줄 |
| R3 | 선 차트는 범례 대신 선 끝에 이름 | 시선 추적(레이블을 먼저 본다), dataviz 직접 레이블 | 테마: 선 차트 범례 끄고 계열 이름을 선 끝에 |
| R4 | 지금 무엇을 보고 있는지(기간·채널)를 제목 줄에 늘 보인다 | Bach 메타 정보 패턴, Microsoft "시간 범위를 섞지 않기" | 제목 오른쪽에 필터 상태 문장 (측정값) |
| R5 | 모든 KPI에 비교 기준 | Microsoft "provide context", Few | 매장 상세의 이익률(%p)·주문(전년 대비)에도 비교 문구 |
| R6 | 임계값은 선으로, 좋고 나쁨은 의미 색으로 | Bach 임계값·의미 색 패턴 | 산점도에 0% 기준선 + 감소 매장 빨강 |
| R7 | 비스듬한 글자 금지, 긴 이름은 가로 막대 | Microsoft 가독성, Quispel(쉬워 보임) | 권역 차트를 가로 막대로 되돌림 (축 이름 폭 40%) |
| R8 | 핵심 차트는 왼쪽 가운데, 나머지는 부분 대칭 | Zhan 2024 | 이미 적용(요약: 추이 왼쪽). 레이아웃 검사 항목으로 고정 |
| R9 | 색은 절제하되 단조롭지 않게: 강조색 1 + 의미 색 2 + 회색 | Harrison 2015 (색 풍부도가 첫인상을 좌우), Bach 공유 색 | 팔레트 유지, 차트마다 색을 새로 쓰지 않는다 |
| R10 | 여백은 넉넉하게, 그러나 캔버스의 절반을 넘기지 않는다 | Coursaris 2012 | 8px 격자·간격 16·카드 안쪽 여백 16~20 유지 |
| R11 | 숫자는 3~4자리 + 단위 | Microsoft | 영어 M·K, 한국어 만·억 (측정값 서식) |
| R12 | 범주형 색은 팔레트에 적힌 순서대로만 쓴다 | IBM Carbon | 테마의 `categorical` 배열 순서를 생성기가 그대로 따른다 (두 번째 자리는 늘 회색 = 작년) |
| R13 | 접근성이 필요한 자리에는 색각 이상에서도 구분되는 세트를 쓴다 | Okabe-Ito | `universal` 테마: 8색 전부 Okabe-Ito |
| R14 | 테마 글꼴은 Power BI 내장 글꼴만 쓴다 | Power BI 글꼴 대체 동작 | `tokens.typefaces` 3종(Segoe·DIN·Editorial)이 모두 내장 글꼴. CJK는 각 세트에서 시스템 UI 글꼴로 넘어간다 |
| R15 | 한 가지만 말하는 페이지는 숫자 하나를 크게 두고 나머지를 받치게 한다 | Zhan 2024(핵심은 왼쪽), Bach 계층 레이아웃 | `hero` 레이아웃: 큰 숫자(왼쪽 위) + 추이 + 받치는 타일 3 + 분해·목록 |

채점표에는 R1~R7을 "근거 기반 항목"으로 더했다 ([review-rubric.md](review-rubric.md)).
