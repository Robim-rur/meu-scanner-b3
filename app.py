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
    "WEGE3.SA B3SA3.SA PETR3.SA ITSA4.SA"
]))

dados_liquidez = []

for t in tickers.tickers:
    try:
        hist = tickers.tickers[t].history(period="5d")
        volume_medio = hist['Volume'].mean()
        dados_liquidez.append((t, volume_medio))
    except:
        pass

df_liq = pd.DataFrame(dados_liquidez, columns=["Ticker", "Volume"])
df_liq = df_liq.sort_values("Volume", ascending=False).head(200)

# ================= SCANNER =================

resultado = []

for ticker in df_liq["Ticker"]:
    try:
        semanal = yf.download(ticker, period="6mo", interval="1wk")
        diario = yf.download(ticker, period="3mo", interval="1d")

        if len(semanal) < 20 or len(diario) < 20:
            continue

        k_w, d_w = estocastico(semanal)
        k_d, d_d = estocastico(diario)
        adx_d = adx(diario)

        if k_w.iloc[-1] <= d_w.iloc[-1]:
            continue
        if k_d.iloc[-1] <= d_d.iloc[-1]:
            continue
        if adx_d.iloc[-1] <= 15:
            continue

        preco = diario['Close'].iloc[-1]
        tipo = "AÇÃO"

        loss = preco * (1 - STOPS[tipo]["loss"])
        gain = preco * (1 + STOPS[tipo]["gain"])

        rr = (gain - preco) / (preco - loss)

        if rr < 1.5:
            continue

        resultado.append([
            ticker.replace(".SA", ""),
            preco,
            loss,
            STOPS[tipo]["loss"] * 100,
            gain,
            STOPS[tipo]["gain"] * 100,
            round(rr, 2)
        ])

    except:
        continue

# ================= TABELA =================

df_resultado = pd.DataFrame(resultado, columns=[
    "Ativo", "Entrada",
    "Stop Loss", "Loss %",
    "Stop Gain", "Gain %",
    "R/R"
])

st.title("Scanner B3 – Entradas do Dia")
st.dataframe(df_resultado, use_container_width=True)

