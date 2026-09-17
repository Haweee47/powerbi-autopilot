# 04 — 명세 → PBIR 생성기 (이 저장소의 방식)

에이전트는 **작은 명세 파일 하나**만 쓴다. 좌표·서식·모델 연결·파일 구조는 스크립트가 채운다.
예제 01~03이 "기존 도구로 만들면 어떻게 되나"라면, 04는 "토큰은 적게, 디자인은 정해진 규칙대로"를 목표로 한 우리 방식이다.

| 누가 | 무엇을 | 파일 |
|---|---|---|
| 에이전트 | 페이지마다 영역 → 필드·제목 | [`report.spec.json`](report.spec.json) |
| 레이아웃 템플릿 | 좌표 (1280×720, 12열 88px, 8px 격자) | [`design-system/layouts`](../../design-system/layouts/README.md) |
| 테마 | 서식 전부 | [`design-system/themes`](../../design-system/themes/README.md) |
| 예제 03 모델 | 테이블·관계·측정값 (TMDL) | [`../03-modeling-mcp/tmdl`](../03-modeling-mcp/tmdl) |
| 생성기 | 필드 대조 → PBIP 쓰기 → 크기 측정 | [`tools/generate_pbir.py`](../../tools/generate_pbir.py) |

```bash
python tools/generate_pbir.py examples/04-autopilot/report.spec.json
powerbi-report-author validate examples/04-autopilot/KoreanRetail.Report
# Desktop에서 열어 볼 사본 (이 PC의 데이터 경로로 바꿔 저장소 밖에 쓴다)
python tools/generate_pbir.py examples/04-autopilot/report.spec.json --local-data --out <작업 폴더>
```

## 명세에서 쓸 수 있는 것

| 키 | 어디에 | 하는 일 |
|---|---|---|
| `measures` | 최상위 | 표시용 측정값을 모델에 더한다. 억·만 단위, "전년 대비 ▲12.3%" 같은 문구, 결론 문장, 증감 색(`@neg` 같은 토큰 이름) |
| `shared` | 최상위 | 레일(리포트 이름·기준일·슬라이서)에 들어갈 내용. 한 번 적으면 모든 페이지에 들어간다 |
| `headline` | 페이지 | 제목 아래 결론 한 줄 (문장을 돌려주는 측정값) |
| `default`, `single` | 슬라이서 | 처음 열 때 선택할 값(예: 2026), 하나만 고르기 |
| `ref`, `ref_color` | 카드 | 값 아래 비교 문구와 그 색 (측정값) |
| `sub` | 차트·표 | 부제목: 단위, 읽는 법 |
| `target` | 선 차트 | 목표 계열을 흐린 점선으로 |
| `color` | 막대 | 막대마다 색을 측정값으로 (목표 미달 빨강) |
| `colors`, `totals` | 표 | 열 글자색을 측정값으로 (감소만 빨강), 합계 줄 끄기 |
| `top` | 표 | `sort` 기준으로 앞의 N행만 남긴다 (Top N 필터). 카드에 들어가는 만큼만 보여 스크롤바가 생기지 않게 |
| `type` | 막대 | 가로·세로 막대만 명세가 바꿀 수 있다 (항목이 많으면 세로) |
| (자동) | 전 페이지 | 레일 바탕과 페이지 선택기는 적지 않아도 놓인다. 이름 끝의 `(만)`·`(억)`은 범례·머리글에서 뗀다. 선 차트 첫 계열(올해)은 굵게 |

## 사용자가 입력한 프롬프트 (원문 그대로)

```
이제 프로젝트 계속 보완해줘. 디자인이랑 구성, 토큰 절약방법등. 일단 디자인과 구성이 제일 우선순위야. 토큰 최적화는 그 다음임
```
```
5hr 토큰 다 쓸때까지 개선하고 중간중간 변경및 진행사항 md로 정리하면서 해.
```

## 사람이 손으로 한 부분

| 단계 | 내용 | 이유 |
|---|---|---|
| (없음) | 생성과 구조 검증까지는 사람이 손대지 않았다 | |

Desktop 렌더링 확인(스크린샷)은 Desktop Bridge가 켜진 뒤 추가한다.
