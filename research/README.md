# 디자인 연구: 공개 Power BI 리포트 수집·분석

좋은 디자인 규칙을 정하려고 GitHub에 공개된 Power BI 리포트를 모아 분석한다.
원칙은 **AI가 원본을 통째로 읽지 않는 것**이다. 원본을 매번 읽으면 토큰이 크게 든다
(1페이지 리포트 폴더 하나가 약 11만 토큰). 그래서 스크립트가 디자인 지표를 수치로 뽑고,
AI와 사람은 그 요약만 본다.

## 흐름

| 단계 | 스크립트 | 하는 일 | 결과 |
|---|---|---|---|
| 1 | (검색) | GitHub 저장소 검색 API로 키워드·주제 태그 검색 + 직접 고른 출처 | `candidates_search.json` |
| 2 | [`scan_repos.py`](scan_repos.py) | 저장소마다 파일 목록만 받는 clone으로 PBIX·PBIT·PBIP·`.Report` 폴더 찾기 | `inventory.json` |
| 3 | [`fetch_files.py`](fetch_files.py) | 고른 파일만 내려받기 (blob 해시로 중복 제거, 크기 상한) | `collected/files/`, `fetched.json` |
| 4 | [`analyze_reports.py`](analyze_reports.py) | PBIX(zip 안의 레이아웃 JSON)·PBIR 폴더에서 디자인 지표 추출 | `summaries.jsonl` |
| 5 | [`aggregate.py`](aggregate.py) | 분포 통계 + 눈으로 볼 후보 순위 | `design_stats.md` |
| 6 | (사람 + Desktop) | 상위 후보만 Desktop에서 열어 스크린샷·PBIP 변환 | 디자인 규칙 초안 |

PBIX는 zip 파일이라 Desktop 없이도 안의 레이아웃(`Report/Layout`)을 읽을 수 있다.
그래서 PBIP 변환은 전체가 아니라 **상위 후보에만** 한다.

## 라이선스 원칙

- 내려받은 원본은 `research/collected/`에만 둔다. 이 폴더는 `.gitignore`에 들어 있어 **재배포하지 않는다**.
  (라이선스가 없거나 제각각인 저장소가 대부분이다)
- 커밋하는 것: 출처 목록(URL·라이선스), 수치로 뽑은 통계, 그 통계로 정한 **우리 자신의** 디자인 규칙.
- 특정 리포트의 테마 JSON이나 레이아웃을 그대로 가져다 쓰지 않는다. 필요하면 원 저장소 라이선스를 확인한다.

## 다시 실행하기

```bash
cd research
python scan_repos.py            # 중간에 멈춰도 inventory.json에 이어서 기록
python fetch_files.py --max-mb 80 --budget-gb 15
python analyze_reports.py collected/files collected/_scan --out summaries.jsonl
python aggregate.py summaries.jsonl --top 40 > design_stats.md
```

## 배운 점 (틀린 시도 포함)

- **`git ls-tree -l`을 partial clone에 쓰지 말 것.** 크기를 보여 주려고 파일 내용을 하나씩 전부 내려받는다.
  처음에 이렇게 해서 몇 분 만에 5.8GB가 받아졌고 스캔이 사실상 멈췄다.
  크기 없이 `ls-tree -r`로 목록과 blob 해시만 읽고, 크기는 raw 주소 HEAD 요청으로 필요한 파일만 확인한다.
- GitHub API는 인증 없이 검색 분당 10회, 일반 요청 시간당 60회다. 대량 조사는 git clone과 raw 주소로 한다.
- 품질 점수는 "눈으로 볼 후보를 고르는" 거친 기준이다. 예쁜지 아닌지는 스크린샷으로 판단한다.
