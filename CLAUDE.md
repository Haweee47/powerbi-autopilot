# CLAUDE.md — Power BI PBIP 자연어 자동 제작

자연어 프롬프트만으로 **심미적으로 수준 높은** Power BI 리포트를 만드는 방법을 정리해
GitHub에 공개한다. 결과물은 "만든 리포트"가 아니라 **누구나 따라 할 수 있는 제작 방법**이다.

---

## 1. Role & Objective

**Role**: Power BI 개발자 겸 BI 디자이너, 그리고 AI 에이전트 워크플로우 설계자

**Objective**
- PBIP(텍스트 기반 Power BI 프로젝트)를 Claude Code가 직접 만들고 고치게 한다.
- 기능 동작보다 **디자인 품질**(레이아웃, 색, 타이포, 정보 위계)을 핵심 가치로 둔다.
- 사용한 프롬프트, 설정, 결과 스크린샷을 함께 남겨 **재현 가능하게** 한다.

## 2. User Profile & Environment

| 항목 | 내용 (2026-09-11 확인) |
|---|---|
| OS / 에디터 | Windows 10 Pro, VS Code + Claude Code |
| Power BI Desktop | 2.157.879.0 (Microsoft Store판, 자동 업데이트) |
| Python | 3.11.9 |
| git / gh | 2.47.1 / 2.98.0 |
| Node.js | **미설치** → 공식 Modeling MCP(npx), Desktop Bridge CLI(npm)에 필요 |

> **설명 톤**: 데이터 분석 입문자 기준. PBIP/PBIR/TMDL/DAX 같은 용어는 처음 나올 때
> 한 줄 풀이를 붙인다. 새 도구·명령은 "무엇을 왜 하는지"를 먼저 설명한다.

## 3. 핵심 용어 한 줄 풀이

| 용어 | 뜻 |
|---|---|
| PBIX | 기존 Power BI 파일. 하나의 바이너리라 AI가 직접 읽고 쓸 수 없다 |
| **PBIP** | 리포트를 폴더와 텍스트 파일로 저장하는 형식. git으로 변경 이력 관리, AI 직접 편집 가능 |
| **PBIR** | PBIP 안의 리포트(화면) 형식. 페이지·비주얼마다 JSON 파일 하나 (`visual.json`) |
| **TMDL** | 시맨틱 모델(테이블·관계·측정값)을 사람이 읽을 수 있는 텍스트로 쓴 형식 |
| 시맨틱 모델 | 리포트가 참조하는 데이터 모델. 테이블, 관계, DAX 측정값 |
| 테마 JSON | 색 팔레트·글꼴·비주얼 기본 서식을 한 파일로 정의. 디자인 일관성의 핵심 |
| Desktop Bridge | 실행 중인 Power BI Desktop에 외부 도구가 접속하는 로컬 통로. 리로드·스크린샷 |
| MCP | AI 에이전트가 외부 도구를 호출하는 표준 프로토콜 |

---

## 4. 기존 도구 조사 결과 (2026-09-11)

### 4-1. Microsoft 공식 (preview)

| 도구 | 역할 | ★ / 라이선스 |
|---|---|---|
| [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) → `powerbi-authoring` 플러그인 | **Report Planner**(요구사항→브리프) → **Report Design**(디자인 브리프) → **Report Authoring**(PBIR 작성·검증) | 1,144 / MIT |
| [microsoft/powerbi-modeling-mcp](https://github.com/microsoft/powerbi-modeling-mcp) | 시맨틱 모델 생성·수정, DAX 검증 (로컬 MCP, Node 20+) | 1,142 / MIT |
| [Desktop Bridge CLI](https://www.npmjs.com/package/@microsoft/powerbi-desktop-bridge-cli) (`powerbi-desktop`) | `open` / `reload` / `status` / `screenshot` / `screenshot-all` | npm |

공식 문서: [Report Authoring skill](https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-report-authoring-skill-overview) ·
[MCP servers](https://learn.microsoft.com/en-us/power-bi/developer/mcp/mcp-servers-overview) ·
[Desktop Bridge](https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-desktop-bridge-overview)

**Report Design 스킬의 방법론** (심미성 관련해 가장 체계적):
- 먼저 디자인 정체성(tone + signature)을 정하고 모든 페이지에 일관되게 적용
- 페이지마다 아키타입 선택: Executive Summary / Operational Monitor / Analytical Canvas / Narrative Story / Comparative Benchmark
- 8px 스냅 그리드, 헤더·필터·본문 영역 구분, 비주얼끼리 겹치지 않음
- 결과는 YAML "디자인 브리프" → Authoring 스킬이 이것을 입력으로 PBIR 작성

### 4-2. 커뮤니티

| 저장소 | 특징 | ★ / 라이선스 |
|---|---|---|
| [data-goblin/power-bi-agentic-development](https://github.com/data-goblin/power-bi-agentic-development) | Claude Code 플러그인 마켓플레이스. `pbi-report-design`(디자인 원칙), `modifying-theme-json`, `review-report`, `create-pbi-report`, Deneb·SVG 커스텀 비주얼 | 910 / **GPL-3.0** |
| [maxanatsko/pbir.tools](https://github.com/maxanatsko/pbir.tools) | `pbir` CLI (위 플러그인이 사용). 탐색·수정·검증·게시 | 277 / **비상업 라이선스** |
| [MinaSaad1/pbi-cli](https://github.com/MinaSaad1/pbi-cli) | Python CLI + Claude 스킬 13종. MCP 없이 동작, 32개 비주얼 타입 | 453 / MIT |
| [lukasreese/powerbi-claude-skills](https://github.com/lukasreese/powerbi-claude-skills) | 요구사항 수집, PBIR 리포트 빌더(IBCS 차이 분석 차트) | 119 / 없음 |
| [jonathan-pap/powerbi-report-mcp](https://github.com/jonathan-pap/powerbi-report-mcp) | 리포트 레이어 MCP 서버 (56개 도구: 페이지·비주얼·테마·필터) | 19 / MIT |
| [allanbrunorj/powerbi-claude](https://github.com/allanbrunorj/powerbi-claude) | CSV → Modeling MCP → 리포트 JSON. `CLAUDE.md` 구성 참고용 | 4 / 없음 |
| [bcastelino/powerbi-dashboard-generator](https://github.com/bcastelino/powerbi-dashboard-generator) | 자연어 → PBIP 스킬 10종, 확인 게이트 2개 | 1 / MIT |
| [zebrabi/zebra-bi-agentic](https://github.com/zebrabi/zebra-bi-agentic) | Zebra BI(유료 비주얼)로 IBCS 재무 리포트 작성, 검사 59개 | 2 / 유료 비주얼 필요 |
| [gusbavia/pbi-theme](https://github.com/gusbavia/pbi-theme) | 브랜드 색 3개 → 37색 테마 + 색각이상 검사. 아이디어는 좋으나 커밋 1개 | 7 |
| [kpbray/power-bi-agent-skills](https://github.com/kpbray/power-bi-agent-skills) | Copilot용 스킬 10종 + 예제 PBIP 1개. 커밋 2개 | 9 |
| [HorizunGroup/horizun-pbi-mcp](https://github.com/HorizunGroup/horizun-pbi-mcp) | 모델·PBIP 감사/수리 MCP | 13 |

### 4-3. 수준 평가 (저장소 트리를 직접 세어 확인)

| 저장소 | 커밋 | 테스트 | 결과물 예제 | 디자인 깊이 | 평가 |
|---|---|---|---|---|---|
| skills-for-fabric (MS) | 62 | 없음 | 이미지 0, PBIP 0 | 디자인 브리프·아키타입·그리드 | **상** (공식, preview) |
| data-goblin | 455 | 2 | 이미지 7, **PBIP 0** | 가장 깊음 (3-30-300, 간격 균일, KPI 규칙) | **상** (GPL) |
| pbi-cli | 313 | 테스트 488개, CI | 이미지 0 (SVG 도식만) | 테마 스킬 1개로 얕음 | 엔지니어링 상 / 디자인 하 |
| lukasreese | 18 | 없음 | IBCS 차트 이미지 4 | IBCS 한정 | 중 (작성자가 JSON 오류·SVG 깨짐 인정) |
| 나머지 (★20 미만) | 1~20 | 대부분 없음 | 거의 없음 | 얕음 | 초기 단계 |

- 제3자 체험기: 공식 스킬을 쓰면 테마·KPI 카드·드릴다운 행렬까지 "깔끔한" 결과가 나왔고,
  **스킬 없이** 맨 AI로 하면 잘못된 비주얼 타입·잘못된 위치의 속성 때문에 리포트가 깨졌다.
- 공통 한계: PBIR이 아직 preview라 스키마가 바뀌고, 문서에 없는 속성이 많다.

### 4-4. 결론: 무엇이 이미 있고 무엇이 비어 있나

- **이미 있음**: PBIR/TMDL 파일 작성, 모델링 MCP, 검증, Desktop 리로드·스크린샷 → **뼈대는 새로 만들지 않는다.**
- **비어 있음** (이 저장소가 채울 부분):
  1. 실제로 **예쁜 결과물을 재현 가능하게 보여 주는 갤러리** (프롬프트 → 스크린샷, 전·후 비교)
  2. 바로 쓸 수 있는 **디자인 시스템**: 검증된 테마 JSON 프리셋 + 페이지 레이아웃 템플릿
  3. **스크린샷 기반 디자인 리뷰 루프**의 채점 기준 (무엇을 보고 "예쁘다/아니다"를 판단하나)
  4. 한국어 문서, 한국어 폰트·숫자 표기(억/만 단위) 대응

## 5. 기술 스택 (초안 — 0단계에서 확정)

| 레이어 | 1순위 | 대안 |
|---|---|---|
| 시맨틱 모델 | powerbi-modeling-mcp | pbi-cli |
| 기획·디자인 브리프 | skills-for-fabric: Planner + Design | data-goblin `pbi-report-design` |
| PBIR 작성·검증 | skills-for-fabric: Authoring | pbi-cli / pbir CLI |
| 시각 검증 | Desktop Bridge CLI `screenshot-all` | 수동 캡처 |

**라이선스 주의**: data-goblin(GPL-3.0) 코드를 이 저장소에 **복사하면** 이 저장소도 GPL이 된다.
설치해서 쓰거나 링크하는 것은 괜찮다. pbir CLI는 비상업 라이선스다. 이 저장소는 MIT로 두고,
외부 스킬은 복사하지 말고 설치 방법만 문서화한다.

---

## 6. Core Workflow (반드시 준수)

한 번에 끝까지 가지 않는다. 단계마다 결과를 사용자가 확인한 뒤 다음으로 넘어간다.

| 단계 | 내용 | 산출물 |
|---|---|---|
| 0 | 환경 세팅: Node.js, 플러그인·MCP 설치, Desktop 미리 보기 기능 확인 | `docs/00_setup.md` |
| 1 | 데이터 준비: 샘플 데이터 선정, 구조 파악 | `examples/<이름>/data/` |
| 2 | 시맨틱 모델: 테이블·관계·측정값 (TMDL) | `*.SemanticModel/` |
| 3 | 디자인 브리프: 톤, 아키타입, 레이아웃, 색, 테마 | `design-brief.yaml` |
| 4 | 리포트 작성: 테마 적용, 페이지·비주얼 (PBIR) | `*.Report/` |
| 5 | 검증: 구조 검증 + Desktop 리로드 + 전 페이지 스크린샷 | `screenshots/` |
| 6 | 디자인 리뷰 루프: 스크린샷을 채점 기준으로 평가 → 수정 → 5단계 반복 | 리뷰 기록 |
| 7 | 정리: 프롬프트·스크린샷·README 갱신, 커밋 | 갤러리 항목 |

**작업 규칙**
- **스크린샷 없이 "완성" 선언 금지.** JSON이 유효해도 화면이 깨질 수 있다. 눈으로 본 것만 믿는다.
- 에이전트가 PBIR을 고치기 전에 **베이스라인을 커밋**한다 (되돌릴 수 있게).
- **PBIR 파일이 원본이다.** Desktop에서 손으로 고친 게 있으면 먼저 저장하게 한 뒤 작업한다.
  저장 안 된 변경은 에이전트가 파일을 다시 쓰면서 사라진다.
- 곧 폐지될 비주얼(Q&A, Bing 지도, 채워진 지도)은 쓰지 않는다. 구형 `card` 대신 `cardVisual`.
- 각 예제에 **실제로 입력한 자연어 프롬프트를 원문 그대로** `prompts.md`에 남긴다.
  이 저장소의 주장은 "자연어만으로 된다"이므로, 손으로 고친 부분이 있으면 반드시 표시한다.
- 테마는 비주얼마다 서식을 따로 넣지 말고 **테마 JSON에서 한 번에** 정의한다.

## 7. 디렉토리 구조 (초안)

```
powerbi-pbip-auto/
├── CLAUDE.md
├── README.md                  # 소개, 갤러리, 빠른 시작
├── LICENSE                    # MIT
├── .gitignore
├── .mcp.json                  # MCP 서버 설정 (공유용, 비밀값 없음)
├── docs/                      # 설치·워크플로우·팁 문서
├── design-system/
│   ├── themes/                # 테마 JSON 프리셋
│   ├── layouts/               # 페이지 아키타입별 레이아웃 템플릿
│   └── review-rubric.md       # 디자인 리뷰 채점 기준
└── examples/
    └── <예제명>/
        ├── data/              # 샘플 데이터 (공개 가능한 것만)
        ├── prompts.md         # 사용한 프롬프트 원문
        ├── design-brief.yaml
        ├── <예제명>.pbip
        ├── <예제명>.Report/
        ├── <예제명>.SemanticModel/
        └── screenshots/
```

## 8. Git 규칙

- 아직 `git init` 전이다. GitHub 원격 저장소 생성·`git push`는 **사용자 확인 후에만** 한다.
- 커밋 메시지: Conventional Commits (`feat:` `fix:` `docs:` `refactor:` `chore:`)
  - 예: `feat: sales 예제 추가 — Executive Summary 1페이지`
- `.gitignore`에 반드시 포함 (Power BI가 로컬에서 만드는 파일):
  `**/.pbi/localSettings.json`, `**/.pbi/cache.abf`
- TMDL 경로가 길어질 수 있으므로 Windows 긴 경로를 켠다: `git config --system core.longpaths true`
- 개인·회사 데이터, 인증 토큰은 절대 커밋하지 않는다. 예제 데이터는 공개 데이터셋만 쓴다.

## 9. 기록

작업 단위가 끝나면 노션에 붙여넣을 수 있는 일지를 출력한다:
목표 / 사용한 프롬프트 / 결과 스크린샷 요약 / 트러블슈팅(문제 → 원인 → 해결, **틀린 가설도**) / 배운 점.
LinkedIn 글은 요청할 때만 쓴다 — 전·후 스크린샷 비교를 중심으로.

## 10. 다음 할 일

- [ ] 0단계: Node.js LTS 설치, 플러그인·MCP 설치 명령을 각 README로 재확인 후 설정
- [ ] Desktop 옵션 → 미리 보기 기능: PBIP 저장, PBIR 형식, 외부 도구 접근(Bridge) 켜져 있는지 확인
- [ ] 기술 스택 확정 (5절 표)
- [ ] 첫 예제용 공개 샘플 데이터 선정
- [ ] `git init` 및 GitHub 저장소 이름 결정
