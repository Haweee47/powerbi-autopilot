# 시작하기

[English](en.md) · **한국어** · [日本語](ja.md) · [简体中文](zh-CN.md)

내려받아서 Power BI 리포트를 여는 데 5분 정도 걸립니다. 그다음 말로 요청해 내 리포트를 만드는 방법을 설명합니다.

## 준비물

| | 필요한 경우 | 받는 곳 |
|---|---|---|
| Windows 10/11 + Power BI Desktop **2.157 이상** | 항상 | Microsoft Store에서 무료 (스스로 업데이트됨). 이전 버전은 글자 몇 곳이 잘립니다 ([#1](https://github.com/Haweee47/powerbi-autopilot/issues/1)) |
| Python 3.10 이상 | 항상 | [python.org](https://www.python.org/downloads/). 설치할 때 **Add python.exe to PATH**를 체크 |
| Claude Code | 말로 요청해 리포트를 만들 때 | [claude.com/claude-code](https://claude.com/claude-code) |
| Microsoft PBIR 검증기 | 선택 | `npm install -g @microsoft/powerbi-report-authoring-cli` |

그 밖에는 설치할 것이 없습니다. 스크립트는 Python 기본 라이브러리만 씁니다.

## 1. 내려받기

초록색 **Code** 버튼 → **Download ZIP** 후 압축을 풉니다. 또는:

```bash
git clone https://github.com/Haweee47/powerbi-autopilot.git
```

## 2. 완성된 리포트 열어 보기 (AI 없이)

폴더 안의 **`quickstart.cmd`**를 더블클릭합니다. 들어 있는 가상 데이터로 대시보드 파일럿을 만들고 Power BI Desktop으로 엽니다.

처음 열 때:

1. 노란 줄에 "일부 테이블에 데이터가 없습니다"가 보이면 → **지금 새로 고침**
2. 이어서 "적용되지 않은 변경 내용"이 보이면 → **변경 내용 적용**

다른 파일럿·테마·언어는 폴더에서 터미널을 열고 실행합니다:

```bash
python tools/quickstart.py --purpose matrix --theme midnight
python tools/quickstart.py --all --lang ko
```

| 옵션 | 값 |
|---|---|
| `--purpose` | `dashboard`(대시보드) · `table`(지표 테이블) · `matrix`(행렬) · `deepdive`(딥다이브) |
| `--theme` | `navy` · `paper` · `midnight` · `aurora` · `coast` · `ledger` · `contrast` |
| `--lang` | `en` · `ko` · `ja` · `zh-CN` |

**회사 브랜드 색.** 색 하나로 테마를 만들고 그 id를 `--theme`에 넣습니다. 파랑·청록·보라 계열은 데이터 색까지 바뀌고,
빨강·주황·노랑·초록 계열은 왼쪽 레일과 선택 표시에만 쓰입니다. 리포트에서 빨강은 이미 "목표 미달"을 뜻하기 때문입니다.

```bash
python tools/brand_theme.py --id acme --accent "#0F62FE" --base navy
python tools/build_themes.py
python tools/quickstart.py --purpose dashboard --theme acme
```

결과는 `out/` 폴더에 생기고 git은 이 폴더를 무시합니다. 필터·시각화·데이터 창을 접으면(») 페이지를 크게 볼 수 있습니다.

## 3. 말로 요청해 리포트 만들기 (Claude Code)

```bash
cd powerbi-autopilot
claude
```

그리고 원하는 것을 적습니다. 예:

> 매장 KPI 테이블을 페이퍼 테마, 한국어로 만들어 줘.

에이전트는 빠진 것(용도·테마·언어)만 묻고, 가장 가까운 파일럿을 복사해 필드와 제목을 바꾼 뒤 PBIP를 생성하고 검증합니다.
에이전트가 따르는 절차는 [`.claude/skills/new-report/SKILL.md`](../../.claude/skills/new-report/SKILL.md)에 있습니다.

## 4. 내 데이터로 만들기

1. 쓰고 있는 리포트를 Power BI Desktop에서 열고 **파일 → 다른 이름으로 저장 → Power BI 프로젝트(.pbip)**로 저장합니다.
   예전 버전이면 먼저 **옵션 → 미리 보기 기능 → Power BI 프로젝트(.pbip) 저장 옵션**을 켭니다.
2. 에이전트에게 모델 위치를 알려 줍니다:
   > C:\Reports\Sales\Sales.SemanticModel\definition 모델로 대시보드를 만들어 줘
3. 에이전트는 모델 파일을 통째로 읽지 않고 한 화면 요약만 봅니다. `new_report.py`가 파일럿에 필요한데 내 모델에 없는 것(DAX 안에서 쓰는 측정값까지)을
   모두 찾아 `model-map.json`에 적고 기준 정의를 힌트로 붙입니다. 에이전트는 이 대응표에 내 열 이름과 DAX만 채웁니다. [예제 05](../../examples/05-own-model/README.md)

데이터 연결(SQL Server, ODBC, SharePoint Online, 파일 등)은 모델과 함께 그대로 복사되고 내 PC에만 있습니다. 자격 증명은 파일에 쓰지 않습니다.
**ODBC.** ODBC 리포트도 위와 같이 PBIP로 저장하면 됩니다. 연결 문자열과 SQL은 그대로 복사되고, 비밀번호는 파일에 들어가지 않습니다. 처음 새로 고칠 때 로그인 방식(기본 또는 사용자 지정, Windows, 데이터베이스)을 한 번 고르면 Desktop이 기억합니다. 로컬 ODBC 드라이버로 확인한 과정은 [예제 06](../../examples/06-odbc/README.md)에 있습니다. 실제 데이터 웨어하우스(Presto, Redshift 등) 연결은 아직 시험하지 못했습니다.

실데이터는 커밋이나 이슈에 올리지 마세요. `out/`은 git이 무시하지만 `examples/` 아래에 만든 리포트는 추적됩니다.

## 언어

| 언어 | 리포트 글자 | 숫자 | 가상 데이터 값 |
|---|---|---|---|
| English | 완성 | K · M | 영어 |
| 한국어 | 완성 | 만 · 억 | 한국어 |
| 日本語 | 아직 대부분 영어 | K · M | 영어 |
| 简体中文 | 아직 대부분 영어 | K · M | 영어 |

내 언어를 완성하고 싶다면 [언어 지원](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=4-language-request.yml) 이슈를 열어 주세요. 검토해 줄 원어민이면 특히 반갑습니다.

## 문제 해결

| 보이는 것 | 할 일 |
|---|---|
| 비주얼이 비어 있다 | 노란 줄의 **지금 새로 고침** 또는 **홈 → 새로 고침** |
| "파일을 찾을 수 없음" 같은 데이터 폴더 오류 | `templates/`가 아니라 quickstart가 만든 `out/`의 리포트를 엽니다 (`templates/`의 파일럿에는 자리표시 경로가 들어 있습니다). 또는 **데이터 변환 → 매개 변수 편집 → 데이터폴더**를 `examples\_data\korean-retail\en`의 전체 경로로 바꿉니다 |
| `python`을 찾을 수 없다 | Python을 **Add python.exe to PATH** 체크하고 다시 설치하거나 `py tools\quickstart.py`로 실행 |
| Desktop이 `.pbip`를 못 연다 | Power BI Desktop 업데이트 |
| KPI 비교 줄이 없거나 글자가 잘린다 | Power BI Desktop이 2.157보다 오래된 버전입니다(**도움말 → 정보**). 설치 관리자판과 Store판이 둘 다 있으면 더블클릭 시 오래된 쪽이 열립니다. `python tools/quickstart.py --open`으로 열거나, 시작 메뉴에서 Desktop을 켜고 **파일 → 열기**를 쓰세요 ([#1](https://github.com/Haweee47/powerbi-autopilot/issues/1)) |
| 그 밖에 이상한 것 | 창 전체 스크린샷과 함께 [알려 주세요](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=1-render-bug.yml) |

## 피드백

모든 이슈를 읽고, 기록하고, 답합니다. [피드백이 변경으로 이어지는 방식](../../CONTRIBUTING.md#how-feedback-becomes-changes)

- [화면이 이상해요](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=1-render-bug.yml)
- [디자인 의견](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=2-design-feedback.yml) (1~5점 평가만 해도 됩니다)
- [새 파일럿·기능 요청](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=3-pilot-request.yml)
- [질문·결과 공유](https://github.com/Haweee47/powerbi-autopilot/discussions)
