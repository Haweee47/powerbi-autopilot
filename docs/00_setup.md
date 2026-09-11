# 0단계: 환경 세팅

이 저장소는 **같은 데이터, 같은 요청문**으로 세 가지 도구가 각각 어떤 Power BI 리포트를
만드는지 비교한다. 이 문서는 그 전에 무엇을 왜 설치했는지 정리한다. (확인일 2026-09-11)

## 비교 대상 저장소 (커밋 고정)

도구가 바뀌면 결과도 바뀌므로, 사용한 시점의 커밋을 기록한다.

| 예제 | 저장소 | 커밋 | 라이선스 |
|---|---|---|---|
| 01 | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) `powerbi-authoring` 플러그인 | `24cc0d2` (2026-09-10) | MIT |
| 02 | [data-goblin/power-bi-agentic-development](https://github.com/data-goblin/power-bi-agentic-development) `reports` + `pbip` + `semantic-models` 플러그인 | `f8495e7` (2026-08-08) | GPL-3.0 |
| 03 | [microsoft/powerbi-modeling-mcp](https://github.com/microsoft/powerbi-modeling-mcp) | `31f2881` (2026-08-19) | EULA |

**격리 원칙**: 세 저장소를 Claude Code 플러그인으로 동시에 설치하지 않았다.
동시에 설치하면 한 예제를 만드는 동안 다른 저장소의 스킬이 자동으로 끼어들 수 있기 때문이다.
대신 각 저장소를 위 커밋으로 clone해 두고, 예제마다 해당 저장소의 스킬 문서만 읽고 따랐다.
이 저장소에는 외부 스킬 코드를 **복사하지 않는다** (GPL 전파 방지).

## 설치한 도구

| 도구 | 버전 | 무엇 / 왜 | 누가 요구하나 |
|---|---|---|---|
| Node.js | 24.19.0 (LTS) | 아래 npm 도구를 실행하는 런타임 | 01, 03 |
| `powerbi-report-author` | 0.1.4 | PBIR 비주얼 역할·서식 속성 조회, PBIR 구조 검증 | 01 |
| `powerbi-desktop` | 0.1.2 | 실행 중인 Desktop에 붙어 리로드·스크린샷 (Desktop Bridge) | 01 |
| Power BI Modeling MCP | 0.5.0-beta.13 | 시맨틱 모델(테이블·관계·측정값)을 AI가 직접 조작 | 01, 03 |
| `pbir` (pbir-cli) | 0.9.32 | 리포트 생성·비주얼 추가·서식·검증을 모두 명령으로 수행 | 02 |

### Node.js — 관리자 권한 없이 설치

`winget install OpenJS.NodeJS.LTS`는 관리자 권한(UAC) 창이 필요하다. 이번엔 창이 취소되어
실패했다(종료 코드 1602). 그래서 관리자 권한이 필요 없는 **포터블 zip**을 받아 사용자 폴더에
풀고 사용자 PATH에 추가했다.

```powershell
$ver = "v24.19.0"; $dest = "$env:LOCALAPPDATA\Programs"
Invoke-WebRequest "https://nodejs.org/dist/$ver/node-$ver-win-x64.zip" -OutFile node.zip
# SHASUMS256.txt와 해시를 대조한 뒤 압축 해제
Expand-Archive node.zip -DestinationPath $dest
[Environment]::SetEnvironmentVariable("Path", "$dest\node-$ver-win-x64;" + [Environment]::GetEnvironmentVariable("Path","User"), "User")
```

> PATH를 바꾼 뒤에는 VS Code를 다시 열어야 새 터미널에서 `node`가 잡힌다.

### 01용 CLI

```powershell
npm install -g @microsoft/powerbi-report-authoring-cli@latest @microsoft/powerbi-desktop-bridge-cli@latest
```

### 02용 CLI

```powershell
pip install pbir-cli==0.9.32
```

> `pbir`는 [maxanatsko/pbir.tools](https://github.com/maxanatsko/pbir.tools)의 도구로 **비상업 라이선스**다.
> data-goblin의 리포트 스킬은 "리포트 JSON을 손으로 쓰지 말고 반드시 `pbir`로 바꿔라"를 원칙으로 한다.

### Modeling MCP 등록

저장소 루트의 [`.mcp.json`](../.mcp.json)에 등록했다. VS Code 확장이 띄운 Claude Code는 새 PATH를
모르므로 `npx.cmd`를 절대 경로로 적었다. 다른 PC에서는 이 경로를 자기 Node 위치로 바꾼다.
등록 후 Claude Code 세션을 다시 시작하고, MCP 서버 사용을 승인해야 도구가 나타난다.

## Power BI Desktop 설정 (사람이 직접)

`파일 > 옵션 및 설정 > 옵션 > 미리 보기 기능`에서 아래를 켜고 Desktop을 다시 시작한다.

- [ ] Power BI 프로젝트(.pbip) 저장 옵션
- [ ] PBIR 형식으로 리포트 저장
- [ ] TMDL 형식으로 시맨틱 모델 저장
- [ ] **Enable external tool access to Power BI Desktop through secure local APIs** (Desktop Bridge — 리로드·스크린샷에 필요)

## 최종 산출물: PBIX

세 예제 모두 PBIP(텍스트 폴더)로 만든 뒤, Desktop에서 데이터를 새로 고치고
`파일 > 다른 이름으로 저장 > .pbix`로 저장한다. 가져오기(Import) 모델의 데이터는 Desktop 엔진만
쓸 수 있는 바이너리라서, 파일 변환 도구보다 Desktop 저장이 확실하다.
