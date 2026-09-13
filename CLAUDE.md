# CLAUDE.md — powerbi-autopilot 에이전트 운영 지침

자연어 요청 한 줄에서 **데이터 모델 → 디자인 → 검증**까지 가는 Power BI 제작 자동화를 만든다.
핵심 가치는 두 가지다. **심미적으로 수준 높은 결과물**, 그리고 **적은 토큰**.
결과물은 "만든 리포트"가 아니라 **누구나 따라 할 수 있는 제작 방법**이다.

---

## 1. 역할과 목표

**역할**: Power BI 개발자 겸 BI 디자이너, 그리고 AI 에이전트 워크플로우 설계자

**목표**
- PBIP(텍스트 기반 Power BI 프로젝트)를 에이전트가 직접 만들고 고치게 한다.
- 기능 동작보다 **디자인 품질**(레이아웃, 색, 타이포, 정보 위계, 페이지 흐름)을 핵심 가치로 둔다.
- 서식은 테마에, 판단은 에이전트에, 반복 작업은 스크립트에 맡겨 **토큰을 줄인다**.
- 사용한 프롬프트, 설정, 결과 스크린샷을 함께 남겨 **재현 가능하게** 한다.

## 2. 작업 환경 (2026-09-13 기준)

| 항목 | 내용 |
|---|---|
| OS / 에디터 | Windows 10 Pro, VS Code + Claude Code |
| Power BI Desktop | 2.157.879.0 (Microsoft Store판, 자동 업데이트) |
| Python / Node.js | 3.11.9 / 24.19.0 (포터블 설치) |
| git / gh | 2.47.1 / 2.98.0 |
| MCP | Power BI Modeling MCP, Notion MCP (`.mcp.json`) |

**문서 원칙**: PBIP·PBIR·TMDL·DAX 같은 전문 용어는 처음 나올 때 한 줄로 풀이한다.
새 도구나 명령은 "무엇을 왜 하는지"를 먼저 쓴다.

## 3. 핵심 용어 한 줄 풀이

| 용어 | 뜻 |
|---|---|
| PBIX | 기존 Power BI 파일. 하나의 바이너리라 AI가 직접 읽고 쓸 수 없다 |
| **PBIP** | 리포트를 폴더와 텍스트 파일로 저장하는 형식. git으로 변경 이력 관리, AI 직접 편집 가능 |
| **PBIR** | PBIP 안의 리포트(화면) 형식. 페이지·비주얼마다 JSON 파일 하나 (`visual.json`) |
| **TMDL** | 시맨틱 모델(테이블·관계·측정값)을 사람이 읽을 수 있는 텍스트로 쓴 형식 |
| 시맨틱 모델 | 리포트가 참조하는 데이터 모델. 테이블, 관계, DAX 측정값 |
| 테마 JSON | 색 팔레트·글꼴·비주얼 기본 서식을 한 파일로 정의. 디자인 일관성과 토큰 절약의 핵심 |
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

### 4-2. 커뮤니티

| 저장소 | 특징 | ★ / 라이선스 |
|---|---|---|
| [data-goblin/power-bi-agentic-development](https://github.com/data-goblin/power-bi-agentic-development) | Claude Code 플러그인 마켓플레이스. 디자인 원칙, 테마, 리뷰, 리포트 생성, 커스텀 비주얼 | 910 / **GPL-3.0** |
| [maxanatsko/pbir.tools](https://github.com/maxanatsko/pbir.tools) | `pbir` CLI. 탐색·수정·검증·게시 | 277 / **비상업 라이선스** |
| [MinaSaad1/pbi-cli](https://github.com/MinaSaad1/pbi-cli) | Python CLI + Claude 스킬 13종. MCP 없이 동작 | 453 / MIT |
| [jonathan-pap/powerbi-report-mcp](https://github.com/jonathan-pap/powerbi-report-mcp) | 리포트 레이어 MCP 서버 | 19 / MIT |

전체 조사와 수준 평가는 [research/](research/README.md)와 [docs/progress-log.md](docs/progress-log.md)에 있다.

### 4-3. 결론: 무엇이 이미 있고 무엇이 비어 있나

- **이미 있음**: PBIR/TMDL 파일 작성, 모델링 MCP, 검증, Desktop 리로드·스크린샷 → **뼈대는 새로 만들지 않는다.**
- **비어 있음** (이 저장소가 채울 부분):
  1. 실제로 **예쁜 결과물을 재현 가능하게 보여 주는 갤러리** (프롬프트 → 스크린샷, 전·후 비교)
  2. 바로 쓸 수 있는 **디자인 시스템**: 원칙, 테마 JSON, 페이지 레이아웃 템플릿, 여러 페이지 흐름
  3. **스크린샷 기반 디자인 리뷰 루프**의 채점 기준
  4. **토큰 비용**을 숫자로 재고 줄이는 방법
  5. 한국어 문서, 한국어 폰트·숫자 표기(억/만 단위) 대응

**라이선스 주의**: data-goblin(GPL-3.0) 코드를 이 저장소에 **복사하면** 이 저장소도 GPL이 된다.
설치해서 쓰거나 읽고 배우는 것은 괜찮다. pbir CLI는 비상업 라이선스다.
이 저장소는 MIT로 두고, 외부 스킬은 복사하지 말고 설치 방법만 문서화한다.

---

## 5. 작업 흐름

| 단계 | 내용 | 산출물 |
|---|---|---|
| 0 | 환경 세팅 | `docs/00_setup.md` |
| 1 | 데이터 준비 | `examples/_data/` |
| 2 | 시맨틱 모델 (TMDL, DAX 검증) | `*.SemanticModel/`, `tmdl/` |
| 3 | 디자인: 원칙 → HTML 시안 → 채점 | `design-system/` |
| 4 | 리포트 작성: 테마 적용, 페이지·비주얼 (PBIR) | `*.Report/` |
| 5 | 검증: 구조 검증 + 전 페이지 스크린샷 | `screenshots/` |
| 6 | 디자인 리뷰 루프: 채점표로 평가 → 수정 → 5단계 반복 | 리뷰 기록 |
| 7 | 정리: 진행 기록, README, 커밋·push, 노션 일지 | 갤러리 항목 |

**작업 규칙**
- 큰 방향 결정만 사용자에게 묻고, 나머지는 진행하면서 `docs/progress-log.md`에 결정과 이유를 남긴다.
- **스크린샷 없이 "완성" 선언 금지.** JSON이 유효해도 화면이 깨질 수 있다. 눈으로 본 것만 믿는다.
- 에이전트가 PBIR을 고치기 전에 **베이스라인을 커밋**한다 (되돌릴 수 있게).
- **PBIR 파일이 원본이다.** Desktop에서 손으로 고친 게 있으면 먼저 저장하게 한 뒤 작업한다.
- 곧 폐지될 비주얼(Q&A, Bing 지도, 채워진 지도)은 쓰지 않는다. 구형 `card` 대신 `cardVisual`.
- 각 예제에 **실제로 입력한 자연어 프롬프트를 원문 그대로** `prompts.md`에 남긴다. 손으로 고친 부분은 반드시 표시한다.
- 서식은 비주얼마다 따로 넣지 말고 **테마 JSON에서 한 번에** 정의한다.
- 원본 파일을 에이전트가 통째로 읽지 않는다. 스크립트로 요약해서 필요한 부분만 본다.

## 6. 디렉토리 구조

```
powerbi-autopilot/
├── README.md                  # 소개, 결과, 빠른 시작
├── CLAUDE.md                  # 이 파일 — 에이전트 운영 지침
├── LICENSE                    # MIT
├── .mcp.json                  # MCP 서버 설정 (비밀값 없음)
├── docs/                      # 세팅, 비교 규칙, 진행 기록
├── design-system/
│   ├── principles.md          # 디자인 원칙 (근거 포함)
│   ├── review-rubric.md       # 디자인 리뷰 채점표
│   ├── prototypes/            # HTML 시안과 캡처
│   ├── themes/                # 테마 JSON 프리셋
│   └── layouts/               # 페이지 유형별 레이아웃 템플릿
│   ├── i18n/locales.json      # 언어 등록부 (기본 영어)
│   └── literature.md          # 논문·자료 → 디자인 규칙
├── templates/                 # 용도별 파일럿 4종 + 공용 측정값(언어별)·용어집 + catalog.json
├── research/                  # 공개 리포트 수집·분석 스크립트와 결과
├── tools/                     # 생성기, new_report, 테마·레이아웃 빌드, 공유 이미지, 토큰 측정
├── .claude/skills/new-report/ # 새 리포트: 용도·테마·언어를 묻고 파일럿으로 시작
└── examples/
    ├── _data/                 # 공용 가상 데이터 (한·영)
    └── <예제명>/              # prompts.md, 모델, 리포트, 스크린샷
```

**새 리포트는 파일럿에서 시작한다.** 용도·테마·언어를 물은 뒤 `tools/new_report.py`로 파일럿 명세를 복사하고,
대상 모델에 없는 필드와 문장만 고친다. 파일럿의 생성 결과·테마 JSON·TMDL을 통째로 읽지 않는다.

## 7. Git 규칙

- 원격 저장소: GitHub `Haweee47/powerbi-autopilot` (공개).
- **작업 단위가 끝날 때마다 커밋하고 push한다** (2026-09-13 사용자 승인).
- push 전에 추적 파일에 로컬 경로·사용자명·개인정보·회사 정보가 없는지 검사한다.
- 커밋 메시지: Conventional Commits (`feat:` `fix:` `docs:` `refactor:` `chore:`)
- `.gitignore`: `**/.pbi/localSettings.json`, `**/.pbi/cache.abf`, `research/collected/`, 자격 증명 파일
- 개인·회사 데이터, 인증 토큰은 절대 커밋하지 않는다. 예제 데이터는 공개 데이터나 가상 데이터만 쓴다.

## 8. 기록

- 작업 단위가 끝나면 `docs/progress-log.md`에 날짜별로 남긴다: 한 일 / 결정과 이유 / 숫자로 본 결과 / 틀린 가설과 실패.
- 같은 내용을 노션 일지(Notion MCP)에 올린다.
- 공개 문서(README, 진행 기록, 노션)는 작성자 본인의 1인칭 목소리로, 구체적인 숫자와 함께 쓴다.
- 이전 직장은 회사명 없이 경험으로만 언급한다.
- LinkedIn 글은 요청할 때만 쓴다. 전·후 스크린샷 비교를 중심으로 한다.

## 9. 다음 할 일

- [x] 환경 세팅, 가상 데이터, 예제 03 (Modeling MCP)
- [x] 공개 리포트 1,700여 개 분석 → 디자인 원칙·채점표·HTML 시안
- [x] 여러 페이지 시안 v2, 테마 JSON + 레이아웃 템플릿, 명세 → PBIR 생성기
- [x] 용도별 파일럿 4종 · 테마 3종 · 다국어(기본 영어) · 논문 기반 규칙
- [ ] GitHub push (`gh auth login` 필요), 노션 업로드 (Notion MCP 연결 필요)
- [ ] 표 안의 미니 추이선(SVG 측정값), 실데이터(Presto·Redshift) 흐름
- [ ] 예제 01·02 (새 세션에서 토큰 측정)
