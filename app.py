import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os, re, time
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
import html
import google.generativeai as genai

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