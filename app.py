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

# =========================================================================
# 0. 基本設定（LABアプリのURLを書き換えてください）
# =========================================================================
LAB_APP_URL = "https://your-yamashishi-lab.streamlit.app/"

st.set_page_config(
    page_title="YAMASHISHI DEEP DIVE v5 [LIVE QUANTUM TERMINAL]",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================================
# 1. スタイリング（スマホ完全最適化 ＋ LAB統一ダークUI ＋ ↑TOPボタン）
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
    .scenario-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 6px;
        margin-bottom: 10px;
    }
    @media (max-width: 640px) {
        .scenario-grid { grid-template-columns: 1fr; }
    }
    .scenario-card {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 8px;
        padding: 9px 10px;
        font-size: 11.5px;
        line-height: 1.5;
    }
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
    .timeline-item {
        border-left: 2px solid #38bdf8;
        padding-left: 9px;
        margin-bottom: 7px;
        font-size: 11.5px;
        line-height: 1.5;
    }
    .table-wrap { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 11px; margin-top: 4px; min-width: 310px; }
    .data-table th {
        background: #1e293b; color: #38bdf8; padding: 6px 7px; text-align: left;
        border-bottom: 1px solid rgba(56, 189, 248, 0.3); white-space: nowrap;
    }
    .data-table td {
        padding: 6px 7px; border-bottom: 1px solid rgba(148, 163, 184, 0.12); color: #e2e8f0;
    }
    .floating-top-btn {
        position: fixed;
        bottom: 18px;
        right: 16px;
        z-index: 99999;
        background: rgba(15, 23, 42, 0.88);
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.6);
        border-radius: 99px;
        padding: 7px 13px;
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
# 2. フォーマット ＆ ビジュアルヘルパー（横幅ズレ完全対策済み）
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
    """ResizeObserver搭載でタブ切替・スマホ幅でも横幅が絶対に崩れないEChartsラッパー"""
    opt_json = json.dumps(option_dict, ensure_ascii=False)
    html_code = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
      html, body {{ width: 100%; height: 100%; margin: 0; padding: 0; background: #0b1120; overflow: hidden; }}
      #c {{ width: 100vw; max-width: 100%; height: {height}px; }}
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
      setTimeout(doResize, 120);
      setTimeout(doResize, 400);
    </script></body></html>
    """
    components.html(html_code, height=height + 4)

def render_live_clock_bar(sync_interval: int = 30):
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
      <div class="right">AUTO-SYNC <span id="cd" class="cnt">{sync_interval}s</span></div>
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
    if len(prices) < 2:
        return ""
    p_min, p_max = float(np.min(prices)), float(np.max(prices))
    span = max(p_max - p_min, 1e-4)
    w, h = 92.0, 26.0
    pts = []
    for i, p in enumerate(prices):
        x = round((i / max(len(prices) - 1, 1)) * w, 1)
        y = round(h - 2.0 - ((float(p) - p_min) / span) * (h - 4.0), 1)
        pts.append(f"{x},{y}")
    col = "#10b981" if prices[-1] >= prices[0] else "#ef4444"
    return f'<svg width="92" height="26" viewBox="0 0 92 26" style="display:block;margin-left:auto;"><polyline fill="none" stroke="{col}" stroke-width="1.8" points="{" ".join(pts)}"/></svg>'

# =========================================================================
# 3. キャッシュ分離型データ取得関数
# =========================================================================
MACRO_TICKERS = {
    "SOX": ("^SOX", "米SOX指数"),
    "SP500": ("^GSPC", "S&P500"),
    "N225": ("^N225", "日経平均"),
    "USDJPY": ("JPY=X", "ドル円"),
    "US10Y": ("^TNX", "米10年債金利"),
    "OIL": ("CL=F", "WTI原油"),
    "VIX": ("^VIX", "VIX恐怖指数"),
}

@st.cache_data(ttl=60)
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
                    diff_pct = (last_c - prev_c) / max(abs(prev_c), 1e-4) * 100.0
                    out[k] = {"label": label, "last": last_c, "diff_pct": round(diff_pct, 2), "series": closes}
            except Exception:
                pass
    except Exception:
        pass
    return out

@st.cache_data(ttl=45)
def load_stock_core(code: str) -> dict:
    tkr = yf.Ticker(code)
    df_1d = tkr.history(period="1y", interval="1d", auto_adjust=True)
    if df_1d is not None and not df_1d.empty:
        df_1d.index = pd.to_datetime(df_1d.index).tz_localize(None).normalize()
        df_1d = df_1d[~df_1d.index.duplicated(keep="last")]

    df_5m = tkr.history(period="1mo", interval="5m", auto_adjust=True)
    if df_5m is not None and not df_5m.empty:
        df_5m = df_5m.dropna(subset=["Close"]).copy()

    try:
        info = tkr.info or {}
    except Exception:
        info = {}

    q_fin = []
    try:
        qf = tkr.quarterly_financials
        if qf is not None and not qf.empty:
            for col in list(qf.columns)[:4][::-1]:
                dt_lbl = col.strftime("%Y/%m") if hasattr(col, "strftime") else str(col)[:7]
                rev = qf.loc["Total Revenue", col] if "Total Revenue" in qf.index else None
                ni = qf.loc["Net Income", col] if "Net Income" in qf.index else None
                q_fin.append({
                    "period": dt_lbl,
                    "revenue": float(rev) if pd.notna(rev) else 0.0,
                    "net_income": float(ni) if pd.notna(ni) else 0.0
                })
    except Exception:
        pass

    earnings_hist = []
    try:
        ed = tkr.earnings_dates
        if ed is not None and not ed.empty:
            ed_clean = ed.dropna(subset=["EPS Estimate", "Reported EPS"], how="all").head(6)
            for idx_dt, row in ed_clean.iterrows():
                dt_s = idx_dt.strftime("%Y-%m-%d") if hasattr(idx_dt, "strftime") else str(idx_dt)[:10]
                est = float(row["EPS Estimate"]) if pd.notna(row.get("EPS Estimate")) else None
                rep = float(row["Reported EPS"]) if pd.notna(row.get("Reported EPS")) else None
                surp = float(row["Surprise(%)"]) if pd.notna(row.get("Surprise(%)")) else None
                earnings_hist.append({"date": dt_s, "est": est, "rep": rep, "surp": surp})
    except Exception:
        pass

    # 保有構成（機関 vs インサイダー vs 一般浮動株）
    holder_breakdown = None
    try:
        inst_p = info.get("heldPercentInstitutions")
        ins_p = info.get("heldPercentInsiders")
        if inst_p is not None or ins_p is not None:
            i_val = round(float(inst_p or 0.0) * 100.0, 1)
            in_val = round(float(ins_p or 0.0) * 100.0, 1)
            pub_val = round(max(0.0, 100.0 - i_val - in_val), 1)
            holder_breakdown = {"inst": i_val, "insider": in_val, "public": pub_val}
    except Exception:
        pass

    # 大口機関投資家トップ5
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
        "df_1d": df_1d, "df_5m": df_5m, "info": info, "q_fin": q_fin,
        "earnings_hist": earnings_hist, "holder_breakdown": holder_breakdown,
        "inst_holders": inst_holders
    }

@st.cache_data(ttl=90)
def fetch_news_and_sentiment(query: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}
    items_out = []
    pos_words = ["上昇", "急騰", "最高益", "上方修正", "増配", "自社株買い", "好調", "提携", "突破", "買い", "黒字", "成長", "目標株価引き上げ"]
    neg_words = ["下落", "急落", "下方修正", "赤字", "減益", "不祥事", "訴訟", "不正", "辞任", "炎上", "懸念", "売り", "リスク", "目標株価引き下げ"]
    pos_c, neu_c, neg_c = 0, 0, 0
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ja&gl=JP&ceid=JP:ja"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=4.0) as r:
            root = ET.fromstring(r.read())
            for it in root.findall("./channel/item")[:10]:
                t = (it.findtext("title") or "").strip()
                link = (it.findtext("link") or "").strip()
                pub = (it.findtext("pubDate") or "").strip()[:16]
                if not t: continue
                p_hit = sum(1 for w in pos_words if w in t)
                n_hit = sum(1 for w in neg_words if w in t)
                if p_hit > n_hit: sent = "POS"; pos_c += 1
                elif n_hit > p_hit: sent = "NEG"; neg_c += 1
                else: sent = "NEU"; neu_c += 1
                items_out.append({"title": t, "link": link, "pub": pub, "sent": sent})
    except Exception:
        pass

    tot = max(pos_c + neu_c + neg_c, 1)
    shock_score = round((pos_c - neg_c) / tot, 2)
    return {
        "items": items_out, "pos_pct": round(pos_c / tot * 100),
        "neu_pct": round(neu_c / tot * 100), "neg_pct": round(neg_c / tot * 100),
        "counts": (pos_c, neu_c, neg_c), "shock_score": shock_score
    }

@st.cache_data(ttl=180)
def fetch_governance_risks(company_name: str) -> list:
    headers = {"User-Agent": "Mozilla/5.0"}
    risks = []
    q = f"{company_name} (不祥事 OR 不正 OR 訴訟 OR 行政処分 OR 辞任 OR リコール)"
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=ja&gl=JP&ceid=JP:ja"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=4.0) as r:
            root = ET.fromstring(r.read())
            for it in root.findall("./channel/item")[:5]:
                t = (it.findtext("title") or "").strip()
                pub = (it.findtext("pubDate") or "").strip()[:16]
                if t: risks.append(f"{t} ({pub})")
    except Exception:
        pass
    return risks

# =========================================================================
# 4. アルゴリズムエンジン（指数減衰ウェイト5分足軌道・VIX連動・AIメモ自動キャッシュ）
# =========================================================================
def compute_macro_sensitivity(stock_close: pd.Series, macro_data: dict) -> list:
    s_ret = stock_close.pct_change().dropna().tail(90)
    results = []
    for k, m in macro_data.items():
        if k == "VIX": continue
        m_ret = m["series"].pct_change().dropna()
        joined = pd.concat([s_ret.rename("stk"), m_ret.rename("mac")], axis=1).dropna()
        if len(joined) >= 20:
            corr = float(joined["stk"].corr(joined["mac"]))
            var_m = float(joined["mac"].var())
            beta = float(joined["stk"].cov(joined["mac"]) / var_m) if var_m > 1e-9 else 0.0
            if np.isnan(corr): corr = 0.0
            if np.isnan(beta): beta = 0.0
            results.append({
                "key": k, "label": m["label"], "corr": round(corr, 2),
                "beta": round(beta, 2), "latest_diff": m["diff_pct"]
            })
    results.sort(key=lambda x: abs(x["corr"]), reverse=True)
    return results

def build_5m_realtime_trajectory(
    curr_px: float, df_5m: pd.DataFrame, macro_sens: list, macro_data: dict, news_res: dict, is_jp: bool
) -> dict:
    if is_jp:
        am = [f"{h:02d}:{m:02d}" for h in range(9, 12) for m in range(0, 60, 5) if not (h == 11 and m > 30)]
        pm = [f"{h:02d}:{m:02d}" for h in range(12, 16) for m in range(0, 60, 5) if not (h == 12 and m < 30) and not (h == 15 and m > 30)]
        slots = am + pm
        lunch_idx = len(am) - 1
    else:
        slots = [f"{h:02d}:{m:02d}" for h in range(9, 17) for m in range(0, 60, 5) if not (h == 9 and m < 30) and not (h == 16 and m > 0)]
        lunch_idx = None

    n_slots = len(slots)
    slot_means = np.zeros(n_slots)
    slot_stds = np.full(n_slots, 0.003)
    slot_vols = np.zeros(n_slots)
    actual_today_map = {}

    if df_5m is not None and not df_5m.empty:
        tmp = df_5m.copy()
        idx_dt = pd.to_datetime(tmp.index)
        tmp["_d"] = idx_dt.strftime("%Y-%m-%d")
        tmp["_hm"] = idx_dt.strftime("%H:%M")

        unique_days = sorted(tmp["_d"].unique().tolist())
        past_days = unique_days[:-1]
        day_ret_maps, day_vol_maps, day_weights = [], [], []

        # 直近重視の指数減衰ウェイト（新しい日ほど重みが大きい）
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
                day_ret_maps.append(r_map)
                day_vol_maps.append(v_map)
                w = np.exp(1.2 * (d_idx / max(n_past - 1, 1)))
                day_weights.append(float(w))

        for i, sl in enumerate(slots):
            r_vals, w_vals, v_vals = [], [], []
            for rm, vm, w in zip(day_ret_maps, day_vol_maps, day_weights):
                if sl in rm:
                    r_vals.append(rm[sl])
                    w_vals.append(w)
                    v_vals.append(vm[sl])
            if len(r_vals) >= 3:
                w_arr = np.array(w_vals) / np.sum(w_vals)
                r_arr = np.array(r_vals)
                w_mean = float(np.sum(w_arr * r_arr))
                w_std = float(np.sqrt(np.sum(w_arr * ((r_arr - w_mean) ** 2))))
                slot_means[i] = w_mean
                slot_stds[i] = max(w_std, 0.0025)
                slot_vols[i] = float(np.mean(v_vals)) if v_vals else 0.0
            else:
                slot_stds[i] = 0.003 + 0.009 * np.sqrt((i + 1) / n_slots)
                u_pos = (i / max(n_slots - 1, 1)) * 2.0 - 1.0
                slot_vols[i] = 100.0 * (0.4 + 1.4 * (u_pos ** 2))

        today_jst = datetime.datetime.now().strftime("%Y-%m-%d")
        if unique_days and unique_days[-1] == today_jst:
            sub_t = tmp[tmp["_d"] == today_jst]
            for _, row in sub_t.iterrows():
                if row["_hm"] in slots:
                    actual_today_map[row["_hm"]] = round(float(row["Close"]), 2)

    # マクロβ ＆ ニュース ＆ VIXボラ連動補正
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
    vix_boost = 1.0 + max(0.0, vix_diff / 100.0) * 1.2
    vol_boost = (1.0 + abs(news_res["shock_score"]) * 0.30) * vix_boost

    p50_arr, p85_arr, p15_arr, band_diff_arr, actual_arr = [], [], [], [], []
    for i, sl in enumerate(slots):
        frac = i / max(n_slots - 1, 1)
        mid = est_open_px * (1.0 + slot_means[i] + intraday_drift * frac)
        band = est_open_px * slot_stds[i] * vol_boost * 1.15
        lo_v = max(mid - band, curr_px * 0.5)
        hi_v = mid + band
        p50_arr.append(round(float(mid), 2))
        p85_arr.append(round(float(hi_v), 2))
        p15_arr.append(round(float(lo_v), 2))
        band_diff_arr.append(round(float(hi_v - lo_v), 2))
        actual_arr.append(actual_today_map.get(sl, None))

    idx_min = int(np.argmin(p50_arr))
    idx_max = int(np.argmax(p50_arr))
    est_close_px = p50_arr[-1]
    est_close_chg = round((est_close_px - curr_px) / max(curr_px, 1e-4) * 100.0, 2)

    return {
        "slots": slots, "lunch_idx": lunch_idx,
        "p50": p50_arr, "p85": p85_arr, "p15": p15_arr, "band_diff": band_diff_arr,
        "vols": [round(float(v), 1) for v in slot_vols],
        "actual": actual_arr, "has_actual": any(x is not None for x in actual_arr),
        "est_open_px": est_open_px, "est_open_gap_pct": round(total_open_gap_pct, 2),
        "est_close_px": est_close_px, "est_close_chg": est_close_chg,
        "dip_idx": idx_min, "dip_time": slots[idx_min], "dip_px": p50_arr[idx_min],
        "peak_idx": idx_max, "peak_time": slots[idx_max], "peak_px": p50_arr[idx_max],
        "bull_trig": round(p85_arr[min(3, n_slots - 1)], 2),
        "bear_trig": round(p15_arr[min(3, n_slots - 1)], 2),
        "factors": {
            "mkt_label": mkt_info["label"], "mkt_diff": mkt_info["latest_diff"],
            "mkt_beta": mkt_info["beta"], "macro_gap_pct": round(macro_gap_pct, 2),
            "fx_diff": fx_info["latest_diff"], "fx_beta": fx_info["beta"],
            "fx_gap_pct": round(fx_gap_pct, 2), "news_shock": news_res["shock_score"],
            "news_gap_pct": round(news_gap_pct, 2),
        }
    }

def compute_volume_profile_detail(df_1d: pd.DataFrame, curr_px: float, is_jp: bool) -> dict:
    sub = df_1d.tail(250)
    if len(sub) < 20:
        return {"overhead_pct": 0.0, "poc_px": curr_px, "labels": [], "vols": [], "res_px": curr_px, "sup_px": curr_px}
    typ = (sub["High"].values + sub["Low"].values + sub["Close"].values) / 3.0
    vol = sub["Volume"].values.astype(float)
    tot_v = max(float(np.sum(vol)), 1.0)
    above_v = float(np.sum(vol[typ > curr_px * 1.01]))

    bins = np.linspace(float(np.min(typ)), float(np.max(typ)) + 1e-4, 15)
    hist = np.bincount(np.clip(np.digitize(typ, bins) - 1, 0, 13), weights=vol, minlength=14)
    centers = [(bins[i] + bins[i + 1]) * 0.5 for i in range(14)]
    poc_idx = int(np.argmax(hist))

    above_idxs = [i for i, c in enumerate(centers) if c > curr_px * 1.005]
    below_idxs = [i for i, c in enumerate(centers) if c < curr_px * 0.995]
    res_px = centers[max(above_idxs, key=lambda i: hist[i])] if above_idxs else curr_px * 1.05
    sup_px = centers[max(below_idxs, key=lambda i: hist[i])] if below_idxs else curr_px * 0.95

    return {
        "overhead_pct": round(above_v / tot_v * 100.0, 1),
        "poc_px": float(centers[poc_idx]),
        "labels": [fmt_currency(c, is_jp) for c in centers],
        "vols": [round(float(v) / 1e6, 2) for v in hist],
        "res_px": float(res_px),
        "sup_px": float(sup_px)
    }

def compute_5axis_scores(info: dict, ovh_pct: float, gov_cnt: int) -> list:
    pe = info.get("trailingPE")
    val_sc = int(np.clip(100 - (pe - 10) * 1.5, 25, 95)) if pe and pe > 0 else 55
    rev_g = info.get("revenueGrowth")
    gro_sc = int(np.clip(55 + rev_g * 120, 20, 98)) if rev_g is not None else 55
    roe = info.get("returnOnEquity")
    prf_sc = int(np.clip(45 + roe * 160, 20, 98)) if roe is not None else 55
    sup_sc = int(np.clip(95 - ovh_pct * 0.85, 20, 95))
    saf_sc = int(np.clip(95 - gov_cnt * 18, 25, 98))
    return [val_sc, gro_sc, prf_sc, sup_sc, saf_sc]

@st.cache_data(ttl=600)
def generate_auto_investment_memo(
    fc: str, corp_name: str, curr_px_str: str, open_gap: float, close_chg: float,
    dip_time: str, peak_time: str, ovh_pct: float, top_m_lbl: str, top_m_corr: float,
    top_m_beta: float, pos_pct: int, gov_cnt: int, upside_s: str
) -> tuple:
    """10分間キャッシュで自動生成（30秒ライブ更新でもAPIを無駄打ちしない）"""
    api_key = get_gemini_api_key()
    prompt = f"""あなたはヘッジファンドのシニア・エクイティアナリストです。以下の実測データに基づき、ファンドマネージャー向けの「1分インベストメントメモ」を日本語で簡潔に作成してください。
銘柄: {corp_name} ({fc}) / 現在値: {curr_px_str} / アナリスト乖離: {upside_s}
翌営業日予測: 寄付き {open_gap:+.2f}% / 大引け予測 {close_chg:+.2f}% / 押し目 {dip_time} / ピーク {peak_time}
上値しこり玉: {ovh_pct}% / 最大マクロ連動: {top_m_lbl} (相関 {top_m_corr}, β={top_m_beta})
ニュース強気度: {pos_pct}% / ガバナンスリスク検知: {gov_cnt}件

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
                        return txt.strip(), f"🔵 AUTO AI ANALYST ({mod})"
            except Exception:
                continue

    bull = f"・アナリスト目標乖離 {upside_s}、翌営業日の大引け予測 {close_chg:+.2f}%。\n・ニュース強気度 {pos_pct}%、上値しこり玉 {ovh_pct}%。"
    bear = f"・{top_m_lbl}との相関係数 {top_m_corr}（β={top_m_beta}）でマクロ急変時の連れ安リスクあり。\n・ガバナンス報道は {gov_cnt}件検知（{'要精査' if gov_cnt else '現時点でクリーン'}）。"
    cat = f"・明日は {dip_time} 頃の押し目反発と {peak_time} 頃のピーク形成が焦点。"
    return f"🟢 Bull Case（強気シナリオ）\n{bull}\n\n🔴 Bear Case（弱気・死角リスク）\n{bear}\n\n⚡ Next Catalyst（次の注目トリガー）\n{cat}", "⚙️ AUTO QUANT MEMO（実測データ自動生成）"

# =========================================================================
# 5. 固定ヘッダー ＆ 入力コントロール
# =========================================================================
h_col1, h_col2 = st.columns([3.1, 1.3])
with h_col1:
    st.markdown(
        '<div class="glass-header" style="margin-bottom:6px;">'
        '<div class="brand-luxury">YAMASHISHI DEEP DIVE v5</div>'
        '<div style="font-size:10.5px;color:#94a3b8;margin-top:2px;">5分刻み確率コーン軌道 × 自動AI監査 × 大口株主トラッカー</div>'
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
# 6. 自動ライブ更新セクション（30秒ごとに裏で自動同期＋秒刻み時計）
# =========================================================================
def render_live_terminal(fc_code: str, style_name: str, is_jp_flag: bool):
    render_live_clock_bar(sync_interval=30)

    with st.spinner(f"📡 【{fc_code}】の5分足波形・マクロ・大口株主・ニュースをライブ同期中..."):
        data = load_stock_core(fc_code)
        macro_data = load_macro_data()

    df_1d, df_5m, info = data["df_1d"], data["df_5m"], data["info"]
    if df_1d is None or df_1d.empty:
        st.error(f"❌ 銘柄コード `{fc_code}` の市場データを取得できませんでした。")
        return

    corp_name = info.get("longName") or info.get("shortName") or fc_code
    sector = info.get("sector") or "セクター未分類"
    industry = info.get("industry") or "-"
    curr_px = float(df_1d["Close"].iloc[-1])
    prev_px = float(df_1d["Close"].iloc[-2]) if len(df_1d) >= 2 else curr_px
    chg_pct = ((curr_px - prev_px) / max(prev_px, 1e-4)) * 100.0
    chg_col = "#10b981" if chg_pct >= 0 else "#ef4444"

    macro_sens = compute_macro_sensitivity(df_1d["Close"], macro_data)
    news_res = fetch_news_and_sentiment(f"{corp_name} OR {fc_code.replace('.T', '')} 株価")
    gov_risks = fetch_governance_risks(corp_name)
    vp = compute_volume_profile_detail(df_1d, curr_px, is_jp_flag)
    traj = build_5m_realtime_trajectory(curr_px, df_5m, macro_sens, macro_data, news_res, is_jp_flag)

    # 総合リスク＆センチメント指数（ニュース感情 - ガバナンス減点）
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

    # --- リッチ化された銘柄トップカード ---
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

    # --- 4タブ集約ビュー ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "翌営業日 1日軌道",
        "マクロβ・決算",
        "財務・大口株主",
        "リスク・AIメモ"
    ])

    # ---------------------------------------------------------------------
    # TAB 1: 5分刻み翌営業日1日軌道（確率コーン塗りつぶし＋前場後場区切り）
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
            {
                "name": "想定出来高", "type": "bar", "yAxisIndex": 1, "data": traj["vols"],
                "itemStyle": {"color": "rgba(148,163,184,0.16)"}, "barMaxWidth": 5
            },
            # 確率コーン塗りつぶし用ベース（透明）
            {
                "name": "下限ベース", "type": "line", "yAxisIndex": 0, "data": traj["p15"],
                "stack": "cone", "lineStyle": {"opacity": 0}, "showSymbol": False, "silent": True
            },
            # 確率コーン帯（15%〜85%の半透明ブルー塗りつぶし）
            {
                "name": "確率コーン(15-85%)", "type": "line", "yAxisIndex": 0, "data": traj["band_diff"],
                "stack": "cone", "lineStyle": {"opacity": 0},
                "areaStyle": {"color": "rgba(56, 189, 248, 0.16)"}, "showSymbol": False, "silent": True
            },
            {
                "name": "強気上限", "type": "line", "yAxisIndex": 0, "data": traj["p85"],
                "lineStyle": {"color": "rgba(16,185,129,0.6)", "width": 1.1, "type": "dashed"}, "showSymbol": False
            },
            {
                "name": "予測中央値", "type": "line", "yAxisIndex": 0, "data": traj["p50"],
                "lineStyle": {"color": "#38bdf8", "width": 2.4}, "showSymbol": False,
                "markLine": mark_line_cfg,
                "markPoint": {
                    "symbolSize": 34, "label": {"fontSize": 9, "color": "#050811", "fontWeight": "bold"},
                    "data": [
                        {"name": "押目", "coord": [traj["dip_idx"], traj["dip_px"]], "value": "押目", "itemStyle": {"color": "#f59e0b"}},
                        {"name": "高値", "coord": [traj["peak_idx"], traj["peak_px"]], "value": "高値", "itemStyle": {"color": "#10b981"}}
                    ]
                }
            },
            {
                "name": "弱気下限", "type": "line", "yAxisIndex": 0, "data": traj["p15"],
                "lineStyle": {"color": "rgba(239,68,68,0.6)", "width": 1.1, "type": "dashed"}, "showSymbol": False
            }
        ]
        legend_names = ["予測中央値", "確率コーン(15-85%)", "想定出来高"]
        if traj["has_actual"]:
            series_list.append({"name": "当日実測", "type": "line", "yAxisIndex": 0, "data": traj["actual"], "lineStyle": {"color": "#ffffff", "width": 2.5}, "showSymbol": False})
            legend_names.insert(0, "当日実測")

        opt_traj = {
            "backgroundColor": "#0b1120",
            "tooltip": {"trigger": "axis"},
            "legend": {"data": legend_names, "textStyle": {"color": "#cbd5e1", "fontSize": 9.5}, "top": 2},
            "grid": {"top": 34, "bottom": 22, "left": 6, "right": 8, "containLabel": True},
            "xAxis": {"type": "category", "data": traj["slots"], "axisLabel": {"color": "#94a3b8", "fontSize": 9.5, "interval": "auto", "hideOverlap": True}},
            "yAxis": [
                {"type": "value", "scale": True, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 9.5}},
                {"type": "value", "show": False, "max": max(traj["vols"] + [1]) * 4.5}
            ],
            "series": series_list
        }
        render_echarts(opt_traj, height=315)

        st.markdown(f"""
        <div class="scenario-grid">
          <div class="scenario-card" style="border-top:3px solid #10b981;">
            <div style="font-weight:800;color:#6ee7b7;">強気突破 (確率 25%)</div>
            <div style="color:#cbd5e1;margin-top:3px;">トリガー: <b>{fmt_currency(traj['bull_trig'], is_jp_flag)}</b> 超え<br>上値目安: <b>{fmt_currency(max(traj['p85']), is_jp_flag)}</b></div>
          </div>
          <div class="scenario-card" style="border-top:3px solid #38bdf8;">
            <div style="font-weight:800;color:#7dd3fc;">標準レンジ (確率 55%)</div>
            <div style="color:#cbd5e1;margin-top:3px;">押し目: <b>{traj['dip_time']}</b> ({fmt_currency(traj['dip_px'], is_jp_flag)})<br>大引け: <b>{fmt_currency(traj['est_close_px'], is_jp_flag)}</b></div>
          </div>
          <div class="scenario-card" style="border-top:3px solid #ef4444;">
            <div style="font-weight:800;color:#fca5a5;">急落警戒 (確率 20%)</div>
            <div style="color:#cbd5e1;margin-top:3px;">トリガー: <b>{fmt_currency(traj['bear_trig'], is_jp_flag)}</b> 割れ<br>下値目安: <b>{fmt_currency(min(traj['p15']), is_jp_flag)}</b></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        f = traj["factors"]
        st.markdown(f"""
        <div class="dark-box">
          <div style="font-size:11px;font-weight:800;color:#38bdf8;margin-bottom:5px;">FACTOR ATTRIBUTION // 軌道自動修正の内訳</div>
          <div class="factor-row"><span>主連動（{html.escape(f['mkt_label'])} {f['mkt_diff']:+.2f}% × β{f['mkt_beta']:+.2f}）</span><span style="font-family:'JetBrains Mono',monospace;color:{'#10b981' if f['macro_gap_pct']>=0 else '#ef4444'};">{f['macro_gap_pct']:+.2f}%</span></div>
          <div class="factor-row"><span>為替（ドル円 {f['fx_diff']:+.2f}% × β{f['fx_beta']:+.2f}）</span><span style="font-family:'JetBrains Mono',monospace;color:{'#10b981' if f['fx_gap_pct']>=0 else '#ef4444'};">{f['fx_gap_pct']:+.2f}%</span></div>
          <div class="factor-row"><span>最新ニュース修正（強気度 {news_res['pos_pct']}%）</span><span style="font-family:'JetBrains Mono',monospace;color:{'#10b981' if f['news_gap_pct']>=0 else '#ef4444'};">{f['news_gap_pct']:+.2f}%</span></div>
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
    # TAB 3: 5軸レーダー ＋ 機関投資家・大口株主グラフ ＋ 仮想板Volume Profile
    # ---------------------------------------------------------------------
    with tab3:
        scores_5 = compute_5axis_scores(info, vp["overhead_pct"], len(gov_risks))
        opt_radar = {
            "backgroundColor": "#0b1120",
            "radar": {
                "radius": "62%",
                "indicator": [
                    {"name": "割安性", "max": 100}, {"name": "成長性", "max": 100},
                    {"name": "収益性", "max": 100}, {"name": "需給軽さ", "max": 100}, {"name": "安全性", "max": 100}
                ],
                "axisName": {"color": "#cbd5e1", "fontSize": 10.5}
            },
            "series": [{"type": "radar", "data": [{"value": scores_5, "name": "総合体力", "itemStyle": {"color": "#38bdf8"}, "areaStyle": {"color": "rgba(56,189,248,0.28)"}}]}]
        }
        render_echarts(opt_radar, height=225)

        # --- 機関投資家・大口株主セクション ---
        st.markdown("##### 機関投資家・大口株主 保有構成")
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
            render_echarts(opt_donut, height=210)

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
            render_echarts(opt_ih, height=195)

            rows_h = "".join([f"<tr><td>{html.escape(x['holder'])}</td><td><b>{x['pct']:.2f}%</b></td><td style='font-family:monospace;'>{x['shares']:,}</td></tr>" for x in inst_h])
            st.markdown(f'<div class="dark-box"><div class="table-wrap"><table class="data-table"><thead><tr><th>大口機関投資家</th><th>保有比率</th><th>保有株数</th></tr></thead><tbody>{rows_h}</tbody></table></div></div>', unsafe_allow_html=True)
        else:
            if is_jp_flag:
                code4 = fc_code.replace(".T", "")
                st.caption("ℹ️ 東証銘柄の大口株主一覧はyfinance非対応のため、株探の大株主データから確認できます。")
                st.link_button(f"🏛️ 株探で {code4} の大株主一覧を見る", f"https://kabutan.jp/stock/holder?code={code4}", use_container_width=True)
            else:
                st.caption("ℹ️ 大口機関投資家データを取得できませんでした。")

        # --- 仮想板（抵抗・支持マップ）＋ 横棒Volume Profile ---
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
            render_echarts(opt_vp, height=240)

    # ---------------------------------------------------------------------
    # TAB 4: CNN風リアル計器メーター ＋ 自動AIメモ ＋ ガバナンス監査
    # ---------------------------------------------------------------------
    with tab4:
        # 1. 多層アナログ計器メーター（CNN Fear & Greed風）
        opt_gauge = {
            "backgroundColor": "#0b1120",
            "series": [{
                "type": "gauge", "startAngle": 180, "endAngle": 0, "min": 0, "max": 100, "splitNumber": 5,
                "center": ["50%", "74%"], "radius": "112%",
                "axisLine": {
                    "lineStyle": {
                        "width": 16,
                        "color": [[0.2, "#dc2626"], [0.4, "#f97316"], [0.6, "#38bdf8"], [0.8, "#10b981"], [1.0, "#059669"]]
                    }
                },
                "pointer": {
                    "icon": "path://M12.8,0.7l12,40.1H0.7L12.8,0.7z",
                    "length": "52%", "width": 10, "offsetCenter": [0, "-12%"],
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

        # 2. 自動生成 1分インベストメントメモ（ボタン廃止・完全自動）
        top_m = macro_sens[0] if macro_sens else {"label": "市場指数", "corr": 0.0, "beta": 1.0}
        m_txt, m_src = generate_auto_investment_memo(
            fc_code, corp_name, fmt_currency(curr_px, is_jp_flag),
            traj["est_open_gap_pct"], traj["est_close_chg"], traj["dip_time"], traj["peak_time"],
            vp["overhead_pct"], top_m["label"], top_m["corr"], top_m["beta"],
            news_res["pos_pct"], len(gov_risks), upside_str
        )
        st.markdown(f'<div class="memo-box"><div style="font-size:10.5px;color:#c084fc;font-weight:800;margin-bottom:5px;">{html.escape(m_src)}</div>{html.escape(m_txt).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

        # 3. ガバナンス監査 ＆ ニュースヘッドライン
        if gov_risks:
            risk_html = "<br>".join([f"・{html.escape(x)}" for x in gov_risks])
            st.markdown(f'<div class="warning-box"><b>ガバナンス・不祥事・訴訟関連ヒット ({len(gov_risks)}件)</b><br>{risk_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="quant-box"><b>ガバナンス・不祥事監査: クリーン</b><br>直近ニュースにおいて不祥事・不正・訴訟などの特異リスクシグナルは検知されていません。</div>', unsafe_allow_html=True)

        if news_res["items"]:
            n_html = ""
            for it in news_res["items"]:
                badge_c = "#10b981" if it["sent"] == "POS" else ("#ef4444" if it["sent"] == "NEG" else "#94a3b8")
                n_html += f'<div style="margin-bottom:7px;padding-bottom:6px;border-bottom:1px solid rgba(148,163,184,0.12);"><span style="color:{badge_c};font-weight:800;font-size:10px;">[{it["sent"]}]</span> <a href="{html.escape(it["link"])}" target="_blank" style="color:#e2e8f0;text-decoration:none;font-weight:600;">{html.escape(it["title"])}</a> <span style="color:#64748b;font-size:10px;">({html.escape(it["pub"])})</span></div>'
            st.markdown(f'<div class="dark-box"><b>最新ニュースヘッドライン ＆ 感情判定</b><br><br>{n_html}</div>', unsafe_allow_html=True)

if hasattr(st, "fragment"):
    @st.fragment(run_every="30s")
    def _auto_live_runner():
        render_live_terminal(fc, in_style, is_jp)
    _auto_live_runner()
else:
    render_live_terminal(fc, in_style, is_jp)
