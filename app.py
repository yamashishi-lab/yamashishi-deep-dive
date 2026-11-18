import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json, os, re, ssl, urllib.request, urllib.parse, hashlib, hmac, datetime
from datetime import datetime, timezone

st.set_page_config(
    page_title="YAMASHISHI DEEP DIVE",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 1. スタイリング・デザイン ---
def inject_css():
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Plus+Jakarta+Sans:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');
    html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif;font-size:14px;background-color:#050811;color:#e2e8f0;}
    .brand-luxury{font-family:'Cinzel',serif!important;font-size:22px;font-weight:800;letter-spacing:2px;background:linear-gradient(90deg,#f8fafc 0%,#38bdf8 50%,#a855f7 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .glass-header{background:radial-gradient(circle at top right,rgba(168,85,247,0.14),transparent 60%),linear-gradient(145deg,#0f172a 0%,#070b14 100%);border:1px solid rgba(148,163,184,0.18);border-radius:14px;padding:16px;margin-bottom:16px;box-shadow:0 10px 28px rgba(0,0,0,0.45);}
    .rank-card{background:linear-gradient(180deg,#0f172a 0%,#090d16 100%)!important;color:#f8fafc!important;border-radius:16px;padding:18px;margin-bottom:20px;border:1px solid rgba(148,163,184,0.22);border-left:5px solid #38bdf8;}
    .ai-council-box{background:rgba(8,12,22,0.98);border:1px solid rgba(56,189,248,0.35);border-radius:10px;padding:14px;margin-top:14px;}
    .chat-bubble-ai{background:rgba(15,23,42,0.85);border-left:3px solid #38bdf8;padding:10px 14px;border-radius:8px;margin-bottom:8px;font-size:12.5px;line-height:1.6;}
    .chat-bubble-user{background:rgba(56,189,248,0.24);border-left:4px solid #38bdf8;padding:10px 14px;border-radius:8px;margin-bottom:8px;font-size:12.5px;line-height:1.6;}
    .pill-badge{font-size:11px;padding:3px 8px;border-radius:4px;border:1px solid rgba(148,163,184,0.3);display:inline-block;margin-right:4px;}
    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

inject_css()

# --- 2. APIキー・設定読み込み ---
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
        return "⚠️ Gemini APIキーが設定されていません。StreamlitのSecretsまたは環境変数に設定してください。"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": sys_p}]},
        "contents": [{"role": "user", "parts": [{"text": user_p}]}]
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=12.0, context=ssl.create_default_context()) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            return "".join([p.get("text", "") for p in parts])
    except Exception as e:
        return f"API呼び出しエラー: {str(e)}"

# --- 3. クエリパラメータおよび入力処理 ---
query_code = st.query_params.get("code", "6920").strip().upper()
query_style = st.query_params.get("style", "デイトレード").strip()

st.markdown('<div class="glass-header"><div class="brand-luxury">YAMASHISHI DEEP DIVE</div><div style="font-size:11px;color:#9
