import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os, re, time
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
import html

st.set_page_config(
    page_title="YAMASHISHI DEEP DIVE [NO-GEMINI HACK]",
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
    .rumor-box{background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.35);border-left:4px solid #f59e0b;padding:12px 14px;border-radius:10px;margin-bottom:12px;font-size:12.5px;line-height:1.6;color:#fef3c7;}
    .fact-box{background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.35);border-left:4px solid #10b981;padding:12px 14px;border-radius:10px;margin-bottom:12px;font-size:12.5px;line-height:1.6;color:#d1fae5;}
    .chat-bubble-ai{background:rgba(15,23,42,0.92);border-left:3px solid #f43f5e;padding:12px 16px;border-radius:10px;margin-bottom:10px;font-size:13px;line-height:1.7;}
    .chat-bubble-user{background:rgba(244,63,94,0.18);border-left:4px solid #f43f5e;padding:12px 16px;border-radius:10px;margin-bottom:10px;font-size:13px;line-height:1.7;}
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
    '<div class="glass-header"><div class="brand-luxury">YAMASHISHI DEEP DIVE [NO-GEMINI HACK]</div>'
    '<div style="font-size:11.5px;color:#cbd5e1;margin-top:4px;">1銘柄極限ハッキング ｜ yfinance株価取得 ＆ WEBマルチサーチ対応版</div></div>',
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
        df_5m = tkr.history(period="1mo", interval="5m")
        df_1d = tkr.history(period="1y", interval="1d")
        try:
            info = tkr.info
        except Exception:
            info = {}
        return df_5m, df_1d, info
    except Exception:
        return None, None, {}

with st.spinner(f"📡 【{fc}】の全株価データ取得 ＆ WEBディープサーチを実行中..."):
    df_5m, df_1d, info = load_deep_stock_data(fc)
    web_snippets = search_web_rumors_and_news(f"{fc} 株価 思惑 噂 決算 ニュース")

if df_5m is None or df_5m.empty:
    st.error(f"❌ 銘柄コード `{fc}` のデータが見つかりません。")
    st.stop()

corp_name = info.get("longName") or info.get("shortName") or fc
sector = info.get("sector") or "個別グロース/主力"
curr_px = float(df_5m["Close"].iloc[-1])
prev_px = float(df_5m["Close"].iloc[-2]) if len(df_5m) >= 2 else curr_px
chg_pct = ((curr_px - prev_px) / max(prev_px, 1e-4)) * 100.0

# --- 4. ダッシュボード ---
st.markdown(f"""
<div class="rank-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <span class="pill-badge" style="background:#f43f5e;color:#fff;font-weight:800;">🔥 ハッキング中 (No-Gemini)</span>
      <span class="pill-badge" style="background:rgba(56,189,248,0.2);color:#38bdf8;">{html.escape(sector)}</span>
      <div style="font-size:22px;font-weight:800;color:#f8fafc;margin-top:6px;">{html.escape(corp_name)} <span style="font-size:13px;color:#f43f5e;">[{html.escape(fc)}]</span></div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:11px;color:#94a3b8;">現在値 (直近5分足)</div>
      <div style="font-size:20px;font-weight:900;color:#f8fafc;">{curr_px:,.1f}円</div>
      <div style="font-size:12.5px;font-weight:700;color:{"#10b981" if chg_pct>=0 else "#ef4444"};">{chg_pct:+.2f}%</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("#### 📈 直近5分足プライスアクション ＆ モメンタム")
st.line_chart(df_5m["Close"])

# --- 5. WEBサーチ＆噂・事実の表示 ---
st.markdown("#### 🌐 WEBマルチサーチ・生データ＆マーケットのヘッドライン")
web_str_joined = "\n".join(web_snippets) if web_snippets else "特段の新規ヘッドライン・噂なし"

st.markdown(f'<div class="fact-box"><b>🔍 【取得したWEBニュースヘッドライン】</b><br>{to_html(web_str_joined)}</div>', unsafe_allow_html=True)

# --- 6. 5名ペルソナ（静的表示版） ---
st.markdown("#### 🏛️ 5名プロフェッショナル・クオンツ監査官による監査ビュー")

default_debate = """**IGNIS**: 短期モメンタムと直近の株価推移を監視中。出来高の急増に警戒しつつ、飛びつき買いは避ける方針を推奨する。
**TECHNOS**: チャート上の移動平均線および価格帯別出来高の壁を意識しろ。上値抵抗帯を明確にブレイクするかどうかが焦点だ。
**SENTINEL**: 取得したWEBニュースやSNS上の噂に惑わされないこと。情報の真偽を冷静に見極める必要がある。
**AEGIS**: 資金管理（ケリー基準等）を徹底し、許容リスクを超えたロットでのエントリーは厳禁とする。
**NEXUS**: 総合裁定。選択されたスタイル（""" + target_style + """）に基づき、規律あるトレード計画を励行せよ。"""

if "chat_history" not in st.session_state or st.session_state.get("target_code_cached") != fc:
    st.session_state["chat_history"] = [{"role": "ai", "text": default_debate}]
    st.session_state["target_code_cached"] = fc

for msg in st.session_state["chat_history"]:
    b_class = "chat-bubble-ai" if msg["role"] == "ai" else "chat-bubble-user"
    st.markdown(f'<div class="{b_class}">{to_html(msg["text"])}</div>', unsafe_allow_html=True)

with st.form("q_form", clear_on_submit=True):
    user_deep_q = st.text_input(
        "💬 この銘柄について監査官ビューに追加するメモや質問",
        placeholder="例: 「押し目買いの具体的なターゲットラインを考察」"
    )
    submitted = st.form_submit_button("メモを追加する", use_container_width=True)

if submitted and user_deep_q.strip():
    st.session_state["chat_history"].append({"role": "user", "text": f"🗣️ **あなた**: {user_deep_q}"})
    reply_text = f"**NEXUS（統括裁定）**: ご提示いただいたメモ「{user_deep_q}」を反映しました。リアルタイムの株価変動と出来高に十分注意してトレードに臨んでください。"
    st.session_state["chat_history"].append({"role": "ai", "text": reply_text})
    st.rerun()
