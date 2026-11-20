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
    page_title="YAMASHISHI DEEP DIVE v2 [QUANTUM TERMINAL]",
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
        margin-bottom: 12px;
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
        grid-template-columns: repeat(auto-fit, minmax(115px, 1fr));
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
        font-size: 14px;
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
    .memo-box {
        background: linear-gradient(180deg, #0b192c 0%, #090d16 100%);
        border: 1px solid rgba(168, 85, 247, 0.45);
        border-left: 4px solid #a855f7;
        padding: 14px 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        font-size: 12.5px;
        line-height: 1.75;
        color: #f1f5f9;
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
# 2. フォーマット ＆ ユーティリティ
# =========================================================================
def fmt_currency(val, is_jp: bool) -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "-"
    return f"{val:,.0f}円" if is_jp else f"${val:,.2f}"

def fmt_large_num(val, is_jp: bool) -> str:
    if not val or (isinstance(val, float) and np.isnan(val)):
        return "-"
    if is_jp:
        if abs(val) >= 1e12: return f"{val/1e12:.2f}兆円"
        if abs(val) >= 1e8:  return f"{val/1e8:,.0f}億円"
        return f"{val:,.0f}円"
    else:
        if abs(val) >= 1e12: return f"${val/1e12:.2f}T"
        if abs(val) >= 1e9:  return f"${val/1e9:.2f}B"
        if abs(val) >= 1e6:  return f"${val/1e6:.1f}M"
        return f"${val:,.0f}"

def get_gemini_api_key() -> str:
    k = os.environ.get("GEMINI_API_KEY", "")
    if not k:
        try:
            k = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            k = ""
    return str(k).strip()

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

@st.cache_data(ttl=300)
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

@st.cache_data(ttl=180)
def load_stock_core(code: str) -> dict:
    tkr = yf.Ticker(code)
    df_1d = tkr.history(period="1y", interval="1d", auto_adjust=True)
    if df_1d is not None and not df_1d.empty:
        df_1d.index = pd.to_datetime(df_1d.index).tz_localize(None).normalize()
        df_1d = df_1d[~df_1d.index.duplicated(keep="last")]

    try:
        info = tkr.info or {}
    except Exception:
        info = {}

    # 四半期財務
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

    # 決算サプライズ履歴
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

    # オプション
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
                "exp": exps[0], "pcr": round(p_vol / max(c_vol, 1.0), 2),
                "call_vol": int(c_vol), "put_vol": int(p_vol),
                "call_iv": round(c_iv, 1), "put_iv": round(p_iv, 1)
            }
    except Exception:
        pass

    return {
        "df_1d": df_1d, "info": info, "q_fin": q_fin,
        "earnings_hist": earnings_hist, "inst_holders": inst_holders,
        "insiders": insiders, "opt_data": opt_data
    }

@st.cache_data(ttl=300)
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
    # -1.0 (極端な弱気) ～ +1.0 (極端な強気) のショック係数
    shock_score = round((pos_c - neg_c) / tot, 2)
    return {
        "items": items_out, "pos_pct": round(pos_c / tot * 100),
        "neu_pct": round(neu_c / tot * 100), "neg_pct": round(neg_c / tot * 100),
        "counts": (pos_c, neu_c, neg_c), "shock_score": shock_score
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
                if t: risks.append(f"{t} ({pub})")
    except Exception:
        pass
    return risks

# =========================================================================
# 4. アルゴリズム計算エンジン（マクロβ・モンテカルロ未来予測・しこり玉）
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

def run_monte_carlo_forecast(
    curr_px: float, df_1d: pd.DataFrame, macro_sens: list, news_shock: float,
    tp_px: float, sl_px: float, whatif_mkt_pct: float = 0.0, whatif_fx_pct: float = 0.0,
    whatif_news_shock: float = 0.0, days: int = 5, n_sims: int = 600
) -> dict:
    rets = df_1d["Close"].pct_change().dropna().tail(60).values
    hist_mu = float(np.mean(rets)) if len(rets) > 5 else 0.0
    hist_sigma = float(np.std(rets)) if len(rets) > 5 else 0.02
    hist_sigma = float(np.clip(hist_sigma, 0.008, 0.08))

    # 1. マクロ連動のリアルタイム・ドリフト算出（上位2相関指標＋ドル円）
    sens_map = {x["key"]: x for x in macro_sens}
    mkt_key = "SOX" if "SOX" in sens_map and abs(sens_map["SOX"]["corr"]) > 0.35 else ("N225" if "N225" in sens_map else "SP500")
    mkt_beta = sens_map.get(mkt_key, {}).get("beta", 0.5)
    fx_beta = sens_map.get("USDJPY", {}).get("beta", 0.0)

    live_mkt_shift = (sens_map.get(mkt_key, {}).get("latest_diff", 0.0) / 100.0) * mkt_beta * 0.45
    whatif_shift = (whatif_mkt_pct / 100.0) * mkt_beta + (whatif_fx_pct / 100.0) * fx_beta

    # 2. ニュース感情ショック（Day+1に強く反映し、徐々に減衰）
    total_news_shock = np.clip(news_shock + whatif_news_shock, -1.5, 1.5)
    news_day1_shift = total_news_shock * hist_sigma * 0.85

    # ニュースが大きい時はボラティリティも拡大
    eff_sigma = hist_sigma * (1.0 + abs(total_news_shock) * 0.25)

    # 3. モンテカルロ・シミュレーション（固定シードでスライダー操作時のチラつき防止）
    rng = np.random.default_rng(42)
    paths = np.zeros((n_sims, days + 1))
    paths[:, 0] = curr_px
    for d in range(1, days + 1):
        shock_d = (live_mkt_shift + whatif_shift + news_day1_shift) if d == 1 else (news_day1_shift * (0.35 ** (d - 1)))
        z = rng.standard_normal(n_sims)
        step_ret = hist_mu + shock_d + eff_sigma * z
        paths[:, d] = np.maximum(paths[:, d - 1] * (1.0 + step_ret), curr_px * 0.3)

    p90 = np.percentile(paths, 85, axis=0)
    p50 = np.percentile(paths, 50, axis=0)
    p10 = np.percentile(paths, 15, axis=0)

    # TP / SL 到達確率（5営業日以内）
    hit_tp_prob = float(np.mean(np.max(paths[:, 1:], axis=1) >= tp_px)) * 100.0
    hit_sl_prob = float(np.mean(np.min(paths[:, 1:], axis=1) <= sl_px)) * 100.0

    return {
        "p90": [round(float(x), 2) for x in p90],
        "p50": [round(float(x), 2) for x in p50],
        "p10": [round(float(x), 2) for x in p10],
        "day1_p50": float(p50[1]),
        "day1_chg": round((float(p50[1]) - curr_px) / max(curr_px, 1e-4) * 100.0, 2),
        "hit_tp_prob": round(hit_tp_prob, 1),
        "hit_sl_prob": round(hit_sl_prob, 1),
        "mkt_driver_lbl": sens_map.get(mkt_key, {}).get("label", "市場指数"),
        "mkt_beta": mkt_beta,
        "eff_sigma_pct": round(eff_sigma * 100.0, 2)
    }

def compute_overhead_supply(df_1d: pd.DataFrame, curr_px: float) -> dict:
    """過去1年の価格帯別出来高から「現在値より上のしこり玉比率」を算出"""
    sub = df_1d.tail(250)
    if len(sub) < 20:
        return {"overhead_pct": 0.0, "poc_px": curr_px}
    typ = (sub["High"].values + sub["Low"].values + sub["Close"].values) / 3.0
    vol = sub["Volume"].values.astype(float)
    tot_v = max(float(np.sum(vol)), 1.0)
    above_v = float(np.sum(vol[typ > curr_px * 1.01]))
    bins = np.linspace(float(np.min(typ)), float(np.max(typ)) + 1e-4, 21)
    hist = np.bincount(np.clip(np.digitize(typ, bins) - 1, 0, 19), weights=vol, minlength=20)
    poc_idx = int(np.argmax(hist))
    poc_px = float((bins[poc_idx] + bins[poc_idx + 1]) * 0.5)
    return {"overhead_pct": round(above_v / tot_v * 100.0, 1), "poc_px": poc_px}

def generate_investment_memo(corp_name: str, fc: str, curr_px: float, is_jp: bool, info: dict, fcst: dict, macro_sens: list, news_res: dict, gov_risks: list, ovh: dict) -> tuple:
    api_key = get_gemini_api_key()
    prompt = f"""あなたはヘッジファンドのシニア・エクイティアナリストです。以下の実測データに基づき、ファンドマネージャー向けの「1分インベストメントメモ」を日本語で簡潔に作成してください。
銘柄: {corp_name} ({fc}) / 現在値: {fmt_currency(curr_px, is_jp)}
PER: {info.get('trailingPE')} / PBR: {info.get('priceToBook')} / EV/EBITDA: {info.get('enterpriseToEbitda')} / 目標株価平均: {info.get('targetMeanPrice')}
明日予測中央値: {fcst['day1_chg']:+.2f}% / 5日以内利確到達率: {fcst['hit_tp_prob']}% / 上値しこり玉比率: {ovh['overhead_pct']}%
最大マクロ連動: {macro_sens[0]['label'] if macro_sens else '-'} (相関 {macro_sens[0]['corr'] if macro_sens else 0})
ニュース強気度: {news_res['pos_pct']}% / ガバナンスリスク検知数: {len(gov_risks)}件

以下の3セクション構成（合計400文字以内、箇条書き）で出力してください：
🟢 Bull Case（強気シナリオ）
🔴 Bear Case（弱気・死角リスク）
⚡ Next Catalyst（次の注目トリガー）"""

    if api_key:
        for mod in ("gemini-2.5-flash", "gemini-2.0-flash"):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent"
                body = json.dumps({"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 700, "temperature": 0.6}}).encode("utf-8")
                req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "x-goog-api-key": api_key}, method="POST")
                with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=12.0) as r:
                    res_j = json.loads(r.read().decode("utf-8"))
                    txt = "".join([p.get("text", "") for p in res_j["candidates"][0]["content"]["parts"] if "text" in p])
                    if txt.strip():
                        return txt.strip(), f"🔵 Gemini AI 生成 ({mod})"
            except Exception:
                continue

    # API未接続時の自動ルールベース・メモ
    top_m = macro_sens[0] if macro_sens else {"label": "市場指数", "corr": 0.0, "beta": 1.0}
    target_m = info.get("targetMeanPrice")
    upside_s = f"{(target_m/curr_px - 1)*100:+.1f}%" if target_m else "算出不可"
    bull = f"・アナリスト目標株価との乖離は {upside_s}、5日以内の利確目安到達確率は {fcst['hit_tp_prob']}%。\n・ニュース強気度 {news_res['pos_pct']}%、上値しこり玉は {ovh['overhead_pct']}%。"
    bear = f"・{top_m['label']}との相関係数が {top_m['corr']}（β={top_m['beta']}）と高く、マクロ急変時の連れ安リスクあり。\n・ガバナンス関連報道は {len(gov_risks)}件検知（{'要精査' if gov_risks else '現時点でクリーン'}）。"
    cat = f"・翌営業日の予測中央値は {fcst['day1_chg']:+.2f}%。{top_m['label']}の夜間動向と出来高急増の有無が直近のトリガー。"
    return f"🟢 Bull Case（強気シナリオ）\n{bull}\n\n🔴 Bear Case（弱気・死角リスク）\n{bear}\n\n⚡ Next Catalyst（次の注目トリガー）\n{cat}", "⚙️ クオンツ自動ルール生成（Gemini API未設定時）"

# =========================================================================
# 5. ヘッダー ＆ コントロール
# =========================================================================
h_col1, h_col2 = st.columns([3.2, 1.2])
with h_col1:
    st.markdown(
        '<div class="glass-header" style="margin-bottom:8px;">'
        '<div class="brand-luxury">YAMASHISHI DEEP DIVE v2</div>'
        '<div style="font-size:11px;color:#94a3b8;margin-top:2px;">未来予測モンテカルロ × マクロβ感応度 × 機関投資家ディープ監査</div>'
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
if not fc: st.stop()
if re.match(r"^[0-9]{3}[0-9A-Z]$", fc): fc = f"{fc}.T"
is_jp = fc.endswith(".T")

with st.spinner(f"📡 【{fc}】の市場データ・マクロ指標・財務・ニュースを統合スキャン中..."):
    data = load_stock_core(fc)
    macro_data = load_macro_data()

df_1d = data["df_1d"]
info = data["info"]
if df_1d is None or df_1d.empty:
    st.error(f"❌ 銘柄コード `{fc}` の市場データを取得できませんでした。")
    st.stop()

corp_name = info.get("longName") or info.get("shortName") or fc
sector = info.get("sector") or "セクター未分類"
industry = info.get("industry") or "-"
curr_px = float(df_1d["Close"].iloc[-1])
prev_px = float(df_1d["Close"].iloc[-2]) if len(df_1d) >= 2 else curr_px
chg_pct = ((curr_px - prev_px) / max(prev_px, 1e-4)) * 100.0
chg_col = "#10b981" if chg_pct >= 0 else "#ef4444"

# ATR14 ＆ スタイル別 TP/SL
h_arr, l_arr, c_arr = df_1d["High"].values, df_1d["Low"].values, df_1d["Close"].values
prev_c = np.roll(c_arr, 1); prev_c[0] = c_arr[0]
atr14 = float(np.mean(np.maximum(h_arr - l_arr, np.maximum(np.abs(h_arr - prev_c), np.abs(l_arr - prev_c)))[-14:]))
mult_map = {"スキャルピング": (0.5, 0.9), "デイトレード": (0.7, 1.4), "スイングトレード": (1.5, 3.0), "バイ＆ホールド": (2.5, 5.0)}
sl_m, tp_m = mult_map.get(in_style, (0.7, 1.4))
tp_px = curr_px + atr14 * tp_m
sl_px = max(curr_px - atr14 * sl_m, curr_px * 0.5)

macro_sens = compute_macro_sensitivity(df_1d["Close"], macro_data)
news_res = fetch_news_and_sentiment(f"{corp_name} OR {fc.replace('.T', '')} 株価")
gov_risks = fetch_governance_risks(corp_name)
ovh_data = compute_overhead_supply(df_1d, curr_px)

# ベース予測（スライダー初期値）
base_fcst = run_monte_carlo_forecast(curr_px, df_1d, macro_sens, news_res["shock_score"], tp_px, sl_px)

# =========================================================================
# 6. トップ企業カード ＆ 4大サマリー（常時表示）
# =========================================================================
target_mean = info.get("targetMeanPrice")
upside_str = f"{((target_mean - curr_px)/curr_px*100):+.1f}%" if (target_mean and curr_px > 0) else "-"
risk_status = f"⚠️ {len(gov_risks)}件検知" if gov_risks else "🟢 クリーン"
risk_col = "#f87171" if gov_risks else "#10b981"
d1_col = "#10b981" if base_fcst["day1_chg"] >= 0 else "#ef4444"

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
    <div><div class="metric-lbl">🔮 明日予測中央値</div><div class="metric-val" style="color:{d1_col};">{base_fcst['day1_chg']:+.2f}%</div></div>
    <div><div class="metric-lbl">🎯 アナリスト目標乖離</div><div class="metric-val" style="color:#fde047;">{upside_str}</div></div>
    <div><div class="metric-lbl">🧱 上値しこり玉比率</div><div class="metric-val" style="color:#c084fc;">{ovh_data['overhead_pct']}%</div></div>
    <div><div class="metric-lbl">🚨 ガバナンス監査</div><div class="metric-val" style="color:{risk_col};">{risk_status}</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# =========================================================================
# 7. 4タブ集約ビュー（メイン：未来予測ファンチャート）
# =========================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 未来予測チャート",
    "🌐 マクロβ・決算",
    "💰 プロ財務・需給",
    "🚨 リスク・AIメモ"
])

# -------------------------------------------------------------------------
# TAB 1: リアルタイム未来予測ファンチャート ＆ What-if ストレステスト
# -------------------------------------------------------------------------
with tab1:
    st.markdown("##### 🎛️ What-if ストレステスト（今夜の急変をリアルタイム反映）")
    wc1, wc2, wc3 = st.columns(3)
    w_mkt = wc1.slider(f"📊 {base_fcst['mkt_driver_lbl']} (%)", -5.0, 5.0, 0.0, 0.5)
    w_fx  = wc2.slider("💴 ドル円変動 (%)", -3.0, 3.0, 0.0, 0.25)
    w_nws = wc3.slider("📰 突発ニュース衝撃", -1.0, 1.0, 0.0, 0.2)

    fcst = run_monte_carlo_forecast(
        curr_px, df_1d, macro_sens, news_res["shock_score"], tp_px, sl_px,
        whatif_mkt_pct=w_mkt, whatif_fx_pct=w_fx, whatif_news_shock=w_nws
    )

    # 過去15営業日（実測）＋ 未来5営業日（確率コーン）を結合
    hist_tail = df_1d.tail(15)
    hist_dates = [d.strftime("%m/%d") for d in hist_tail.index]
    hist_vals = [round(float(x), 2) for x in hist_tail["Close"].values]
    fut_labels = ["明日(+1d)", "+2d", "+3d", "+4d", "+5d"]
    all_x = hist_dates + fut_labels

    n_hist = len(hist_vals)
    pad_none = [None] * (n_hist - 1)
    series_actual = hist_vals + [None] * 5
    series_p90 = pad_none + fcst["p90"]
    series_p50 = pad_none + fcst["p50"]
    series_p10 = pad_none + fcst["p10"]

    opt_fan = {
        "backgroundColor": "#0b1120",
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["実測終値", "強気軌道(85%)", "予測中央値(50%)", "弱気軌道(15%)"], "textStyle": {"color": "#cbd5e1", "fontSize": 10}, "top": 4},
        "grid": {"top": 34, "bottom": 26, "left": 58, "right": 18},
        "xAxis": {"type": "category", "data": all_x, "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
        "yAxis": {"type": "value", "scale": True, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
        "series": [
            {"name": "実測終値", "type": "line", "data": series_actual, "lineStyle": {"color": "#f8fafc", "width": 2.5}, "showSymbol": False},
            {"name": "強気軌道(85%)", "type": "line", "data": series_p90, "smooth": True, "lineStyle": {"color": "#10b981", "width": 1.8, "type": "dashed"}, "showSymbol": False},
            {"name": "予測中央値(50%)", "type": "line", "data": series_p50, "smooth": True, "lineStyle": {"color": "#38bdf8", "width": 3.0}, "areaStyle": {"color": "rgba(56,189,248,0.12)"}, "showSymbol": True, "symbolSize": 5},
            {"name": "弱気軌道(15%)", "type": "line", "data": series_p10, "smooth": True, "lineStyle": {"color": "#ef4444", "width": 1.8, "type": "dashed"}, "showSymbol": False},
            {"name": "TP", "type": "line", "data": [round(tp_px, 2)] * len(all_x), "lineStyle": {"color": "rgba(16,185,129,0.5)", "type": "dotted", "width": 1.2}, "showSymbol": False},
            {"name": "SL", "type": "line", "data": [round(sl_px, 2)] * len(all_x), "lineStyle": {"color": "rgba(239,68,68,0.5)", "type": "dotted", "width": 1.2}, "showSymbol": False}
        ]
    }
    render_echarts(opt_fan, height=310)

    st.markdown(f"""
    <div class="quant-box">
      <b>🔮 モンテカルロ600回試行・リアルタイム予測サマリー（{html.escape(in_style)}基準）</b><br>
      ・<b>明日の予測中央値:</b> <b>{fmt_currency(fcst['day1_p50'], is_jp)}</b>（現在値比 <b style="color:{'#6ee7b7' if fcst['day1_chg']>=0 else '#fca5a5'};">{fcst['day1_chg']:+.2f}%</b>）<br>
      ・<b>5営業日以内の到達確率:</b> 利確目安({fmt_currency(tp_px, is_jp)}) <b style="color:#6ee7b7;">{fcst['hit_tp_prob']}%</b> ｜ 損切目安({fmt_currency(sl_px, is_jp)}) <b style="color:#fca5a5;">{fcst['hit_sl_prob']}%</b><br>
      ・<b>適用アルゴリズム:</b> 主連動ドライバー <b>{html.escape(fcst['mkt_driver_lbl'])} (β={fcst['mkt_beta']})</b> ＋ ニュース衝撃({news_res['shock_score']:+.2f}) ＋ 想定日次ボラ <b>{fcst['eff_sigma_pct']}%</b>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# TAB 2: マクロ感応度マトリクス ＆ 決算サプライズ履歴
# -------------------------------------------------------------------------
with tab2:
    st.markdown("##### 🌐 マクロ感応度マトリクス（過去90営業日の相関・β）")
    if macro_sens:
        opt_corr = {
            "backgroundColor": "#0b1120",
            "tooltip": {"trigger": "axis"},
            "grid": {"top": 18, "bottom": 24, "left": 88, "right": 24},
            "xAxis": {"type": "value", "min": -1, "max": 1, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}, "axisLabel": {"color": "#94a3b8", "fontSize": 10}},
            "yAxis": {"type": "category", "data": [x["label"] for x in macro_sens][::-1], "axisLabel": {"color": "#e2e8f0", "fontSize": 11}},
            "series": [{"type": "bar", "data": [
                {"value": x["corr"], "itemStyle": {"color": "#10b981" if x["corr"] >= 0 else "#ef4444"}}
                for x in macro_sens[::-1]
            ]}]
        }
        render_echarts(opt_corr, height=230)

        rows_m = "".join([
            f"<tr><td><b>{html.escape(x['label'])}</b></td>"
            f"<td style='color:{'#10b981' if x['corr']>=0 else '#ef4444'};font-weight:700;'>{x['corr']:+.2f}</td>"
            f"<td>{x['beta']:+.2f}</td>"
            f"<td style='color:{'#10b981' if x['latest_diff']>=0 else '#ef4444'};'>{x['latest_diff']:+.2f}%</td></tr>"
            for x in macro_sens
        ])
        st.markdown(f'<div class="dark-box"><table class="data-table"><thead><tr><th>マクロ指標</th><th>相関係数</th><th>感応度(β)</th><th>直近変動</th></tr></thead><tbody>{rows_m}</tbody></table></div>', unsafe_allow_html=True)
    else:
        st.info("マクロ指標データを取得できませんでした。")

    st.markdown("##### 📅 決算サプライズ履歴（予想EPS vs 実績EPS）")
    eh = data["earnings_hist"]
    if eh:
        rows_e = ""
        for e in eh:
            est_s = f"{e['est']:.2f}" if e["est"] is not None else "-"
            rep_s = f"{e['rep']:.2f}" if e["rep"] is not None else "発表待ち"
            if e["surp"] is not None:
                sc = "#10b981" if e["surp"] >= 0 else "#ef4444"
                surp_s = f"<span style='color:{sc};font-weight:800;'>{e['surp']:+.1f}%</span>"
            else:
                surp_s = "-"
            rows_e += f"<tr><td>{html.escape(e['date'])}</td><td>{est_s}</td><td>{rep_s}</td><td>{surp_s}</td></tr>"
        st.markdown(f'<div class="dark-box"><table class="data-table"><thead><tr><th>決算日</th><th>予想EPS</th><th>実績EPS</th><th>サプライズ</th></tr></thead><tbody>{rows_e}</tbody></table></div>', unsafe_allow_html=True)
    else:
        st.caption("ℹ️ この銘柄のEPSサプライズ履歴はyfinanceから取得できませんでした。")

# -------------------------------------------------------------------------
# TAB 3: プロ仕様財務（EV/EBITDA・FCF・PEG）＆ 空売り・しこり玉レーダー
# -------------------------------------------------------------------------
with tab3:
    ev_ebitda = f"{info.get('enterpriseToEbitda'):.1f}倍" if info.get("enterpriseToEbitda") else "-"
    peg_r = f"{info.get('pegRatio'):.2f}" if info.get("pegRatio") else "-"
    fcf = info.get("freeCashflow")
    mcap_raw = info.get("marketCap")
    fcf_yield = f"{(fcf / mcap_raw * 100):.2f}%" if (fcf and mcap_raw and mcap_raw > 0) else "-"
    short_pct = f"{info.get('shortPercentOfFloat')*100:.1f}%" if info.get("shortPercentOfFloat") else "-"
    short_ratio = f"{info.get('shortRatio'):.1f}日" if info.get("shortRatio") else "-"

    st.markdown(f"""
    <div class="winrate-bar" style="margin-bottom:10px;">
      <div><div class="metric-lbl">EV / EBITDA</div><div class="metric-val">{ev_ebitda}</div></div>
      <div><div class="metric-lbl">FCF利回り</div><div class="metric-val" style="color:#10b981;">{fcf_yield}</div></div>
      <div><div class="metric-lbl">PEGレシオ</div><div class="metric-val" style="color:#fde047;">{peg_r}</div></div>
      <div><div class="metric-lbl">空売り比率 / 日数</div><div class="metric-val" style="color:#f87171;">{short_pct} / {short_ratio}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # しこり玉 & 空売り踏み上げアラート
    if info.get("shortPercentOfFloat") and info["shortPercentOfFloat"] >= 0.15:
        st.markdown(f'<div class="warning-box"><b>🔥 ショートスクイーズ（空売り踏み上げ）警戒</b><br>浮動株に対する空売り比率が <b>{short_pct}</b>（カバー日数 {short_ratio}）と高水準です。好材料で急騰しやすい需給構造です。</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dark-box">
      <b>🧱 価格帯別出来高（Volume Profile）しこり玉診断（過去1年）</b><br>
      ・<b>現在値より上の戻り売り（しこり玉）比率:</b> <b style="color:#c084fc;">{ovh_data['overhead_pct']}%</b><br>
      ・<b>1年最大出来高価格帯 (POC):</b> <b>{fmt_currency(ovh_data['poc_px'], is_jp)}</b>（{'現在値はPOCより上方＝下値支持' if curr_px >= ovh_data['poc_px'] else '現在値はPOCより下方＝上値抵抗'}）
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
        render_echarts(opt_fin, height=230)

    opt_d = data["opt_data"]
    if opt_d:
        st.markdown(f'<div class="quant-box"><b>📈 オプション市場（満期: {html.escape(opt_d["exp"])}）</b><br>PCR: <b>{opt_d["pcr"]}</b> ｜ Call IV: <b>{opt_d["call_iv"]}%</b> ｜ Put IV: <b>{opt_d["put_iv"]}%</b></div>', unsafe_allow_html=True)

    if data["inst_holders"]:
        rows_h = "".join([f"<tr><td>{html.escape(x['holder'])}</td><td>{x['pct']:.2f}%</td><td>{x['shares']:,}</td></tr>" for x in data["inst_holders"]])
        st.markdown(f'<div class="dark-box"><b>🏛️ 主要機関投資家トップ5</b><table class="data-table"><thead><tr><th>機関名</th><th>保有比率</th><th>株数</th></tr></thead><tbody>{rows_h}</tbody></table></div>', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# TAB 4: リスク監査・ニュース感情 ＆ 1分インベストメントメモ
# -------------------------------------------------------------------------
with tab4:
    memo_key = f"memo_{fc}"
    if st.button("🧠 機関投資家向け「1分インベストメントメモ」を生成", use_container_width=True, type="primary"):
        with st.spinner("🧠 全データ（財務・マクロβ・ニュース・しこり玉）を統合してメモを作成中..."):
            m_txt, m_src = generate_investment_memo(corp_name, fc, curr_px, is_jp, info, base_fcst, macro_sens, news_res, gov_risks, ovh_data)
            st.session_state[memo_key] = (m_txt, m_src)

    if memo_key in st.session_state:
        m_txt, m_src = st.session_state[memo_key]
        st.markdown(f'<div class="memo-box"><div style="font-size:11px;color:#c084fc;font-weight:800;margin-bottom:6px;">{html.escape(m_src)}</div>{html.escape(m_txt).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    if gov_risks:
        risk_html = "<br>".join([f"・{html.escape(x)}" for x in gov_risks])
        st.markdown(f'<div class="warning-box"><b>🚨 ガバナンス・不祥事・訴訟関連ヒット ({len(gov_risks)}件)</b><br>{risk_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="quant-box"><b>🟢 ガバナンス・不祥事監査: クリーン</b><br>直近ニュースにおいて不祥事・不正・訴訟などの特異リスクシグナルは検知されていません。</div>', unsafe_allow_html=True)

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
    render_echarts(opt_sent, height=190)

    if news_res["items"]:
        n_html = ""
        for it in news_res["items"]:
            badge_c = "#10b981" if it["sent"] == "POS" else ("#ef4444" if it["sent"] == "NEG" else "#94a3b8")
            n_html += f'<div style="margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid rgba(148,163,184,0.12);"><span style="color:{badge_c};font-weight:800;font-size:10.5px;">[{it["sent"]}]</span> <a href="{html.escape(it["link"])}" target="_blank" style="color:#e2e8f0;text-decoration:none;font-weight:600;">{html.escape(it["title"])}</a> <span style="color:#64748b;font-size:10.5px;">({html.escape(it["pub"])})</span></div>'
        st.markdown(f'<div class="dark-box"><b>📰 最新ニュースヘッドライン ＆ 感情判定</b><br><br>{n_html}</div>', unsafe_allow_html=True)
