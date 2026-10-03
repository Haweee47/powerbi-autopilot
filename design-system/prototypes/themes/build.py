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


# ── 분석용 그리기 조각 ────────────────────────────────────────────────────────────────────────────
import json as _json

AN = _json.loads((OUT / "_analysis.json").read_text(encoding="utf-8"))
AN2 = _json.loads((OUT / "_analysis2.json").read_text(encoding="utf-8"))


def mix(c1, c2, t):
    """두 색 사이를 t(0~1)로 섞는다. 히트맵 칸 색은 값에서 바로 계산한다."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def corr_grid(w, cell, names, M, lo, mid, hi, fs=9.5):
    """상관 행렬. 위쪽 삼각만 칠한다 — 아래쪽은 같은 값이라 잉크를 두 번 쓰는 셈이다."""
    lw = max(len(n) for n in names) * fs * 0.58 + 10
    out = []
    for i, rn in enumerate(names):
        y = 18 + i * cell
        out.append('<text class="lb" x="%.1f" y="%.1f" font-size="%s" text-anchor="end">%s</text>'
                   % (lw - 7, y + cell / 2 + 3.5, fs, rn))
        for j in range(len(names)):
            if j < i:
                continue
            x = lw + j * cell
            v = M[i][j]
            col = "#DCE3EA" if i == j else (mix(mid, hi, v) if v >= 0 else mix(mid, lo, -v))
            ink = "#FFFFFF" if (i != j and abs(v) > .55) else "#263043"
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" rx="2"/>'
                       % (x + 1, y + 1, cell - 2, cell - 2, col))
            if i != j:
                lab = ("%+.2f" % v).replace("+0.", ".").replace("-0.", "-.")
                out.append('<text x="%.1f" y="%.1f" font-size="%s" text-anchor="middle" fill="%s">%s</text>'
                           % (x + cell / 2, y + cell / 2 + 3.5, fs - .5, ink, lab))
    for j, cn in enumerate(names):
        short = cn.replace(" %", "").replace("Avg order", "AOV").replace("Store age", "Age")
        out.append('<text class="lb" x="%.1f" y="12" font-size="%s" text-anchor="middle">%s</text>'
                   % (lw + j * cell + cell / 2, fs - .5, short))
    h = 18 + len(names) * cell + 4
    return '<svg viewBox="0 0 %d %d" width="100%%" height="%d">%s</svg>' % (w, h, h, "".join(out))


def heat_grid(w, cell, rows, cols, data, lo, mid, hi, base=100.0, fs=9.5):
    """행 × 열 히트맵. 기준값(달성률 100%)을 가운데 두고 양쪽으로 색이 갈린다."""
    lw = max(len(r) for r in rows) * fs * 0.58 + 10
    span = max(abs(v - base) for r in rows for v in data[r] if v is not None) or 1
    out = []
    for j, c in enumerate(cols):
        out.append('<text class="lb" x="%.1f" y="12" font-size="%s" text-anchor="middle">%s</text>'
                   % (lw + j * cell + cell / 2, fs - .5, c))
    for i, r in enumerate(rows):
        y = 18 + i * cell
        out.append('<text class="lb" x="%.1f" y="%.1f" font-size="%s" text-anchor="end">%s</text>'
                   % (lw - 7, y + cell / 2 + 3.5, fs, r))
        for j, v in enumerate(data[r]):
            if v is None:
                continue
            x = lw + j * cell
            t = min(abs(v - base) / span, 1)
            col = mix(mid, hi, t) if v >= base else mix(mid, lo, t)
            ink = "#FFFFFF" if t > .55 else "#263043"
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" rx="2"/>'
                       % (x + 1, y + 1, cell - 2, cell - 2, col))
            out.append('<text x="%.1f" y="%.1f" font-size="%s" text-anchor="middle" fill="%s">%d</text>'
                       % (x + cell / 2, y + cell / 2 + 3.5, fs - .5, ink, round(v)))
    h = 18 + len(rows) * cell + 4
    return '<svg viewBox="0 0 %d %d" width="100%%" height="%d">%s</svg>' % (w, h, h, "".join(out))


def scatter_xy(w, h, pts, xlab, ylab, fs=9):
    """점 하나가 매장 하나. 추세선은 최소제곱으로 긋는다."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = min(xs) * .95, max(xs) * 1.05
    y0, y1 = min(ys) * .95, max(ys) * 1.05
    l, b, t, r = 46, 26, 8, 12
    px = lambda v: l + (v - x0) / (x1 - x0) * (w - l - r)
    py = lambda v: t + (y1 - v) / (y1 - y0) * (h - t - b)
    n = len(pts)
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs) or 1
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    out = ['<line class="ax2" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (l, h - b, w - r, h - b),
           '<line class="ax2" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (l, t, l, h - b),
           '<line class="trend" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
           % (px(x0), py(my + slope * (x0 - mx)), px(x1), py(my + slope * (x1 - mx)))]
    for x, y in pts:
        out.append('<circle class="pt" cx="%.1f" cy="%.1f" r="3.6"/>' % (px(x), py(y)))
    out.append('<text class="lb" x="%.1f" y="%.1f" font-size="%s" text-anchor="middle">%s</text>'
               % ((l + w - r) / 2, h - 5, fs, xlab))
    cy = (t + h - b) / 2
    out.append('<text class="lb" x="11" y="%.1f" font-size="%s" text-anchor="middle" '
               'transform="rotate(-90 11 %.1f)">%s</text>' % (cy, fs, cy, ylab))
    return '<svg viewBox="0 0 %d %d" width="100%%" height="%d">%s</svg>' % (w, h, h, "".join(out))


def boxplot(w, h, st, fs=9.5):
    """상자 수염 + 점 흩뿌리기. 평균 하나로는 안 보이는 쏠림을 보여 준다."""
    hi = st["max"] * 1.06
    l, r = 36, 150
    px = lambda v: l + v / hi * (w - l - r)
    cy = h * .42
    bh = h * .30
    out = ['<line class="whisk" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (px(st["min"]), cy, px(st["max"]), cy),
           '<rect class="box" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2"/>'
           % (px(st["q1"]), cy - bh / 2, px(st["q3"]) - px(st["q1"]), bh),
           '<line class="med" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
           % (px(st["med"]), cy - bh / 2, px(st["med"]), cy + bh / 2)]
    for i, v in enumerate(st["all"]):
        out.append('<circle class="jit" cx="%.1f" cy="%.1f" r="2.6"/>' % (px(v), cy + bh * .82 + (i % 5) * 4.6))
    for nm, v in st["out"]:
        out.append('<circle class="outl" cx="%.1f" cy="%.1f" r="4.2"/>' % (px(v), cy))
        out.append('<text class="lb" x="%.1f" y="%.1f" font-size="%s">%s %.1fM</text>'
                   % (px(v) + 8, cy + 3.5, fs, nm, v))
    for k, lab in (("min", "min"), ("q1", "Q1"), ("med", "median"), ("q3", "Q3")):
        out.append('<text class="lb" x="%.1f" y="%.1f" font-size="%s" text-anchor="middle">%s %.1fM</text>'
                   % (px(st[k]), cy - bh / 2 - 8, fs - 1, lab, st[k]))
    return '<svg viewBox="0 0 %d %d" width="100%%" height="%d">%s</svg>' % (w, h, h, "".join(out))


def radar_svg(w, h, dims, series, fs=9.5, rings=4, cls_offset=0):
    """레이더. Power BI 기본에는 없어서 AppSource 커스텀 개체가 필요한 모양이다."""
    import math
    cx, cy = w / 2, h / 2 + 4
    rad = min(w, h) / 2 - (44 if fs > 8 else 26)
    n = len(dims)
    ang = lambda i: -math.pi / 2 + i * 2 * math.pi / n
    out = []
    for k in range(1, rings + 1):
        pts = " ".join("%.1f,%.1f" % (cx + rad * k / rings * math.cos(ang(i)),
                                      cy + rad * k / rings * math.sin(ang(i))) for i in range(n))
        out.append('<polygon class="ring" points="%s"/>' % pts)
    for i in range(n):
        out.append('<line class="spoke" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
                   % (cx, cy, cx + rad * math.cos(ang(i)), cy + rad * math.sin(ang(i))))
        if fs > 8:
            lx = cx + (rad + 20) * math.cos(ang(i))
            ly = cy + (rad + 20) * math.sin(ang(i))
            anchor = "middle" if abs(math.cos(ang(i))) < .3 else ("start" if math.cos(ang(i)) > 0 else "end")
            out.append('<text class="lb" x="%.1f" y="%.1f" font-size="%s" text-anchor="%s">%s</text>'
                       % (lx, ly + 3.5, fs, anchor, dims[i]))
    for s_i, s in enumerate(series):
        pts = " ".join("%.1f,%.1f" % (cx + rad * (v / 100) * math.cos(ang(i)),
                                      cy + rad * (v / 100) * math.sin(ang(i))) for i, v in enumerate(s["v"]))
        out.append('<polygon class="s%d" points="%s"/>' % (s_i + 1 + cls_offset, pts))
    return '<svg viewBox="0 0 %d %d" width="100%%" height="%d">%s</svg>' % (w, h, h, "".join(out))


def waterfall(w, h, items, start, fs=9.5):
    """작년에서 올해로 가는 다리. 어느 칸이 전체를 끌어내렸는지가 길이로 보인다."""
    run = start
    pts = []
    for _, v in items:
        pts.append((run, run + v))
        run += v
    end = run
    lo = min([start, end] + [min(a, b) for a, b in pts]) * .985
    hi = max([start, end] + [max(a, b) for a, b in pts]) * 1.015
    b, t = 32, 16
    n = len(items) + 2
    bw = (w - 16) / n
    py = lambda v: t + (hi - v) / (hi - lo) * (h - t - b)
    out = []

    def bar(i, y0, y1, cls, label, cap):
        x = 8 + i * bw
        top = min(py(y0), py(y1))
        out.append('<rect class="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>'
                   % (cls, x + bw * .18, top, bw * .64, max(abs(py(y0) - py(y1)), 2)))
        out.append('<text class="lb" x="%.1f" y="%.1f" font-size="%s" text-anchor="middle">%s</text>'
                   % (x + bw / 2, h - 14, fs, label))
        out.append('<text class="vl" x="%.1f" y="%.1f" font-size="%s" text-anchor="middle">%s</text>'
                   % (x + bw / 2, top - 6, fs, cap))

    bar(0, lo, start, "tot", "2025", "%.1f" % start)
    for i, ((nm, v), (y0, y1)) in enumerate(zip(items, pts), start=1):
        bar(i, y0, y1, "pos" if v >= 0 else "neg", nm, "%+.1f" % v)
    bar(n - 1, lo, end, "tot", "2026", "%.1f" % end)
    return '<svg viewBox="0 0 %d %d" width="100%%" height="%d">%s</svg>' % (w, h, h, "".join(out))


# ── 11 상관: 무엇과 무엇이 같이 움직이는가 ---------------------------------------------------------
design(11, "correlation", "Correlation", "매장 20개의 지표 7개가 서로 어떻게 움직이는지 한 판에 본다.",
       '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">',
       """
:root{--bg:#F3F6F9;--sheet:#FFF;--ink:#16202E;--ink2:#5E6B7E;--rule:#DFE4EB;--accent:#1F6FEB;--neg:#C2410C;--pos:#0E7490}
.page{background:var(--bg);color:var(--ink);font-family:'IBM Plex Sans',system-ui,sans-serif;padding:22px 26px;
  display:grid;grid-template-rows:auto 1fr;gap:14px}
h1{font-size:22px;margin:0;letter-spacing:-.3px}
.lede{font-size:13px;color:var(--ink2);margin-top:4px;max-width:96ch}
.lede b{color:var(--ink)}
.cols{display:grid;grid-template-columns:1.12fr .88fr;gap:18px;min-height:0}
.panel{background:var(--sheet);border:1px solid var(--rule);border-radius:7px;padding:14px 16px;min-width:0;
  display:flex;flex-direction:column}
h3{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;color:var(--ink2);margin:0 0 9px;font-weight:700}
.note{font-size:11.5px;color:var(--ink2);line-height:1.55;margin-top:10px}
.note b{color:var(--ink)}
.findings{display:flex;flex-direction:column;gap:7px;margin-top:auto}
.f{display:flex;gap:11px;align-items:baseline;border-top:1px solid var(--rule);padding-top:7px}
.f .r{font-family:'IBM Plex Mono';font-size:16px;font-weight:600;min-width:56px}
.f .r.hi{color:var(--pos)}
.f .r.lo{color:var(--ink2)}
.f .t{font-size:12px;line-height:1.42}
svg .lb{fill:var(--ink2)}
svg .ax2{stroke:var(--rule);stroke-width:1}
svg .trend{stroke:var(--accent);stroke-width:1.6;stroke-dasharray:4 3}
svg .pt{fill:var(--accent);fill-opacity:.6}
""",
       T("""
<div><h1>What moves with what</h1>
  <div class="lede">Seven measures across the 20 stores. <b>Margin and average order move together (r = +0.84)</b>,
   while sales, profit and orders are three readings of the same thing (r &ge; 0.97) and say nothing new.</div></div>
<div class="cols">
  <div class="panel"><h3>Pearson r · upper triangle only</h3>{{CORR}}
    <div class="note">The lower triangle repeats the upper one, so it is left unpainted, and a diagonal
      of 1.00 is not a finding either. Both are ink spent on nothing.</div></div>
  <div class="panel"><h3>Margin % against average order · one dot per store</h3>{{SC}}
    <div class="findings">
      <div class="f"><span class="r hi">+0.84</span><span class="t"><b>Margin ~ average order.</b>
        Stores selling bigger baskets keep more of each sale.</span></div>
      <div class="f"><span class="r hi">+0.56</span><span class="t"><b>Growth ~ average order.</b>
        The same stores are the ones growing.</span></div>
      <div class="f"><span class="r lo">−0.21</span><span class="t"><b>Growth ~ store age.</b>
        Older stores grow slightly slower, but weakly.</span></div>
      <div class="f"><span class="r lo">+1.00</span><span class="t"><b>Sales ~ profit.</b>
        Mechanical, not a finding — profit is a fixed share of sales in this model.</span></div>
    </div></div>
</div>""",
         CORR=corr_grid(600, 44, AN["vars"], AN["m"], "#C2410C", "#EEF2F7", "#0E7490"),
         SC=scatter_xy(440, 300, [(r["aov"] / 1000, r["margin"]) for r in AN["rows"]],
                       "Average order (K)", "Margin %")))

# ── 12 히트맵: 어디가 언제 무너졌나 ----------------------------------------------------------------
design(12, "heatmap", "Heat grid", "카테고리 × 월 달성률. 한 칸이 한 달의 한 카테고리다.",
       '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Public+Sans:wght@400;600&display=swap" rel="stylesheet">',
       """
:root{--bg:#0E1420;--panel:#151D2C;--ink:#E8EDF5;--ink2:#8595AD;--rule:#222C3E;--hot:#14B8A6;--cold:#F43F5E}
.page{background:var(--bg);color:var(--ink);font-family:'Public Sans',system-ui,sans-serif;padding:22px 26px;
  display:grid;grid-template-rows:auto auto 1fr;gap:14px}
h1{font-family:'Space Grotesk';font-size:23px;margin:0;letter-spacing:-.3px}
.lede{font-size:13px;color:var(--ink2);margin-top:4px;max-width:94ch}
.lede b{color:var(--ink)}
.legend{display:flex;align-items:center;gap:9px;font-size:11px;color:var(--ink2)}
.ramp{height:9px;width:190px;border-radius:9px;background:linear-gradient(90deg,var(--cold),#EEF2F7,var(--hot))}
.panel{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:15px 18px;min-width:0;
  display:flex;flex-direction:column}
.two{display:grid;grid-template-columns:1.5fr .5fr;gap:16px;min-height:0}
h3{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;color:var(--ink2);margin:0 0 10px;font-weight:600}
.rows{display:flex;flex-direction:column;gap:6px}
.r{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--rule);padding-bottom:6px}
.r .n{font-size:12px}
.r .v{font-family:'Space Grotesk';font-size:15px;font-weight:700}
.r .v.bad{color:var(--cold)}
.r .v.good{color:var(--hot)}
.foot{font-size:11.5px;color:var(--ink2);line-height:1.55;margin-top:auto;padding-top:10px}
.foot b{color:var(--ink)}
svg .lb{fill:var(--ink2)}
""",
       T("""
<div><h1>Attainment, month by month</h1>
  <div class="lede">Each cell is one category in one month against that month's target.
   <b>Electronics missed in six of eight months</b>; Food and Home cleared six each.</div></div>
<div class="legend"><span>Behind</span><div class="ramp"></div><span>Ahead</span>
  <span style="margin-left:auto">100 = exactly on plan</span></div>
<div class="two">
  <div class="panel"><h3>Attainment % · category × month</h3>{{HEAT}}
    <div class="foot">February, March and June are the months where more categories missed than cleared.
      <b>Electronics never recovered after February.</b></div></div>
  <div class="panel"><h3>Months on target</h3><div class="rows">
      <div class="r"><span class="n">Food</span><span class="v good">6 / 8</span></div>
      <div class="r"><span class="n">Home</span><span class="v good">6 / 8</span></div>
      <div class="r"><span class="n">Beauty</span><span class="v good">5 / 8</span></div>
      <div class="r"><span class="n">Fashion</span><span class="v bad">2 / 8</span></div>
      <div class="r"><span class="n">Electronics</span><span class="v bad">2 / 8</span></div>
    </div>
    <div class="foot">Counting months rather than totals separates a category that is
      <b>steadily behind</b> from one that had a single bad month.</div></div>
</div>""", HEAT=heat_grid(690, 62, list(AN2["heat"]), AN2["months"], AN2["heat"], "#F43F5E", "#EEF2F7", "#14B8A6")))

# ── 13 분포: 평균이 숨기는 것 ----------------------------------------------------------------------
design(13, "spread", "Spread", "평균 대신 분포를 본다. 상자 수염과 이상치.",
       '<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">',
       """
:root{--bg:#FDFCFA;--sheet:#FFF;--ink:#1D1B18;--ink2:#6B675F;--rule:#E5E1D9;--accent:#3F6C51;--warn:#B45309}
.page{background:var(--bg);color:var(--ink);font-family:'Source Sans 3',system-ui,sans-serif;padding:26px 30px;
  display:grid;grid-template-rows:auto auto 1fr;gap:15px}
h1{font-family:'Source Serif 4',serif;font-size:26px;margin:0;font-weight:600;letter-spacing:-.3px}
.lede{font-size:13.5px;color:var(--ink2);margin-top:5px;max-width:92ch}
.lede b{color:var(--ink)}
.panel{background:var(--sheet);border:1px solid var(--rule);border-radius:5px;padding:16px 18px;min-width:0}
h3{font-size:10px;letter-spacing:1.3px;text-transform:uppercase;color:var(--ink2);margin:0 0 12px;font-weight:600}
.two{display:grid;grid-template-columns:1fr .8fr;gap:18px;min-height:0}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.s .k{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--ink2)}
.s .v{font-family:'Source Serif 4',serif;font-size:25px;font-weight:600}
.s .d{font-size:11px;color:var(--ink2)}
.callout{border-left:3px solid var(--warn);padding:9px 0 9px 13px;margin-top:14px;font-size:12.5px;line-height:1.55}
.callout b{color:var(--warn)}
.callout.calm{border-color:var(--accent)}
.callout.calm b{color:var(--accent)}
svg .box{fill:rgba(63,108,81,.15);stroke:var(--accent);stroke-width:1.4}
svg .med{stroke:var(--accent);stroke-width:2.4}
svg .whisk{stroke:var(--ink2);stroke-width:1.2}
svg .jit{fill:var(--accent);fill-opacity:.38}
svg .outl{fill:var(--warn)}
svg .lb{fill:var(--ink2)}
""",
       T("""
<div><h1>The average store does not exist</h1>
  <div class="lede">Twenty stores, 2026 sales. The mean is 42.1M, but
   <b>half the estate sits between 26.7M and 46.6M</b>, and two online channels sit far outside it.</div></div>
<div class="panel"><h3>Sales per store · box with every store as a dot</h3>{{BOX}}</div>
<div class="two">
  <div class="panel"><h3>Where the middle is</h3>
    <div class="stats">
      <div class="s"><div class="k">Median</div><div class="v">36.9M</div><div class="d">half above, half below</div></div>
      <div class="s"><div class="k">Mean</div><div class="v">42.1M</div><div class="d">pulled up by two outliers</div></div>
      <div class="s"><div class="k">Interquartile range</div><div class="v">19.9M</div><div class="d">26.7M to 46.6M</div></div>
      <div class="s"><div class="k">Range</div><div class="v">98.4M</div><div class="d">12.2M to 110.6M</div></div>
    </div>
    <div class="callout"><b>Mean minus median is 5.2M.</b> Reporting the mean alone describes a store
      that exists nowhere in the estate.</div></div>
  <div class="panel"><h3>Outside 1.5 × IQR</h3>
    <div class="callout calm" style="margin-top:0"><b>Online Store 110.6M</b> and <b>Mobile App 104.2M</b>
      are not shops. They are channels sharing the store table, and they distort every
      per-store average that includes them.</div>
    <div class="callout">Decide once whether channels belong in the store list. Every ranking,
      average and target split downstream depends on that answer.</div></div>
</div>""", BOX=boxplot(1120, 148, AN2["box"])))

# ── 14 레이더: 매장 성격 비교 ----------------------------------------------------------------------
design(14, "radar", "Radar profile", "매장 셋의 성격을 여섯 축으로 겹쳐 본다. 커스텀 개체가 필요한 모양.",
       '<link href="https://fonts.googleapis.com/css2?family=Chivo:wght@400;600;800&display=swap" rel="stylesheet">',
       """
:root{--bg:#131019;--panel:#1C1824;--ink:#EFEAF5;--ink2:#9289A3;--rule:#2B2534;--s1:#F2B134;--s2:#51CDA0;--s3:#E26D7E}
.page{background:var(--bg);color:var(--ink);font-family:Chivo,system-ui,sans-serif;padding:22px 26px;
  display:grid;grid-template-rows:auto 1fr;gap:14px}
h1{font-size:23px;font-weight:800;margin:0;letter-spacing:-.4px}
.lede{font-size:13px;color:var(--ink2);margin-top:4px;max-width:92ch}
.lede b{color:var(--ink)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:18px;min-height:0}
.panel{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:14px 18px;min-width:0;
  display:flex;flex-direction:column}
h3{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;color:var(--ink2);margin:0 0 4px;font-weight:600}
.keys{display:flex;gap:16px;margin-top:2px;justify-content:center}
.key{display:flex;align-items:center;gap:7px;font-size:12px}
.sw{width:11px;height:11px;border-radius:3px}
.mini{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.mini .c{background:rgba(255,255,255,.035);border-radius:8px;padding:8px 6px 2px;text-align:center}
.mini .n{font-size:11px;color:var(--ink2);margin-bottom:1px}
.note{font-size:12px;color:var(--ink2);line-height:1.55;margin-top:12px}
.note b{color:var(--ink)}
code{font-family:ui-monospace,monospace;font-size:11px;background:rgba(255,255,255,.07);padding:1px 5px;border-radius:3px}
svg .ring{fill:none;stroke:var(--rule);stroke-width:1}
svg .spoke{stroke:var(--rule);stroke-width:1}
svg .lb{fill:var(--ink2)}
svg .s1{fill:rgba(242,177,52,.20);stroke:var(--s1);stroke-width:2}
svg .s2{fill:rgba(81,205,160,.18);stroke:var(--s2);stroke-width:2}
svg .s3{fill:rgba(226,109,126,.18);stroke:var(--s3);stroke-width:2}
""",
       T("""
<div><h1>Three stores, six axes</h1>
  <div class="lede">Every axis is scaled 0–100 across all 20 stores, so the shape shows the store's character
   rather than its size. <b>Online Store tops sales, orders and age but sits lowest on average order</b>; Jamsil is its mirror image.</div></div>
<div class="two">
  <div class="panel"><h3>Overlaid profiles</h3>{{RADAR}}<div class="keys">{{KEYS}}</div></div>
  <div class="panel"><h3>One store at a time</h3>
    <div class="mini">{{MINIS}}</div>
    <div class="note">Three overlapping shapes is already the limit of what reads.
      Past three, small multiples beat one chart.</div>
    <div class="note"><b>Power BI ships no radar visual.</b> This shape needs a visual from AppSource.
      The report names it in <code>publicCustomVisuals</code> and Desktop loads it when the file opens.</div></div>
</div>""",
         RADAR=radar_svg(470, 400, AN2["radar"]["dims"], AN2["radar"]["series"]),
         KEYS="".join('<div class="key"><span class="sw" style="background:var(--s%d)"></span>%s</div>'
                      % (i + 1, s["name"]) for i, s in enumerate(AN2["radar"]["series"])),
         MINIS="".join('<div class="c"><div class="n">%s</div>%s</div>'
                       % (s["name"], radar_svg(165, 165, AN2["radar"]["dims"], [s], fs=7, cls_offset=i))
                       for i, s in enumerate(AN2["radar"]["series"]))))

# ── 15 폭포: 작년에서 올해까지 ----------------------------------------------------------------------
design(15, "bridge", "Bridge", "작년 합계에서 올해 합계로 가는 다리. 어느 칸이 끌어내렸나.",
       '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap" rel="stylesheet">',
       """
:root{--bg:#FFFFFF;--ink:#111827;--ink2:#6B7280;--rule:#E5E7EB;--pos:#0F766E;--neg:#BE123C;--tot:#334155}
.page{background:var(--bg);color:var(--ink);font-family:Manrope,system-ui,sans-serif;padding:26px 30px;
  display:grid;grid-template-rows:auto 1fr auto;gap:14px}
h1{font-size:25px;font-weight:800;margin:0;letter-spacing:-.6px}
.lede{font-size:13.5px;color:var(--ink2);margin-top:5px;max-width:92ch}
.lede b{color:var(--ink)}
.chart{display:flex;flex-direction:column;justify-content:center;min-height:0}
.strip{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;border-top:1px solid var(--rule);padding-top:13px}
.c .n{font-size:11px;color:var(--ink2);letter-spacing:.4px}
.c .v{font-size:22px;font-weight:800;letter-spacing:-.6px;margin-top:2px}
.c .v.up{color:var(--pos)}
.c .v.dn{color:var(--neg)}
.c .d{font-size:11px;color:var(--ink2);margin-top:1px;min-height:14px}
svg .pos{fill:var(--pos)}
svg .neg{fill:var(--neg)}
svg .tot{fill:var(--tot)}
svg .lb{fill:var(--ink2)}
svg .vl{fill:var(--ink)}
""",
       T("""
<div><h1>From 829.5M to 841.8M</h1>
  <div class="lede">The year grew 12.4M. <b>Food added 24.8M and Beauty 13.3M</b>, while Electronics gave back 25.2M —
   which is why the total barely moved.</div></div>
<div class="chart">{{WF}}</div>
<div class="strip">{{CARDS}}</div>""",
         WF=waterfall(1180, 336, AN2["wf"], 829.5),
         CARDS="".join('<div class="c"><div class="n">%s</div><div class="v %s">%+.1fM</div><div class="d">%s</div></div>'
                       % (n, "up" if v >= 0 else "dn", v,
                          "largest gain" if v == max(x for _, x in AN2["wf"])
                          else ("largest loss" if v == min(x for _, x in AN2["wf"]) else ""))
                       for n, v in AN2["wf"])))


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
