# 도구 3종 비교 규칙

같은 데이터, 같은 요청문으로 세 도구가 각각 만든 리포트를 비교한다.
비교 기준은 **디자인 품질**과 **토큰 사용량**이다.

## 공통 조건

- 데이터: [`examples/_data/korean-retail/`](../examples/_data/korean-retail/README.md)
- 요청문 (세 예제 모두 이 문장 그대로):

  ```
  2026년 8월 기준, 경영진이 한눈에 보는 판매 실적 요약 대시보드 1페이지를 만들어줘.
  매출·이익·목표 달성률, 전년 대비 증감, 카테고리·채널·매장별 성과를 보여줘.
  ```

- 격리: 예제마다 해당 저장소의 스킬 문서와 그 저장소가 요구하는 도구만 쓴다.
  - 저장소는 [00_setup.md](00_setup.md)에 적은 커밋으로 clone해서 읽는다.
  - 다른 저장소의 스킬은 설치하지도 읽지도 않는다.
- 산출물: `examples/<예제>/` 아래 `prompts.md`, `KoreanRetail.pbix`, 스크린샷, 토큰 기록
- PBIX는 Desktop `파일 > 다른 이름으로 저장`으로 만든다. 사람이 한 일은 `prompts.md`에 표시한다.

## 예제별 도구

| 예제 | 저장소 | 모델 | 리포트 | 검증 |
|---|---|---|---|---|
| 01 | skills-for-fabric `powerbi-authoring` | Modeling MCP (플러그인에 포함된 1순위 도구) | `powerbi-report-author` + 스킬 문서 | `validate` + `powerbi-desktop` 스크린샷 |
| 02 | data-goblin `reports`·`pbip`·`semantic-models` | TMDL 직접 작성 (`tmdl` 스킬, 저장소 내 검증기) | `pbir` CLI만 사용 (JSON 직접 작성 금지) | `pbir validate` + `pbir desktop screenshot` |
| 03 | powerbi-modeling-mcp | MCP | 없음 (MCP 범위 밖) | DAX 쿼리 — **완료** |

## 토큰 측정

- 예제마다 **새 Claude Code 세션**에서 시작한다. 앞선 대화가 남아 있으면 매 응답마다 다시 읽혀서 수치가 부푼다.
- 시작할 때 UTC 시각을 적어 두고, 끝나면 이렇게 합산한다:
  `python tools/token_usage.py --start <시작> --end <끝>`
- 출력 토큰, 새 입력, 캐시 읽기, 응답 수를 `prompts.md`에 기록한다.

## 디자인 평가 (초안)

스크린샷을 보고 판단한다. 데이터에 넣어 둔 흐름이 한눈에 보이는지를 함께 본다
(가전 역성장, 온라인 성장, 일산점 부진, 목표 미달).
세부 채점 기준은 `design-system/review-rubric.md`에서 확정한다.
