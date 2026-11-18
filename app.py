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
    page_title="YAMASHISHI DEEP DIVE [ECHARTS HACK]",
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
    '<div class="glass-header"><div class="brand-luxury">YAMASHISHI DEEP DIVE [ECHARTS HACK]</div>'
    '<div style="font-size:11.5px;color:#cbd5e1;margin-top:4px;">1銘柄極限ハッキング ｜ Apache ECharts ヌルヌル動く最新チャート</div></div>',
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

# --- 5. Apache ECharts（ヌルヌル動くハイエンド・スムーズチャート） ---
st.markdown("#### 📈 プロフェッショナル・インタラクティブ・チャート (Apache ECharts)")

times_list = []
prices_list = []
for idx, row in df_5m.iterrows():
    try:
        t_str = idx.strftime('%m/%d %H:%M')
    except Exception:
        t_str = str(idx)
    times_list.append(t_str)
    prices_list.append(round(float(row["Close"]), 1))

times_json = json.dumps(times_list)
prices_json = json.dumps(prices_list)

echarts_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
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
            box-shadow: 0 12px 32px rgba(0,0,0,0.6);
        }
    </style>
</head>
<body>
    <div id="chart-container"></div>
    <script>
        var chartDom = document.getElementById('chart-container');
        var myChart = echarts.init(chartDom, 'dark');
        
        var option = {
            backgroundColor: '#070b14',
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    lineStyle: { color: '#38bdf8', width: 1, type: 'dashed' }
                },
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                borderColor: '#f43f5e',
                textStyle: { color: '#f8fafc', fontSize: 12 }
            },
            grid: {
                top: 30,
                bottom: 40,
                left: 60,
                right: 20
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: __TIMES_DATA__,
                axisLine: { lineStyle: { color: '#334155' } },
                axisLabel: { color: '#94a3b8', fontSize: 10 }
            },
            yAxis: {
                type: 'value',
                scale: true,
                splitLine: { lineStyle: { color: 'rgba(30, 41, 59, 0.4)', type: 'dotted' } },
                axisLine: { lineStyle: { color: '#334155' } },
                axisLabel: { color: '#94a3b8', fontSize: 10 }
            },
            dataZoom: [
                {
                    type: 'inside',
                    start: 50,
                    end: 100
                },
                {
                    type: 'slider',
                    show: true,
                    borderColor: 'transparent',
                    backgroundColor: 'rgba(15, 23, 42, 0.5)',
                    fillerColor: 'rgba(244, 63, 94, 0.2)',
                    handleStyle: { color: '#f43f5e' },
                    textStyle: { color: '#94a3b8' },
                    bottom: 5,
                    height: 18
                }
            ],
            series: [{
                name: '終値',
                type: 'line',
                smooth: 0.2,
                symbol: 'none',
                lineStyle: {
                    color: '#f43f5e',
                    width: 2.5
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(244, 63, 94, 0.45)' },
                        { offset: 1, color: 'rgba(244, 63, 94, 0.0)' }
                    ])
                },
                data: __PRICES_DATA__
            }]
        };

        myChart.setOption(option);

        window.addEventListener('resize', function () {
            myChart.resize();
        });
    </script>
</body>
</html>
"""

echarts_code = echarts_template.replace('__TIMES_DATA__', times_json).replace('__PRICES_DATA__', prices_json)

components.html(echarts_code, height=410)
st.caption("💡 ヌルヌル操作ヒント: マウスホイールや下のスクロールバーで拡大・縮小、ドラッグで自由に移動できます。美しく洗練されたプロ仕様の最新チャートです。")

# --- 6. WEBサーチ結果の表示 ---
st.markdown("#### 🌐 WEBマルチサーチ・生データ＆マーケットのヘッドライン")
web_str_joined = "\n".join(web_snippets) if web_snippets else "特段の新規ヘッドライン・噂なし"

st.markdown(f'<div class="fact-box"><b>🔍 【取得したWEBニュースヘッドライン】</b><br>{to_html(web_str_joined)}</div>', unsafe_allow_html=True)
