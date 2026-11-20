import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
import re
import html
import json
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# =========================================================================
# 0. 基本設定（LABアプリのURLをここに設定）
# =========================================================================
LAB_APP_URL = "https://your-yamashishi-lab.streamlit.app/"

st.set_page_config(
    page_title="YAMASHISHI DEEP DIVE",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================================
# 1. スタイリング（YAMASHISHI LAB 統一ダーク・クオンツUI）
# =========================================================================
def inject_css():
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Plus+Jakarta+Sans:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 14px;
        background-color: #050811;
        color: #e2e8f0;
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
        font-size: clamp(17px, 4.5vw, 24px) !important;
        font-weight: 800 !important;
        letter-spacing: clamp(1px, 0.4vw, 2.5px) !important;
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
        padding: 14px 16px;
        margin-bottom: 14px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
    }
    .rank-card {
        background: linear-gradient(180deg, #0f172a 0%, #090d16 100%) !important;
        color: #f8fafc !important;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 14px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.55);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-left: 5px solid #38bdf8;
    }
    .winrate-bar {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
        gap: 6px;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 8px;
        padding: 8px;
        margin-top: 8px;
        text-align: center;
    }
    .metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 14.5px;
        font-weight: 800;
        color: #38bdf8;
        margin-top: 2px;
    }
    .metric-lbl {
        font-size: 10px;
        color: #94a3b8;
        font-weight: 600;
    }
    .pill-badge {
        font-size: 10.5px;
        padding: 2px 7px;
        border-radius: 4px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        background: rgba(56, 189, 248, 0.14);
        color: #7dd3fc;
        font-weight: 700;
        display: inline-block;
        margin-right: 4px;
    }
    .dark-box {
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(148, 163, 184, 0.18);
        padding: 12px 14px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 12.5px;
        line-height: 1.65;
        color: #cbd5e1;
    }
    .warning-box {
        background: rgba(239, 68, 68, 0.10);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-left: 4px solid #ef4444;
        padding: 12px 14px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 12.5px;
        line-height: 1.65;
        color: #fecaca;
    }
    .quant-box {
        background: rgba(16, 185, 129, 0.10);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-left: 4px solid #10b981;
        padding: 12px 14px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 12.5px;
        line-height: 1.65;
        color: #d1fae5;
    }
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11.5px;
        margin-top: 6px;
    }
    .data-table th {
        background: #1e293b;
        color: #38bdf8;
        padding: 7px 8px;
        text-align: left;
        border-bottom: 1px solid rgba(56, 189, 248, 0.3);
    }
    .data-table td {
        padding: 7px 8px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
        color: #e2e8f0;
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

inject_css()

# =========================================================================
# 2. ユーティリティ ＆ データ取得関数（実データ優先）
# =========================================================================
def fmt_currency(val, is_jp: bool) -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "-"
    return f"{val:,.0f}円" if is_jp else f"${val:,.2f}"

def fmt_large_num(val, is_jp: bool) -> str:
    if not val or (isinstance(val, float) and np.isnan(val)):
        return "-"
    if is_jp:
        if abs(val) >= 1e12:
            return f"{val/1e12:.2f}兆円"
        if abs(val) >= 1e8:
            return f"{val/1e8:,.0f}億円"
        return f"{val:,.0f}円"
    else:
        if abs(val) >= 1e12:
            return f"${val/1e12:.2f}T"
        if abs(val) >= 1e9:
            return f"${val/1e9:.2f}B"
        if abs(val) >= 1e6:
            return f"${val/1e6:.1f}M"
        return f"${val:,.0f}"

@st.cache_data(ttl=180)
def load_deep_stock_data(code: str) -> dict:
    tkr = yf.Ticker(code)
    df_1d = tkr.history(period="6mo", interval="1d", auto_adjust=True)
    df_5m = tkr.history(period="5d", interval="5m", auto_adjust=True)

    try:
        info = tkr.info or {}
    except Exception:
        info = {}

    # 四半期財務データ
    q_fin = []
    try:
        qf = tkr.quarterly_financials
        if qf is not None and not qf.empty:
            cols = list(qf.columns)[:4][::-1]
            for col in cols:
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

    # 機関投資家保有
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

    # インサイダー売買
    insiders = []
    try:
        itx = tkr.insider_transactions
        if itx is not None and not itx.empty:
            for _, row in itx.head(5).iterrows():
                insiders.append({
                    "insider": str(row.get("Insider", "-")),
                    "text": str(row.get("Text", row.get("Transaction", "-"))),
                    "shares": int(row.get("Shares", 0)) if pd.notna(row.get("Shares")) else 0
                })
    except Exception:
        pass

    # オプション（米国株等で取得可能な場合）
    opt_data = None
    try:
        exps = tkr.options
        if exps:
            chain = tkr.option_chain(exps[0])
            c_vol = float(chain.calls["volume"].fillna(0).sum())
            p_vol = float(chain.puts["volume"].fillna(0).sum())
            c_iv = float(chain.calls["impliedVolatility"].dropna().median()) * 100.0 if not chain.calls.empty else 0.0
            p_iv = float(chain.puts["impliedVolatility"].dropna().median()) * 100.0 if not chain.puts.empty else 0.0
            opt_data = {
                "exp": exps[0],
                "pcr": round(p_vol / max(c_vol, 1.0), 2),
                "call_vol": int(c_vol),
                "put_vol": int(p_vol),
                "call_iv": round(c_iv, 1),
                "put_iv": round(p_iv, 1)
            }
    except Exception:
        pass

    return {
        "df_1d": df_1d,
        "df_5m": df_5m,
        "info": info,
        "q_fin": q_fin,
        "inst_holders": inst_holders,
        "insiders": insiders,
        "opt_data": opt_data
    }

@st.cache_data(ttl=300)
def fetch_news_and_sentiment(query: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}
    items_out = []
    pos_words = ["上昇", "急騰", "最高益", "上方修正", "増配", "自社株買い", "好調", "提携", "突破", "買い", "黒字", "成長"]
    neg_words = ["下落", "急落", "下方修正", "赤字", "減益", "不祥事", "訴訟", "不正", "辞任", "炎上", "懸念", "売り", "リスク"]
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
                if not t:
                    continue
                p_hit = sum(1 for w in pos_words if w in t)
                n_hit = sum(1 for w in neg_words if w in t)
                if p_hit > n_hit:
                    sent = "POS"; pos_c += 1
                elif n_hit > p_hit:
                    sent = "NEG"; neg_c += 1
                else:
                    sent = "NEU"; neu_c += 1
                items_out.append({"title": t, "link": link, "pub": pub, "sent": sent})
    except Exception:
        pass

    tot = max(pos_c + neu_c + neg_c, 1)
    return {
        "items": items_out,
        "pos_pct": round(pos_c / tot * 100),
        "neu_pct": round(neu_c / tot * 100),
        "neg_pct": round(neg_c / tot * 100),
        "counts": (pos_c, neu_c, neg_c)
    }

@st.cache_data(ttl=300)
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
                if t:
                    risks.append(f"{t} ({pub})")
    except Exception:
        pass
    return risks

# =========================================================================
# 3. ECharts 描画ヘルパー（レスポンシブ・リサイズ対応）
# =========================================================================
def render_echarts(option_dict: dict, height: int = 280):
    opt_json = json.dumps(option_dict, ensure_ascii=False)
    html_code = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>body{{margin:0;background:#0b1120;overflow:hidden;}} #c{{width:100%;height:{height}px;}}</style>
    </head><body><div id="c"></div><script>
    var chart = echarts.init(document.getElementById('c'), 'dark');
    chart.setOption({opt_json});
    window.addEventListener('resize', function() {{ chart.resize(); }});
    </script></body></html>
    """
    components.html(html_code, height=height + 6)

# =========================================================================
# 4. ヘッダー ＆ コントロール
# =========================================================================
h_col1, h_col2 = st.columns([3.2, 1.2])
with h_col1:
    st.markdown(
        '<div class="glass-header" style="margin-bottom:8px;">'
        '<div class="brand-luxury">YAMASHISHI DEEP DIVE</div>'
        '<div style="font-size:11px;color:#94a3b8;margin-top:2px;">1銘柄極限リサーチ ｜ 財務・需給・リスク完全監査ターミナル</div>'
        '</div>',
        unsafe_allow_html=True
    )
with h_col2:
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    st.link_button("⬅️ LABへ戻る", LAB_APP_URL, use_container_width=True)

STYLES = ["デイトレード", "スキャルピング", "スイングトレード", "バイ＆ホールド"]
qp_code = st.query_params.get("code", "NVDA")
query_code = str(qp_code[0] if isinstance(qp_code, list) else qp_code).strip().upper()
qp_style = st.query_params.get("style", "デイトレード")
query_style = str(qp_style[0] if isinstance(qp_style, list) else qp_style).strip()

c1, c2, c3 = st.columns([2.2, 1.5, 1.0])
in_code = c1.text_input("銘柄コード", value=query_code, placeholder="例: NVDA / 6920", label_visibility="collapsed")
in_style = c2.selectbox("スタイル", STYLES, index=STYLES.index(query_style) if query_style in STYLES else 0, label_visibility="collapsed")
c3.button("⚡ 極限解析", use_container_width=True, type="primary")

fc = in_code.strip().upper()
if not fc:
    st.stop()
if re.match(r"^[0-9]{3}[0-9A-Z]$", fc):
    fc = f"{fc}.T"
is_jp = fc.endswith(".T")

with st.spinner(f"📡 【{fc}】の実測データ・財務・ニュースをスキャン中..."):
    data = load_deep_stock_data(fc)
    df_1d = data["df_1d"]
    info = data["info"]

if df_1d is None or df_1d.empty:
    st.error(f"❌ 銘柄コード `{fc}` の市場データを取得できませんでした。コードを確認してください。")
    st.stop()

corp_name = info.get("longName") or info.get("shortName") or fc
sector = info.get("sector") or "セクター未分類"
industry = info.get("industry") or "-"
curr_px = float(df_1d["Close"].iloc[-1])
prev_px = float(df_1d["Close"].iloc[-2]) if len(df_1d) >= 2 else curr_px
chg_pct = ((curr_px - prev_px) / max(prev_px, 1e-4)) * 100.0
chg_col = "#10b981" if chg_pct >= 0 else "#ef4444"

# スタイル別のTP/SL（日足ATR14ベースの実測算出）
h_arr, l_arr, c_arr = df_1d["High"].values, df_1d["Low"].values, df_1d["Close"].values
prev_c = np.roll(c_arr, 1); prev_c[0] = c_arr[0]
atr14 = float(np.mean(np.maximum(h_arr - l_arr, np.maximum(np.abs(h_arr - prev_c), np.abs(l_arr - prev_c)))[-14:]))
mult_map = {"スキャルピング": (0.5, 0.9), "デイトレード": (0.7, 1.4), "スイングトレード": (1.5, 3.0), "バイ＆ホールド": (2.5, 5.0)}
sl_m, tp_m = mult_map.get(in_style, (0.7, 1.4))
tp_px = curr_px + atr14 * tp_m
sl_px = max(curr_px - atr14 * sl_m, curr_px * 0.5)

# アナリスト目標株価
target_mean = info.get("targetMeanPrice")
upside_pct = ((target_mean - curr_px) / curr_px * 100.0) if (target_mean and curr_px > 0) else None
rec_key = str(info.get("recommendationKey", "-")).upper()

# ニュース＆リスク取得
news_res = fetch_news_and_sentiment(f"{corp_name} OR {fc.replace('.T', '')} 株価")
gov_risks = fetch_governance_risks(corp_name)

# =========================================================================
# 5. トップ企業カード ＆ 4大サマリー（常時表示）
# =========================================================================
upside_str = f"{upside_pct:+.1f}%" if upside_pct is not None else "-"
pe_val = info.get("trailingPE")
pe_str = f"{pe_val:.1f}倍" if pe_val else "-"
risk_status = "⚠️ 要確認" if gov_risks else "🟢 クリーン"
risk_col = "#f87171" if gov_risks else "#10b981"

st.markdown(f"""
<div class="rank-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;flex-wrap:wrap;">
    <div>
      <div>
        <span class="pill-badge">{html.escape(fc)}</span>
        <span class="pill-badge" style="border-color:rgba(168,85,247,0.45);background:rgba(168,85,247,0.16);color:#e9d5ff;">{html.escape(in_style)}</span>
      </div>
      <div style="font-size:19px;font-weight:800;color:#ffffff;margin-top:4px;">{html.escape(corp_name)}</div>
      <div style="font-size:11.5px;color:#94a3b8;margin-top:2px;">🏢 {html.escape(sector)} / {html.escape(industry)}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:10px;color:#64748b;font-weight:700;">LIVE REFERENCE PRICE</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:21px;font-weight:800;color:#ffffff;">{fmt_currency(curr_px, is_jp)}</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:12.5px;font-weight:700;color:{chg_col};">{chg_pct:+.2f}%</div>
    </div>
  </div>
  <div class="winrate-bar">
    <div><div class="metric-lbl">🎯 アナリスト目標乖離</div><div class="metric-val" style="color:#fde047;">{upside_str}</div></div>
    <div><div class="metric-lbl">📊 実績PER / 評価</div><div class="metric-val">{pe_str} ({html.escape(rec_key)})</div></div>
    <div><div class="metric-lbl">📰 ニュース強気度</div><div class="metric-val" style="color:#10b981;">{news_res['pos_pct']}%</div></div>
    <div><div class="metric-lbl">🚨 ガバナンス監査</div><div class="metric-val" style="color:{risk_col};">{risk_status}</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# =========================================================================
# 6. 4タブ集約ビュー（ワンタップ切替）
# =========================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 戦略・チャート",
    "💰 財務・バリュエーション",
    "🏛️ 需給・オプション",
    "🚨 リスク・ニュース監査"
])

# --- TAB 1: 戦略・チャート ---
with tab1:
    df_tail = df_1d.tail(60).copy()
    dates_s = [d.strftime("%m/%d") for d in df_tail.index]
    closes_s = [round(float(x), 2) for x in df_tail["Close"].values]
    ma25_s = [round(float(x), 2) if pd.notna(x) else None for x in df_1d["Close"].rolling(25).mean().tail(60).values]

    opt_price = {
        "backgroundColor": "#0b1120",
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["終値", "25日線", "利確目安(TP)", "損切目安(SL)"], "textStyle": {"color": "#cbd5e1", "fontSize": 10}, "top": 4},
        "grid": {"top": 34, "bottom": 24, "left": 55, "right": 18},
        "xAxis": {"type": "category", "data": dates_s, "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
        "yAxis": {"type": "value", "scale": True, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
        "series": [
            {"name": "終値", "type": "line", "data": closes_s, "smooth": True, "lineStyle": {"color": "#38bdf8", "width": 2.5}, "showSymbol": False},
            {"name": "25日線", "type": "line", "data": ma25_s, "smooth": True, "lineStyle": {"color": "#f59e0b", "width": 1.5}, "showSymbol": False},
            {"name": "利確目安(TP)", "type": "line", "data": [round(tp_px, 2)] * len(dates_s), "lineStyle": {"color": "#10b981", "type": "dashed", "width": 1.2}, "showSymbol": False},
            {"name": "損切目安(SL)", "type": "line", "data": [round(sl_px, 2)] * len(dates_s), "lineStyle": {"color": "#ef4444", "type": "dashed", "width": 1.2}, "showSymbol": False}
        ]
    }
    render_echarts(opt_price, height=290)

    st.markdown(f"""
    <div class="quant-box">
      <b>⚡ {html.escape(in_style)} 基準トレード目安（日足ATR14 = {fmt_currency(atr14, is_jp)} 算出）</b><br>
      ・<b>利確目安 (TP):</b> <span style="color:#6ee7b7;font-weight:800;">{fmt_currency(tp_px, is_jp)}</span> ({(tp_px/curr_px - 1)*100:+.1f}%)<br>
      ・<b>損切目安 (SL):</b> <span style="color:#fca5a5;font-weight:800;">{fmt_currency(sl_px, is_jp)}</span> ({(sl_px/curr_px - 1)*100:+.1f}%)<br>
      ・<b>アナリスト目標レンジ:</b> 安値 {fmt_currency(info.get("targetLowPrice"), is_jp)} ～ 平均 <b>{fmt_currency(target_mean, is_jp)}</b> ～ 高値 {fmt_currency(info.get("targetHighPrice"), is_jp)}
    </div>
    """, unsafe_allow_html=True)

# --- TAB 2: 財務・バリュエーション ---
with tab2:
    mcap = fmt_large_num(info.get("marketCap"), is_jp)
    rev_tot = fmt_large_num(info.get("totalRevenue"), is_jp)
    pbr = f"{info.get('priceToBook'):.2f}倍" if info.get("priceToBook") else "-"
    roe = f"{info.get('returnOnEquity')*100:.1f}%" if info.get("returnOnEquity") else "-"
    div_y = f"{info.get('dividendYield')*100:.2f}%" if info.get("dividendYield") else "-"
    f_pe = f"{info.get('forwardPE'):.1f}倍" if info.get("forwardPE") else "-"

    st.markdown(f"""
    <div class="winrate-bar" style="margin-bottom:10px;">
      <div><div class="metric-lbl">時価総額</div><div class="metric-val">{mcap}</div></div>
      <div><div class="metric-lbl">年間売上高</div><div class="metric-val">{rev_tot}</div></div>
      <div><div class="metric-lbl">予想PER / PBR</div><div class="metric-val">{f_pe} / {pbr}</div></div>
      <div><div class="metric-lbl">ROE / 配当利回り</div><div class="metric-val" style="color:#10b981;">{roe} / {div_y}</div></div>
    </div>
    """, unsafe_allow_html=True)

    q_fin = data["q_fin"]
    if q_fin:
        scale_div = 1e8 if is_jp else 1e9
        unit_lbl = "億円" if is_jp else "B$"
        opt_fin = {
            "backgroundColor": "#0b1120",
            "tooltip": {"trigger": "axis"},
            "legend": {"data": [f"売上高({unit_lbl})", f"純利益({unit_lbl})"], "textStyle": {"color": "#cbd5e1", "fontSize": 10}, "top": 4},
            "grid": {"top": 34, "bottom": 24, "left": 55, "right": 18},
            "xAxis": {"type": "category", "data": [x["period"] for x in q_fin], "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
            "yAxis": {"type": "value", "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
            "series": [
                {"name": f"売上高({unit_lbl})", "type": "bar", "data": [round(x["revenue"]/scale_div, 2) for x in q_fin], "itemStyle": {"color": "#38bdf8"}},
                {"name": f"純利益({unit_lbl})", "type": "bar", "data": [round(x["net_income"]/scale_div, 2) for x in q_fin], "itemStyle": {"color": "#10b981"}}
            ]
        }
        render_echarts(opt_fin, height=250)
    else:
        st.info("ℹ️ この銘柄の四半期財務データ（売上・純利益）はAPIから取得できませんでした。")

    summary_txt = info.get("longBusinessSummary") or "企業概要データなし"
    st.markdown(f'<div class="dark-box"><b>🏢 事業概要（yfinance公式）</b><br>{html.escape(summary_txt[:450])}{"..." if len(summary_txt) > 450 else ""}</div>', unsafe_allow_html=True)

# --- TAB 3: 需給・オプション ---
with tab3:
    opt_d = data["opt_data"]
    if opt_d:
        st.markdown(f"""
        <div class="quant-box">
          <b>📈 オプション市場・実測センチメント（満期: {html.escape(opt_d['exp'])}）</b><br>
          ・<b>プット・コール比率 (PCR):</b> <b>{opt_d['pcr']}</b>（Put出来高 {opt_d['put_vol']:,} / Call出来高 {opt_d['call_vol']:,}）<br>
          ・<b>中央値IV:</b> Call IV <b>{opt_d['call_iv']}%</b> ｜ Put IV <b>{opt_d['put_iv']}%</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ オプションチェーンは主に米国株向けデータのため、この銘柄では直近出来高推移を表示します。")
        vol_tail = df_1d.tail(20)
        opt_vol = {
            "backgroundColor": "#0b1120",
            "tooltip": {"trigger": "axis"},
            "grid": {"top": 24, "bottom": 24, "left": 60, "right": 16},
            "xAxis": {"type": "category", "data": [d.strftime("%m/%d") for d in vol_tail.index], "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
            "yAxis": {"type": "value", "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
            "series": [{"name": "出来高", "type": "bar", "data": [int(v) for v in vol_tail["Volume"].values], "itemStyle": {"color": "#a855f7"}}]
        }
        render_echarts(opt_vol, height=220)

    inst_h = data["inst_holders"]
    if inst_h:
        rows_h = "".join([f"<tr><td>{html.escape(x['holder'])}</td><td>{x['pct']:.2f}%</td><td>{x['shares']:,}</td></tr>" for x in inst_h])
        st.markdown(f'<div class="dark-box"><b>🏛️ 主要機関投資家トップ5</b><table class="data-table"><thead><tr><th>機関名</th><th>保有比率</th><th>保有株数</th></tr></thead><tbody>{rows_h}</tbody></table></div>', unsafe_allow_html=True)

    ins_tx = data["insiders"]
    if ins_tx:
        rows_i = "".join([f"<tr><td>{html.escape(x['insider'])}</td><td>{html.escape(x['text'][:36])}</td><td>{x['shares']:,}</td></tr>" for x in ins_tx])
        st.markdown(f'<div class="dark-box"><b>🕵️ 直近インサイダー売買履歴（Form 4）</b><table class="data-table"><thead><tr><th>役員・関係者</th><th>取引内容</th><th>株数</th></tr></thead><tbody>{rows_i}</tbody></table></div>', unsafe_allow_html=True)
    elif not inst_h:
        st.caption("※ 東証銘柄など一部市場では機関保有・Form 4データはyfinance非対応です。")

# --- TAB 4: リスク・ニュース監査 ---
with tab4:
    if gov_risks:
        risk_html = "<br>".join([f"・{html.escape(x)}" for x in gov_risks])
        st.markdown(f'<div class="warning-box"><b>🚨 ガバナンス・不祥事・訴訟関連ヒット ({len(gov_risks)}件)</b><br>{risk_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="quant-box"><b>🟢 ガバナンス・不祥事監査: クリーン</b><br>直近ニュースにおいて、不祥事・不正・訴訟・行政処分などの特異リスクシグナルは検知されていません。</div>', unsafe_allow_html=True)

    pos_c, neu_c, neg_c = news_res["counts"]
    opt_sent = {
        "backgroundColor": "#0b1120",
        "tooltip": {"trigger": "axis"},
        "grid": {"top": 20, "bottom": 24, "left": 45, "right": 16},
        "xAxis": {"type": "category", "data": ["ポジティブ", "ニュートラル", "ネガティブ"], "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
        "yAxis": {"type": "value", "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
        "series": [{"type": "bar", "data": [
            {"value": pos_c, "itemStyle": {"color": "#10b981"}},
            {"value": neu_c, "itemStyle": {"color": "#38bdf8"}},
            {"value": neg_c, "itemStyle": {"color": "#ef4444"}}
        ]}]
    }
    render_echarts(opt_sent, height=200)

    if news_res["items"]:
        n_html = ""
        for it in news_res["items"]:
            badge_c = "#10b981" if it["sent"] == "POS" else ("#ef4444" if it["sent"] == "NEG" else "#94a3b8")
            n_html += f'<div style="margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid rgba(148,163,184,0.12);"><span style="color:{badge_c};font-weight:800;font-size:10.5px;">[{it["sent"]}]</span> <a href="{html.escape(it["link"])}" target="_blank" style="color:#e2e8f0;text-decoration:none;font-weight:600;">{html.escape(it["title"])}</a> <span style="color:#64748b;font-size:10.5px;">({html.escape(it["pub"])})</span></div>'
        st.markdown(f'<div class="dark-box"><b>📰 最新ニュースヘッドライン ＆ 感情判定</b><br><br>{n_html}</div>', unsafe_allow_html=True)
    else:
        st.info("現在表示できる最新ニュースはありません。")
