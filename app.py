import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os, re, time
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
import html
import altair as alt
import datetime

st.set_page_config(
    page_title="YAMASHISHI DEEP DIVE [ULTRA SMOOTH CHART]",
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
    '<div class="glass-header"><div class="brand-luxury">YAMASHISHI DEEP DIVE [ULTRA SMOOTH CHART]</div>'
    '<div style="font-size:11.5px;color:#cbd5e1;margin-top:4px;">1銘柄極限ハッキング ｜ クロスヘア・なめらかズーム対応 高性能チャート</div></div>',
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
        dates = pd.date_range(end=datetime.datetime.now(), periods=120, freq="5min")
        base_price = 18500.0 if "6920" in code else 3000.0
        walk = np.random.normal(0, 50, size=120).cumsum()
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

# --- 5. ヌルヌル動くハイパフォーマンス・モダンチャート (Altair + クロスヘア＆なめらかズーム) ---
st.markdown("#### 📈 プロフェッショナル・インタラクティブ・チャート")

df_chart = df_5m.reset_index()
time_col = "Datetime" if "Datetime" in df_chart.columns else df_chart.columns[0]

# 選択・ズーム用のセレクター定義
zoom_selector = alt.selection_interval(encodings=['x', 'y'], bind='scales')
nearest_selector = alt.selection_point(on='mouseover', nearest=True, fields=[time_col], empty=False)

# ベースラインチャート
line_chart = alt.Chart(df_chart).mark_line(
    color="#f43f5e",
    strokeWidth=2.5
).encode(
    x=alt.X(f'{time_col}:T', title='日時', axis=alt.Axis(grid=False, labelColor="#94a3b8", titleColor="#94a3b8")),
    y=alt.Y('Close:Q', title='株価 (円)', scale=alt.Scale(zero=False), axis=alt.Axis(grid=True, gridColor="#1e293b", labelColor="#94a3b8", titleColor="#94a3b8"))
)

# グラデーション背景エリア
area_chart = alt.Chart(df_chart).mark_area(
    line=False,
    color=alt.Gradient(
        gradient='linear',
        stops=[
            alt.GradientStop(color='rgba(244, 63, 94, 0.4)', offset=0),
            alt.GradientStop(color='rgba(244, 63, 94, 0.0)', offset=1)
        ],
        x1=1, x2=1, y1=1, y2=0
    )
).encode(
    x=f'{time_col}:T',
    y='Close:Q'
)

# ホバー時の十字カーソル（クロスヘア）とポイント表示用のレイヤー
selectors_layer = alt.Chart(df_chart).mark_point().encode(
    x=f'{time_col}:T',
    opacity=alt.value(0)
).add_params(
    nearest_selector
)

# ホバー時に追従する垂直ライン（クロスヘア）
rule_layer = alt.Chart(df_chart).mark_rule(
    color="#38bdf8",
    strokeWidth=1,
    strokeDash=[4, 4]
).encode(
    x=f'{time_col}:T'
).transform_filter(
    nearest_selector
)

# ホバー時に浮き出る価格・日時インジケータポイント
points_layer = alt.Chart(df_chart).mark_circle(
    size=70,
    color="#38bdf8",
    stroke="#f8fafc",
    strokeWidth=2
).encode(
    x=f'{time_col}:T',
    y='Close:Q'
).transform_filter(
    nearest_selector
)

# ホバー時の詳細ツールチップテキスト表示
text_layer = alt.Chart(df_chart).mark_text(
    align='left',
    dx=10,
    dy=-15,
    fontSize=13,
    fontWeight=700,
    color='#f8fafc'
).encode(
    x=f'{time_col}:T',
    y='Close:Q',
    text=alt.Text('Close:Q', format=',.1f')
).transform_filter(
    nearest_selector
)

# すべてのレイヤーを合成し、ズーム＆パンを有効化
interactive_chart = alt.layer(
    area_chart, line_chart, selectors_layer, rule_layer, points_layer, text_layer
).properties(
    height=360,
    background='#03050a'
).add_params(
    zoom_selector
).configure_view(
    stroke=None
).configure_axis(
    domainColor='#334155'
)

st.altair_chart(interactive_chart, use_container_width=True)
st.caption("💡 ヒント: チャート上でマウスホイールを回すと拡大・縮小、ドラッグすると左右へスムーズに移動（パン）できます。ポイントにカーソルを合わせると詳細な株価が追従します。")

# --- 6. WEBサーチ結果の表示 ---
st.markdown("#### 🌐 WEBマルチサーチ・生データ＆マーケットのヘッドライン")
web_str_joined = "\n".join(web_snippets) if web_snippets else "特段の新規ヘッドライン・噂なし"

st.markdown(f'<div class="fact-box"><b>🔍 【取得したWEBニュースヘッドライン】</b><br>{to_html(web_str_joined)}</div>', unsafe_allow_html=True)
