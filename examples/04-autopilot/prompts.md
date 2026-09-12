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
```

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
