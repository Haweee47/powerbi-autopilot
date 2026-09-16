# Themes

`autopilot-<preset>.json`, seven presets. Don't edit them by hand: change [the design tokens](../tokens.json) and rebuild.

```bash
python tools/build_themes.py      # every preset + design-system/tokens.css, checked against the official theme schema 2.157
```

## A preset is a palette plus a card shape

```
tokens.json ── themes.<preset>.color + categorical ─┐
            ── styles.<soft|bold|flat> ─────────────┼─→ autopilot-<preset>.json   (Power BI)
            ── font · type · space · shadow ────────┘   tokens.css                (HTML prototypes)
```

| Style | Corners | Border | Shadow | Used by |
|---|---|---|---|---|
| soft | 12 px | hairline | barely visible | Navy, Paper, Midnight, Coast |
| bold | 16 px | card-colored (it only rounds the corners) | deeper | Aurora |
| flat | 2 px | hairline | none | Ledger, Contrast |

Layout, fonts and type sizes are shared, so a spec renders in any preset without changes, and the generated visual files stay the same size.

**Adding a preset:** copy a theme block in `tokens.json`, pick a style, run the palette check below, add the preset to
`templates/catalog.json` (with a `group`), rebuild, and capture a pilot with `tools/render_check.ps1 -Theme <preset>`.

**From a brand color:** `tools/brand_theme.py --id <id> --accent "#RRGGBB" --base <preset>` writes the preset into the tokens and the catalog.
Brands with a hue of 165–330° (blue, teal, violet) become the data accent; other hues only tint the rail and selections, so red keeps meaning
"below target" and no red–green pair appears in the data. Text on the brand color is darkened or lightened to at least 4.5:1.

**Series colors.** The first color is the accent (this year), the second is gray on purpose (last year), and the rest were ordered so that
neighbors stay apart for color-blind viewers. Check a palette with the dataviz validator
(`node validate_palette.js "<hex,…>" --mode light`): every check should pass except the chroma floor on the gray.
Contrast uses a colorblind-safe set (Okabe–Ito hues).

## Why tokens

Colors, type and spacing written separately into themes, HTML prototypes and docs always drift apart, so there is one source.
The bigger reason is tokens of the other kind: in the PBIR reports I collected, 67% of `visual.json` bytes were formatting, mostly
repeated per visual. With formatting in the theme, a visual file keeps only its position, fields and title.

The notes below (Korean) record why each formatting choice was made.

## 테마에 넣은 것

| 영역 | 결정 | 근거 |
|---|---|---|
| 범주 색 순서 | 1번 강조 파랑, **2번 회색**, 3~8번은 색각이상 검증을 통과한 순서 | 두 계열 차트(올해·작년)가 테마만으로 "실적 파랑, 전년 회색"이 된다 (IBCS) |
| 좋음·나쁨 | 파랑 / 빨강, 중립은 회색 | 한국 증시의 "빨강 = 상승"과 헷갈리지 않게 증감에는 늘 ▲▼를 함께 쓴다 |
| 글자 | 9 · 10 · 12 · 16 · 24pt, Segoe UI → 맑은 고딕 | 5단계 원칙. Segoe UI에는 한글 글자가 없다 |
| 카드(컨테이너) | 흰 배경, 모서리 8px, 테두리·그림자 없음, 안쪽 여백 16 | 카드와 같은 색의 테두리로 모서리만 둥글게 한다 |
| 격자선 | 실선 1px, 연한 회색 | 기본 테마의 점선은 "예측·기준선"으로 읽힌다 |
| 선 차트 | 2px 직선, 면 채우기·표식 없음, 범례 위 | 곡선 보간은 굴곡을 가린다 |
| 막대 | 값 축 숨기고 막대 끝 레이블, 막대 사이 여백 40% | 얇은 막대, 숫자는 레이블로 |
| 표 | 가로 줄만, 줄무늬 없음, 머리글은 흐린 글자 | 줄무늬 설정은 `tableEx`·`pivotTable`에만 (`*`에 두면 다른 비주얼까지 번진다) |
| 페이지 선택기 | 선택된 탭만 흰색, 나머지는 페이지 바탕색 | 시안 v2 상단 탭 |
| 버튼 슬라이서 | 회색 틀 안에서 선택된 값만 흰색 | 시안 v2의 기간·채널 버튼 |
| 필터 창 | 배경·글자·테두리를 직접 지정 | 필터 창은 구조 색을 따르지 않는다 |

어두운 테마는 **구조 색 7종을 한꺼번에** 바꿨다. 배경만 어둡게 하면 글자가 사라진다.

## 발견한 것

- **속성 이름과 허용값은 반드시 도구로 확인한다.**
  - 선 종류를 처음에 `straight`로 쓰려 했는데, CLI로 확인하니 허용값은 `linear | smooth | step`이었다. 기억대로 썼다면 설정이 조용히 무시됐을 것이다.
  - 범례 위치도 `TopLeft`가 아니라 `Top`이다.
- **같은 "선택됨"도 표기가 다르다.** 버튼 슬라이서의 선택 상태를 PBIR(CLI 메타데이터)은 `selected`로, 테마 스키마는 `selection:selected`로 쓴다. 페이지 선택기는 테마에서도 `selected`다.
  스키마 검증이 이 차이를 잡았다.
- **아직 화면으로 확인하지 못한 것**: 버튼 슬라이서의 상태별 배경. 스키마는 통과했지만 Desktop 렌더링은 PBIR 생성기 단계에서 캡처로 확인한다.
