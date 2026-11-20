import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
import os
import re
import ssl
import html
import json
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

# =========================================================================
# 0. 基本設定（LABアプリのURLを書き換えてください）
# =========================================================================
LAB_APP_URL = "https://your-yamashishi-lab.streamlit.app/"

st.set_page_config(
    page_title="YAMASHISHI DEEP DIVE v6 [LIVE QUANTUM TERMINAL]",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================================
# 1. スタイリング（暗転完全防止・スマホ最適化・2分割シナリオカード）
# =========================================================================
def inject_css():
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Plus+Jakarta+Sans:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 13.5px;
        background-color: #050811;
        color: #e2e8f0;
        scroll-behavior: smooth;
    }
    /* 更新時のブラックアウト・一瞬暗転を完全無効化 */
    [data-stale="true"] {
        opacity: 1 !important;
        transition: none !important;
    }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #050811 !important;
        color: #e2e8f0 !important;
    }
    header[data-testid="stHeader"] [data-testid="stToolbar"],
    header[data-testid="stHeader"] [data-testid="stActionButtons"] {
        display: none !important;
    }
    .stApp input, .stApp textarea {
        color: #ffffff !important;
        background-color: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 8px !important;
    }
    .stApp [data-baseweb="select"] > div {
        background-color: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    .brand-luxury {
        font-family: 'Cinzel', serif !important;
        font-size: clamp(16px, 4.6vw, 23px) !important;
        font-weight: 800 !important;
        letter-spacing: clamp(0.8px, 0.4vw, 2.2px) !important;
        background: linear-gradient(90deg, #f8fafc 0%, #38bdf8 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.25;
    }
    .glass-header {
        background: radial-gradient(circle at top right, rgba(168, 85, 247, 0.14), transparent 60%),
                    linear-gradient(145deg, #0f172a 0%, #070b14 100%);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 10px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
    }
    .rank-card {
        background: linear-gradient(180deg, #0f172a 0%, #090d16 100%) !important;
        color: #f8fafc !important;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-left: 5px solid #38bdf8;
    }
    .trajectory-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 6px;
        padding: 8px 10px;
        margin-bottom: 6px;
        background: linear-gradient(90deg, rgba(15, 23, 42, 0.96) 0%, rgba(15, 23, 42, 0.45) 100%);
        border-left: 3px solid #38bdf8;
        border-bottom: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 4px;
        flex-wrap: wrap;
    }
    .trajectory-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: clamp(10.5px, 3vw, 12px);
        font-weight: 700;
        letter-spacing: 0.4px;
        color: #f8fafc;
        white-space: normal;
        word-break: break-word;
    }
    .trajectory-title span { color: #38bdf8; font-weight: 500; }
    .winrate-bar {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 8px;
        padding: 8px 6px;
        margin-top: 8px;
        text-align: center;
    }
    @media (max-width: 640px) {
        .winrate-bar { grid-template-columns: repeat(2, 1fr); }
    }
    .metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13.5px;
        font-weight: 800;
        color: #38bdf8;
        margin-top: 2px;
    }
    .metric-lbl { font-size: 10px; color: #94a3b8; font-weight: 600; }
    .pill-badge {
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        background: rgba(56, 189, 248, 0.14);
        color: #7dd3fc;
        font-weight: 700;
        display: inline-block;
        margin-right: 4px;
    }
    .range-track {
        width: 100%;
        height: 6px;
        background: rgba(148, 163, 184, 0.2);
        border-radius: 99px;
        position: relative;
        margin: 6px 0 3px 0;
    }
    .range-dot {
        width: 11px;
        height: 11px;
        background: #38bdf8;
        border: 2px solid #ffffff;
        border-radius: 50%;
        position: absolute;
        top: -2.5px;
        transform: translateX(-50%);
        box-shadow: 0 0 8px rgba(56, 189, 248, 0.9);
    }
    /* 左右2分割シナリオカード */
    .scenario-stack {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin: 8px 0 12px 0;
    }
    .sc-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(9, 13, 22, 0.96) 100%);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 10px;
        padding: 10px 12px;
    }
    .sc-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
    }
    .sc-left { flex: 1; min-width: 0; }
    .sc-right { text-align: right; flex-shrink: 0; }
    .sc-price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 17px;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.15;
    }
    .sc-pct {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        margin-top: 2px;
    }
    .sc-bar-bg {
        width: 100%;
        height: 4px;
        background: rgba(148, 163, 184, 0.16);
        border-radius: 99px;
        margin-top: 8px;
        overflow: hidden;
    }
    .sc-bar-fill { height: 100%; border-radius: 99px; }
    .dark-box {
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(148, 163, 184, 0.18);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 12px;
        line-height: 1.65;
        color: #cbd5e1;
    }
    .warning-box {
        background: rgba(239, 68, 68, 0.10);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-left: 4px solid #ef4444;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 12px;
        line-height: 1.65;
        color: #fecaca;
    }
    .quant-box {
        background: rgba(16, 185, 129, 0.10);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-left: 4px solid #10b981;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 12px;
        line-height: 1.65;
        color: #d1fae5;
    }
    .memo-box {
        background: linear-gradient(180deg, #0b192c 0%, #090d16 100%);
        border: 1px solid rgba(168, 85, 247, 0.45);
        border-left: 4px solid #a855f7;
        padding: 12px 14px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 12px;
        line-height: 1.7;
        color: #f1f5f9;
    }
    .factor-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        padding: 5px 0;
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
        font-size: 11.5px;
    }
    .factor-row:last-child { border-bottom: none; padding-top: 7px; font-weight: 800; }
    .table-wrap { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 11px; margin-top: 4px; min-width: 310px; }
    .data-table th {
        background: #1e293b; color: #38bdf8; padding: 6px 7px; text-align: left;
        border-bottom: 1px solid rgba(56, 189, 248, 0.3); white-space: nowrap;
    }
    .data-table td {
        padding: 6px 7px; border-bottom: 1px solid rgba(148, 163, 184, 0.12); color: #e2e8f0;
    }
    /* Manage appボタンとの重なりを回避するためbottom: 62pxに設定 */
    .floating-top-btn {
        position: fixed;
        bottom: 62px;
        right: 14px;
        z-index: 99999;
        background: rgba(15, 23, 42, 0.90);
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.6);
        border-radius: 99px;
        padding: 6px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 800;
        text-decoration: none !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.65);
        backdrop-filter: blur(8px);
    }
    """
    st.markdown(f'<div id="top_anchor"></div><style>{css}</style><a href="#top_anchor" class="floating-top-btn">↑ TOP</a>', unsafe_allow_html=True)

inject_css()

# =========================================================================
# 2. フォーマット ＆ ビジュアルヘルパー
# =========================================================================
def fmt_currency(val, is_jp: bool) -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "-"
    return f"{val:,.0f}円" if is_jp else f"${val:,.2f}"

def get_gemini_api_key() -> str:
    k = os.environ.get("GEMINI_API_KEY", "")
    if not k:
        try:
            k = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            k = ""
    return str(k).strip()

def render_echarts(option_dict: dict, height: int = 300):
    opt_json = json.dumps(option_dict, ensure_ascii=False)
    html_code = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
      html, body {{ width: 100%; height: 100%; margin: 0; padding: 0; background: #0b1120; overflow: hidden; }}
      #c {{ width: 100%; height: {height}px; }}
    </style>
    </head><body><div id="c"></div><script>
      var el = document.getElementById('c');
      var chart = echarts.init(el, 'dark');
      chart.setOption({opt_json});
      function doResize() {{ chart.resize(); }}
      window.addEventListener('resize', doResize);
      if (typeof ResizeObserver !== 'undefined') {{
        new ResizeObserver(doResize).observe(el);
      }}
      setTimeout(doResize, 80);
      setTimeout(doResize, 300);
    </script></body></html>
    """
    components.html(html_code, height=height + 2)

def render_live_clock_bar(sync_interval: int = 60):
    html_code = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <style>
      html, body {{ width:100%; margin:0; padding:0; background:transparent; font-family:'JetBrains Mono',monospace; }}
      .bar {{
        display:flex; justify-content:space-between; align-items:center;
        background:rgba(15,23,42,0.85); border:1px solid rgba(16,185,129,0.35);
        border-radius:8px; padding:5px 10px; font-size:11px; color:#e2e8f0;
      }}
      .dot {{
        width:7px; height:7px; background:#10b981; border-radius:50%;
        display:inline-block; margin-right:6px; box-shadow:0 0 8px #10b981;
      }}
      .left {{ display:flex; align-items:center; color:#6ee7b7; font-weight:700; }}
      .right {{ color:#94a3b8; font-size:10.5px; }}
      .cnt {{ color:#38bdf8; font-weight:700; }}
    </style></head><body>
    <div class="bar">
      <div class="left"><span class="dot"></span>LIVE FEED <span id="clk" style="margin-left:8px;color:#fff;">--:--:--</span> JST</div>
      <div class="right">SILENT SYNC <span id="cd" class="cnt">{sync_interval}s</span></div>
    </div>
    <script>
      var rem = {sync_interval};
      function tick() {{
        var now = new Date();
        var jst = new Date(now.getTime() + (now.getTimezoneOffset() + 540) * 60000);
        var hh = String(jst.getHours()).padStart(2,'0');
        var mm = String(jst.getMinutes()).padStart(2,'0');
        var ss = String(jst.getSeconds()).padStart(2,'0');
        document.getElementById('clk').textContent = hh + ':' + mm + ':' + ss;
        document.getElementById('cd').textContent = rem + 's';
        rem = rem > 1 ? rem - 1 : {sync_interval};
      }}
      tick();
      setInterval(tick, 1000);
    </script></body></html>
    """
    components.html(html_code, height=34)

def build_mini_sparkline_svg(prices: np.ndarray) -> str:
    if len(prices) < 2: return ""
    p_min, p_max = float(np.min(prices)), float(np.max(prices))
    span = max(p_max - p_min, 1e-4)
    w, h = 92.0, 26.0
    pts = [f"{round((i/max(len(prices)-1,1))*w,1)},{round(h-2.0-((float(p)-p_min)/span)*(h-4.0),1)}" for i, p in enumerate(prices)]
    col = "#10b981" if prices[-1] >= prices[0] else "#ef4444"
    return f'<svg width="92" height="26" viewBox="0 0 92 26" style="display:block;margin-left:auto;"><polyline fill="none" stroke="{col}" stroke-width="1.8" points="{" ".join(pts)}"/></svg>'

# =========================================================================
# 3. キャッシュ分離型データ取得 ＆ 日英グローバル高信頼フィルタ
# =========================================================================
MACRO_TICKERS = {
    "SOX": ("^SOX", "米SOX指数"), "SP500": ("^GSPC", "S&P500"),
    "N225": ("^N225", "日経平均"), "USDJPY": ("JPY=X", "ドル円"),
    "US10Y": ("^TNX", "米10年債金利"), "OIL": ("CL=F", "WTI原油"), "VIX": ("^VIX", "VIX恐怖指数"),
}

TIER1_SOURCES = ["REUTERS", "ロイター", "BLOOMBERG", "ブルームバーグ", "WSJ", "WALL STREET JOURNAL", "FINANCIAL TIMES", "NIKKEI", "日経", "日本経済新聞", "KABUTAN", "株探", "PR TIMES", "CNBC", "SEC"]
TIER2_SOURCES = ["YAHOO", "MINKABU", "みんかぶ", "MARKETWATCH", "BARRON", "FORBES", "東洋経済", "ダイヤモンド", "JIJI", "時事", "共同通信"]
NOISE_SOURCES = ["まとめ", "ブログ", "2ch", "5ch", "note.com"]

@st.cache_data(ttl=90)
def load_macro_data() -> dict:
    codes = [v[0] for v in MACRO_TICKERS.values()]
    out = {}
    try:
        raw = yf.download(codes, period="6mo", interval="1d", group_by="ticker", threads=True, progress=False, timeout=8.0)
        for k, (tk, label) in MACRO_TICKERS.items():
            try:
                df_m = raw[tk].dropna(subset=["Close"]) if isinstance(raw.columns, pd.MultiIndex) else raw.dropna(subset=["Close"])
                if len(df_m) >= 2:
                    closes = df_m["Close"].copy()
                    closes.index = pd.to_datetime(closes.index).tz_localize(None).normalize()
                    closes = closes[~closes.index.duplicated(keep="last")]
                    last_c, prev_c = float(closes.iloc[-1]), float(closes.iloc[-2])
                    out[k] = {"label": label, "last": last_c, "diff_pct": round((last_c - prev_c) / max(abs(prev_c), 1e-4) * 100.0, 2), "series": closes}
            except Exception:
                pass
    except Exception:
        pass
    return out

@st.cache_data(ttl=60)
def load_stock_core(code: str) -> dict:
    tkr = yf.Ticker(code)
    df_1d = tkr.history(period="1y", interval="1d", auto_adjust=True)
    if df_1d is not None and not df_1d.empty:
        df_1d.index = pd.to_datetime(df_1d.index).tz_localize(None).normalize()
        df_1d = df_1d[~df_1d.index.duplicated(keep="last")]

    df_5m = tkr.history(period="1mo", interval="5m", auto_adjust=True)
    if df_5m is not None and not df_5m.empty:
        df_5m = df_5m.dropna(subset=["Close"]).copy()

    try: info = tkr.info or {}
    except Exception: info = {}

    earnings_hist = []
    try:
        ed = tkr.earnings_dates
        if ed is not None and not ed.empty:
            for idx_dt, row in ed.dropna(subset=["EPS Estimate", "Reported EPS"], how="all").head(6).iterrows():
                earnings_hist.append({
                    "date": idx_dt.strftime("%Y-%m-%d") if hasattr(idx_dt, "strftime") else str(idx_dt)[:10],
                    "est": float(row["EPS Estimate"]) if pd.notna(row.get("EPS Estimate")) else None,
                    "rep": float(row["Reported EPS"]) if pd.notna(row.get("Reported EPS")) else None,
                    "surp": float(row["Surprise(%)"]) if pd.notna(row.get("Surprise(%)")) else None
                })
    except Exception:
        pass

    holder_breakdown = None
    try:
        inst_p, ins_p = info.get("heldPercentInstitutions"), info.get("heldPercentInsiders")
        if inst_p is not None or ins_p is not None:
            i_val, in_val = round(float(inst_p or 0.0) * 100.0, 1), round(float(ins_p or 0.0) * 100.0, 1)
            holder_breakdown = {"inst": i_val, "insider": in_val, "public": round(max(0.0, 100.0 - i_val - in_val), 1)}
    except Exception:
        pass

    inst_holders = []
    try:
        ih = tkr.institutional_holders
        if ih is not None and not ih.empty:
            for _, row in ih.head(5).iterrows():
                inst_holders.append({
                    "holder": str(row.get("Holder", "-")),
                    "pct": float(row.get("pctHeld", 0.0)) * 100.0 if pd.notna(row.get("pctHeld")) else 0.0,
                    "shares": int(row.get("Shares", 0)) if pd.notna(row.get("Shares")) else 0
                })
    except Exception:
        pass

    return {
        "df_1d": df_1d, "df_5m": df_5m, "info": info,
        "earnings_hist": earnings_hist, "holder_breakdown": holder_breakdown, "inst_holders": inst_holders
    }

def _fetch_rss_raw(url: str, lang_tag: str) -> list:
    out = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4.0) as r:
            root = ET.fromstring(r.read())
            for it in root.findall("./channel/item")[:10]:
                t = (it.findtext("title") or "").strip()
                link = (it.findtext("link") or "").strip()
                src = (it.findtext("source") or "").strip()
                pub = (it.findtext("pubDate") or "").strip()[:16]
                if t:
                    out.append({"title": t, "link": link, "source": src, "pub": pub, "lang": lang_tag})
    except Exception:
        pass
    return out

@st.cache_data(ttl=120)
def fetch_global_trusted_intelligence(corp_name: str, short_code: str) -> dict:
    """日英マルチソース並列収集 ＋ 3段階トラスト・フィルタ ＋ クロス検証"""
    q_jp = f"{corp_name} OR {short_code} 株価"
    q_en = f"{short_code} OR \"{corp_name.split(' ')[0]}\" stock (Reuters OR Bloomberg OR CNBC OR WSJ)"
    url_jp = f"https://news.google.com/rss/search?q={urllib.parse.quote(q_jp)}&hl=ja&gl=JP&ceid=JP:ja"
    url_en = f"https://news.google.com/rss/search?q={urllib.parse.quote(q_en)}&hl=en-US&gl=US&ceid=US:en"

    raw_items = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(_fetch_rss_raw, url_jp, "JP")
        f2 = ex.submit(_fetch_rss_raw, url_en, "EN")
        raw_items.extend(f1.result())
        raw_items.extend(f2.result())

    pos_w = ["上昇", "急騰", "最高益", "上方修正", "増配", "自社株買い", "好調", "提携", "買い", "黒字", "成長", "SURGE", "BEAT", "UPGRADE", "RECORD", "BUY", "GROWTH", "RALLY"]
    neg_w = ["下落", "急落", "下方修正", "赤字", "減益", "不祥事", "訴訟", "不正", "辞任", "懸念", "売り", "リスク", "DROP", "FALL", "MISS", "DOWNGRADE", "LAWSUIT", "PROBE", "CUT", "SLUMP"]

    filtered = []
    seen_t = set()
    for it in raw_items:
        src_up = (it["source"] + " " + it["title"]).upper()
        if any(ns.upper() in src_up for ns in NOISE_SOURCES):
            continue
        norm_k = re.sub(r"\W+", "", it["title"].lower())[:24]
        if norm_k in seen_t:
            continue
        seen_t.add(norm_k)

        if any(t1 in src_up for t1 in TIER1_SOURCES):
            trust, w_trust = "S", 2.0
        elif any(t2 in src_up for t2 in TIER2_SOURCES):
            trust, w_trust = "A", 1.3
        else:
            trust, w_trust = "B", 0.7

        t_up = it["title"].upper()
        p_hit = sum(1 for w in pos_w if w in t_up)
        n_hit = sum(1 for w in neg_w if w in t_up)
        sent = "POS" if p_hit > n_hit else ("NEG" if n_hit > p_hit else "NEU")

        filtered.append({**it, "trust": trust, "w_trust": w_trust, "sent": sent})

    # 信頼度S・Aを優先ソート
    tier_ord = {"S": 0, "A": 1, "B": 2}
    filtered.sort(key=lambda x: (tier_ord[x["trust"]], 0 if x["lang"] == "EN" else 1))

    # 加重センチメント算出（信頼度Sの記事ほどメーターと予測軌道に強く効く）
    w_pos = sum(x["w_trust"] for x in filtered if x["sent"] == "POS")
    w_neg = sum(x["w_trust"] for x in filtered if x["sent"] == "NEG")
    w_tot = max(sum(x["w_trust"] for x in filtered), 1.0)
    shock_score = round(float(np.clip((w_pos - w_neg) / w_tot, -1.0, 1.0)), 2)
    pos_pct = round(w_pos / w_tot * 100)
    tier1_cnt = sum(1 for x in filtered if x["trust"] == "S")

    return {
        "items": filtered[:10], "pos_pct": pos_pct, "shock_score": shock_score,
        "tier1_cnt": tier1_cnt, "total_cnt": len(filtered)
    }

@st.cache_data(ttl=180)
def fetch_governance_and_whale_scans(company_name: str, short_code: str) -> tuple:
    """ガバナンス監査 ＋ 大量保有報告書(5%ルール)・機関空売り動向スキャンを並列実行"""
    q_gov = f"{company_name} (不祥事 OR 不正 OR 訴訟 OR 行政処分 OR 辞任 OR リコール)"
    q_whale = f"({company_name} OR {short_code}) (大量保有 OR 変更報告書 OR 機関投資家 OR 空売り残高 OR 5%ルール)"
    u_gov = f"https://news.google.com/rss/search?q={urllib.parse.quote(q_gov)}&hl=ja&gl=JP&ceid=JP:ja"
    u_whale = f"https://news.google.com/rss/search?q={urllib.parse.quote(q_whale)}&hl=ja&gl=JP&ceid=JP:ja"

    with ThreadPoolExecutor(max_workers=2) as ex:
        fg = ex.submit(_fetch_rss_raw, u_gov, "JP")
        fw = ex.submit(_fetch_rss_raw, u_whale, "JP")
        gov_list = [f"{x['title']} ({x['pub']})" for x in fg.result()[:5]]
        whale_list = fw.result()[:5]
    return gov_list, whale_list

# =========================================================================
# 4. アルゴリズムエンジン（指数減衰ウェイト5分足軌道・AIメモ自動キャッシュ）
# =========================================================================
def compute_macro_sensitivity(stock_close: pd.Series, macro_data: dict) -> list:
    s_ret = stock_close.pct_change().dropna().tail(90)
    results = []
    for k, m in macro_data.items():
        if k == "VIX": continue
        joined = pd.concat([s_ret.rename("stk"), m["series"].pct_change().dropna().rename("mac")], axis=1).dropna()
        if len(joined) >= 20:
            corr = float(joined["stk"].corr(joined["mac"]))
            var_m = float(joined["mac"].var())
            beta = float(joined["stk"].cov(joined["mac"]) / var_m) if var_m > 1e-9 else 0.0
            results.append({"key": k, "label": m["label"], "corr": round(0.0 if np.isnan(corr) else corr, 2), "beta": round(0.0 if np.isnan(beta) else beta, 2), "latest_diff": m["diff_pct"]})
    results.sort(key=lambda x: abs(x["corr"]), reverse=True)
    return results

def build_5m_realtime_trajectory(
    curr_px: float, df_5m: pd.DataFrame, macro_sens: list, macro_data: dict, news_res: dict, is_jp: bool
) -> dict:
    if is_jp:
        am = [f"{h:02d}:{m:02d}" for h in range(9, 12) for m in range(0, 60, 5) if not (h == 11 and m > 30)]
        pm = [f"{h:02d}:{m:02d}" for h in range(12, 16) for m in range(0, 60, 5) if not (h == 12 and m < 30) and not (h == 15 and m > 30)]
        slots, lunch_idx = am + pm, len(am) - 1
    else:
        slots = [f"{h:02d}:{m:02d}" for h in range(9, 17) for m in range(0, 60, 5) if not (h == 9 and m < 30) and not (h == 16 and m > 0)]
        lunch_idx = None

    n_slots = len(slots)
    slot_means, slot_stds, slot_vols = np.zeros(n_slots), np.full(n_slots, 0.003), np.zeros(n_slots)
    actual_today_map = {}

    if df_5m is not None and not df_5m.empty:
        tmp = df_5m.copy()
        idx_dt = pd.to_datetime(tmp.index)
        tmp["_d"], tmp["_hm"] = idx_dt.strftime("%Y-%m-%d"), idx_dt.strftime("%H:%M")
        unique_days = sorted(tmp["_d"].unique().tolist())
        past_days = unique_days[:-1]
        day_ret_maps, day_vol_maps, day_weights = [], [], []
        n_past = len(past_days)
        for d_idx, d_str in enumerate(past_days):
            sub = tmp[tmp["_d"] == d_str]
            if len(sub) < 10: continue
            open_p = float(sub["Open"].iloc[0])
            if open_p <= 0: continue
            r_map, v_map = {}, {}
            for _, row in sub.iterrows():
                hm = row["_hm"]
                if hm in slots:
                    r_map[hm] = (float(row["Close"]) - open_p) / open_p
                    v_map[hm] = float(row["Volume"])
            if r_map:
                day_ret_maps.append(r_map); day_vol_maps.append(v_map)
                day_weights.append(float(np.exp(1.2 * (d_idx / max(n_past - 1, 1)))))

        for i, sl in enumerate(slots):
            r_vals, w_vals, v_vals = [], [], []
            for rm, vm, w in zip(day_ret_maps, day_vol_maps, day_weights):
                if sl in rm: r_vals.append(rm[sl]); w_vals.append(w); v_vals.append(vm[sl])
            if len(r_vals) >= 3:
                w_arr, r_arr = np.array(w_vals) / np.sum(w_vals), np.array(r_vals)
                w_mean = float(np.sum(w_arr * r_arr))
                slot_means[i] = w_mean
                slot_stds[i] = max(float(np.sqrt(np.sum(w_arr * ((r_arr - w_mean) ** 2)))), 0.0025)
                slot_vols[i] = float(np.mean(v_vals)) if v_vals else 0.0
            else:
                slot_stds[i] = 0.003 + 0.009 * np.sqrt((i + 1) / n_slots)
                u_pos = (i / max(n_slots - 1, 1)) * 2.0 - 1.0
                slot_vols[i] = 100.0 * (0.4 + 1.4 * (u_pos ** 2))

        today_jst = datetime.datetime.now().strftime("%Y-%m-%d")
        if unique_days and unique_days[-1] == today_jst:
            for _, row in tmp[tmp["_d"] == today_jst].iterrows():
                if row["_hm"] in slots: actual_today_map[row["_hm"]] = round(float(row["Close"]), 2)

    sens_map = {x["key"]: x for x in macro_sens}
    mkt_key = "SOX" if ("SOX" in sens_map and abs(sens_map["SOX"]["corr"]) > 0.35) else ("N225" if "N225" in sens_map else "SP500")
    mkt_info = sens_map.get(mkt_key, {"label": "市場指数", "beta": 0.5, "latest_diff": 0.0})
    fx_info = sens_map.get("USDJPY", {"label": "ドル円", "beta": 0.0, "latest_diff": 0.0})
    vix_diff = macro_data.get("VIX", {}).get("diff_pct", 0.0)

    macro_gap_pct = (mkt_info["latest_diff"] * mkt_info["beta"]) * 0.45
    fx_gap_pct = (fx_info["latest_diff"] * fx_info["beta"]) * 0.35
    news_gap_pct = news_res["shock_score"] * 0.85
    total_open_gap_pct = float(np.clip(macro_gap_pct + fx_gap_pct + news_gap_pct, -5.0, 5.0))
    est_open_px = curr_px * (1.0 + total_open_gap_pct / 100.0)

    intraday_drift = float(np.clip((news_res["shock_score"] * 0.006) + (macro_gap_pct / 100.0 * 0.15), -0.02, 0.02))
    vol_boost = (1.0 + abs(news_res["shock_score"]) * 0.30) * (1.0 + max(0.0, vix_diff / 100.0) * 1.2)

    p50_arr, p85_arr, p15_arr, band_diff_arr, actual_arr = [], [], [], [], []
    for i, sl in enumerate(slots):
        frac = i / max(n_slots - 1, 1)
        mid = est_open_px * (1.0 + slot_means[i] + intraday_drift * frac)
        band = est_open_px * slot_stds[i] * vol_boost * 1.15
        lo_v, hi_v = max(mid - band, curr_px * 0.5), mid + band
        p50_arr.append(round(float(mid), 2)); p85_arr.append(round(float(hi_v), 2))
        p15_arr.append(round(float(lo_v), 2)); band_diff_arr.append(round(float(hi_v - lo_v), 2))
        actual_arr.append(actual_today_map.get(sl, None))

    idx_min, idx_max = int(np.argmin(p50_arr)), int(np.argmax(p50_arr))
    est_close_px = p50_arr[-1]
    return {
        "slots": slots, "lunch_idx": lunch_idx,
        "p50": p50_arr, "p85": p85_arr, "p15": p15_arr, "band_diff": band_diff_arr,
        "vols": [round(float(v), 1) for v in slot_vols],
        "actual": actual_arr, "has_actual": any(x is not None for x in actual_arr),
        "est_open_px": est_open_px, "est_open_gap_pct": round(total_open_gap_pct, 2),
        "est_close_px": est_close_px, "est_close_chg": round((est_close_px - curr_px) / max(curr_px, 1e-4) * 100.0, 2),
        "dip_idx": idx_min, "dip_time": slots[idx_min], "dip_px": p50_arr[idx_min],
        "peak_idx": idx_max, "peak_time": slots[idx_max], "peak_px": p50_arr[idx_max],
        "bull_trig": round(p85_arr[min(3, n_slots - 1)], 2), "bull_target": round(max(p85_arr), 2),
        "bear_trig": round(p15_arr[min(3, n_slots - 1)], 2), "bear_target": round(min(p15_arr), 2),
        "factors": {
            "mkt_label": mkt_info["label"], "mkt_diff": mkt_info["latest_diff"], "mkt_beta": mkt_info["beta"],
            "macro_gap_pct": round(macro_gap_pct, 2), "fx_diff": fx_info["latest_diff"], "fx_beta": fx_info["beta"],
            "fx_gap_pct": round(fx_gap_pct, 2), "news_shock": news_res["shock_score"], "news_gap_pct": round(news_gap_pct, 2),
        }
    }

def compute_volume_profile_detail(df_1d: pd.DataFrame, curr_px: float, is_jp: bool) -> dict:
    sub = df_1d.tail(250)
    if len(sub) < 20:
        return {"overhead_pct": 0.0, "poc_px": curr_px, "labels": [], "vols": [], "res_px": curr_px, "sup_px": curr_px}
    typ = (sub["High"].values + sub["Low"].values + sub["Close"].values) / 3.0
    vol = sub["Volume"].values.astype(float)
    above_v = float(np.sum(vol[typ > curr_px * 1.01]))
    bins = np.linspace(float(np.min(typ)), float(np.max(typ)) + 1e-4, 15)
    hist = np.bincount(np.clip(np.digitize(typ, bins) - 1, 0, 13), weights=vol, minlength=14)
    centers = [(bins[i] + bins[i + 1]) * 0.5 for i in range(14)]
    poc_idx = int(np.argmax(hist))
    above_idxs = [i for i, c in enumerate(centers) if c > curr_px * 1.005]
    below_idxs = [i for i, c in enumerate(centers) if c < curr_px * 0.995]
    return {
        "overhead_pct": round(above_v / max(float(np.sum(vol)), 1.0) * 100.0, 1),
        "poc_px": float(centers[poc_idx]),
        "labels": [fmt_currency(c, is_jp) for c in centers],
        "vols": [round(float(v) / 1e6, 2) for v in hist],
        "res_px": float(centers[max(above_idxs, key=lambda i: hist[i])]) if above_idxs else curr_px * 1.05,
        "sup_px": float(centers[max(below_idxs, key=lambda i: hist[i])]) if below_idxs else curr_px * 0.95
    }

def compute_5axis_scores(info: dict, ovh_pct: float, gov_cnt: int) -> list:
    pe = info.get("trailingPE")
    val_sc = int(np.clip(100 - (pe - 10) * 1.5, 25, 95)) if pe and pe > 0 else 55
    rev_g = info.get("revenueGrowth")
    gro_sc = int(np.clip(55 + rev_g * 120, 20, 98)) if rev_g is not None else 55
    roe = info.get("returnOnEquity")
    prf_sc = int(np.clip(45 + roe * 160, 20, 98)) if roe is not None else 55
    return [val_sc, gro_sc, prf_sc, int(np.clip(95 - ovh_pct * 0.85, 20, 95)), int(np.clip(95 - gov_cnt * 18, 25, 98))]

@st.cache_data(ttl=600)
def generate_auto_investment_memo(
    fc: str, corp_name: str, curr_px_str: str, open_gap: float, close_chg: float,
    dip_time: str, peak_time: str, ovh_pct: float, top_m_lbl: str, top_m_corr: float,
    top_m_beta: float, pos_pct: int, tier1_cnt: int, gov_cnt: int, upside_s: str
) -> tuple:
    api_key = get_gemini_api_key()
    prompt = f"""あなたはヘッジファンドのシニアアナリストです。以下の日英グローバル高信頼ソース（一次報道{tier1_cnt}件）と実測データに基づき、ファンドマネージャー向けの「1分インベストメントメモ」を日本語で簡潔に作成してください。
銘柄: {corp_name} ({fc}) / 現在値: {curr_px_str} / アナリスト乖離: {upside_s}
翌営業日予測: 寄付き {open_gap:+.2f}% / 大引け予測 {close_chg:+.2f}% / 押し目 {dip_time} / ピーク {peak_time}
上値しこり玉: {ovh_pct}% / 最大マクロ連動: {top_m_lbl} (相関 {top_m_corr}, β={top_m_beta})
高信頼ニュース強気度: {pos_pct}% / ガバナンスリスク検知: {gov_cnt}件

以下の3セクション構成（合計350文字以内、箇条書き）で出力してください：
🟢 Bull Case（強気シナリオ）
🔴 Bear Case（弱気・死角リスク）
⚡ Next Catalyst（次の注目トリガー）"""

    if api_key:
        for mod in ("gemini-2.5-flash", "gemini-2.0-flash"):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent"
                body = json.dumps({"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 650, "temperature": 0.6}}).encode("utf-8")
                req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "x-goog-api-key": api_key}, method="POST")
                with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=10.0) as r:
                    res_j = json.loads(r.read().decode("utf-8"))
                    txt = "".join([p.get("text", "") for p in res_j["candidates"][0]["content"]["parts"] if "text" in p])
                    if txt.strip():
                        return txt.strip(), f"🔵 AUTO GLOBAL AI ANALYST ({mod} / 一次報道{tier1_cnt}件反映)"
            except Exception:
                continue

    bull = f"・アナリスト目標乖離 {upside_s}、翌営業日の大引け予測 {close_chg:+.2f}%。\n・高信頼ニュース強気度 {pos_pct}%（一次報道{tier1_cnt}件）、上値しこり玉 {ovh_pct}%。"
    bear = f"・{top_m_lbl}との相関係数 {top_m_corr}（β={top_m_beta}）でマクロ急変時の連れ安リスクあり。\n・ガバナンス報道は {gov_cnt}件検知（{'要精査' if gov_cnt else '現時点でクリーン'}）。"
    cat = f"・明日は {dip_time} 頃の押し目反発と {peak_time} 頃のピーク形成が焦点。"
    return f"🟢 Bull Case（強気シナリオ）\n{bull}\n\n🔴 Bear Case（弱気・死角リスク）\n{bear}\n\n⚡ Next Catalyst（次の注目トリガー）\n{cat}", f"⚙️ AUTO QUANT MEMO（一次報道{tier1_cnt}件・実測自動生成）"

# =========================================================================
# 5. 固定ヘッダー ＆ 入力コントロール
# =========================================================================
h_col1, h_col2 = st.columns([3.1, 1.3])
with h_col1:
    st.markdown(
        '<div class="glass-header" style="margin-bottom:6px;">'
        '<div class="brand-luxury">YAMASHISHI DEEP DIVE v6</div>'
        '<div style="font-size:10.5px;color:#94a3b8;margin-top:2px;">フル幅5分足確率コーン × 日英高信頼フィルタ × 無暗転ライブ同期</div>'
        '</div>',
        unsafe_allow_html=True
    )
with h_col2:
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    st.link_button("⬅️ LABへ戻る", LAB_APP_URL, use_container_width=True)

STYLES = ["デイトレード", "スキャルピング", "スイングトレード", "バイ＆ホールド"]
qp_code = st.query_params.get("code", "NVDA")
query_code = str(qp_code[0] if isinstance(qp_code, list) else qp_code).strip().upper()
qp_style = st.query_params.get("style", "デイトレード")
query_style = str(qp_style[0] if isinstance(qp_style, list) else qp_style).strip()

c1, c2 = st.columns([2.2, 1.6])
in_code = c1.text_input("銘柄コード", value=query_code, placeholder="例: NVDA / 6920", label_visibility="collapsed")
in_style = c2.selectbox("スタイル", STYLES, index=STYLES.index(query_style) if query_style in STYLES else 0, label_visibility="collapsed")

fc = in_code.strip().upper()
if not fc: st.stop()
if re.match(r"^[0-9]{3}[0-9A-Z]$", fc): fc = f"{fc}.T"
is_jp = fc.endswith(".T")

# =========================================================================
# 6. 無暗転・自動ライブ更新セクション（60秒ごとに静かに裏同期）
# =========================================================================
def render_live_terminal(fc_code: str, style_name: str, is_jp_flag: bool):
    render_live_clock_bar(sync_interval=60)

    # spinnerを外すことで更新時の暗転・カクつきを完全防止
    data = load_stock_core(fc_code)
    macro_data = load_macro_data()

    df_1d, df_5m, info = data["df_1d"], data["df_5m"], data["info"]
    if df_1d is None or df_1d.empty:
        st.error(f"❌ 銘柄コード `{fc_code}` の市場データを取得できませんでした。")
        return

    corp_name = info.get("longName") or info.get("shortName") or fc_code
    short_code = fc_code.replace(".T", "")
    sector = info.get("sector") or "セクター未分類"
    industry = info.get("industry") or "-"
    curr_px = float(df_1d["Close"].iloc[-1])
    prev_px = float(df_1d["Close"].iloc[-2]) if len(df_1d) >= 2 else curr_px
    chg_pct = ((curr_px - prev_px) / max(prev_px, 1e-4)) * 100.0
    chg_col = "#10b981" if chg_pct >= 0 else "#ef4444"

    macro_sens = compute_macro_sensitivity(df_1d["Close"], macro_data)
    news_res = fetch_global_trusted_intelligence(corp_name, short_code)
    gov_risks, whale_news = fetch_governance_and_whale_scans(corp_name, short_code)
    vp = compute_volume_profile_detail(df_1d, curr_px, is_jp_flag)
    traj = build_5m_realtime_trajectory(curr_px, df_5m, macro_sens, macro_data, news_res, is_jp_flag)

    comp_score = int(np.clip(round(50 + news_res["shock_score"] * 45 - len(gov_risks) * 9), 5, 98))
    if comp_score >= 75:   meter_lbl = "EXTREME GREED // 極度の強気"
    elif comp_score >= 58: meter_lbl = "BULLISH // 強気優勢"
    elif comp_score >= 42: meter_lbl = "NEUTRAL // 均衡・様子見"
    elif comp_score >= 25: meter_lbl = "FEAR // 警戒・弱気"
    else:                  meter_lbl = "EXTREME FEAR // リスク警戒"

    hi_52, lo_52 = float(df_1d["High"].max()), float(df_1d["Low"].min())
    pos_52 = float(np.clip((curr_px - lo_52) / max(hi_52 - lo_52, 1e-4) * 100.0, 2.0, 98.0))
    spark_svg = build_mini_sparkline_svg(df_1d["Close"].tail(20).values)

    aura_col = "#10b981" if traj["est_open_gap_pct"] >= 0 else "#ef4444"
    aura_glow = "rgba(16,185,129,0.22)" if traj["est_open_gap_pct"] >= 0 else "rgba(239,68,68,0.22)"
    target_mean = info.get("targetMeanPrice")
    upside_str = f"{((target_mean - curr_px)/curr_px*100):+.1f}%" if (target_mean and curr_px > 0) else "-"
    risk_status = f"⚠️ {len(gov_risks)}件" if gov_risks else "🟢 クリーン"
    risk_col = "#f87171" if gov_risks else "#10b981"

    st.markdown(f"""
    <div class="rank-card" style="border-left-color:{aura_col};box-shadow:0 8px 26px {aura_glow};">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap;">
        <div style="min-width:0;flex:1;">
          <div>
            <span class="pill-badge">{html.escape(fc_code)}</span>
            <span class="pill-badge" style="border-color:rgba(168,85,247,0.45);background:rgba(168,85,247,0.16);color:#e9d5ff;">{html.escape(style_name)}</span>
          </div>
          <div style="font-size:17.5px;font-weight:800;color:#ffffff;margin-top:4px;word-break:break-word;">{html.escape(corp_name)}</div>
          <div style="font-size:11px;color:#94a3b8;margin-top:2px;">{html.escape(sector)} / {html.escape(industry)}</div>
        </div>
        <div style="text-align:right;flex-shrink:0;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:19.5px;font-weight:800;color:#ffffff;">{fmt_currency(curr_px, is_jp_flag)}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:{chg_col};margin-bottom:3px;">{chg_pct:+.2f}%</div>
          {spark_svg}
        </div>
      </div>

      <div style="margin-top:8px;">
        <div style="display:flex;justify-content:space-between;font-size:9.5px;color:#94a3b8;font-family:'JetBrains Mono',monospace;">
          <span>52W安 {fmt_currency(lo_52, is_jp_flag)}</span>
          <span style="color:#7dd3fc;">52W位置 {pos_52:.0f}%</span>
          <span>52W高 {fmt_currency(hi_52, is_jp_flag)}</span>
        </div>
        <div class="range-track"><div class="range-dot" style="left:{pos_52:.1f}%;"></div></div>
      </div>

      <div class="winrate-bar">
        <div><div class="metric-lbl">明日寄付き予測</div><div class="metric-val" style="color:{aura_col};">{traj['est_open_gap_pct']:+.2f}%</div></div>
        <div><div class="metric-lbl">アナリスト乖離</div><div class="metric-val" style="color:#fde047;">{upside_str}</div></div>
        <div><div class="metric-lbl">上値しこり玉</div><div class="metric-val" style="color:#c084fc;">{vp['overhead_pct']}%</div></div>
        <div><div class="metric-lbl">ガバナンス</div><div class="metric-val" style="color:{risk_col};">{risk_status}</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "翌営業日 1日軌道",
        "マクロβ・決算",
        "財務・大口株主",
        "リスク・AIメモ"
    ])

    # ---------------------------------------------------------------------
    # TAB 1: フル幅5分刻み軌道 ＋ 左右2分割シナリオカード
    # ---------------------------------------------------------------------
    with tab1:
        st.markdown(
            '<div class="trajectory-header">'
            '<div class="trajectory-title">NEXT SESSION 5M TRAJECTORY <span>// 翌営業日 5分刻み確率コーン軌道</span></div>'
            '</div>',
            unsafe_allow_html=True
        )

        mark_line_cfg = {}
        if traj["lunch_idx"] is not None:
            mark_line_cfg = {
                "symbol": ["none", "none"],
                "lineStyle": {"color": "rgba(148,163,184,0.35)", "type": "dashed"},
                "label": {"formatter": "前場/後場", "color": "#94a3b8", "fontSize": 9, "position": "insideEndTop"},
                "data": [{"xAxis": traj["lunch_idx"]}]
            }

        series_list = [
            {"name": "想定出来高", "type": "bar", "yAxisIndex": 1, "data": traj["vols"], "itemStyle": {"color": "rgba(148,163,184,0.16)"}, "barMaxWidth": 4},
            {"name": "下限ベース", "type": "line", "yAxisIndex": 0, "data": traj["p15"], "stack": "cone", "lineStyle": {"opacity": 0}, "showSymbol": False, "silent": True},
            {"name": "確率コーン(15-85%)", "type": "line", "yAxisIndex": 0, "data": traj["band_diff"], "stack": "cone", "lineStyle": {"opacity": 0}, "areaStyle": {"color": "rgba(56, 189, 248, 0.16)"}, "showSymbol": False, "silent": True},
            {"name": "強気上限", "type": "line", "yAxisIndex": 0, "data": traj["p85"], "lineStyle": {"color": "rgba(16,185,129,0.55)", "width": 1.1, "type": "dashed"}, "showSymbol": False},
            {
                "name": "予測中央値", "type": "line", "yAxisIndex": 0, "data": traj["p50"],
                "lineStyle": {"color": "#38bdf8", "width": 2.4}, "showSymbol": False,
                "markLine": mark_line_cfg,
                "markPoint": {
                    "symbolSize": 32, "label": {"fontSize": 9, "color": "#050811", "fontWeight": "bold"},
                    "data": [
                        {"name": "押目", "coord": [traj["dip_idx"], traj["dip_px"]], "value": "押目", "itemStyle": {"color": "#f59e0b"}},
                        {"name": "高値", "coord": [traj["peak_idx"], traj["peak_px"]], "value": "高値", "itemStyle": {"color": "#10b981"}}
                    ]
                }
            },
            {"name": "弱気下限", "type": "line", "yAxisIndex": 0, "data": traj["p15"], "lineStyle": {"color": "rgba(239,68,68,0.55)", "width": 1.1, "type": "dashed"}, "showSymbol": False}
        ]
        legend_names = ["予測中央値", "確率コーン(15-85%)", "想定出来高"]
        if traj["has_actual"]:
            series_list.append({"name": "当日実測", "type": "line", "yAxisIndex": 0, "data": traj["actual"], "lineStyle": {"color": "#ffffff", "width": 2.5}, "showSymbol": False})
            legend_names.insert(0, "当日実測")

        # boundaryGap: False + 非表示Y軸の領域ゼロ化で右側余白を完全解消
        opt_traj = {
            "backgroundColor": "#0b1120",
            "tooltip": {"trigger": "axis"},
            "legend": {"data": legend_names, "textStyle": {"color": "#cbd5e1", "fontSize": 9.5}, "top": 2},
            "grid": {"top": 32, "bottom": 20, "left": 4, "right": 6, "containLabel": True},
            "xAxis": {"type": "category", "boundaryGap": False, "data": traj["slots"], "axisLabel": {"color": "#94a3b8", "fontSize": 9.5, "interval": "auto", "hideOverlap": True}},
            "yAxis": [
                {"type": "value", "scale": True, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 9.5}},
                {"type": "value", "show": False, "axisLabel": {"show": False}, "axisTick": {"show": False}, "splitLine": {"show": False}, "max": max(traj["vols"] + [1]) * 4.5}
            ],
            "series": series_list
        }
        render_echarts(opt_traj, height=315)

        # 左右2分割 ＋ 確率ゲージバー付きシナリオカード
        bull_pct = (traj["bull_target"] - curr_px) / max(curr_px, 1e-4) * 100.0
        bear_pct = (traj["bear_target"] - curr_px) / max(curr_px, 1e-4) * 100.0
        st.markdown(f"""
        <div class="scenario-stack">
          <div class="sc-card" style="border-left:4px solid #10b981;">
            <div class="sc-top">
              <div class="sc-left">
                <div style="font-weight:800;color:#6ee7b7;font-size:12.5px;">強気突破シナリオ（確率 25%）</div>
                <div style="font-size:11px;color:#cbd5e1;margin-top:2px;">トリガー: <b>{fmt_currency(traj['bull_trig'], is_jp_flag)}</b> 超えで順張り追随</div>
              </div>
              <div class="sc-right">
                <div class="sc-price" style="color:#6ee7b7;">{fmt_currency(traj['bull_target'], is_jp_flag)}</div>
                <div class="sc-pct" style="color:#10b981;">{bull_pct:+.2f}%</div>
              </div>
            </div>
            <div class="sc-bar-bg"><div class="sc-bar-fill" style="width:25%;background:#10b981;"></div></div>
          </div>

          <div class="sc-card" style="border-left:4px solid #38bdf8;">
            <div class="sc-top">
              <div class="sc-left">
                <div style="font-weight:800;color:#7dd3fc;font-size:12.5px;">標準レンジシナリオ（確率 55%）</div>
                <div style="font-size:11px;color:#cbd5e1;margin-top:2px;">押し目候補: <b>{traj['dip_time']}</b> ({fmt_currency(traj['dip_px'], is_jp_flag)}) → 高値 <b>{traj['peak_time']}</b></div>
              </div>
              <div class="sc-right">
                <div class="sc-price" style="color:#7dd3fc;">{fmt_currency(traj['est_close_px'], is_jp_flag)}</div>
                <div class="sc-pct" style="color:#38bdf8;">{traj['est_close_chg']:+.2f}%</div>
              </div>
            </div>
            <div class="sc-bar-bg"><div class="sc-bar-fill" style="width:55%;background:#38bdf8;"></div></div>
          </div>

          <div class="sc-card" style="border-left:4px solid #ef4444;">
            <div class="sc-top">
              <div class="sc-left">
                <div style="font-weight:800;color:#fca5a5;font-size:12.5px;">急落警戒シナリオ（確率 20%）</div>
                <div style="font-size:11px;color:#cbd5e1;margin-top:2px;">トリガー: <b>{fmt_currency(traj['bear_trig'], is_jp_flag)}</b> 割れで撤退・下値警戒</div>
              </div>
              <div class="sc-right">
                <div class="sc-price" style="color:#fca5a5;">{fmt_currency(traj['bear_target'], is_jp_flag)}</div>
                <div class="sc-pct" style="color:#ef4444;">{bear_pct:+.2f}%</div>
              </div>
            </div>
            <div class="sc-bar-bg"><div class="sc-bar-fill" style="width:20%;background:#ef4444;"></div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        f = traj["factors"]
        st.markdown(f"""
        <div class="dark-box">
          <div style="font-size:11px;font-weight:800;color:#38bdf8;margin-bottom:5px;">FACTOR ATTRIBUTION // 軌道自動修正の内訳</div>
          <div class="factor-row"><span>主連動（{html.escape(f['mkt_label'])} {f['mkt_diff']:+.2f}% × β{f['mkt_beta']:+.2f}）</span><span style="font-family:'JetBrains Mono',monospace;color:{'#10b981' if f['macro_gap_pct']>=0 else '#ef4444'};">{f['macro_gap_pct']:+.2f}%</span></div>
          <div class="factor-row"><span>為替（ドル円 {f['fx_diff']:+.2f}% × β{f['fx_beta']:+.2f}）</span><span style="font-family:'JetBrains Mono',monospace;color:{'#10b981' if f['fx_gap_pct']>=0 else '#ef4444'};">{f['fx_gap_pct']:+.2f}%</span></div>
          <div class="factor-row"><span>日英高信頼ニュース修正（一次報道 {news_res['tier1_cnt']}件）</span><span style="font-family:'JetBrains Mono',monospace;color:{'#10b981' if f['news_gap_pct']>=0 else '#ef4444'};">{f['news_gap_pct']:+.2f}%</span></div>
          <div class="factor-row"><span>合成・明日寄付き予測 → 大引け予測</span><span style="font-family:'JetBrains Mono',monospace;color:{'#10b981' if traj['est_close_chg']>=0 else '#ef4444'};">{traj['est_open_gap_pct']:+.2f}% → {traj['est_close_chg']:+.2f}%</span></div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # TAB 2: マクロβ感応度 ＆ EPS比較バーチャート
    # ---------------------------------------------------------------------
    with tab2:
        st.markdown("##### マクロ感応度マトリクス（過去90営業日の相関・β）")
        if macro_sens:
            opt_corr = {
                "backgroundColor": "#0b1120",
                "tooltip": {"trigger": "axis"},
                "grid": {"top": 12, "bottom": 20, "left": 6, "right": 14, "containLabel": True},
                "xAxis": {"type": "value", "min": -1, "max": 1, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 9.5}},
                "yAxis": {"type": "category", "data": [x["label"] for x in macro_sens][::-1], "axisLabel": {"color": "#e2e8f0", "fontSize": 10.5}},
                "series": [{"type": "bar", "data": [{"value": x["corr"], "itemStyle": {"color": "#10b981" if x["corr"] >= 0 else "#ef4444"}} for x in macro_sens[::-1]]}]
            }
            render_echarts(opt_corr, height=220)

            rows_m = "".join([f"<tr><td><b>{html.escape(x['label'])}</b></td><td style='color:{'#10b981' if x['corr']>=0 else '#ef4444'};font-weight:700;'>{x['corr']:+.2f}</td><td>{x['beta']:+.2f}</td><td style='color:{'#10b981' if x['latest_diff']>=0 else '#ef4444'};'>{x['latest_diff']:+.2f}%</td></tr>" for x in macro_sens])
            st.markdown(f'<div class="dark-box"><div class="table-wrap"><table class="data-table"><thead><tr><th>マクロ指標</th><th>相関係数</th><th>感応度(β)</th><th>直近変動</th></tr></thead><tbody>{rows_m}</tbody></table></div></div>', unsafe_allow_html=True)

        st.markdown("##### 決算サプライズ（予想EPS vs 実績EPS）")
        eh = [e for e in data["earnings_hist"] if e["est"] is not None or e["rep"] is not None]
        if eh:
            eh_rev = eh[::-1]
            opt_eps = {
                "backgroundColor": "#0b1120",
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["予想EPS", "実績EPS"], "textStyle": {"color": "#cbd5e1", "fontSize": 10}, "top": 2},
                "grid": {"top": 30, "bottom": 20, "left": 6, "right": 10, "containLabel": True},
                "xAxis": {"type": "category", "data": [e["date"][2:7] for e in eh_rev], "axisLabel": {"color": "#94a3b8", "fontSize": 9.5}},
                "yAxis": {"type": "value", "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 9.5}},
                "series": [
                    {"name": "予想EPS", "type": "bar", "data": [e["est"] for e in eh_rev], "itemStyle": {"color": "#64748b"}},
                    {"name": "実績EPS", "type": "bar", "data": [{"value": e["rep"], "itemStyle": {"color": "#10b981" if (e["surp"] or 0) >= 0 else "#ef4444"}} for e in eh_rev]}
                ]
            }
            render_echarts(opt_eps, height=210)
        else:
            st.caption("ℹ️ この銘柄のEPSサプライズ履歴はyfinanceから取得できませんでした。")

    # ---------------------------------------------------------------------
    # TAB 3: 5軸レーダー ＋ 機関投資家・大量保有スキャン ＋ 仮想板Volume Profile
    # ---------------------------------------------------------------------
    with tab3:
        scores_5 = compute_5axis_scores(info, vp["overhead_pct"], len(gov_risks))
        opt_radar = {
            "backgroundColor": "#0b1120",
            "radar": {
                "radius": "62%",
                "indicator": [{"name": "割安性", "max": 100}, {"name": "成長性", "max": 100}, {"name": "収益性", "max": 100}, {"name": "需給軽さ", "max": 100}, {"name": "安全性", "max": 100}],
                "axisName": {"color": "#cbd5e1", "fontSize": 10.5}
            },
            "series": [{"type": "radar", "data": [{"value": scores_5, "name": "総合体力", "itemStyle": {"color": "#38bdf8"}, "areaStyle": {"color": "rgba(56,189,248,0.28)"}}]}]
        }
        render_echarts(opt_radar, height=220)

        st.markdown("##### 機関投資家・大口株主 保有構成 ＆ 大量保有スキャン")
        hb = data["holder_breakdown"]
        if hb:
            opt_donut = {
                "backgroundColor": "#0b1120",
                "tooltip": {"trigger": "item", "formatter": "{b}: {c}%"},
                "legend": {"bottom": 2, "textStyle": {"color": "#cbd5e1", "fontSize": 10}},
                "series": [{
                    "type": "pie", "radius": ["42%", "68%"], "center": ["50%", "44%"],
                    "label": {"show": True, "formatter": "{c}%", "color": "#fff", "fontSize": 10},
                    "data": [
                        {"value": hb["inst"], "name": "機関投資家", "itemStyle": {"color": "#38bdf8"}},
                        {"value": hb["insider"], "name": "役員・大株主", "itemStyle": {"color": "#a855f7"}},
                        {"value": hb["public"], "name": "一般浮動株", "itemStyle": {"color": "#475569"}}
                    ]
                }]
            }
            render_echarts(opt_donut, height=205)

        inst_h = data["inst_holders"]
        if inst_h:
            opt_ih = {
                "backgroundColor": "#0b1120",
                "tooltip": {"trigger": "axis"},
                "grid": {"top": 10, "bottom": 20, "left": 6, "right": 14, "containLabel": True},
                "xAxis": {"type": "value", "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 9.5, "formatter": "{value}%"}},
                "yAxis": {"type": "category", "data": [x["holder"][:18] for x in inst_h][::-1], "axisLabel": {"color": "#e2e8f0", "fontSize": 9.5}},
                "series": [{"name": "保有比率", "type": "bar", "data": [round(x["pct"], 2) for x in inst_h][::-1], "itemStyle": {"color": "#10b981"}}]
            }
            render_echarts(opt_ih, height=190)

            rows_h = "".join([f"<tr><td>{html.escape(x['holder'])}</td><td><b>{x['pct']:.2f}%</b></td><td style='font-family:monospace;'>{x['shares']:,}</td></tr>" for x in inst_h])
            st.markdown(f'<div class="dark-box"><div class="table-wrap"><table class="data-table"><thead><tr><th>大口機関投資家</th><th>保有比率</th><th>保有株数</th></tr></thead><tbody>{rows_h}</tbody></table></div></div>', unsafe_allow_html=True)
        elif is_jp_flag:
            st.link_button(f"🏛️ 株探で {short_code} の大株主一覧を見る", f"https://kabutan.jp/stock/holder?code={short_code}", use_container_width=True)

        # 大量保有報告書(5%ルール)・機関空売り動向スキャン
        if whale_news:
            w_html = "".join([f'<div style="margin-bottom:6px;"><a href="{html.escape(x["link"])}" target="_blank" style="color:#7dd3fc;text-decoration:none;font-weight:600;">・{html.escape(x["title"])}</a> <span style="color:#64748b;font-size:10px;">({html.escape(x["pub"])})</span></div>' for x in whale_news])
            st.markdown(f'<div class="dark-box"><b>WHALE TRACKER // 大量保有(5%ルール)・機関空売り最新動向</b><br><br>{w_html}</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="dark-box">
          <b>VIRTUAL ORDERBOOK // 仮想板・抵抗＆支持マップ（1年実測）</b><br>
          ・<span style="color:#fca5a5;">大口売り壁（抵抗帯）:</span> <b>{fmt_currency(vp['res_px'], is_jp_flag)}</b><br>
          ・<span style="color:#38bdf8;">最大出来高帯 (POC):</span> <b>{fmt_currency(vp['poc_px'], is_jp_flag)}</b><br>
          ・<span style="color:#6ee7b7;">大口買い支え（支持帯）:</span> <b>{fmt_currency(vp['sup_px'], is_jp_flag)}</b>
        </div>
        """, unsafe_allow_html=True)

        if vp["labels"]:
            opt_vp = {
                "backgroundColor": "#0b1120",
                "tooltip": {"trigger": "axis"},
                "grid": {"top": 10, "bottom": 20, "left": 6, "right": 14, "containLabel": True},
                "xAxis": {"type": "value", "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 9.5}},
                "yAxis": {"type": "category", "data": vp["labels"], "axisLabel": {"color": "#cbd5e1", "fontSize": 9.5}},
                "series": [{"name": "出来高(M)", "type": "bar", "data": vp["vols"], "itemStyle": {"color": "#a855f7"}}]
            }
            render_echarts(opt_vp, height=235)

    # ---------------------------------------------------------------------
    # TAB 4: CNN風リアル計器メーター ＋ 自動AIメモ ＋ 日英高信頼フィード
    # ---------------------------------------------------------------------
    with tab4:
        opt_gauge = {
            "backgroundColor": "#0b1120",
            "series": [{
                "type": "gauge", "startAngle": 180, "endAngle": 0, "min": 0, "max": 100, "splitNumber": 5,
                "center": ["50%", "74%"], "radius": "112%",
                "axisLine": {"lineStyle": {"width": 16, "color": [[0.2, "#dc2626"], [0.4, "#f97316"], [0.6, "#38bdf8"], [0.8, "#10b981"], [1.0, "#059669"]]}},
                "pointer": {
                    "icon": "path://M12.8,0.7l12,40.1H0.7L12.8,0.7z", "length": "52%", "width": 10, "offsetCenter": [0, "-12%"],
                    "itemStyle": {"color": "#f8fafc", "shadowBlur": 8, "shadowColor": "rgba(56,189,248,0.8)"}
                },
                "anchor": {"show": True, "showAbove": True, "size": 14, "itemStyle": {"color": "#38bdf8", "borderWidth": 2, "borderColor": "#fff"}},
                "axisTick": {"length": 6, "lineStyle": {"color": "auto", "width": 1.5}},
                "splitLine": {"length": 12, "lineStyle": {"color": "auto", "width": 2.5}},
                "axisLabel": {"color": "#94a3b8", "fontSize": 9.5, "distance": -36},
                "title": {"offsetCenter": [0, "18%"], "fontSize": 10.5, "color": "#7dd3fc", "fontWeight": "bold"},
                "detail": {"fontSize": 26, "fontWeight": "bold", "offsetCenter": [0, "-3%"], "valueAnimation": True, "color": "#ffffff", "formatter": "{value}"},
                "data": [{"value": comp_score, "name": meter_lbl}]
            }]
        }
        render_echarts(opt_gauge, height=225)

        top_m = macro_sens[0] if macro_sens else {"label": "市場指数", "corr": 0.0, "beta": 1.0}
        m_txt, m_src = generate_auto_investment_memo(
            fc_code, corp_name, fmt_currency(curr_px, is_jp_flag),
            traj["est_open_gap_pct"], traj["est_close_chg"], traj["dip_time"], traj["peak_time"],
            vp["overhead_pct"], top_m["label"], top_m["corr"], top_m["beta"],
            news_res["pos_pct"], news_res["tier1_cnt"], len(gov_risks), upside_str
        )
        st.markdown(f'<div class="memo-box"><div style="font-size:10.5px;color:#c084fc;font-weight:800;margin-bottom:5px;">{html.escape(m_src)}</div>{html.escape(m_txt).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

        if gov_risks:
            risk_html = "<br>".join([f"・{html.escape(x)}" for x in gov_risks])
            st.markdown(f'<div class="warning-box"><b>ガバナンス・不祥事・訴訟関連ヒット ({len(gov_risks)}件)</b><br>{risk_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="quant-box"><b>ガバナンス・不祥事監査: クリーン</b><br>直近ニュースにおいて不祥事・不正・訴訟などの特異リスクシグナルは検知されていません。</div>', unsafe_allow_html=True)

        if news_res["items"]:
            n_html = ""
            for it in news_res["items"]:
                sc = "#10b981" if it["sent"] == "POS" else ("#ef4444" if it["sent"] == "NEG" else "#94a3b8")
                tc = "#fde047" if it["trust"] == "S" else ("#38bdf8" if it["trust"] == "A" else "#64748b")
                n_html += (
                    f'<div style="margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid rgba(148,163,184,0.12);">'
                    f'<span style="color:{tc};font-weight:800;font-size:10px;border:1px solid {tc};padding:0 4px;border-radius:3px;margin-right:4px;">信頼度{it["trust"]}/{it["lang"]}</span>'
                    f'<span style="color:{sc};font-weight:800;font-size:10px;margin-right:4px;">[{it["sent"]}]</span>'
                    f'<a href="{html.escape(it["link"])}" target="_blank" style="color:#e2e8f0;text-decoration:none;font-weight:600;">{html.escape(it["title"])}</a> '
                    f'<span style="color:#64748b;font-size:10px;">({html.escape(it["source"] or "Wire")} / {html.escape(it["pub"])})</span></div>'
                )
            st.markdown(f'<div class="dark-box"><b>GLOBAL INTELLIGENCE FEED // 日英高信頼ニュース（一次報道 {news_res["tier1_cnt"]}件）</b><br><br>{n_html}</div>', unsafe_allow_html=True)

if hasattr(st, "fragment"):
    @st.fragment(run_every="60s")
    def _auto_live_runner():
        render_live_terminal(fc, in_style, is_jp)
    _auto_live_runner()
else:
    render_live_terminal(fc, in_style, is_jp)
