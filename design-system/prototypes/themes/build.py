"""열 가지 대시보드 구성 시안을 HTML로 만든다.

왜: 테마 10종을 만들어 놓고 보니 전부 "왼쪽 레일 + 흰 카드"였다. 바뀌는 건 색·모서리·글꼴뿐이라
나란히 놓으면 같은 리포트로 보인다. 색은 테마의 문제지만 **닮아 보이는 원인은 구성**이다.

그래서 색이 아니라 배치·타이포·정보 구조가 서로 다른 열 가지를 먼저 HTML로 그린다.
Power BI로 옮기기 전에 브라우저에서 빠르게 비교하고 고르기 위한 시안이다.

숫자는 전부 예제 03 모델의 실제 값이다(2026년 1~8월). 시안마다 같은 숫자를 쓰므로
달라 보이는 것은 오직 디자인이다.

    python design-system/prototypes/themes/build.py
    # → 01-*.html … 10-*.html, index.html
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

# ── 숫자: examples/03-modeling-mcp 모델의 DAX 검증값 ──────────────────────────────────────────────
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
SALES = [146.1, 78.2, 100.0, 90.0, 123.2, 98.8, 104.0, 101.5]   # 2026, 백만 원
PY = [128.4, 77.2, 109.9, 92.6, 116.3, 105.4, 102.1, 97.6]      # 2025
TARGET = [136.0, 82.0, 117.0, 98.0, 122.0, 112.0, 109.0, 103.0]
TOTAL, TOTAL_PY, TOTAL_TGT = 841.8, 829.5, 879.0
KPI = [("Sales", "841.8M", "+1.5%", 1), ("Profit", "338.8M", "+3.1%", 1),
       ("Attainment", "95.8%", "-37.2M", -1), ("Avg order", "127.2K", "-5.3%", -1)]
CATS = [("Food", 14.8), ("Beauty", 7.4), ("Home", 2.3), ("Fashion", -16.8), ("Electronics", -44.9)]
REGIONS = [("Capital Area", 345.2), ("Online", 214.8), ("Yeongnam", 133.1), ("Chungcheong", 61.9),
           ("Honam", 61.2), ("Gangwon", 13.6), ("Jeju", 12.2)]
STORES = [("Ilsan", "23.5M", -38.6), ("Jeju", "12.2M", -29.7), ("Ulsan", "21.2M", -24.9)]
LEDE = "Target attainment 95.8%, up 1.5% on last year. Electronics is 44.9M behind and carries the whole gap."
ASOF = "Data as of 2026-08-31 · 2026 Jan–Aug · all channels"


def T(s: str, **kw: str) -> str:
    for k, v in kw.items():
        s = s.replace("{{%s}}" % k, str(v))
    return s


# ── 차트 조각: 시안마다 색은 CSS 변수로 받고, 모양만 여기서 그린다 ────────────────────────────────
def line(w, h, series, pad=(8, 8, 18, 8), labels=None, fs=9):
    """series: [(값목록, css클래스, 'line'|'dash'|'area')]"""
    l, r, b, t = pad
    lo = min(min(v) for v, *_ in series) * 0.88
    hi = max(max(v) for v, *_ in series) * 1.06
    px = lambda i, n: l + i * (w - l - r) / max(n - 1, 1)
    py = lambda v: t + (hi - v) * (h - t - b) / (hi - lo)
    out = []
    for vals, cls, kind in series:
        pts = " ".join(f"{px(i, len(vals)):.1f},{py(v):.1f}" for i, v in enumerate(vals))
        if kind == "area":
            out.append(f'<polygon class="{cls}" points="{px(0, len(vals)):.1f},{h - b:.1f} {pts} '
                       f'{px(len(vals) - 1, len(vals)):.1f},{h - b:.1f}"/>')
        else:
            out.append(f'<polyline class="{cls}" points="{pts}"/>')
    if labels:
        for i, m in enumerate(labels):
            out.append(f'<text class="ax" x="{px(i, len(labels)):.1f}" y="{h - 4}" font-size="{fs}" '
                       f'text-anchor="middle">{m}</text>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}">{"".join(out)}</svg>'


def diverge(w, h, rows, fs=10, lw=None):
    """0을 기준으로 좌우로 뻗는 막대. 목표 대비처럼 부호가 뜻을 갖는 값에 쓴다."""
    lw = lw or max(len(n) for n, _ in rows) * fs * 0.56 + 12   # 가장 긴 이름이 들어갈 만큼
    vw = max(len(f"{v:+.1f}M") for _, v in rows) * fs * 0.6 + 10   # 값 글자 칸, 양쪽에 하나씩
    mx = max(abs(v) for _, v in rows) * 1.12
    span = w - lw - 2 * vw
    zero = lw + vw + span / 2
    rh = (h - 4) / len(rows)
    out = []
    for i, (name, v) in enumerate(rows):
        y = 2 + i * rh
        bw = abs(v) / mx * span / 2
        x = zero if v >= 0 else zero - bw
        cls = "pos" if v >= 0 else "neg"
        out.append(f'<text class="lb" x="{lw - 8}" y="{y + rh / 2 + 3.5}" font-size="{fs}" text-anchor="end">{name}</text>'
                   f'<rect class="{cls}" x="{x:.1f}" y="{y + rh * .22:.1f}" width="{bw:.1f}" height="{rh * .56:.1f}"/>'
                   f'<text class="vl {cls}" x="{(x + bw + 5) if v >= 0 else (x - 5):.1f}" y="{y + rh / 2 + 3.5}" '
                   f'font-size="{fs}" text-anchor="{"start" if v >= 0 else "end"}">{v:+.1f}M</text>')
    out.append(f'<line class="zero" x1="{zero}" y1="0" x2="{zero}" y2="{h}"/>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}">{"".join(out)}</svg>'


def hbars(w, h, rows, fs=10, lw=None, unit="M"):
    lw = lw or max(len(n) for n, _ in rows) * fs * 0.56 + 12
    vw = max(len(f"{v:.1f}{unit}") for _, v in rows) * fs * 0.6 + 10
    mx = max(v for _, v in rows) * 1.06
    rh = (h - 2) / len(rows)
    out = []
    for i, (name, v) in enumerate(rows):
        y = 1 + i * rh
        bw = v / mx * (w - lw - vw)
        out.append(f'<text class="lb" x="{lw - 8}" y="{y + rh / 2 + 3.5}" font-size="{fs}" text-anchor="end">{name}</text>'
                   f'<rect class="bar" x="{lw}" y="{y + rh * .2:.1f}" width="{bw:.1f}" height="{rh * .6:.1f}"/>'
                   f'<text class="vl" x="{lw + bw + 5:.1f}" y="{y + rh / 2 + 3.5}" font-size="{fs}">{v:.1f}{unit}</text>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}">{"".join(out)}</svg>'


def spark(w, h, vals, cls="sp"):
    lo, hi = min(vals) * .9, max(vals) * 1.05
    pts = " ".join(f"{i * w / (len(vals) - 1):.1f},{(hi - v) * h / (hi - lo):.1f}" for i, v in enumerate(vals))
    last = f"{w},{(hi - vals[-1]) * h / (hi - lo):.1f}"
    return (f'<svg viewBox="0 0 {w} {h + 4}" width="100%" height="{h + 4}">'
            f'<polyline class="{cls}" points="{pts}"/>'
            f'<circle class="dot" cx="{last.split(",")[0]}" cy="{last.split(",")[1]}" r="2.5"/></svg>')


def cols(w, h, vals, tgt, fs=9):
    """실적 기둥 + 목표 눈금. 막대 길이 비교가 핵심인 구성에 쓴다."""
    hi = max(max(vals), max(tgt)) * 1.1
    bw = (w - 8) / len(vals)
    out = []
    for i, (v, t) in enumerate(zip(vals, tgt)):
        x = 4 + i * bw
        bh, th = v / hi * (h - 16), t / hi * (h - 16)
        out.append(f'<rect class="col" x="{x + bw * .22:.1f}" y="{h - 16 - bh:.1f}" width="{bw * .56:.1f}" height="{bh:.1f}"/>'
                   f'<line class="tgt" x1="{x + bw * .12:.1f}" y1="{h - 16 - th:.1f}" x2="{x + bw * .88:.1f}" y2="{h - 16 - th:.1f}"/>'
                   f'<text class="ax" x="{x + bw / 2:.1f}" y="{h - 4}" font-size="{fs}" text-anchor="middle">{MONTHS[i]}</text>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}">{"".join(out)}</svg>'


def store_rows(cls_neg="neg"):
    return "".join(f'<tr><td>{n}</td><td class="num">{s}</td><td class="num {cls_neg}">{d:.1f}%</td></tr>'
                   for n, s, d in STORES)


# ── 시안 ─────────────────────────────────────────────────────────────────────────────────────────
DESIGNS = []


def design(num, slug, name, idea, font_link, css, body):
    DESIGNS.append(dict(num=num, slug=slug, name=name, idea=idea, font=font_link, css=css, body=body))


# 1 ── 벤토: 레일 없음. 크기가 다른 타일이 정보 위계를 대신한다 -------------------------------------
design(1, "bento", "Bento", "타일 크기로 위계를 만든다. 레일도 카드 테두리도 없다.",
       '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700&family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet">',
       """
:root{--bg:#E8EAEF;--tile:#FFF;--ink:#101521;--ink2:#5B6474;--accent:#3B5BDB;--neg:#D6336C;--pos:#2B8A3E;--line:#E2E5EB}
.page{background:var(--bg);font-family:'IBM Plex Sans',system-ui,sans-serif;color:var(--ink);padding:22px 24px;
  display:grid;grid-template-rows:auto 1fr;gap:16px}
.top{display:flex;align-items:baseline;justify-content:space-between}
h1{font-family:Outfit,sans-serif;font-size:25px;font-weight:700;margin:0;letter-spacing:-.4px}
.lede{font-family:Outfit;font-size:13px;color:var(--ink2);margin-top:3px}
.chips{display:flex;gap:6px}
.chip{background:var(--tile);border-radius:999px;padding:5px 13px;font-size:11px;color:var(--ink2)}
.chip.on{background:var(--ink);color:#fff}
.grid{display:grid;grid-template-columns:repeat(6,1fr);grid-template-rows:repeat(3,1fr);gap:14px}
.t{background:var(--tile);border-radius:18px;padding:16px 18px;display:flex;flex-direction:column;min-width:0}
.t h3{font-size:11px;font-weight:600;color:var(--ink2);margin:0 0 2px;letter-spacing:.3px}
.big{grid-column:span 2;grid-row:span 2;justify-content:center}
.big .v{font-family:Outfit;font-size:54px;font-weight:700;letter-spacing:-2px;line-height:1}
.big .d{font-size:13px;color:var(--pos);margin-top:8px}
.big svg{margin-top:14px}
.sm svg{margin-top:auto}
.wide{grid-column:span 4}
.half{grid-column:span 3}
.sm{grid-column:span 2}
.sm .v{font-family:Outfit;font-size:28px;font-weight:700;letter-spacing:-.8px}
.sm .d{font-size:11px;color:var(--ink2)}
.sm .d.bad{color:var(--neg)}
svg .ln{fill:none;stroke:var(--accent);stroke-width:2.4}
svg .ln2{fill:none;stroke:var(--accent);stroke-width:2;opacity:.75}
svg .dot{fill:var(--accent)}
svg .pyl{fill:none;stroke:#B6BCC8;stroke-width:1.6}
svg .ar{fill:rgba(59,91,219,.1)}
svg .ax,svg .lb{fill:var(--ink2)}svg .vl{fill:var(--ink2)}
svg .pos{fill:var(--accent)}svg .neg{fill:var(--neg)}svg .vl.neg{fill:var(--neg)}svg .vl.pos{fill:var(--accent)}
svg .zero{stroke:var(--line)}
""",
       T("""
<div class="top"><div><h1>Sales performance</h1><div class="lede">{{LEDE}}</div></div>
  <div class="chips"><span class="chip">2024</span><span class="chip">2025</span><span class="chip on">2026</span>
  <span class="chip">All channels</span></div></div>
<div class="grid">
  <div class="t big"><h3>SALES</h3><div class="v">841.8M</div><div class="d">▲ 1.5% vs last year</div>{{SP}}</div>
  <div class="t wide"><h3>MONTHLY · THIS YEAR, LAST YEAR</h3>{{TREND}}</div>
  <div class="t sm"><h3>PROFIT</h3><div class="v">338.8M</div><div class="d">▲ 3.1%</div>{{SP2}}</div>
  <div class="t sm"><h3>ATTAINMENT</h3><div class="v">95.8%</div><div class="d bad">37.2M short</div>{{SP3}}</div>
  <div class="t half"><h3>VS TARGET BY CATEGORY</h3>{{CATS}}</div>
  <div class="t half"><h3>BY REGION</h3>{{REG}}</div>
</div>""",
         LEDE=LEDE,
         TREND=line(560, 140, [(PY, "pyl", "line"), (SALES, "ar", "area"), (SALES, "ln", "line")], labels=MONTHS),
         SP=spark(220, 52, SALES, "ln2"), SP2=spark(180, 34, [x * .4 for x in SALES], "ln2"),
         SP3=spark(180, 34, [s_ / t * 100 for s_, t in zip(SALES, TARGET)], "ln2"),
         CATS=diverge(400, 126, CATS), REG=hbars(400, 126, REGIONS)))

# 2 ── 터미널: 어둡고 조밀하다. 숫자를 계기판처럼 읽는다 ---------------------------------------------
design(2, "terminal", "Terminal", "관제 화면. 등폭 숫자, 1px 격자, 카드 없음.",
       '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Barlow+Condensed:wght@500;600&display=swap" rel="stylesheet">',
       """
:root{--bg:#070B0C;--panel:#0D1416;--ink:#C9D6D8;--ink2:#6B8084;--accent:#5BE3A8;--neg:#FF6B6B;--grid:#172124}
.page{background:var(--bg);color:var(--ink);font-family:'JetBrains Mono',monospace;font-size:11px;
  display:grid;grid-template-rows:auto auto 1fr;padding:0}
.bar{display:flex;gap:0;border-bottom:1px solid var(--grid)}
.bar div{padding:8px 14px;border-right:1px solid var(--grid);font-family:'Barlow Condensed';font-size:14px;
  letter-spacing:.6px;text-transform:uppercase;color:var(--ink2)}
.bar div.on{color:var(--accent)}
.bar .sp{flex:1;border-right:none}
.strip{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid var(--grid)}
.strip div{padding:12px 16px;border-right:1px solid var(--grid)}
.strip .k{color:var(--ink2);font-size:10px;letter-spacing:.8px}
.strip .v{font-size:26px;font-weight:700;letter-spacing:-1px;margin-top:2px}
.strip .d{font-size:10px;color:var(--accent)}
.strip .d.bad{color:var(--neg)}
.body{display:grid;grid-template-columns:1.5fr 1fr;min-height:0}
.body>section{padding:14px 16px;border-right:1px solid var(--grid);min-width:0}
.body>section:last-child{border-right:none}
h3{font-family:'Barlow Condensed';font-size:13px;letter-spacing:1px;text-transform:uppercase;color:var(--ink2);
  margin:0 0 10px;font-weight:600}
table{width:100%;border-collapse:collapse}
td{padding:5px 0;border-bottom:1px solid var(--grid)}
.num{text-align:right;font-variant-numeric:tabular-nums}
.neg{color:var(--neg)}
svg .ln{fill:none;stroke:var(--accent);stroke-width:1.6}
svg .pyl{fill:none;stroke:#2F4145;stroke-width:1.4;stroke-dasharray:3 3}
svg .ax,svg .lb,svg .vl{fill:var(--ink2)}
svg .pos{fill:var(--accent)}svg .neg{fill:var(--neg)}svg .vl.neg{fill:var(--neg)}svg .vl.pos{fill:var(--accent)}
svg .zero{stroke:var(--grid)}
""",
       T("""
<div class="bar"><div class="on">SALES</div><div>CATEGORY</div><div>STORES</div><div class="sp"></div>
  <div>2026 JAN–AUG</div><div>ALL CHANNELS</div></div>
<div class="strip">
  <div><div class="k">SALES</div><div class="v">841.8M</div><div class="d">+1.5% YOY</div></div>
  <div><div class="k">PROFIT</div><div class="v">338.8M</div><div class="d">+3.1% YOY</div></div>
  <div><div class="k">ATTAINMENT</div><div class="v">95.8%</div><div class="d bad">-37.2M VS TARGET</div></div>
  <div><div class="k">AVG ORDER</div><div class="v">127.2K</div><div class="d bad">-5.3% YOY</div></div>
</div>
<div class="body">
  <section><h3>Monthly · actual vs last year</h3>{{TREND}}
    <h3 style="margin-top:14px">Vs target by category</h3>{{CATS}}</section>
  <section><h3>Stores falling behind</h3><table>{{ST}}</table>
    <h3 style="margin-top:16px">By region</h3>{{REG}}</section>
</div>""",
         TREND=line(620, 196, [(PY, "pyl", "line"), (SALES, "ln", "line")], labels=MONTHS),
         CATS=diverge(620, 186, CATS, fs=10), ST=store_rows(), REG=hbars(400, 232, REGIONS, fs=10)))

# 3 ── 장부: 카드도 그림자도 없다. 괘선과 정렬만으로 읽힌다 -----------------------------------------
design(3, "ledger", "Ledger", "인쇄물 규칙. 선과 정렬만 쓰고 면을 쓰지 않는다.",
       '<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;700&display=swap" rel="stylesheet">',
       """
:root{--bg:#FFF;--ink:#16181D;--ink2:#6A6F7A;--rule:#D7DAE0;--rule2:#16181D;--accent:#0B4F6C;--neg:#A4161A}
.page{background:var(--bg);color:var(--ink);font-family:'Libre Franklin',system-ui,sans-serif;padding:26px 32px;
  display:grid;grid-template-rows:auto auto auto 1fr;gap:0}
.hd{display:flex;justify-content:space-between;align-items:flex-end;padding-bottom:8px;border-bottom:2px solid var(--rule2)}
h1{font-size:20px;font-weight:700;margin:0;letter-spacing:-.2px}
.meta{font-size:10.5px;color:var(--ink2);letter-spacing:.3px}
.lede{font-size:13.5px;padding:11px 0;border-bottom:1px solid var(--rule);font-weight:500}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid var(--rule)}
.kpis div{padding:11px 16px 11px 0}
.kpis .k{font-size:10px;letter-spacing:.9px;text-transform:uppercase;color:var(--ink2)}
.kpis .v{font-size:27px;font-weight:700;letter-spacing:-1px;font-variant-numeric:tabular-nums;margin-top:1px}
.kpis .d{font-size:11px;color:var(--ink2)}
.kpis .d.bad{color:var(--neg)}
.cols{display:grid;grid-template-columns:1.25fr 1fr;gap:28px;padding-top:14px;min-height:0}
h3{font-size:10.5px;letter-spacing:1px;text-transform:uppercase;color:var(--ink2);font-weight:600;
  margin:0 0 7px;padding-bottom:4px;border-bottom:1px solid var(--rule)}
table{width:100%;border-collapse:collapse;font-size:12px}
td{padding:6px 0;border-bottom:1px solid var(--rule)}
.num{text-align:right;font-variant-numeric:tabular-nums}
.neg{color:var(--neg)}
svg .col{fill:var(--accent)}
svg .tgt{stroke:var(--ink);stroke-width:1.4}
svg .ax,svg .lb,svg .vl{fill:var(--ink2)}
svg .pos{fill:var(--accent)}svg .neg{fill:var(--neg)}svg .vl.neg{fill:var(--neg)}svg .vl.pos{fill:var(--accent)}
svg .zero{stroke:var(--ink)}
""",
       T("""
<div class="hd"><h1>Sales performance</h1><div class="meta">{{ASOF}}</div></div>
<div class="lede">{{LEDE}}</div>
<div class="kpis">
  <div><div class="k">Sales</div><div class="v">841.8M</div><div class="d">prior year 829.5M · +1.5%</div></div>
  <div><div class="k">Profit</div><div class="v">338.8M</div><div class="d">+3.1%</div></div>
  <div><div class="k">Attainment</div><div class="v">95.8%</div><div class="d bad">target 879.0M · 37.2M short</div></div>
  <div><div class="k">Avg order</div><div class="v">127.2K</div><div class="d bad">-5.3%</div></div>
</div>
<div class="cols">
  <div><h3>Monthly actual against target</h3>{{COLS}}
    <h3 style="margin-top:14px">Variance to target by category</h3>{{CATS}}</div>
  <div><h3>Stores furthest behind</h3><table>{{ST}}</table>
    <h3 style="margin-top:14px">Sales by region</h3>{{REG}}</div>
</div>""",
         ASOF=ASOF, LEDE=LEDE, COLS=cols(520, 128, SALES, TARGET),
         CATS=diverge(520, 112, CATS, fs=10, lw=86), ST=store_rows(), REG=hbars(380, 136, REGIONS)))

# 4 ── 제호: 신문 1면. 쓴 문장이 먼저고 숫자가 받친다 -----------------------------------------------
design(4, "masthead", "Masthead", "읽는 자료. 제호와 리드 문장이 먼저, 숫자가 뒤를 받친다.",
       '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">',
       """
:root{--bg:#F1F2F4;--sheet:#FFF;--ink:#0B0F19;--ink2:#555C6B;--rule:#CBCFD8;--accent:#1F3A8A;--neg:#B42318}
.page{background:var(--bg);color:var(--ink);font-family:'Source Sans 3',system-ui,sans-serif;padding:0}
.sheet{background:var(--sheet);height:100%;padding:24px 30px;display:grid;grid-template-rows:auto auto auto 1fr;gap:0}
.mast{border-bottom:3px double var(--ink);padding-bottom:7px;display:flex;justify-content:space-between;align-items:flex-end}
h1{font-family:'Playfair Display',serif;font-weight:900;font-size:34px;margin:0;letter-spacing:-.6px}
.dateline{font-size:10.5px;letter-spacing:1.4px;text-transform:uppercase;color:var(--ink2)}
.lede{font-family:'Playfair Display',serif;font-size:19px;line-height:1.38;padding:13px 0 12px;
  border-bottom:1px solid var(--rule);max-width:62ch;text-wrap:balance}
.figs{display:flex;gap:0;border-bottom:1px solid var(--rule)}
.figs div{padding:9px 20px 9px 0;margin-right:20px;border-right:1px solid var(--rule)}
.figs div:last-child{border-right:none}
.figs .k{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--ink2)}
.figs .v{font-family:'Playfair Display',serif;font-size:26px;font-weight:700;letter-spacing:-.5px}
.figs .d{font-size:11px;color:var(--ink2)}.figs .d.bad{color:var(--neg)}
.body{display:grid;grid-template-columns:.85fr 1.5fr .95fr;gap:22px;padding-top:13px;min-height:0}
.body>div{min-width:0}
.body>div+div{border-left:1px solid var(--rule);padding-left:22px}
h3{font-size:10px;letter-spacing:1.3px;text-transform:uppercase;color:var(--ink2);margin:0 0 8px;font-weight:600}
p{font-size:12px;line-height:1.5;margin:0 0 9px;color:var(--ink2)}
p b{color:var(--ink)}
table{width:100%;border-collapse:collapse;font-size:11.5px}
td{padding:5px 0;border-bottom:1px solid var(--rule)}
.num{text-align:right;font-variant-numeric:tabular-nums}.neg{color:var(--neg)}
svg .ln{fill:none;stroke:var(--accent);stroke-width:2.2}
svg .pyl{fill:none;stroke:#A9AFBC;stroke-width:1.5}
svg .ar{fill:rgba(31,58,138,.08)}
svg .ax,svg .lb,svg .vl{fill:var(--ink2)}
svg .pos{fill:var(--accent)}svg .neg{fill:var(--neg)}svg .vl.neg{fill:var(--neg)}svg .vl.pos{fill:var(--accent)}
svg .zero{stroke:var(--rule)}
""",
       T("""
<div class="sheet">
<div class="mast"><h1>The Sales Review</h1><div class="dateline">2026 Jan–Aug · All channels</div></div>
<div class="lede">{{LEDE}}</div>
<div class="figs">
  <div><div class="k">Sales</div><div class="v">841.8M</div><div class="d">+1.5%</div></div>
  <div><div class="k">Profit</div><div class="v">338.8M</div><div class="d">+3.1%</div></div>
  <div><div class="k">Attainment</div><div class="v">95.8%</div><div class="d bad">-37.2M</div></div>
  <div><div class="k">Avg order</div><div class="v">127.2K</div><div class="d bad">-5.3%</div></div>
</div>
<div class="body">
  <div><h3>What happened</h3>
    <p>Sales finished the eight months at <b>841.8M</b>, ahead of last year but <b>37.2M short of plan</b>.</p>
    <p>Four of five categories beat their target. <b>Electronics missed by 44.9M</b>, more than the shortfall itself.</p>
    <p>Three stores fell more than a fifth behind last year, led by <b>Ilsan at −38.6%</b>.</p></div>
  <div><h3>Monthly, against last year</h3>{{TREND}}
    <h3 style="margin-top:12px">Variance to target</h3>{{CATS}}</div>
  <div><h3>Stores behind</h3><table>{{ST}}</table>
    <h3 style="margin-top:12px">Region</h3>{{REG}}</div>
</div></div>""",
         LEDE=LEDE,
         TREND=line(420, 124, [(PY, "pyl", "line"), (SALES, "ar", "area"), (SALES, "ln", "line")], labels=MONTHS),
         CATS=diverge(420, 104, CATS, fs=9, lw=74), ST=store_rows(), REG=hbars(250, 128, REGIONS, fs=9, lw=74)))

# 5 ── 전면: 차트가 화면을 채우고 숫자가 그 위에 뜬다 -----------------------------------------------
design(5, "fullbleed", "Full bleed", "차트가 캔버스를 채우고 숫자는 그 위에 올라탄다.",
       '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&display=swap" rel="stylesheet">',
       """
:root{--ink:#F2FBF8;--ink2:#9FC4BC;--accent:#FFD166;--neg:#FF8A7A}
.page{background:linear-gradient(160deg,#05322B 0%,#073F38 55%,#0A5248 100%);color:var(--ink);
  font-family:Archivo,system-ui,sans-serif;position:relative;overflow:hidden}
.chartwrap{position:absolute;inset:92px 0 104px 0}
.chartwrap svg{display:block;width:100%;height:100%}
svg .ar{fill:rgba(255,209,102,.16)}
svg .ln{fill:none;stroke:var(--accent);stroke-width:3}
svg .pyl{fill:none;stroke:rgba(242,251,248,.3);stroke-width:1.6;stroke-dasharray:5 4}
svg .ax{fill:var(--ink2)}
.hd{position:absolute;top:26px;left:30px;right:30px;display:flex;justify-content:space-between;align-items:flex-start}
h1{font-size:27px;font-weight:800;margin:0;letter-spacing:-.6px}
.lede{font-size:13px;color:var(--ink2);margin-top:5px;max-width:52ch}
.legend{font-size:11px;color:var(--ink2);text-align:right;line-height:1.7}
.legend b{color:var(--accent)}
.chips{position:absolute;left:30px;bottom:26px;display:flex;gap:10px}
.c{backdrop-filter:blur(8px);background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);
  border-radius:14px;padding:11px 16px;min-width:116px}
.c .k{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--ink2)}
.c .v{font-size:25px;font-weight:800;letter-spacing:-1px;margin-top:1px}
.c .d{font-size:11px;color:var(--accent)}
.c .d.bad{color:var(--neg)}
.note{position:absolute;right:30px;bottom:34px;font-size:11px;color:var(--ink2);text-align:right;line-height:1.6}
""",
       T("""
<div class="chartwrap">{{TREND}}</div>
<div class="hd"><div><h1>Sales performance</h1><div class="lede">{{LEDE}}</div></div>
  <div class="legend"><b>— 2026</b><br>— — 2025<br>{{ASOF}}</div></div>
<div class="chips">
  <div class="c"><div class="k">Sales</div><div class="v">841.8M</div><div class="d">▲ 1.5%</div></div>
  <div class="c"><div class="k">Profit</div><div class="v">338.8M</div><div class="d">▲ 3.1%</div></div>
  <div class="c"><div class="k">Attainment</div><div class="v">95.8%</div><div class="d bad">37.2M short</div></div>
  <div class="c"><div class="k">Avg order</div><div class="v">127.2K</div><div class="d bad">▼ 5.3%</div></div>
</div>
<div class="note">Electronics −44.9M · Fashion −16.8M<br>Food +14.8M · Beauty +7.4M</div>""",
         LEDE=LEDE, ASOF="2026 Jan–Aug · all channels",
         TREND=line(1280, 524, [(PY, "pyl", "line"), (SALES, "ar", "area"), (SALES, "ln", "line")],
                    pad=(40, 40, 26, 10), labels=MONTHS, fs=13)))

# 6 ── 브리프: 왼쪽은 글, 오른쪽은 그림 -------------------------------------------------------------
design(6, "brief", "Brief", "왼쪽 글이 결론을 말하고 오른쪽 그림이 근거를 댄다.",
       '<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;600&family=Public+Sans:wght@400;600;700&display=swap" rel="stylesheet">',
       """
:root{--bg:#FBFAF7;--sheet:#FFF;--ink:#1B1C19;--ink2:#64665F;--rule:#E3E2DC;--accent:#2D6A4F;--neg:#9B2226}
.page{background:var(--bg);color:var(--ink);font-family:'Public Sans',system-ui,sans-serif;
  display:grid;grid-template-columns:366px 1fr}
.brief{padding:26px 26px 22px;border-right:1px solid var(--rule);display:flex;flex-direction:column}
.eyebrow{font-size:10px;letter-spacing:1.6px;text-transform:uppercase;color:var(--accent);font-weight:700}
h1{font-family:Spectral,serif;font-size:25px;font-weight:600;margin:7px 0 0;letter-spacing:-.3px;line-height:1.15}
.brief p{font-family:Spectral,serif;font-size:13.5px;line-height:1.62;color:var(--ink2);margin:13px 0 0}
.brief p b{color:var(--ink);font-weight:600}
.pull{margin-top:auto;border-top:1px solid var(--rule);padding-top:13px;display:grid;grid-template-columns:1fr 1fr;gap:11px}
.pull .k{font-size:10px;letter-spacing:.9px;text-transform:uppercase;color:var(--ink2)}
.pull .v{font-size:23px;font-weight:700;letter-spacing:-.8px}
.pull .d{font-size:11px;color:var(--accent)}.pull .d.bad{color:var(--neg)}
.vis{padding:26px 28px;display:grid;grid-template-rows:auto 1fr auto;gap:15px;min-width:0}
h3{font-size:10px;letter-spacing:1.3px;text-transform:uppercase;color:var(--ink2);margin:0 0 7px;font-weight:700}
.panel{background:var(--sheet);border:1px solid var(--rule);border-radius:4px;padding:14px 16px;min-width:0}
.two{display:grid;grid-template-columns:1.1fr 1fr;gap:15px;min-height:0}
table{width:100%;border-collapse:collapse;font-size:12px}
td{padding:6px 0;border-bottom:1px solid var(--rule)}
.num{text-align:right;font-variant-numeric:tabular-nums}.neg{color:var(--neg)}
svg .ln{fill:none;stroke:var(--accent);stroke-width:2.2}
svg .pyl{fill:none;stroke:#B9BAB2;stroke-width:1.5}
svg .ar{fill:rgba(45,106,79,.09)}
svg .ax,svg .lb,svg .vl{fill:var(--ink2)}
svg .pos{fill:var(--accent)}svg .neg{fill:var(--neg)}svg .vl.neg{fill:var(--neg)}svg .vl.pos{fill:var(--accent)}
svg .zero{stroke:var(--rule)}svg .bar{fill:var(--accent)}
""",
       T("""
<div class="brief">
  <div class="eyebrow">Monthly review</div>
  <h1>The year is on track, one category is not</h1>
  <p>Sales reached <b>841.8M</b> through August, <b>1.5% ahead</b> of the same months last year.</p>
  <p>Against plan the picture is tighter: <b>95.8% attainment</b>, <b>37.2M short</b>. Four categories beat
     their target; <b>Electronics missed by 44.9M</b> on its own, more than the whole gap.</p>
  <p>Store performance is uneven. <b>Ilsan is down 38.6%</b> on last year, Jeju 29.7%, Ulsan 24.9%.</p>
  <div class="pull">
    <div><div class="k">Sales</div><div class="v">841.8M</div><div class="d">▲ 1.5%</div></div>
    <div><div class="k">Attainment</div><div class="v">95.8%</div><div class="d bad">−37.2M</div></div>
  </div>
</div>
<div class="vis">
  <div class="panel"><h3>Monthly sales against last year</h3>{{TREND}}</div>
  <div class="two">
    <div class="panel"><h3>Variance to target</h3>{{CATS}}</div>
    <div class="panel"><h3>Stores behind</h3><table>{{ST}}</table></div>
  </div>
  <div class="panel"><h3>Sales by region</h3>{{REG}}</div>
</div>""",
         TREND=line(820, 126, [(PY, "pyl", "line"), (SALES, "ar", "area"), (SALES, "ln", "line")], labels=MONTHS),
         CATS=diverge(420, 118, CATS, fs=9, lw=76), ST=store_rows(),
         REG=hbars(820, 96, REGIONS[:5], fs=10, lw=96)))

# 7 ── 관제실: 같은 크기 타일을 훑는다 ---------------------------------------------------------------
design(7, "control", "Control room", "같은 크기 타일 12개. 읽는 게 아니라 훑는 화면.",
       '<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700&family=Barlow+Semi+Condensed:wght@500;600&display=swap" rel="stylesheet">',
       """
:root{--bg:#10141C;--tile:#19202C;--ink:#E6EBF4;--ink2:#7A879E;--accent:#4CC9F0;--neg:#F7577A;--pos:#52E0A3;--line:#242D3C}
.page{background:var(--bg);color:var(--ink);font-family:Barlow,system-ui,sans-serif;padding:16px 18px;
  display:grid;grid-template-rows:auto 1fr;gap:13px}
.top{display:flex;align-items:center;gap:14px}
h1{font-size:17px;font-weight:700;margin:0;letter-spacing:.2px}
.hl{font-family:'Barlow Semi Condensed';font-size:13px;color:var(--ink2);flex:1}
.hl b{color:var(--neg)}
.tag{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--ink2);border:1px solid var(--line);
  border-radius:3px;padding:3px 9px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(3,1fr);gap:11px;min-height:0}
.t{background:var(--tile);border-radius:6px;padding:11px 13px;display:flex;flex-direction:column;
  border-left:3px solid var(--line);min-width:0}
.t.good{border-left-color:var(--pos)}.t.bad{border-left-color:var(--neg)}
.t .k{font-family:'Barlow Semi Condensed';font-size:11px;letter-spacing:.8px;text-transform:uppercase;color:var(--ink2)}
.t .v{font-size:25px;font-weight:700;letter-spacing:-.9px;line-height:1.1;margin-top:1px;font-variant-numeric:tabular-nums}
.t .d{font-size:11px;color:var(--ink2);margin-top:auto}
.t .d.up{color:var(--pos)}.t .d.dn{color:var(--neg)}
.t svg{margin-top:5px}
svg .sp{fill:none;stroke:var(--accent);stroke-width:1.8}
svg .dot{fill:var(--accent)}
.t.bad svg .sp{stroke:var(--neg)}.t.bad svg .dot{fill:var(--neg)}
.t.good svg .sp{stroke:var(--pos)}.t.good svg .dot{fill:var(--pos)}
""",
       "".join(["""
<div class="top"><h1>Sales monitor</h1>
  <div class="hl">Attainment 95.8% · <b>Electronics −44.9M carries the gap</b></div>
  <span class="tag">2026 Jan–Aug</span><span class="tag">All channels</span></div>
<div class="grid">"""] + [
           T('<div class="t {{C}}"><div class="k">{{K}}</div><div class="v">{{V}}</div>{{SP}}'
             '<div class="d {{DC}}">{{D}}</div></div>',
             C=c, K=k, V=v, D=d, DC=dc, SP=spark(240, 58, s))
           for k, v, d, dc, c, s in [
               ("Sales", "841.8M", "▲ 1.5% YoY", "up", "good", SALES),
               ("Profit", "338.8M", "▲ 3.1% YoY", "up", "good", [x * .4 for x in SALES]),
               ("Attainment", "95.8%", "▼ 37.2M vs target", "dn", "bad",
                [s / t * 100 for s, t in zip(SALES, TARGET)]),
               ("Avg order", "127.2K", "▼ 5.3% YoY", "dn", "bad", PY),
               ("Food", "+14.8M", "ahead of target", "up", "good", [1, 1.1, 1.2, 1.15, 1.3, 1.28, 1.4, 1.45]),
               ("Beauty", "+7.4M", "ahead of target", "up", "good", [1, 1.05, 1.02, 1.1, 1.15, 1.12, 1.2, 1.24]),
               ("Home", "+2.3M", "just ahead", "up", "good", [1, .98, 1.02, 1.0, 1.05, 1.03, 1.06, 1.08]),
               ("Fashion", "−16.8M", "behind target", "dn", "bad", [1, .97, .95, .92, .9, .88, .86, .84]),
               ("Electronics", "−44.9M", "furthest behind", "dn", "bad", [1, .94, .9, .85, .8, .76, .72, .68]),
               ("Ilsan store", "23.5M", "▼ 38.6% YoY", "dn", "bad", [1, .9, .82, .75, .7, .66, .63, .61]),
               ("Jeju store", "12.2M", "▼ 29.7% YoY", "dn", "bad", [1, .95, .88, .84, .79, .75, .72, .7]),
               ("Capital Area", "345.2M", "largest region", "up", "good", [1, 1.02, 1.06, 1.05, 1.1, 1.12, 1.16, 1.2]),
           ]] + ["</div>"]))

# 8 ── 포스터: 숫자 하나가 화면을 지배한다 ----------------------------------------------------------
design(8, "poster", "Poster", "숫자 하나가 화면을 지배하고 나머지는 작게 받친다.",
       '<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;600&family=Karla:wght@400;600&display=swap" rel="stylesheet">',
       """
:root{--bg:#FFF;--ink:#0A2342;--ink2:#6D7A8C;--accent:#2CA58D;--neg:#C1272D;--rule:#E6E9EE}
.page{background:var(--bg);color:var(--ink);font-family:Karla,system-ui,sans-serif;
  display:grid;grid-template-columns:1.25fr 1fr;gap:0}
.left{padding:46px 42px;display:flex;flex-direction:column;justify-content:center;border-right:1px solid var(--rule)}
.k{font-size:11px;letter-spacing:2.4px;text-transform:uppercase;color:var(--ink2)}
.huge{font-family:Oswald,sans-serif;font-size:148px;font-weight:600;line-height:.86;letter-spacing:-4px;margin:12px 0 0}
.sub{font-size:16px;margin-top:16px;max-width:34ch;line-height:1.46}
.sub b{color:var(--neg)}
.meter{margin-top:22px;height:9px;background:var(--rule);border-radius:9px;overflow:hidden;max-width:360px}
.meter i{display:block;height:100%;width:95.8%;background:var(--accent)}
.meterlab{display:flex;justify-content:space-between;max-width:360px;margin-top:6px;font-size:11px}
.meterlab span{color:var(--ink2)}
.right{padding:40px 38px;display:flex;flex-direction:column;gap:20px;justify-content:center}
.row{display:flex;align-items:baseline;justify-content:space-between;border-bottom:1px solid var(--rule);padding-bottom:9px}
.row .n{font-size:12px;color:var(--ink2);letter-spacing:.3px}
.row .v{font-family:Oswald;font-size:27px;font-weight:600;letter-spacing:-.5px}
.row .d{font-size:11px;color:var(--accent);margin-left:9px}
.row .d.bad{color:var(--neg)}
.foot{font-size:11px;color:var(--ink2);margin-top:4px}
""",
       T("""
<div class="left">
  <div class="k">Target attainment · 2026 Jan–Aug</div>
  <div class="huge">95.8%</div>
  <div class="sub">841.8M of the 879.0M plan. <b>Electronics is 44.9M behind</b> — more than the whole shortfall.</div>
  <div class="meter"><i></i></div>
  <div class="meterlab"><span>0</span><span>Plan 879.0M</span></div>
</div>
<div class="right">
  <div class="row"><span class="n">Sales</span><span><span class="v">841.8M</span><span class="d">▲1.5%</span></span></div>
  <div class="row"><span class="n">Profit</span><span><span class="v">338.8M</span><span class="d">▲3.1%</span></span></div>
  <div class="row"><span class="n">Average order</span><span><span class="v">127.2K</span><span class="d bad">▼5.3%</span></span></div>
  <div class="row"><span class="n">Weakest store · Ilsan</span><span><span class="v">23.5M</span><span class="d bad">▼38.6%</span></span></div>
  <div class="row"><span class="n">Largest region · Capital</span><span><span class="v">345.2M</span><span class="d">41% of sales</span></span></div>
  <div class="foot">{{ASOF}}</div>
</div>""", ASOF=ASOF))

# 9 ── 분할: 왼쪽은 색 면, 오른쪽은 흰 면 -----------------------------------------------------------
design(9, "split", "Split field", "색 면과 흰 면을 맞붙인다. 결론은 색 면, 근거는 흰 면.",
       '<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">',
       """
:root{--field:#331A63;--fieldink:#F4EEFF;--fieldink2:#B9A6DC;--bg:#FFF;--ink:#1A1A2E;--ink2:#6B6B80;
  --accent:#C4336B;--pos:#2F9E6E;--rule:#E8E6EF}
.page{background:var(--bg);color:var(--ink);font-family:'DM Sans',system-ui,sans-serif;
  display:grid;grid-template-columns:430px 1fr}
.field{background:var(--field);color:var(--fieldink);padding:30px 28px;display:flex;flex-direction:column}
.field .k{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--fieldink2)}
.field h1{font-family:'DM Serif Display',serif;font-size:31px;font-weight:400;margin:9px 0 0;line-height:1.14;
  letter-spacing:-.3px;text-wrap:balance}
.field p{font-size:13px;line-height:1.55;color:var(--fieldink2);margin:13px 0 0}
.field p b{color:var(--fieldink)}
.kpis{margin-top:auto;display:grid;grid-template-columns:1fr 1fr;gap:16px;border-top:1px solid rgba(244,238,255,.17);padding-top:16px}
.kpis .n{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;color:var(--fieldink2)}
.kpis .v{font-family:'DM Serif Display',serif;font-size:31px;letter-spacing:-.5px;margin-top:2px}
.kpis .d{font-size:11px;color:var(--fieldink2)}
.right{padding:28px 30px;display:grid;grid-template-rows:auto auto 1fr;gap:17px;min-width:0}
h3{font-size:10px;letter-spacing:1.4px;text-transform:uppercase;color:var(--ink2);margin:0 0 8px;font-weight:700}
.two{display:grid;grid-template-columns:1fr .85fr;gap:24px;min-height:0}
table{width:100%;border-collapse:collapse;font-size:12px}
td{padding:6px 0;border-bottom:1px solid var(--rule)}
.num{text-align:right;font-variant-numeric:tabular-nums}.neg{color:var(--accent)}
svg .ln{fill:none;stroke:var(--field);stroke-width:2.4}
svg .pyl{fill:none;stroke:#C3BFD0;stroke-width:1.5}
svg .ar{fill:rgba(51,26,99,.08)}
svg .ax,svg .lb,svg .vl{fill:var(--ink2)}
svg .pos{fill:var(--pos)}svg .neg{fill:var(--accent)}
svg .vl.neg{fill:var(--accent)}svg .vl.pos{fill:var(--pos)}
svg .zero{stroke:var(--rule)}svg .bar{fill:var(--field)}
""",
       T("""
<div class="field">
  <div class="k">2026 Jan–Aug · all channels</div>
  <h1>Ahead of last year, behind the plan</h1>
  <p>Sales of <b>841.8M</b> beat last year by 1.5%, but the plan asked for <b>879.0M</b>.</p>
  <p>Four categories cleared their target. <b>Electronics missed by 44.9M</b> — larger than the 37.2M gap,
     so every other category is covering for it.</p>
  <div class="kpis">
    <div><div class="n">Sales</div><div class="v">841.8M</div><div class="d">▲ 1.5% YoY</div></div>
    <div><div class="n">Attainment</div><div class="v">95.8%</div><div class="d">37.2M short</div></div>
  </div>
</div>
<div class="right">
  <div><h3>Monthly sales against last year</h3>{{TREND}}</div>
  <div><h3>Variance to target by category</h3>{{CATS}}</div>
  <div class="two">
    <div><h3>Sales by region</h3>{{REG}}</div>
    <div><h3>Stores furthest behind</h3><table>{{ST}}</table></div>
  </div>
</div>""",
         TREND=line(790, 118, [(PY, "pyl", "line"), (SALES, "ar", "area"), (SALES, "ln", "line")], labels=MONTHS),
         CATS=diverge(790, 104, CATS, fs=9.5, lw=86), REG=hbars(430, 128, REGIONS, fs=9.5, lw=92), ST=store_rows()))

# 10 ── 작업대: 도구처럼 보인다. 표가 주인공 --------------------------------------------------------
design(10, "workbench", "Workbench", "도구 화면. 탭과 툴바가 있고 표가 주인공이다.",
       '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">',
       """
:root{--chrome:#EFF1F4;--sheet:#FFF;--ink:#17263F;--ink2:#67748B;--accent:#0B5FD0;--neg:#D23B2E;--pos:#1C7C54;--rule:#DCE0E7}
.page{background:var(--chrome);color:var(--ink);font-family:'IBM Plex Sans',system-ui,sans-serif;
  display:grid;grid-template-rows:auto auto 1fr}
.tabs{display:flex;gap:2px;padding:9px 14px 0;border-bottom:1px solid var(--rule)}
.tab{padding:7px 15px;font-size:12px;color:var(--ink2);border:1px solid transparent;border-bottom:none;border-radius:5px 5px 0 0}
.tab.on{background:var(--sheet);border-color:var(--rule);color:var(--ink);font-weight:600;margin-bottom:-1px}
.tools{display:flex;align-items:center;gap:8px;padding:8px 14px;background:var(--sheet);border-bottom:1px solid var(--rule)}
.btn{font-size:11.5px;border:1px solid var(--rule);border-radius:5px;padding:4px 11px;color:var(--ink2);background:#fff}
.btn.pri{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
.sp{flex:1}
.stat{font-size:11.5px;color:var(--ink2)}
.stat b{color:var(--ink);font-variant-numeric:tabular-nums}
.main{display:grid;grid-template-columns:1fr 330px;background:var(--sheet);min-height:0}
.sheetwrap{padding:14px 16px;min-width:0;overflow:hidden}
.side{border-left:1px solid var(--rule);padding:14px 16px;display:flex;flex-direction:column;gap:15px;min-width:0}
h3{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;color:var(--ink2);margin:0 0 8px;font-weight:700}
table{width:100%;border-collapse:collapse;font-size:12px}
th{font-size:10px;letter-spacing:.8px;text-transform:uppercase;color:var(--ink2);text-align:left;
  padding:0 8px 7px 0;border-bottom:1px solid var(--rule);font-weight:600}
td{padding:7px 8px 7px 0;border-bottom:1px solid var(--rule);font-variant-numeric:tabular-nums}
td.name{font-variant-numeric:normal}
.num{text-align:right;font-family:'IBM Plex Mono',monospace}
.neg{color:var(--neg)}.pos{color:var(--pos)}
.cell{position:relative}
.cell i{position:absolute;left:0;top:50%;transform:translateY(-50%);height:15px;background:rgba(11,95,208,.14);border-radius:2px}
.cell span{position:relative;padding-left:5px}
svg .ln{fill:none;stroke:var(--accent);stroke-width:2}
svg .pyl{fill:none;stroke:#AFB7C4;stroke-width:1.4}
svg .ax,svg .lb,svg .vl{fill:var(--ink2)}
svg .pos{fill:var(--pos)}svg .neg{fill:var(--neg)}svg .vl.neg{fill:var(--neg)}svg .vl.pos{fill:var(--pos)}
svg .zero{stroke:var(--rule)}
""",
       T("""
<div class="tabs"><div class="tab on">Summary</div><div class="tab">Categories</div><div class="tab">Stores</div>
  <div class="tab">Raw data</div></div>
<div class="tools"><span class="btn pri">2026</span><span class="btn">2025</span><span class="btn">2024</span>
  <span class="btn">All channels ▾</span><span class="sp"></span>
  <span class="stat">Sales <b>841.8M</b> · Attainment <b>95.8%</b> · Short <b class="neg">37.2M</b></span></div>
<div class="main">
  <div class="sheetwrap"><h3>Category performance against target</h3>
    <table><thead><tr><th>Category</th><th class="num">Sales</th><th class="num">Target</th>
      <th class="num">Variance</th><th style="width:34%">Share of sales</th></tr></thead><tbody>{{ROWS}}</tbody></table>
    <h3 style="margin-top:18px">Stores, weakest first</h3>
    <table><thead><tr><th>Store</th><th class="num">Sales</th><th class="num">YoY</th>
      <th style="width:34%">Against the store average</th></tr></thead><tbody>{{SROWS}}</tbody></table>
  </div>
  <div class="side">
    <div><h3>Monthly sales</h3>{{TREND}}</div>
    <div><h3>Stores furthest behind</h3><table>{{ST}}</table></div>
    <div><h3>Top regions</h3>{{REG}}</div>
  </div>
</div>""",
         ROWS="".join(
             T('<tr><td class="name">{{N}}</td><td class="num">{{S}}</td><td class="num">{{T}}</td>'
               '<td class="num {{C}}">{{V}}</td><td class="cell"><i style="width:{{W}}%"></i>'
               '<span>{{P}}%</span></td></tr>',
               N=n, S=f"{s:.1f}M", T=f"{s - v:.1f}M", V=f"{v:+.1f}M",
               C="neg" if v < 0 else "pos", W=f"{s / 345.2 * 100:.0f}", P=f"{s / TOTAL * 100:.1f}")
             for n, v, s in [("Food", 14.8, 266.9), ("Fashion", -16.8, 186.3), ("Electronics", -44.9, 158.1),
                             ("Home", 2.3, 118.7), ("Beauty", 7.4, 111.8)]),
         SROWS="".join(
             T('<tr><td class="name">{{N}}</td><td class="num">{{S}}</td><td class="num neg">{{D}}%</td>'
               '<td class="cell"><i style="width:{{W}}%"></i><span>{{R}}</span></td></tr>',
               N=n, S=s_, D=f"{d:.1f}", W=f"{w:.0f}", R=r)
             for n, s_, d, w, r in [("Ilsan", "23.5M", -38.6, 34, "lowest of 12"),
                                    ("Jeju", "12.2M", -29.7, 18, "smallest store"),
                                    ("Ulsan", "21.2M", -24.9, 31, "below average"),
                                    ("Gangwon", "13.6M", -11.2, 20, "below average"),
                                    ("Chungcheong", "61.9M", -3.4, 89, "near average")]),
         TREND=line(300, 96, [(PY, "pyl", "line"), (SALES, "ln", "line")], labels=MONTHS, fs=8),
         ST=store_rows(), REG=hbars(300, 92, REGIONS[:4], fs=9, lw=86)))


# ── 파일로 쓰기 ──────────────────────────────────────────────────────────────────────────────────
PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{{NAME}} — dashboard study</title>
{{FONT}}
<style>
*{box-sizing:border-box}
html,body{margin:0;background:#9AA0A8}
.frame{width:1280px;height:720px;margin:0 auto;position:relative;overflow:hidden}
.page{width:100%;height:100%;overflow:hidden}
text{font-family:inherit}
svg .bar{fill:var(--accent)}            /* 시안이 따로 정하지 않으면 강조색 */
svg .lb,svg .vl,svg .ax{fill:var(--ink2)}
{{CSS}}
</style></head>
<body><div class="frame"><div class="page">{{BODY}}</div></div></body></html>
"""

INDEX_HEAD = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>대시보드 구성 시안 10가지</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
body{margin:0;background:#15181D;color:#E7EAEF;font-family:'IBM Plex Sans',system-ui,sans-serif;padding:28px 30px 40px}
h1{font-size:23px;margin:0;letter-spacing:-.3px}
.sub{color:#8C94A3;font-size:13.5px;margin-top:7px;max-width:84ch;line-height:1.55}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(520px,1fr));gap:24px;margin-top:26px}
figure{margin:0}
.shot{width:100%;aspect-ratio:16/9;border-radius:7px;overflow:hidden;background:#000;border:1px solid #2A2F38}
.shot iframe{width:1280px;height:720px;border:0;transform-origin:0 0;display:block}
figcaption{margin-top:9px;display:flex;gap:9px;align-items:baseline}
.n{font-variant-numeric:tabular-nums;color:#636B7A;font-size:12px}
.t{font-weight:700;font-size:14px}
.i{color:#8C94A3;font-size:12.5px}
a{color:#7FB2F0}
</style></head><body>
<h1>대시보드 구성 시안 10가지</h1>
<div class="sub">테마 10종이 전부 "왼쪽 레일 + 흰 카드"라 색만 바뀌고 같은 리포트로 보였다.
닮아 보이는 원인은 색이 아니라 구성이다. 그래서 배치·타이포·정보 구조가 서로 다른 열 가지를 먼저 그렸다.
숫자는 모두 예제 03 모델의 실제 값(2026년 1~8월)이라, 달라 보이는 것은 오직 디자인이다.</div>
<div class="grid">
"""


def main() -> None:
    cards = []
    for d in DESIGNS:
        f = OUT / f"{d['num']:02d}-{d['slug']}.html"
        f.write_text(T(PAGE, NAME=d["name"], FONT=d["font"], CSS=d["css"], BODY=d["body"]), encoding="utf-8")
        cards.append(T("""<figure><div class="shot"><iframe src="{{F}}" scrolling="no" loading="lazy"
        onload="this.style.transform='scale('+(this.parentNode.clientWidth/1280)+')'"></iframe></div>
      <figcaption><span class="n">{{N}}</span><span class="t"><a href="{{F}}">{{T}}</a></span>
      <span class="i">{{I}}</span></figcaption></figure>""",
                       F=f.name, N=f"{d['num']:02d}", T=d["name"], I=d["idea"]))
    (OUT / "index.html").write_text(INDEX_HEAD + "\n".join(cards) + "\n</div></body></html>", encoding="utf-8")
    print(f"{OUT}: {len(DESIGNS)} studies + index.html")
    for d in DESIGNS:
        print(f"  {d['num']:02d} {d['name']:<14} {d['idea']}")


if __name__ == "__main__":
    main()
