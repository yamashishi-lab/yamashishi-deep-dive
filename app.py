import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json, os, re, ssl, urllib.request, urllib.parse, hashlib, hmac, datetime
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import html

st.set_page_config(
    page_title="YAMASHISHI DEEP DIVE [ULTIMATE HACK]",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 1. スタイリング・デザイン ---
def inject_css():
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Plus+Jakarta+Sans:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif;font-size:14px;background-color:#03050a;color:#e2e8f0;}
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

inject_css()

# --- 2. APIキー・Gemini通信 ---
def get_gemini_key():
    val = os.environ.get("GEMINI_API_KEY", "")
    if not val:
        try:
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                val = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
    return str(val).strip()

GEMINI_API_KEY = get_gemini_key()

def call_gemini(sys_p: str, user_p: str) -> str:
    if not GEMINI_API_KEY:
        return "⚠️ Gemini APIキーが設定されていません。StreamlitのSecretsに設定してください。"
    
    # 修正：有効な最新のモデル名を使用
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": sys_p}]},
        "contents": [{"role": "user", "parts": [{"text": user_p}]}]
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15.0, context=ssl.create_default_context()) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            return "".join([p.get("text", "") for p in parts])
    except Exception as e:
        return f"API呼び出しエラー: {str(e)}"

# --- 3. WEBサーチ＆ニュース収集関数 ---
def search_web_rumors_and_news(query: str) -> list:
    res = []
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ja&gl=JP&ceid=JP:ja"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3.0, context=ssl.create_default_context()) as r:
            for it in ET.fromstring(r.read()).findall("./channel/item")[:8]:
                t = (it.findtext("title") or "").strip()
                d = (it.findtext("description") or "").strip()
                if t:
                    res.append(f"・{t} ({d[:100]}...)")
    except Exception:
        pass
    return res

# --- 4. クエリパラメータおよび入力（安全な取得に修正） ---
qp_code = st.query_params.get("code", "6920")
query_code = str(qp_code[0] if isinstance(qp_code, list) else qp_code).strip().upper()

qp_style = st.query_params.get("style", "デイトレード")
query_style = str(qp_style[0] if isinstance(qp_style, list) else qp_style).strip()

st.markdown('<div class="glass-header"><div class="brand-luxury">YAMASHISHI DEEP DIVE [ULTIMATE HACK]</div><div style="font-size:11.5px;color:#cbd5e1;margin-top:4px;">1銘柄極限ハッキング ｜ WEBマルチサーチ・噂の真偽判定 ＆ 5名ペルソナ容赦なきクロス尋問</div></div>', unsafe_allow_html=True)

col_in1, col_in2 = st.columns([2.5, 1])
target_code = col_in1.text_input("🎯 調査対象銘柄コード", value=query_code, placeholder="例: 6920.T または 7203.T")
target_style = col_in2.selectbox("📊 分析スタイル", ["デイトレード", "スキャルピング", "スイングトレード", "バイ＆ホールド"], index=["デイトレード", "スキャルピング", "スイングトレード", "バイ＆ホールド"].index(query_style) if query_style in ["デイトレード", "スキャルピング", "スイングトレード", "バイ＆ホールド"] else 0)

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
        info = tkr.info
        return df_5m, df_1d, info
    except Exception as e:
        return None, None, {}

with st.spinner(f"📡 【{fc}】の全株価データ取得 ＆ WEBディープサーチ（事実・噂の収集）を実行中..."):
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

# --- 5. メインダッシュボード ---
st.markdown(f"""
<div class="rank-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <span class="pill-badge" style="background:#f43f5e;color:#fff;font-weight:800;">🔥 極限ハッキング中</span>
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

# チャート表示
st.markdown("#### 📈 直近5分足プライスアクション ＆ モメンタム")
st.line_chart(df_5m["Close"])

# --- 6. WEBサーチ＆噂・事実の仕分け ---
st.markdown("#### 🌐 WEBマルチサーチ・生データ＆マーケットの噂")
web_str_joined = "\n".join(web_snippets) if web_snippets else "特段の新規ヘッドライン・噂なし"

with st.spinner("🤖 AIがWEB上の最新情報・噂話を「事実（ファクト）」と「根拠なき噂（思惑）」に仕分け中..."):
    sorting_sys = "あなたは極限までシニカルな金融アナリストです。提供されたWEB上のヘッドラインや噂について、ファクト（確度の高い事実）と、思惑・仕手系ウワサ（根拠の薄い噂・思惑）に綺麗に分類し、それぞれの危険度や影響度を日本語で解説してください。"
    sorting_user = f"対象銘柄: {corp_name} ({fc})\nWEB収集データ:\n{web_str_joined}"
    sorted_analysis = call_gemini(sorting_sys, sorting_user)

st.markdown(f'<div class="fact-box"><b>🔍 【事実・ファクト分析】</b><br>{sorted_analysis.split("【思惑】")[0] if "【思惑】" in sorted_analysis else sorted_analysis}</div>', unsafe_allow_html=True)
if "【思惑】" in sorted_analysis:
    st.markdown(f'<div class="rumor-box"><b>🕵️‍♂️ 【市場の噂・仕手系思惑（要注意）】</b><br>{sorted_analysis.split("【思惑】")[1]}</div>', unsafe_allow_html=True)

# --- 7. 5名ペルソナによる容赦なきクロス尋問合議 ---
st.markdown("#### 🏛️ 5名プロフェッショナル・クオンツ監査官による極限クロス尋問")

council_sys = f"""あなたはプロフェッショナル・クオンツ監査委員会の5名の専門監査官（IGNIS / TECHNOS / SENTINEL / AEGIS / NEXUS）です。
対象銘柄「{corp_name}（{fc}）」、分析スタイル「{target_style}」、および先ほど収集したWEB上の最新情報・噂話をすべて踏まえ、この銘柄を徹底的に深掘りした「容赦ない監査合議」を出力してください。
甘い見通しは一切排除し、噂がハメ込み（ダマシ）なのか本物なのかを激論させてください。
以下の5名の発言をマークダウン形式（「**[名前]**: 内容」）で明確に分けて出力してください。
1. IGNIS（短期モメンタム執行 / 飛びつき厳禁の判断）
2. TECHNOS（3階層MTF・価格帯別出来高 / 上値の壁の分析）
3. SENTINEL（リスク・しこり壁・悪材料・噂のダマシ監査）
4. AEGIS（検証・最大DD・ケリー資金管理 / ロットの許容度）
5. NEXUS（最終執行裁定統括 / 買いか、空売りか、完全見送りかの最終ジャッジ）"""

council_user = f"現在値: {curr_px}円, スタイル: {target_style}。収集されたWEB情報・噂を考慮し、この銘柄の真の優位性と致命的リスクを徹底的にクロス尋問してください。"

if "ultimate_chat_history" not in st.session_state or st.session_state.get("target_code_cached") != fc:
    st.session_state["ultimate_chat_history"] = []
    st.session_state["target_code_cached"] = fc

if st.button("🔥 5名の監査官にこの銘柄の極限クロス尋問を行わせる", type="primary", use_container_width=True):
    with st.spinner("🔵 5名の監査官がバチバチに議論中..."):
        initial_debate = call_gemini(council_sys, council_user)
        st.session_state["ultimate_chat_history"] = [{"role": "ai", "text": initial_debate}]

for msg in st.session_state["ultimate_chat_history"]:
    b_class = "chat-bubble-ai" if msg["role"] == "ai" else "chat-bubble-user"
    st.markdown(f'<div class="{b_class}">{msg["text"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

# 無限壁打ちフォーム
with st.form("ultimate_q_form", clear_on_submit=True):
    user_deep_q = st.text_input("💬 この銘柄について監査官に追加で突っ込む・質問する", placeholder="例: 「この噂は仕手の嵌め込みの可能性が高いのでは？」「具体的な損切りラインを再計算して」")
    if st.form_submit_button("突撃質問を投下する", use_container_width=True) and user_deep_q.strip():
        st.session_state["ultimate_chat_history"].append({"role": "user", "text": f"🗣️ **あなた**: {user_deep_q}"})
        with st.spinner("監査官が回答を再構築中..."):
            history_str = "\n".join([m['text'] for m in st.session_state["ultimate_chat_history"]])
            follow_res = call_gemini(council_sys, f"これまでの議論・対話履歴:\n{history_str}\n\n追加の突撃質問: {user_deep_q}")
            st.session_state["ultimate_chat_history"].append({"role": "ai", "text": follow_res})
        st.rerun()
