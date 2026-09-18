# 진행 기록

무엇을 했고, 왜 그렇게 결정했고, 숫자로 무엇이 나왔는지 작업 단위마다 적는다.
틀린 가설과 실패도 지우지 않고 남긴다. 다음에 같은 실수를 하지 않으려는 기록이기 때문이다.

---

## 2026-09-11 · 방향 정하기

**배경.** 이전 직장에서 Power BI 리포트를 PBIP로 바꿔 LLM에게 학습시키고, 템플릿을 참고해 새 리포트를 만드는 방식을 직접 만들어 팀에 배포했다.
만들어는 졌지만 두 가지가 발목을 잡았다. **토큰이 너무 많이 들었고, 결과물이 예쁘지 않았다.**
이 프로젝트는 그 두 문제를 공개 데이터로 다시 풀어 보는 작업이다.

- 공개 도구 11개를 조사했다. 결론은 "PBIR·TMDL 파일을 쓰는 도구는 이미 많다. 비어 있는 건 **재현 가능한 디자인 품질**과 **비용**이다."
- 비교 실험을 설계했다. 같은 데이터, 같은 요청문으로 세 도구가 각각 만든 결과를 디자인 품질과 토큰으로 비교한다.
  - Microsoft skills-for-fabric
  - data-goblin
  - Power BI Modeling MCP
- 가상 소매 데이터를 만들었다. 판매 26,194행, 총매출 35.8억 원, 시드를 고정해 누구나 똑같이 생성할 수 있다.
  리포트가 드러내야 할 흐름을 데이터에 일부러 심었다: 가전 −7.3%, 온라인 +18.6%, 일산점 −38.6%.

## 2026-09-12 · Modeling MCP만으로 모델 만들기 (예제 03)

- 빈 Power BI Desktop에 MCP로 붙어 모델을 만들었다: 테이블 7개, 관계 6개, 측정값 29개.
- **숫자는 눈이 아니라 쿼리로 확인했다.** DAX 쿼리 4개의 결과가 데이터 생성 때 Python으로 계산해 둔 값과 전부 일치했다.
- 설계에서 신경 쓴 두 가지.
  - 목표는 카테고리 × 월 단위로만 있다. 그래서 매장이나 제품으로 걸러지면 달성률을 빈칸으로 둔다. 틀린 비교가 보이는 것보다 빈칸이 낫다.
  - 올해는 8월까지만 있다. 그래서 전년 비교도 1~8월끼리만 한다(`실적기간` 열).
- 배운 점: MCP의 진짜 가치는 "만들자마자 DAX로 검증"에 있다. README에도 적혀 있듯 리포트 화면은 만들 수 없다.
- 실수: 토큰을 긴 대화가 이어지는 세션에서 쟀더니 앞선 대화가 매번 다시 읽혀 수치가 부풀었다. 이후 비교는 예제마다 새 세션에서 재기로 했다.

## 2026-09-12 · 공개 리포트 1,700여 개 분석

- GitHub 저장소 1,737개를 훑어 Power BI 파일이 있는 1,208개를 찾았다. 그중 PBIX·PBIT 1,830개와 PBIP 폴더 271개를 분석했다.
- 원본을 AI에게 통째로 읽히지 않았다. 스크립트가 레이아웃·간격·정렬·색·글꼴·테마를 수치로 뽑고, 사람과 AI는 요약만 봤다.
  이 방식 자체가 이 프로젝트가 말하려는 토큰 절약법이다.
- 발견한 것.
  - 전문가 리포트는 포트폴리오보다 비주얼이 적고(페이지당 5.8개 대 10개) 간격이 넓었다(32px 대 18px).
  - **PBIR 파일의 서식 대부분은 테마가 아니라 비주얼마다 따로 박혀 있었다.** 공식 템플릿도 마찬가지였다. `visual.json` 용량의 67%가 서식이다.
- 실패: 파일 목록만 받으려던 스캔이 크기 옵션(`ls-tree -l`) 때문에 파일 내용을 전부 내려받았다. 몇 분 만에 5.8GB가 쌓였다.
  옵션을 빼고 해시만 읽도록 고치자 1,737개를 15분에 훑었다.
- 수집한 저장소의 73%는 라이선스가 없다. 그래서 원본은 재배포하지 않고 출처 목록과 통계만 공개한다.

## 2026-09-13 · 디자인 원칙, 채점표, 첫 HTML 시안

- 원칙 문서를 만들었다. 근거는 Stephen Few, Microsoft Learn, Nielsen Norman Group, IBCS, 공식·커뮤니티 스킬, 그리고 앞의 수집 데이터다.
  "요약 → 맥락 → 상세", "강조색 하나", "모든 숫자에 비교 기준", "억·만·%p 표기" 같은 규칙에 근거를 붙여 정리했다.
- 원칙을 채점표(20항목)로 바꿨다. 원칙이 문서로만 있으면 결과물을 검사할 수 없다.
- 원칙을 적용한 반응형 HTML 대시보드를 만들었다.
  - 필터를 바꾸면 헤더의 인사이트 문장과 차트 제목이 다시 계산된다.
  - 색 조합은 색각이상 검증 스크립트를 통과했다.
  - 데스크톱과 휴대폰 폭에서 캡처해 직접 확인했다.
- **스스로 채점하니 37/40.** 우리가 정한 규칙을 스스로 어긴 곳이 3개 나왔다. 세로 경계선이 이어지지 않고, 글자 크기가 7단계이고, 안쪽 여백이 8의 배수가 아니다.
  채점표가 제 역할을 한다는 증거라서 오히려 반가웠다.

## 2026-09-13 · 여러 페이지와 이동 설계

- 페이지 선택기, 책갈피, 드릴스루, 툴팁 페이지, 필드 매개변수를 공식 문서로 정리하고, 수집한 리포트에서 실제 사용률을 쟀다.
  - 여러 페이지로 된 리포트는 65%. 그중 **리포트 안에 이동 수단을 둔 곳은 28%뿐**이다.
  - 책갈피 파일은 평균 15KB로 비주얼 파일(6.5KB)의 두 배가 넘는다. 책갈피가 있는 리포트는 책갈피만 중앙값 약 2.2만 토큰이다.
- 결정: 역할을 나눈다.
  - 지표 전환 → 필드 매개변수
  - 상세 → 드릴스루
  - 순서 있는 이야기 → 페이지
  - 책갈피 → 같은 자리에서 보기 전환할 때만

  디자인과 토큰 양쪽에서 같은 결론이 나왔다.

## 2026-09-13 · 포트폴리오 공개 준비

- 저장소 이름을 `powerbi-autopilot`으로 정했다. 요청 한 줄에서 모델·디자인·검증까지 가는 자동화를 목표로 한다는 뜻이다.
- 공개 전에 개인 흔적을 걷어냈다.
  - 로컬 경로가 들어간 파일 3개를 고쳤다.
  - 커밋 이메일을 비공개 주소로 바꾸기로 했다.
  - 이전 직장은 회사명 없이 경험으로만 쓴다.

## 2026-09-13 · 여러 페이지 시안 v2

- 1페이지 시안을 4페이지 리포트로 키웠다: 요약 / 카테고리 / 매장 / 매장 상세.
  페이지마다 질문 하나, 유형 하나(경영 요약·분석·비교·상세)를 정하고 만들었다.
- 앞에서 정한 이동 원칙을 그대로 적용했다.
  - 페이지 선택기
  - 페이지를 옮겨도 유지되는 필터
  - "처음 상태로" 초기화
  - 지표 전환: 필드 매개변수 방식
  - 매장 행·산점도 점 → 매장 상세: 드릴스루 방식, 뒤로 가기·경로 표시
  - 마우스를 올리면 월별 미니 차트: 툴팁 페이지 방식
- 인사이트 문장을 전부 데이터로 계산했다. 예를 들어 매장 상세의 "가장 크게 줄어든 카테고리는 가전(▼53.6%)"은
  매장×카테고리 매출 차이에서 뽑는다. 사람이 적어 넣은 문장은 없다.
- v1의 감점 3개를 고쳤다.
  - 글자 크기를 7단계에서 5단계로 줄였다.
  - 안쪽 여백을 8의 배수로 맞췄다.
  - 세로 경계선을 모든 페이지에서 이었다.
- 캡처를 한 번 보고 네 가지를 고쳤다.
  - 한 축에 억과 만이 섞인 것
  - 산점도 이름표 겹침
  - 휴대폰 폭에서 11월·12월 겹침
  - 온라인 매장 설명 중복("온라인 · 온라인")
- 잘못 짚은 것: 캡처 파일 세 장의 크기가 거의 같아서 빈 화면이 찍혔다고 의심했다. 열어 보니 모두 정상이었다. 파일 크기로는 판단할 수 없다.

## 2026-09-13 · 디자인 시스템: 토큰 → 테마, 레이아웃 템플릿

- **시안의 약점을 찾았다.** HTML 요약 페이지는 높이가 약 1,500px라 스크롤된다. 그런데 Power BI 페이지는 1280×720 한 화면이다.
  원칙에 적어 둔 Few의 1번 함정(한 화면을 넘어감)을 시안이 그대로 안고 있었다.
  그래서 고정 캔버스용 레이아웃 템플릿을 따로 만들었다.
- **격자를 숫자로 정했다.** 바깥 여백 24 · 간격 16이면 1280에서 12열이 정확히 88px로 나뉜다. 모든 좌표가 정수이자 8의 배수가 된다.
  - 페이지 유형 4개(요약·분석·비교·상세)를 열·폭으로 적었다.
  - 스크립트가 좌표를 풀면서 네 가지를 검사한다: 8의 배수, 캔버스 이탈, 겹침, 세로 경계선 공유. 결과는 문제 0건이다.
- **디자인 토큰 하나로 테마와 CSS를 만든다.** 색·글자·간격을 `tokens.json`에 두고, 스크립트가 밝은·어두운 테마와 CSS 변수를 생성한다.
  두 테마 모두 Microsoft 공식 스키마 2.157(Desktop과 같은 버전) 검증을 통과했다.
- **범주 색 1번은 파랑, 2번은 회색으로 두었다.** 올해·작년 두 계열 차트가 비주얼마다 색을 지정하지 않아도 "실적 파랑, 전년 회색"이 된다.
  서식을 비주얼이 아니라 테마에 두는 원칙을 색 순서로 푼 것이다.
- **틀린 가정 두 가지.**
  - 선 종류를 `straight`로 쓰려 했는데, CLI로 확인하니 허용값은 `linear`였다.
  - 버튼 슬라이서의 선택 상태는 CLI는 `selected`, 테마 스키마는 `selection:selected`였다. 스키마 검증이 이 차이를 잡았다.

  속성 이름은 기억이 아니라 도구로 확인해야 한다는 걸 다시 배웠다.

## 2026-09-13 · 명세 → PBIR 생성기 (예제 04)

이전 직장에서 토큰이 새던 곳은 에이전트가 `visual.json`을 한 줄씩 직접 쓰는 단계였다. 좌표·서식·필드 연결까지 전부 AI가 만들어 냈다.
그래서 역할을 나눴다. **에이전트는 페이지별로 "어느 영역에 무엇을" 적은 명세 한 장만 쓴다.** 나머지는 스크립트가 채운다.

| 누가 | 무엇을 |
|---|---|
| 에이전트 | `report.spec.json` — 영역 이름 → 필드·제목 |
| 레이아웃 템플릿 | 좌표 (1280×720, 12열) |
| 테마 | 서식 전부 |
| 생성기 | TMDL과 필드 대조 → PBIP 폴더 쓰기 → 크기 측정 |

- **숫자.** 4페이지 · 비주얼 37개 리포트.
  - 에이전트가 쓰는 명세: 4.3KB, 약 1,460 토큰
  - 생성된 리포트 JSON: 58KB, 약 19,900 토큰 (테마 제외)
  - 쓰는 양이 **약 7%**로 줄었다. 에이전트가 직접 쓰면 쓰기만 해도 비슷한 출력 토큰이 들고, 고칠 때마다 다시 읽는다.
- **비주얼 파일도 가벼워졌다.** `visual.json` 평균 1.49KB로, 수집한 공개 PBIR 평균(6.5KB)의 23%다.
  서식을 비주얼마다 넣지 않고 테마에 둔 효과가 그대로 숫자로 나왔다. 앞의 분석에서 "용량의 67%가 서식"이라고 한 부분이다.
- **필드 오타는 토큰 0으로 잡는다.** 생성기가 TMDL에서 열·측정값 목록을 읽어 명세와 대조한다.
  없는 필드를 쓰면 Desktop을 열기 전에 스크립트가 멈추고 비슷한 이름을 알려 준다.
- **공식 CLI 검증(`powerbi-report-author validate`)을 통과했다: 오류 0 · 경고 0.** 처음에는 오류 6개였다.
  - 테마 등록에 `reportVersionAtImport`가 빠졌다.
  - 테마 파일 안의 `name`이 report.json이 부르는 이름과 달랐다.
    그런데 Desktop이 저장한 실제 리포트를 열어 보면 표시 이름("Sunflower Twilight")을 넣는다. 검증기가 Desktop보다 엄격한 셈이다. 통과를 우선해 검증기 규칙에 맞췄다.
  - 필터 창 서식(`outspacePane`·`filterCard`)을 모든 비주얼(`*`)에 뒀더니 모르는 객체라고 했다. Microsoft 문서 예시대로 쓴 것인데, 페이지 쪽으로 옮기니 통과했다.
  - 카드의 `spacing.customizeSpacing`은 공식 디자인 스킬 파일에서 가져온 속성인데 검증기가 모르는 속성이라고 했다. 뺐다.
- **잘못 짚은 것.** 비주얼 스키마 경고를 네트워크 문제로 생각했다. 직접 요청해 보니 2.10.0 이상은 404였다.
  Desktop은 이미 2.11·2.12 버전으로 저장하는데(수집한 파일의 약 45%), 스키마는 2.9.0까지만 공개돼 있다.
  2.9.0으로 낮추자 스키마 검증까지 돌았다.
- 남은 일: Desktop에서 열어 캡처하고 채점표로 보는 것. 구조 검증을 통과해도 화면은 깨질 수 있다.

## 2026-09-13 · Desktop에서 처음 열어 보고, 디자인 v3 (앱형)

Desktop Bridge 없이도 화면을 볼 방법을 만들었다. 생성한 PBIP를 Desktop으로 열고, Modeling MCP로 모델을 새로 고치고,
페이지 탭은 Windows UI Automation으로 넘기면서(마우스를 움직이지 않는다) 창을 캡처한다. 저장소 사본은 건드리지 않도록
데이터 경로만 바꾼 사본을 작업 폴더에 따로 만들어 연다.

**첫 캡처에서 나온 것.** 구조 검증은 통과했는데 화면에는 문제가 7개 있었다.

| 보인 것 | 원인 | 고친 방법 |
|---|---|---|
| 매출이 35.8억(전 기간 합계), 일산점이 +40.3% | 연도 슬라이서 기본값 필터가 무시됨. 날짜는 계산 테이블이라 TMDL에 형식이 없어 `'2026'`(문자)으로 썼다 | 형식을 모르면 명세 값의 형식으로 판단 → `2026L` |
| 축에 "40천만", 막대에 "+4.6천만" | 측정값 서식(만)에 Power BI 자동 단위(천)가 한 번 더 붙음 | 테마에서 자동 단위를 끔 |
| 슬라이서가 빈 칸 | 제목(필드 이름)이 56px 높이를 다 차지 | 레일 위에 작은 제목 + 버튼 한 줄 |
| KPI 값이 위로 잘림 | 비교 문구의 기본 회색 상자와 여백 | 상자·여백 끔 (`$id` 없이 쓰면 적용되지 않았다) |
| 페이지 선택기에 숨긴 상세 페이지까지 보임 | 기본값이 숨김 페이지 표시 | `showHiddenPages: false` |
| 권역 7개 막대에 스크롤바 | 최소 항목 폭 × 7 > 카드 높이 | 세로 막대로 바꿈 (명세에서 `type`) |
| 작은 여러 차트가 2열로 쌓여 스크롤 | 자동 배치 | 1행 × 5열 |

**"너무 기본 같다"는 피드백.** 문제를 다 고쳐도 흰 카드가 격자로 늘어선 모습은 Power BI 기본 템플릿 그대로였다.
그래서 구성 자체를 바꿨다.

- **왼쪽 어두운 레일**에 리포트 이름, 페이지 선택기(세로), 기간·채널 슬라이서, 기준일을 모았다. 본문은 분석에만 쓴다.
  레일 폭 192에 본문 12열 × 72px로 잡으니 좌표가 모두 8의 배수로 떨어졌다.
- **제목 아래에 결론 한 줄**을 두었다. 문장을 돌려주는 DAX 측정값이라 필터를 바꾸면 문장도 바뀐다.
  예: "목표 달성률 95.8% · 전년 대비 ▲1.5% · 가장 모자란 카테고리 가전 ▼4,486만".
  한국어 조사(이/가, 은/는)는 받침에 따라 달라져서, 문장을 "항목 이름 + 숫자" 꼴로 짜 조사를 피했다.
- **KPI 카드**는 작은 이름 → 큰 숫자 → 비교 문구 순서로 왼쪽 정렬했다. 비교 문구 색은 부호 측정값으로 ▲ 파랑, ▼ 빨강.
- **카드**는 머리카락 두께 테두리와 거의 안 보이는 그림자로 "종이 한 장" 정도의 깊이만 줬다.
- **차트**: 올해 선만 굵게, 작년은 회색, 목표는 흐린 점선. 차트마다 부제목에 단위와 읽는 법을 적었다.
- 레일에 들어가는 내용은 명세에 한 번만 적는다(`shared`). 네 페이지에 같은 슬라이서를 네 번 적던 것을 없앴다.

**틀린 가정들.** 버튼 슬라이서의 버튼 칠은 `background`가 아니라 `fillCustom`이었다. `background`로 칠했더니 흰 버튼 안에
어두운 글자 상자가 생겼다. 공개 PBIR 수백 개에서 버튼 슬라이서를 찾아 실제로 어떻게 저장돼 있는지 대조해서 알았다.
페이지 선택기의 기본 칸은 `show: false`로는 사라지지 않아서 레일과 같은 색으로 칠했다.
뒤로 가기 버튼은 글자가 끝내 나오지 않았는데, 공개 PBIR의 버튼을 보니 켜고 끄기(`show`)는 상태 없는 항목에,
글자 내용은 `default` 상태 항목에 따로 두고 있었다. 같은 규칙을 테마의 버튼 칠·테두리에도 적용했다.
작은 여러 차트는 칸이 좁아 월 축에 가로 스크롤이 생겼다. 최소 항목 폭을 줄여도 안 없어져서, 월 번호를 숫자 축(연속)으로 바꿨다.
결론 문장 뒤의 흰 띠도 같은 규칙이었다. 카드 칠·배치 바탕·숫자 영역 바탕을 차례로 꺼 봐도 남아 있다가,
끄는 항목을 선택자 없이 한 번 더 쓰자 사라졌다. 세 번 틀리고 나서야 "켜고 끄기는 선택자 없는 항목"이 이 버전의 공통 규칙이라는 걸 받아들였다.
KPI 카드는 비교 문구를 넣으면 카드 안쪽 배치가 지표 이름 줄을 눌러 잘랐다. 높이·여백을 바꿔도 같아서,
지표 이름을 카드 안 라벨 대신 컨테이너 제목으로 옮겼다. 제목은 카드 내용 밖에 그려지니 눌리지 않는다.

돌아보면 이번 단위의 문제 대부분은 **검증기가 잡을 수 없는 종류**였다. 파일 형식은 맞는데 화면이 틀린 것들이다.
그래서 "생성 → 검증 → Desktop 캡처 → 고침"을 한 번에 도는 절차가 이 저장소의 핵심 도구가 됐다.

## 2026-09-13 · 용도별 파일럿 4종, 테마 3종, 다국어(영어 기본), 논문 기반 개선

리포트를 매번 새로 만들지 않기로 했다. 용도별로 완성된 **파일럿**을 미리 만들어 두고, 새 요청이 오면
"용도 → 테마 → 언어"만 물은 뒤 파일럿을 복사해 필드만 바꾼다. 토큰을 줄이는 가장 확실한 방법은 덜 쓰는 것이다.

- **파일럿 4종** ([templates/](../templates/catalog.json)): 대시보드 · 지표 테이블(측정값 입력 매트릭스) · 지표 확인(행렬) · 딥다이브.
  행렬은 모든 행 수준을 펼친 채로 열리고, 요인 분해 트리는 첫 기준(권역)까지 펼쳐서 연다(`expansionStates`).
  표·행렬 조건부 서식은 열마다 한 단어(`bar`·`heat`·`sign`)로 적고, `sign`의 색 측정값은 생성기가 만든다.
- **테마 3종**: 네이비 · 페이퍼(흰 레일 + 경계선) · 미드나잇(다크). 구조는 같고 색 토큰만 다르다. 셋 다 공식 스키마 통과.
- **다국어, 기본 영어.** 글자를 번역하는 것만으로는 부족했다. 네 층을 나눴다.
  - 화면 글자: 명세에 `{"en": ..., "ko": ...}`. 없는 언어는 영어로 대신하고 생성기가 몇 개를 대신했는지 알려 준다.
  - 필드 이름: 용어집 한 파일. 모델 식별자(한국어)는 그대로, 표 머리글·범례만 바뀐다.
  - 숫자와 문장: `measures.en.json`(M·K) / `measures.ko.json`(만·억). 측정값 이름이 같아서 명세는 언어와 무관하다.
  - 데이터 값: 가상 데이터를 영어로도 생성하고(`generate.py --lang en`), 모델의 월·요일 글자와 데이터 폴더는 생성기가 치환한다.
- **시작 흐름**: [`tools/new_report.py`](../tools/new_report.py) + [`new-report` 스킬](../.claude/skills/new-report/SKILL.md).
  파일럿을 복사하면서 한 언어만 남기면 한국어·페이퍼 테이블 명세가 **1.6K 토큰**이다. 대상 모델에 없는 필드만 목록으로 알려 준다.
- **검증**: 파일럿 4종(영어) + 한국어 예제 모두 공식 검증 오류 0 · 경고 0. 명세는 1.3K~3.4K 토큰, 생성물의 약 6%.

**캡처에서 나온 것.**
- 영어 숫자가 "110,558,285.0,,M"으로 나왔다. 서식 문자열의 쉼표 스케일링(`#,0.0,,`)을 Desktop이 무시했다. 한국어처럼 측정값에서 나누는 방식으로 통일했다.
- 표 결론 문장만 오류가 났다. DAX 변수 이름 `top`에서 구문 오류가 났다(모델이 식을 `SYNTAXERROR`로 바꿔 둠). `best`로 바꿨다.
- 합계 줄에 "합계", 드롭다운에 "모두"가 보였다. Desktop 표시 언어를 따라가는 글자다. 합계 이름은 리포트 언어로 고정했고, "모두"는 보는 사람의 Power BI 언어를 따른다.
- 캡처 스크립트가 페이지 탭을 위치로 추정하다가 리본 탭을 38번 눌렀다. 페이지 이름을 생성된 리포트의 `pages.json`에서 읽게 바꿨다.

**논문에서 가져온 규칙.** "더 예뻐져야 한다"는 말을 감으로 풀지 않으려고 연구 11편·공식 가이드를 읽고 규칙 11개로 바꿨다
([literature.md](../design-system/literature.md)). 결론 문장을 제목 다음으로 강하게(Kim 2021, Borkin 2016), 선 차트는 범례 대신 선 끝 이름,
제목 줄에 지금 보는 범위(Bach 2023 메타 정보), 모든 KPI에 비교 기준, 산점도 0% 기준선과 의미 색, 비스듬한 글자 금지.
채점표에 H1~H7로 더했다.

**반영 결과 (Desktop 캡처로 확인).**
- 결론 줄이 진한 세미볼드가 되자 페이지를 열었을 때 제목 다음으로 눈이 가는 곳이 결론이 됐다. 결론이 가리키는 가전·일산점은 차트에서도 빨강·맨 윗줄이다 (H1·H2).
- 제목 오른쪽에 "2026 · Jan–Aug · All channels". 기간 버튼을 누르면 문구도 바뀐다 (H4).
- 매장 상세의 이익률·주문에도 "YoY ▲0.6pp", "YoY ▲7.1%"가 붙어 숫자만 있는 카드가 없어졌다 (H5).
- 산점도에 0% 점선과 감소 매장 빨강. 20개 점 중 줄어든 10곳이 한눈에 갈린다 (H6).
- 권역 차트는 가로 막대로 되돌리고 행 높이를 216 → 232로 조정해 7개 막대가 스크롤 없이 들어간다 (H7).
- 선 끝 계열 이름만 두고 범례를 껐더니, 선 끝이 가까운 계열(작년·목표)은 Power BI가 이름을 숨겨 이름 없는 선이 남았다. 범례를 되살려 둘 다 둔다.
- 페이지 선택기 칸 테두리가 페이퍼·미드나잇에서만 보였다. 네이비에서는 레일 색과 비슷해 보이지 않았을 뿐, 같은 "끄기는 상태 없는 항목에" 규칙 위반이었다.

**틀린 가설.** 주문 카드의 "6.620"을 서식 오류로 보고 서식 문자열 두 번, 텍스트 측정값까지 바꿨다. 결과가 매번 같아서 캡처를 3배로 키워 보니
아래로 꼬리가 있는 쉼표였다. 24pt 세미볼드에서 쉼표가 마침표처럼 보였을 뿐 처음 서식이 맞았다. 되돌렸다.
"틀렸다고 확신하기 전에 확대해서 본다"를 캡처 절차에 넣었다.

**공유 자료.** [`tools/make_media.py`](../tools/make_media.py)가 캡처로 표지(4종 콜라주)·테마 비교·페이지 GIF·PDF 캐러셀을 만든다.
LinkedIn 초안은 [docs/share/linkedin-post.md](share/linkedin-post.md)에 영어·한국어로 있다.

## 2026-09-14 · GitHub 공개, 노션 정리

- 저장소를 공개했다: [github.com/Haweee47/powerbi-autopilot](https://github.com/Haweee47/powerbi-autopilot).
- **첫 push 전에 커밋 기록을 검사했더니 모든 커밋의 작성자에 개인 이메일이 들어 있었다.** 공개하면 되돌릴 수 없어서
  push 전에 기록 전체의 작성자를 GitHub 비공개(no-reply) 주소로 바꿨다. 이후 커밋은 저장소 전용 설정으로 비공개 주소만 쓴다.
- push 전 검사: 추적 파일 전체에서 로컬 경로·사용자명·이메일·회사명 0건.
- 노션에 포트폴리오 허브와 날짜별 작업 일지를 만들었다. 이미지는 저장소의 캡처를 GitHub raw 링크로 붙여 한 곳만 고치면 되게 했다.

## 2026-09-14 · 누구나 쓸 수 있게: 한 번에 시작, 4개 언어 안내서, 피드백 구조

**처음 받은 사람의 눈으로 다시 봤다.** 저장소를 내려받아 파일럿을 바로 열면 데이터가 없다. 파일럿 모델의 데이터 폴더가
자리표시 경로(`C:\path\to\...`)이기 때문이다. 생성기에는 이미 `--local-data` 옵션이 있었지만, 그걸 아는 사람은 나뿐이었다.

- **`quickstart.cmd` 더블클릭 한 번.** 데이터 경로를 그 PC에 맞춘 파일럿을 `out/`에 만들고 Desktop으로 연다. Python 기본 라이브러리만 쓴다.
  파일럿 4종 + 일본어 빌드 모두 공식 검증 오류 0 · 경고 0.
- **안내서 4개 언어** (영어·한국어·일본어·중국어, 리포트 언어 목록과 같다): 준비물 → 열어 보기 → 말로 요청해 만들기 → 내 데이터(ODBC 주의 포함) → 문제 해결 → 피드백.
- **처음 여는 사람이 보는 화면을 캡처로 확인했다.** 빈 비주얼 + "데이터 없음" 노란 줄 → **지금 새로 고침** → "적용되지 않은 변경" → **변경 내용 적용**.
  UI Automation으로 사용자와 같은 버튼을 눌러 확인했고, 이 두 번의 클릭을 안내서에 그대로 적었다.
- 일본어·중국어 리포트의 데이터 값이 한국어로 나오던 것을 영어로 바꿨다(화면 글자의 대체 언어와 같게).
  다만 두 언어는 아직 화면 글자도 대부분 영어라서, 안내서에 "현재 대부분 영어"라고 적고 언어 지원 이슈로 연결했다.

**피드백 구조.** 이슈 양식 4종(화면 오류·디자인 의견·파일럿 요청·언어), Discussions, 분류 라벨, [CHANGELOG](../CHANGELOG.md),
[피드백 기록표](feedback-log.md), 그리고 이슈를 분류하는 에이전트 스킬(`triage-feedback`).
- 디자인 의견은 1~5점 평가와 채점표 영역을 함께 받는다. 같은 지적이 3건 이상 모이면 디자인 규칙을 다시 본다.
  점수는 내가 연구와 수집 데이터로 정한 디자인이 실제 사용자에게 통하는지 확인하는 데이터가 된다.
- 이슈 본문은 누구나 쓸 수 있으니 에이전트는 **지시가 아니라 데이터**로만 읽는다. 답글은 내가 확인한 뒤에 올린다.

**틀린 가설: "Desktop 자동 업데이트가 깨뜨렸다".** 첫 사용자 흐름을 캡처하다가 대시보드가 09-13 캡처와 다르게 보였다.
KPI 카드의 비교 줄("YoY ▲1.5%")이 사라지고, 결론 한 줄 윗부분이 잘리고, 표 열이 넓어지지 않고, 채널 버튼이 "Offli…"로 잘렸다.
- 원인을 하나씩 지웠다. 테마(커밋된 페이퍼 캡처는 정상) → 언어(영어·일본어 빌드 차이는 "Total" 한 단어) → 화면 크기(창을 접어 110%로 키워도 같음)
  → 적용 대기 상태(변경 내용 적용 후에도 같음) → 페이지 다시 그리기(같음). 생성된 파일도 커밋된 파일럿과 **데이터 경로 한 줄 말고는 같았다**.
- 버전을 조회하니 Store 앱이 2.157.879.0에서 2.157.1354.0으로 올라가 있었다. 여기서 "자동 업데이트가 깨뜨렸다"고 결론 내리고 CHANGELOG·README·노션에까지 적었다.
- **틀렸다.** 같은 출력의 둘째 줄, 실행 중인 프로세스의 파일 버전은 **2.147.1085.0**이었다. 이 PC에는 설치 관리자(MSI)판 Desktop 2.147이 따로 있었고,
  `.pbip` 더블클릭은 그쪽을 열었다. 테스트하던 창은 처음부터 옛 버전이었다. 옛 버전은 저장할 때 `cardCalloutArea`를 지우고 스키마를 2.2.0으로 낮춰 쓴다는 것도 확인했다.
- 같은 파일을 Store판 2.157.1354.0으로 여니 README 캡처와 똑같이 나왔다. 최신 버전에는 문제가 없었다 ([비교 이미지](share/media/desktop-2147-vs-2157.png)).
- 고친 것: quickstart가 Store판을 먼저 쓰고, 오래된 Desktop만 있으면 경고한다. 안내서 4개 언어에 "2.157 이상"을 적었다.
  이 문제를 첫 이슈([#1](https://github.com/Haweee47/powerbi-autopilot/issues/1))로 올리고 수정 커밋으로 닫았다. 피드백 흐름의 첫 사례다.
- 배운 점: 버전 번호를 두 개 봤으면 어느 쪽이 실제로 실행 중인지 확인한다. 그리고 사용자 PC에는 Desktop이 두 개 있을 수 있다. 회사 PC라면 더 그렇다.

**첫 릴리스 v0.1.0.** Store판 2.157.1354로 파일럿 4종 11페이지를 다시 열어(새로 고침 → 변경 내용 적용 → 페이지마다 캡처) 모두 README 캡처와 같은 것을 확인한 뒤
[v0.1.0](https://github.com/Haweee47/powerbi-autopilot/releases/tag/v0.1.0)을 냈다. 이제 "무엇이 언제 바뀌었나"는 CHANGELOG와 릴리스로, "무엇이 문제인가"는 이슈로 남는다.

**공개 알림 준비.** 스타는 광고보다 첫 화면과 찾기 쉬움에서 나온다고 보고, 저장소 안에서 할 수 있는 것부터 했다.
검색 주제 15개와 홈페이지 링크, README 배지, 소셜 미리보기 이미지(1280×640), Discussions 첫 글([#4](https://github.com/Haweee47/powerbi-autopilot/discussions/4)),
번역을 도와줄 사람을 위한 good first issue 두 개([#2](https://github.com/Haweee47/powerbi-autopilot/issues/2)·[#3](https://github.com/Haweee47/powerbi-autopilot/issues/3)), 채널별 알림 초안([launch-posts.md](share/launch-posts.md)).
- awesome 목록은 규칙부터 읽었다. awesome-claude-code(5.4만 스타)는 **사람이 웹 양식으로**, 첫 커밋 14일 뒤(09-25)부터 추천할 수 있다.
  Power BI awesome 목록 두 곳은 2024년에 올라온 PR도 아직 열려 있어서 PR은 보류했다. 받아 줄 가능성이 낮은 곳에 포크만 늘리지 않는다.

## 2026-09-15 · 검사 도구를 저장소로, 다른 모델로 끝까지 (예제 05)

**검사 도구를 저장소로.** README에는 "모든 페이지를 Desktop에서 확인"이라고 적어 놓고, 그 캡처 스크립트는 내 작업 폴더에만 있었다.
- [`tools/check.py`](../tools/check.py): 레이아웃·테마·파일럿을 다시 만들어 커밋과 비교하고, 파일럿 × 테마 × 언어 24개를 생성해 공식 검증한다.
  GitHub Actions가 push·PR마다 같은 명령을 돌린다.
- CI를 붙이며 찾은 버그: 테마 파일 이름의 해시를 Windows 줄바꿈(CRLF) 바이트로 계산하고 있어서 Linux에서는 다른 이름이 나왔다. 줄바꿈을 맞춘 뒤 해시한다.
- [`tools/render_check.ps1`](../tools/render_check.ps1): Store판 Desktop으로 열고 새로 고침한 뒤 전 페이지를 캡처한다. 버튼·탭은 이름이 아니라 클래스와 위치로 찾아서 Desktop 표시 언어와 무관하다.
- [`tools/render_report.py`](../tools/render_report.py): 처음 방식(픽셀 차이)은 정상 페이지도 7~14% 다르다고 했다. 예전 캡처가 10px 어긋나 있었기 때문이다.
  두 이미지를 먼저 맞춘 뒤 비교하니 정상 0.00~0.01%, 결함(KPI 비교 줄 4개 삭제) 0.17%, 결론 줄 삭제 0.51%로 갈렸다. 경계는 0.1%.
- **검사 도구의 거짓 통과.** 리포트가 열리지 않았는데 폴더에 남은 옛 캡처로 "11페이지 모두 일치"라고 보고했다. 이런 착오를 막으려고 만든 도구가 같은 착오를 했다.
  이제 열기 전에 옛 캡처를 지우고, 못 열면 실패로 끝나고, 페이지가 모자라면 MISSING으로 표시한다.

**다른 모델로 끝까지 ([예제 05](../examples/05-own-model/README.md)).** 파일럿은 한국어 기준 모델 하나를 위해 쓰였다.
영어 이름, 측정값이 사실 테이블에 있고, 예산은 달력에만 연결되고, 전년 측정값이 단순한 모델(가상 아웃도어 용품점)을 만들어 대시보드를 끝까지 만들었다.
- 기존 `new_report.py`는 "없는 필드 19개"라고 했다. 8개는 글자 조각(한 개짜리 필드를 글자 단위로 쪼갠 버그)이었고,
  **파일럿 DAX 안에서 쓰는 기본 측정값 12개와 열 7개는 놓쳤다.** 목록만 고치면 검증기는 통과하고 Desktop에서 깨진다.
- **모델 대응표.** `new_report.py --model`이 DAX까지 뒤져 없는 열 10개·측정값 13개를 찾고, 기준 정의·서식·쓰이는 곳을 힌트로 붙인 `model-map.json`을 쓴다.
  에이전트는 빈칸만 채운다(2.3KB, 약 770토큰). 생성기가 필드 이름과 DAX 속 열을 바꾸고, 숨긴 연결 측정값을 넣는다.
- 첫 캡처: 모든 비주얼이 그려지고 전년 대비가 CSV와 전부 맞았다(▲0.4%, 벌링턴 ▼48.6%). 틀린 것 둘: 달성률 64.5%(8개월 매출 ÷ 12개월 예산), 금액이 "0.6M"(영어 표시 측정값이 M 고정).
- **틀린 판단(내 것).** 기준 모델의 목표 데이터가 8월에서 끝나서 식에 "같은 기간" 규칙이 드러나지 않았고, 대응표를 채울 때 나도 놓쳤다. 이제 뼈대 힌트에 RULE로 적는다.
- **단위.** 금액 측정값이 선택 범위의 매출 크기로 K·M·B를 고르게 했다(동적 서식 문자열). 넣자마자 Desktop이 파일럿을 하나도 열지 못했고, 원인까지 세 번 헛짚었다.
  1. 고정 서식과 동적 서식이 겹친다는 검색 결과를 믿고 고쳤다 → 그대로 안 열림.
  2. 화면을 찍어 오류 창을 읽으니 "들여쓰기 오류": `formatStringDefinition`은 속성이 아니라 하위 개체라 속성들 뒤 맨 끝에 와야 했다 → 고쳤지만 여전히 안 열림.
  3. 오류 대화 상자 창만 따로 찍으니 진짜 원인은 "호환성 수준 1550 < 필요한 1601". 생성한 사본의 수준을 1601로 올린다(원본 모델은 그대로).
- 결과: 기준 파일럿 11페이지는 커밋된 캡처와 0.00~0.01%로 같고, 아웃도어는 매출 634.3K · 이익 308.1K · 달성률 95.6% · 목표 대비 ▼29.5K로 CSV와 전부 일치한다.
- 버그 하나 더: 대응표 반복문의 변수 `name`이 리포트 이름을 덮어써 리포트가 "매출 구성비.pbip"로 생성됐다. 검증기는 통과했다.

배운 점: 검증기를 통과하는 것, 화면이 열리는 것, 숫자가 맞는 것은 각각 따로 확인해야 한다. 이번에는 셋이 모두 한 번씩 어긋났다.

**v0.2.0 발표.** 위 내용을 [v0.2.0](https://github.com/Haweee47/powerbi-autopilot/releases/tag/v0.2.0)으로 냈다: 내 모델 대응표, 데이터 크기에 맞는 금액 단위, 누구나 돌릴 수 있는 검사 도구, 예제 05.

## 2026-09-15 · 같은 모델로 나머지 파일럿 3종, 트리 정렬, 한국어 자동 단위

**README에 첫 번째 목적을 적었다.** 분석가(DA·BA)가 대시보드 만들기가 아니라 데이터 분석과 비즈니스 분석에 시간을 쓰게 해서
비즈니스 임팩트를 높이는 것. 보기 좋은 리포트와 적은 토큰은 그 위에서 지키는 기준이다. CLAUDE.md에도 판단 기준으로 적었다.

**나머지 파일럿도 내 모델로.** 예제 05에서 대시보드만 해 봤던 것을 지표 테이블·행렬·딥다이브까지 넓혔다.
- `new_report.py --reuse-map`: 같은 모델로 이미 채운 대응표를 가져와 아는 값은 미리 채우고, 힌트는 빈칸에만 붙인다.
  새로 채운 값은 지표 테이블 5개(19개 미리 채움), 행렬 1개(20개), 딥다이브 8개(19개). `Orders PY`를 바꿔 쓴 덕분에 날짜 열 두 개는 목록에서 빠졌다.
- 세 리포트 모두 공식 검증 오류 0 · 경고 0이고, 결론 문장이 CSV와 전부 맞았다. 매장 12곳 중 1위 Web Store 120.6K·최저 Burlington ▼48.6%,
  제품 1위 Ultralight 1P Tent 65.6K, 최고 월 6월 88.1K·최저 2월 65.7K, 서부 36%, 할인 상위 5개 제품 이익률 48.9% 대 나머지 48.5%, 주문 3,422건.

**틀린 것: 요인 분해 트리가 1위를 숨겼다.** 딥다이브 결론 문장은 "1위 권역 West 36%"인데 트리에는 West가 없었다.
트리가 첫 단계를 알파벳 순으로 늘어놓고 한 칸에 막대 3개만 보였기 때문이다. 기준 파일럿도 같은 버그로 2·3위 권역(Online, Yeongnam)을 숨기고 있었는데,
1위(Capital Area)가 알파벳으로도 첫 번째라 그럴듯해 보였다. 공개 PBIR의 요인 분해 트리 18개 중 13개가 값 기준 내림차순 정렬을 저장한다는 걸 확인하고
같은 방식으로 고쳤다. 이제 Capital Area·Online·Yeongnam, 아웃도어는 West·Online·Midwest 순이다.

**한국어 금액 단위도 자동으로.** 차트·표는 만(1조 이상이면 억), KPI는 억(1억 미만이면 만)으로 선택 범위의 크기에 따라 고른다.
바꾸기 전과 후를 캡처해 비교하니 한국어 파일럿 11페이지 중 10페이지가 0.00%로 같았고, 달라진 1페이지는 일부러 고친 트리였다.

## 2026-09-15 · Sparklines in tables, and a DAX check before writing

*From this entry on, the log is written in English: the repository is for a global audience (CLAUDE.md §7).*

**Sparklines.** A measure table answers "how much" but not "which way". A `Sales Trend` measure now draws each row's monthly
sales for the selected year as a small SVG line: muted gray, with an end dot that is blue when the row grew year over year and
red when it shrank, so the single accent color still means one thing. It sits next to Sales in the measure table (stores and
products), the matrix scorecard (regions and stores, subtotals included) and the dashboard's store ranking.
- The theme sets the image size once (84×20 for a 100×24 drawing). Coordinates are formatted with `"en-US"` so the SVG stays
  valid in locales that use a decimal comma.
- Checked in Desktop: the pilots and the outdoor shop versions draw the lines, and the 12-column store table still fits without
  a horizontal scroll. Pages without sparklines match the committed screenshots.

**A DAX check before writing.** Several of today's bugs had one thing in common: DAX pointing at a column or measure the model
didn't have passed Microsoft's validator and only broke in Desktop. The generator now reads the DAX of every display and adapter
measure and stops with the measure's name when a reference is missing. It caught the new case at once: the sparkline needs the
month number, which three of the example 05 model maps didn't have. The bundled pilots pass with no false alarms.

**v0.3.0.** Released as [v0.3.0](https://github.com/Haweee47/powerbi-autopilot/releases/tag/v0.3.0): all four pilots on your own
model, sparklines, the DAX check, Korean units that follow the data, and the decomposition tree fix.

## 2026-09-16 · What one report costs

**The question.** The project's first goal is analyst time, and its second is token cost, but I had no per-report number.
The only total I had was the development itself: five days in one session, about 275M tokens, $262 at Opus 5 API prices,
96% of it cache reads because every request re-read a long conversation.

**Two reports, end to end.** A: the dashboard pilot on the bundled model, cut to one page with a channel bar, in Korean.
B: an English dashboard on a model the agent had never seen, filling the model map from the tool's hints.
Both passed Microsoft's validator on the first build, and B's numbers matched the source CSVs.
- A: 8 requests, 3.7K output tokens, 2 min 26 s. B: 28 requests, 20.2K output tokens, 7 min 35 s.
- Both ran inside this long session, so I removed the extra context from the cache reads, using the 45.8K-token first request of a
  new session as the baseline. Result: **A $0.57–0.93, B $2.07–2.43.** Band for users: $0.6–4 and 2–10 minutes per report
  ([write-up](cost-per-report.md)).
- I first tried to run each report in a separate headless Claude Code session. The permission check blocked starting an agent
  with broad tool access, so the runs happened here and were converted. Independent new sessions are still the next step,
  together with the Microsoft and data-goblin skills.

**What the measurement found.** `new_report.py` listed `SalesV`, a name the sparkline measure creates inside its own DAX, as a
measure the model lacked. The generator already skipped it, the copy tool didn't, and a user would have been stuck on a blank the
generator refuses. Both now use the same rule in `dax_refs`. I also suspected `3.422` on the orders card again. I had already been fooled by this on 2026-09-13,
so this time one zoom settled it: a comma at 24pt Segoe UI in a 1280×720 capture, not a locale bug.

**README.** The top image is now the page-by-page GIF of all four pilots instead of the tall static cover.

## 2026-09-16 · Seven themes: a palette plus a card shape

**Why.** Three themes that differed only in color were too few to choose from. I wanted two kinds of additions: themes that look good
at first glance, and themes that people who read reports all day would pick for work.

**A theme is now two choices.** The token file gained card shapes next to the palettes:
`soft` (the original: 12 px corners, hairline, barely visible shadow), `bold` (16 px, the border drawn in the card color so it only
rounds the corners, a deeper shadow) and `flat` (2 px, hairline, no shadow). Layouts, fonts and type sizes stay shared, so every spec
renders in every theme without changes. Four new presets:

| Group | Theme | Shape | For |
|---|---|---|---|
| Showcase | Aurora | bold | launches and first impressions: deep violet rail, rounder borderless cards |
| Showcase | Coast | soft | operations, retail and service reviews: deep teal rail |
| Practical | Ledger | flat | finance packs, month-end reviews, print: white page, square corners, no shadows |
| Practical | Contrast | flat | accessibility, projectors, bright rooms: black rail, darker lines and text, Okabe–Ito series |

**Series colors, checked rather than eyeballed.** Every palette went through the dataviz validator. Navy itself "fails" one check,
the chroma floor, because its second color is gray on purpose (last year), so I held the new palettes to Navy's result: everything
else passes. Three first drafts didn't:
- Coast's teal sat too close to the gray: ΔE 5.6 for protan viewers and 11.4 even with normal vision. A deeper teal (#008C9E) with a
  lighter gray fixed both (10.9 and 16.3).
- Ledger's navy was darker than the lightness band, and its green and orange were only 7.0 apart for protan viewers.
- Contrast had a dark yellow next to red that deutan viewers can't tell apart (ΔE 1.1); a purple took its place.

**Checked in Desktop.** The dashboard in each new theme, all four pages: nothing clipped, sparklines, bars and scatter colors follow
the palette. Navy, Paper and Midnight theme files came out byte-identical, and all 56 pilot × theme × language builds pass
Microsoft's validator. The capture script had the old three theme names hard-coded, so it now takes any preset.

The `new-report` skill can only show four options per question, so it now offers the recommended theme plus the three closest and
names the rest.

**A preset from a brand color.** Seven presets still don't include a company's own color, so `tools/brand_theme.py` makes one from a
single hex value and a base preset. The rule that took thought is where the brand color may go. Blue, teal and violet brands (hue
165–330°) become the data accent. Red, orange, yellow and green brands only tint the rail and the selected buttons: in these reports
red already means "below target", and a green "up" next to a red "down" is the pair color-blind readers confuse most. Text on the
brand color is darkened or lightened to at least 4.5:1.
- Tried with a blue brand on Navy and a red brand on Paper, both 0 errors in the validator and checked in Desktop: the blue one
  recolors the rail and the data, the red one only the rail and selections, and "Red = below target" still reads true.

**A false pass in the capture script, again.** The red brand's first capture came out with every visual empty under a second yellow
bar ("pending changes"), and the script still reported four pages captured. It now clicks each bar in turn and fails the report if one
is still showing. Re-run on the Navy dashboard: all four pages 0.00% against the committed screenshots, so no new false alarm.

## 2026-09-17 · Reading the model through ODBC (example 06)

**Why.** Analysts at work rarely load CSV files; they reach a warehouse through ODBC, and my own notes said "ODBC not validated".
The plan for tonight was to check it without installing anything.

**A driver that was already there.** `Get-OdbcDriver` listed the 64-bit *Microsoft Access Text Driver*, which comes with Office.
It reads CSV files through ODBC, so I copied the example 05 model and replaced each table's `Csv.Document` with
`Odbc.Query(OdbcConnection, "SELECT * FROM [Orders.csv]")` over one shared connection string. No password in any file.
- The report built from it unchanged: same spec, same model map, 4 pages, 0 errors and 0 warnings in the validator.
  Switching the source to ODBC didn't change the model's shape, so nothing downstream noticed.
- The same driver, connection string and SQL from PowerShell returned the CSV row counts (13,559 orders, 12 stores, 24 products,
  180 budget rows), typed the dates and amounts correctly, and gave the totals the report shows: sales 634,304 (+0.4%),
  profit 308,137, attainment 95.6%.

**Where it stopped.** On the first refresh Desktop asked how to sign in to the ODBC source (Default or Custom, Windows, Database),
exactly as it does for a real warehouse. It is a native dialog with no accessibility tree, clicks sent to it did nothing at 4 a.m.,
and I didn't want to push further on a sign-in step. So the Desktop capture of example 06 waits for one manual choice.
- The capture script did its job: it failed the run because the refresh never finished. It now also says why that probably
  happened ("a data source is asking how to sign in"), which the next person with a real ODBC source will need.

**Not done yet.** A live warehouse (Presto, Redshift): SQL dialects differ, and the agent is told to leave SQL alone and map renamed
columns instead. The flow and the sign-in choice are written into the guides in four languages.

## 2026-09-17 · Every new theme on every pilot, and three layout fixes

**All 44 pages looked at.** Yesterday the four new themes were only checked on the dashboard. Today the measure table, matrix and
deep dive went through Desktop in each of them: 44 pages, nothing clipped, heatmaps, bars and sparklines follow each palette.
One thing that isn't a theme issue: the rail's dropdown slicers say "모두" in an English report, because that placeholder follows
the Desktop display language, not the report's. The batch stopped halfway when the session ended; the capture log showed 8 of 12
reports done, so it resumed from there.

**Three fixes from looking at the captures.**
- *A short list that scrolled.* The summary's "weakest stores" card showed three rows and a scrollbar. Table specs now take
  `"top": N`, a Top N visual filter by the table's sort measure. I didn't write the filter from memory: the first public report I
  found saved one without a body, the second had the full shape Desktop writes, and the generator copies that. The validator then
  flagged two filters with the same name across the report (both tables rank stores by YoY), so names now include the visual id.
  The card shows the three weakest stores and the watch list the five weakest, without scrollbars; against the old captures the
  pages changed 0.07% and 0.05%, the titles and the scrollbars.
- *One page, one lonely tab.* A report with a single visible page no longer gets a page selector, and the rail slicers move up
  into its place. Checked on yesterday's one-page cost run, before and after.
- *Rail text that wraps.* The generator estimates the width of the report name and subtitle and warns when a line won't fit the
  160 px rail. My first estimate flagged a Korean subtitle that fits on screen, so full-width glyphs now count 0.92 em and the
  check allows 5%: yesterday's "Executive dashboard · sample data" (about 198 px) still warns, the Korean one no longer does.

The theme comparison images of the other six themes still show the old table title; the difference is a few pixels at that size,
so I didn't re-capture them.

## 2026-09-17 · A second layout, and a pilot for fulfillment operations

**A second layout.** Seven themes still shared one composition. `--frame top` builds every page with the report name, page tabs
and slicers in a bar across the top and gives the body the rail's width (columns 72 → 88 px). It is computed from the same layout
templates, so no spec changes.
- The first version scaled the body into the shorter space, and the summary page's bar charts started to scroll (five categories
  no longer fit in 200 px). The second keeps every body row at its rail height and takes 8 px from the first row only; the bar
  is 48 px, the title 32 and the headline 24.
- Horizontal tabs sized themselves to their text and cut "Discount vs margin"; a one-row grid shares the width. Dropdowns show only
  "All", so they get a small label; the validator wants a dropdown at least 48 px tall, so it takes the bar's full height.
- A page packs only the slicers it uses, and tabs keep one width across the report so they don't jump between pages.

**A pilot for fulfillment centers.** The people I build reports for work in fulfillment operations: outbound first, inbound and
inventory second, delivery third, and productivity (UPH, also called HTP) across all of it. The retail pilots don't speak that
language, so I built a domain pilot from public concepts (WERC's DC measures, labor-management practice) and synthetic data:
- **Data**: 16 teams by hour for January–August 2026, orders by cut-off and carrier, 13,926 inbound deliveries, daily cycle counts.
  Performance is zone × tenure × hour of day, with planted events: a quiet February, an August promotion with backlog, a night
  outage, a rebuilt night pick team with 60% new hires, late arrivals that wait for putaway, a supplier with more damage.
- **The productivity spine**: UPH on paid hours; % of standard = standard hours / direct hours; hours lost = paid − standard,
  split into slow work, support work and waiting, and decomposed by flow → process → shift → zone → team.
- **Pages** in priority order: Outbound, Lost hours, By hour, Teams, Inbound, plus a team drill-through. Bars show gaps to
  standard or target, because 91% and 97% bars look alike.
- **Checked**: every headline and KPI in the Q3 view matched the values the generator prints (outbound UPH 41.2, on-time ship
  85.2%, 43,859 hours lost, dock-to-stock 4.4 h, zone C accuracy 97.69%, lowest team PUT-C-N 71.2%). English, Korean and the
  top-bar layout in Ledger, all captured in Desktop. In Korean the data values follow too (processes, zones, shifts, carriers,
  loss types), except the flow names the measures compare against.
- **Fixed on the way**: the hour heatmap had 21 columns and scrolled in the rail layout, so matrix specs can drop the total column;
  a team-detail bar of "% of standard by hour" was a wall of red bars of similar length, so it now shows the gap as columns.

Concepts, formulas and page choices: [design-system/domains/fulfillment.md](../design-system/domains/fulfillment.md).

---

## 2026-09-18 · Order type and travel per unit (DPU)

The fulfillment pilot measured productivity but not the driver that moves picking most after the standard itself: how far people
walk. Two additions, both asked for by the analyst the pilot is built for - order type and travel distance.

- **Data**: orders are now split by type (single unit, multi unit, bulk), and every labor row carries the metres walked by the work
  that walks (picking, putaway, counting). Distance per unit follows the zone (A 9.5 m, B 14, C 26) and the order mix, because a
  single-unit order walks a full pick path for one unit. The August promotion shifts the mix to multi-unit and bulk, so DPU falls
  that week - a second cluster in the scatter.
- **Model** (12 tables, 51 measures): Travel Distance, DPU, Pick DPU, DPU Target (13.5 m), Single-unit Share, Order Mix, and an
  Order Types table.
- **A seventh page, Travel**: one dot per day - share of single-unit orders against metres walked per picked unit, sized by orders
  shipped, red above the plan - metres per unit by zone, and order type as a dropdown. The team table gained a DPU column.
- **DPU counts only the work that walks.** The first version divided by every unit handled, so pack and ship teams read 0.0 and the
  team total read 6.1 m/unit. The denominator is now the units whose rows carry distance: pack and ship are blank, the dock drops
  out of the zone bars, and the total reads 15.2.
- **Two locale bugs the validator cannot see.** In the Korean build the Order Types table was translated but `Orders[Order Type]`
  was not, so the relationship matched nothing and the page came up empty; and `Pick DPU` filtered `Processes[Process] = "Pick"`,
  which is translated too. Measures now compare against the key (`Process ID = "PCK"`) and the Korean patch translates both sides
  of the relationship. The rule the flow names already followed: a measure never compares against a value that gets translated.
  Korean also says 집품 for picking everywhere now, instead of 피킹 in the data and 집품 in the sentences.
- **Checked in Desktop**: pick DPU 14.7 m/unit, single-unit orders 50%, zone A 9.5 / B 13.9 / C 25.9 - the values the generator
  prints. English, Korean and the top-bar layout, all seven pages each.
- **Also fixed**: the top-bar layout gave the headline 24 px, less than the text needs - every headline with a descender was
  clipped ("per unit", "single-unit"). The headline now has the rail's 32 px, taken from the gap under the bar rather than from the
  body: the first attempt took it from the first body row, and the KPI cards lost their third line.
- **Still open**: the captures are taken on a Korean Desktop, so date axes read "2026년 7월" and a dropdown's "All" reads "모두"
  even in the English builds. That is Desktop's display language, not the report - the model's culture is already `en-US`.

---

## 다음 계획

| 순서 | 할 일 | 목표 |
|---|---|---|
| 1 | ~~여러 페이지 시안 v2~~ | 완료 |
| 2 | ~~테마 JSON + 페이지 레이아웃 템플릿~~ | 완료 |
| 3 | ~~명세 → PBIR 생성기~~ | 완료 (공식 검증 통과, 쓰는 양 약 7%) |
| 3-1 | Desktop 렌더링 확인 | 캡처 → 채점표 → 수정 반복 |
| 4 | 도구 비교 마무리 (예제 01·02) | 새 세션에서 토큰 측정, 채점표로 디자인 비교 |
