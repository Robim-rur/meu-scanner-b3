import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ================= CONFIGURAÇÕES =================

SENHA = "CRUVINEL2026"
DATA_EXPIRACAO = "2026-02-15"

# Stops por tipo
STOPS = {
    "AÇÃO": {"loss": 0.05, "gain": 0.08},
    "BDR": {"loss": 0.04, "gain": 0.06},
    "ETF": {"loss": 0.03, "gain": 0.05},
}

# ================= SEGURANÇA =================

hoje = datetime.now().date()
expira = datetime.strptime(DATA_EXPIRACAO, "%Y-%m-%d").date()

st.set_page_config(page_title="Scanner B3", layout="wide")

if hoje > expira:
    st.error("Acesso expirado. Entre em contato para renovar.")
    st.stop()

senha = st.text_input("Digite a senha:", type="password")
if senha != SENHA:
    st.stop()

# ================= FUNÇÕES =================

def estocastico(df):
    low14 = df['Low'].rolling(14).min()
    high14 = df['High'].rolling(14).max()
    k = 100 * (df['Close'] - low14) / (high14 - low14)
    d = k.rolling(3).mean()
    return k, d

def adx(df, n=14):
    df['TR'] = pd.concat([
        df['High'] - df['Low'],
        abs(df['High'] - df['Close'].shift()),
        abs(df['Low'] - df['Close'].shift())
    ], axis=1).max(axis=1)

    df['DM+'] = df['High'].diff()
    df['DM-'] = df['Low'].diff().abs()

    trn = df['TR'].rolling(n).sum()
    dip = (df['DM+'].rolling(n).sum() / trn) * 100
    din = (df['DM-'].rolling(n).sum() / trn) * 100

    dx = abs(dip - din) / (dip + din) * 100
    return dx.rolling(n).mean()

# ================= LISTA AUTOMÁTICA =================

tickers = yf.Tickers(" ".join([
    "PETR4.SA VALE3.SA ITUB4.SA BBDC4.SA BBAS3.SA ABEV3.SA",
    "WEGE3.SA B3SA3.SA PETR3.SA ITSA

