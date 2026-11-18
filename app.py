import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os, re, time
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
import html
import json
import datetime
import streamlit.components.v1 as components

st.set_page_config(
    page_title="YAMASHISHI DEEP DIVE [TRADINGVIEW HACK]",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 1. スタイリング・デザイン ---
def inject_css():
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Plus+Jakarta+Sans:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    html,body{font-family:'Plus Jakarta Sans',sans-serif;font-size:14px;}
    .stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background-color:#03050a!important;color:#e2e8f0!important;}
    .stApp p,.stApp label,.stApp span,.stApp li,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5{color:#e2e8f0;}
    .stApp input,.stApp textarea{color:#f8fafc!important;background-color:#0f172a!important;}
    .stApp [data-baseweb="select"] *{color:#f8fafc!important;}
    .stApp [data-baseweb="select"] > div{background-color:#0f172a!important;}
    .brand-luxury{font-family:'Cinzel',serif!important;font-size:24px;font-weight:800;letter-spacing:2px;background:linear-gradient(90deg,#f8fafc 0%,#38bdf8 30%,#f43f5e 70%,#a855f7 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .glass-header{background:radial-gradient(circle at top right,rgba(244,63,94,0.12),transparent 60%),linear-gradient(145deg,#0f172a 0%,#050811 100%);border:1px solid rgba(244,63,94,0.25);border-radius:16px;padding:18px;margin-bottom:18px;box-shadow:0 12px 32px rgba(0,0,0,0.6);}
    .rank-card{background:linear-gradient(180deg,#0f172a 0%,#070b14 100%)!important;color:#f8fafc!important;border-radius:16px;padding:18px;margin-bottom:18px;border:1px solid rgba(148,163,184,0.22);border-left:5px solid #f43f5e;}
    .fact-box{background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.35);border-left:4px solid #10b981;padding:12px 14px;border-radius:10px;margin-bottom:12px;font-size:12.5px;line-height:1.6;color:#d1fae5;}
    .pill-badge{font-size:11px;padding:3px 8px;border-radius:4px;border:1px solid rgba(148,163,184,0.3);display:inline-block;margin-right:4px;font-weight:700;}
    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

_boot = st.empty()
_boot.caption("⏳ 起動中...")
if st.query_params.get("safe", "0") != "1":
    inject_css()

def to_html(text: str) -> str:
    t = html.escape(str(text))
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t.replace("\n", "<br>")

# --- 2. WEBサーチ ---
def search_web_rumors_and_news(query: str) -> list:
    res = []
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ja&gl=JP&ceid=JP:ja"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5.0) as r:
            for it in ET.fromstring(r.read()).findall("./channel/item")[:8]:
                t = (it.findtext("title") or "").strip()
                d = re.sub(r"<[^>]+>", "", (it.findtext("description") or "")).strip()
                if t:
                    res.append(f"・{t} ({d[:100]}...)")
    except Exception:
        pass
    return res

# --- 3. 入力 ---
STYLES = ["デイトレード", "スキャルピング", "スイングトレード", "バイ＆ホールド"]

qp_code = st.query_params.get("code", "6920")
query_code = str(qp_code[0] if isinstance(qp_code, list) else qp_code).strip().upper()

qp_style = st.query_params.get("style", "デイトレード")
query_style = str(qp_style[0] if isinstance(qp_style, list) else qp_style).strip()

st.markdown(
    '<div class="glass-header"><div class="brand-luxury">YAMASHISHI DEEP DIVE [TRADINGVIEW HACK]</div>'
    '<div style="font-size:11.5px;color:#cbd5e1;margin-top:4px;">1銘柄極限ハッキング ｜ TradingViewエンジン搭載・超滑らかチャート</div></div>',
    unsafe_allow_html=True
)

_boot.empty()
col_in1, col_in2 = st.columns([2.5, 1])
target_code = col_in1.text_input("🎯 調査対象銘柄コード", value=query_code, placeholder="例: 6920.T または 7203.T")
target_style = col_in2.selectbox(
    "📊 分析スタイル", STYLES,
    index=STYLES.index(query_style) if query_style in STYLES else 0
)

target_code = target_code.strip().upper()
if not target_code:
    st.stop()

fc = target_code
if re.match(r"^[0-9]{3}[0-9A-Z]$", fc):
    fc = f"{fc}.T"

@st.cache_data(ttl=120)
def load_deep_stock_data(code: str):
    try:
        tkr = yf.Ticker(code)
        df_5m = tkr.history(period="1.5mo", interval="5m")
        df_1d = tkr.history(period="1y", interval="1d")
        try:
            info = tkr.info
        except Exception:
            info = {}
        
        if df_5m is None or df_5m.empty:
            raise ValueError("Empty dataframe from yfinance")
            
        return df_5m, df_1d, info, False
    except Exception:
        np.random.seed(hash(code) % 2**32)
        dates = pd.date_range(end=datetime.datetime.now(), periods=150, freq="5min")
        base_price = 18500.0 if "6920" in code else 3000.0
        walk = np.random.normal(0, 45, size=150).cumsum()
        prices = base_price + walk
        df_5m = pd.DataFrame({"Close": prices}, index=dates)
        info = {
            "longName": f"銘柄データ ({code})",
            "sector": "半導体・製造装置 (フォールバックデータ)"
        }
        return df_5m, None, info, True

with st.spinner(f"📡 【{fc}】の全株価データ取得 ＆ WEBディープサーチを実行中..."):
    df_5m, df_1d, info, is_fallback = load_deep_stock_data(fc)
    web_snippets = search_web_rumors_and_news(f"{fc} 株価 思惑 噂 決算 ニュース")

corp_name = info.get("longName") or info.get("shortName") or fc
sector = info.get("sector") or "個別グロース/主力"
curr_px = float(df_5m["Close"].iloc[-1])
prev_px = float(df_5m["Close"].iloc[-2]) if len(df_5m) >= 2 else curr_px
chg_pct = ((curr_px - prev_px) / max(prev_px, 1e-4)) * 100.0

color_code = "#10b981" if chg_pct >= 0 else "#ef4444"

# --- 4. ダッシュボード ---
st.markdown(f"""
<div class="rank-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <span class="pill-badge" style="background:#f43f5e;color:#fff;font-weight:800;">🔥 ハッキング中</span>
      <span class="pill-badge" style="background:rgba(56,189,248,0.2);color:#38bdf8;">{html.escape(sector)}</span>
      <div style="font-size:22px;font-weight:800;color:#f8fafc;margin-top:6px;">{html.escape(corp_name)} <span style="font-size:13px;color:#f43f5e;">[{html.escape(fc)}]</span></div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:11px;color:#94a3b8;">現在値 (直近5分足)</div>
      <div style="font-size:20px;font-weight:900;color:#f8fafc;">{curr_px:,.1f}円</div>
      <div style="font-size:12.5px;font-weight:700;color:{color_code};">{chg_pct:+.2f}%</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if is_fallback:
    st.info("ℹ️ 現在のホスティング環境制限によりYahoo Financeからの直接取得が制限されたため、スムーズなモックシミュレーションデータでチャートを表示しています。")

# --- 5. TradingView Lightweight Charts（通常の文字列テンプレートを使用し、括弧エラーを完全に防止） ---
st.markdown("#### 📈 プロフェッショナル・インタラクティブ・チャート (TradingView Engine)")

chart_data = []
for idx, row in df_5m.iterrows():
    try:
        ts = int(idx.timestamp())
    except Exception:
        ts = int(pd.Timestamp(idx).timestamp())
    chart_data.append({"time": ts, "value": float(row["Close"])})

chart_json_str = json.dumps(chart_data)

# fではなく通常のトリプルクォーテーション文字列にする
tv_html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        body {
            margin: 0;
            background-color: #03050a;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        #chart-container {
            width: 100%;
            height: 380px;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.2);
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
    </style>
</head>
<body>
    <div id="chart-container"></div>
    <script>
        const chartContainer = document.getElementById('chart-container');
        
        const chart = LightweightCharts.createChart(chartContainer, {
            width: chartContainer.clientWidth,
            height: 380,
            layout: {
                background: { type: 'solid', color: '#070b14' },
                textColor: '#94a3b8',
            },
            grid: {
                vertLines: { color: 'rgba(30, 41, 59, 0.5)' },
                horzLines: { color: 'rgba(30, 41, 59, 0.5)' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
                vertLine: {
                    color: '#38bdf8',
                    width: 1,
                    style: LightweightCharts.LineStyle.Dashed,
                    labelBackgroundColor: '#0284c7',
                },
                horzLine: {
                    color: '#38bdf8',
                    width: 1,
                    style: LightweightCharts.LineStyle.Dashed,
                    labelBackgroundColor: '#0284c7',
                },
            },
            rightPriceScale: {
                borderColor: 'rgba(51, 65, 85, 0.6)',
            },
            timeScale: {
                borderColor: 'rgba(51, 65, 85, 0.6)',
                timeVisible: true,
                secondsVisible: false,
            },
        });

        const areaSeries = chart.addAreaSeries({
            topColor: 'rgba(244, 63, 94, 0.45)',
            bottomColor: 'rgba(244, 63, 94, 0.02)',
            lineColor: '#f43f5e',
            lineWidth: 2.5,
        });

        const rawData = __CHART_DATA_PLACEHOLDER__;
        areaSeries.setData(rawData);

        chart.timeScale().fitContent();

        window.addEventListener('resize', () => {
            chart.resize(chartContainer.clientWidth, 380);
        });
    </script>
</body>
</html>
"""

# プレースホルダーを実際の株価データJSONに置換する
tv_html_code = tv_html_template.replace('__CHART_DATA_PLACEHOLDER__', chart_json_str)

components.html(tv_html_code, height=400)
st.caption("💡 ヌルヌル操作ヒント: マウスドラッグでチャートの左右移動、マウスホイールで拡大・縮小が完全に滑らかに行えます。")

# --- 6. WEBサーチ結果の表示 ---
st.markdown("#### 🌐 WEBマルチサーチ・生データ＆マーケットのヘッドライン")
web_str_joined = "\n".join(web_snippets) if web_snippets else "特段の新規ヘッドライン・噂なし"

st.markdown(f'<div class="fact-box"><b>🔍 【取得したWEBニュースヘッドライン】</b><br>{to_html(web_str_joined)}</div>', unsafe_allow_html=True)
