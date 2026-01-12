import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="Scanner VIP GOLD", layout="wide")

# ======================
# 🔐 SISTEMA DE LOGIN
# ======================
SENHA_CORRETA = "mestre10"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acesso Restrito")
    senha = st.text_input("Digite sua senha:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_CORRETA:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# ======================
# 📊 LISTA DE ATIVOS
# ======================
ATIVOS = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "BBDC4.SA",
    "WEGE3.SA", "ABEV3.SA", "BOVA11.SA"
]

# ======================
# 🔎 FUNÇÃO DE ANÁLISE
# ======================
def analisar_ativo(ticker):
    df_d = yf.download(ticker, period="6mo", interval="1d")
    df_w = yf.download(ticker, period="2y", interval="1wk")

    if df_d.empty or df_w.empty:
        return None

    # ===== SEMANAL =====
    df_w["EMA69"] = ta.ema(df_w["Close"], length=69)
    dmi_w = ta.dmi(df_w["High"], df_w["Low"], df_w["Close"])
    stoch_w = ta.stoch(df_w["High"], df_w["Low"], df_w["Close"])

    if df_w["Close"].iloc[-1] <= df_w["EMA69"].iloc[-1]:
        return None
    if dmi_w["DMP_14"].iloc[-1] <= dmi_w["DMN_14"].iloc[-1]:
        return None
    if stoch_w["STOCHk_14_3_3"].iloc[-1] < stoch_w["STOCHk_14_3_3"].iloc[-2]:
        return None

    # ===== DIÁRIO =====
    df_d["EMA69"] = ta.ema(df_d["Close"], length=69)
    dmi_d = ta.dmi(df_d["High"], df_d["Low"], df_d["Close"])
    stoch_d = ta.stoch(df_d["High"], df_d["Low"], df_d["Close"])

    if df_d["Close"].iloc[-1] <= df_d["EMA69"].iloc[-1]:
        return None
    if dmi_d["DMP_14"].iloc[-1] <= dmi_d["DMN_14"].iloc[-1]:
        return None
    if stoch_d["STOCHk_14_3_3"].iloc[-1] >= 80:
        return None
    if df_d["Close"].iloc[-1] <= df_d["High"].iloc[-2]:
        return None

    preco = df_d["Close"].iloc[-1]

    # Stops padrão (ações)
    stop = preco * 0.95
    gain = preco * 1.075

    return {
        "Ativo": ticker.replace(".SA", ""),
        "Preço": round(preco, 2),
        "Stop": round(stop, 2),
        "Gain": round(gain, 2)
    }

# ======================
# 🖥️ INTERFACE
# ======================
st.title("📈 Scanner VIP GOLD")
st.write("Ativos que **deram entrada hoje** segundo o setup proprietário")

if st.button("Rodar Scanner"):
    resultados = []

    with st.spinner("Analisando mercado..."):
        for

