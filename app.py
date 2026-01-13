import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="B3 VIP GOLD", layout="wide")

# ======================
# LOGIN
# ======================
SENHA = "mestre10"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acesso Restrito")
    senha = st.text_input("Senha de acesso", type="password")
    if st.button("Entrar"):
        if senha == SENHA:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# ======================
# CONFIGURAÇÃO
# ======================
st.title("📊 Scanner B3 VIP GOLD")

st.info(
    "Os ativos listados abaixo **passaram pelo filtro do Setup VIP GOLD**.\n\n"
    "O setup utiliza **múltiplos indicadores técnicos combinados**, "
    "com análise de **tendência no semanal** e **entrada no diário**.\n\n"
    "⚠️ O método não mostra todos os ativos — apenas os **tecnicamente autorizados**."
)

# Lista inicial
ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA",
    "ABEV3.SA", "BBDC4.SA", "WEGE3.SA", "BOVA11.SA"
]

resultados = []

# ======================
# LOOP PRINCIPAL
# ======================
for ativo in ativos:
    # Coleta de dados
    df_d = yf.download(ativo, period="1y", interval="1d", progress=False)
    df_w = yf.download(ativo, period="2y", interval="1wk", progress=False)

    if df_d.empty or df_w.empty:
        continue

    # Limpeza de MultiIndex (Correção para versões novas do yfinance)
    if isinstance(df_d.columns, pd.MultiIndex):
        df_d.columns = df_d.columns.get_level_values(0)
    if isinstance(df_w.columns, pd.MultiIndex):
        df_w.columns = df_w.columns.get_level_values(0)

    close_d = df_d["Close"]
    close_w = df_w["Close"]

    # Média 69
    ema69_d = close_d.ewm(span=69).mean()
    ema69_w = close_w.ewm(span=69).mean()

    # Estocástico Diário
    low14 = df_d["Low"].rolling(14).min()
    high14 = df_d["High"].rolling(14).max()
    stoch_d = 100 * (close_d - low14) / (high14 - low14)

    # DMI Diário
    up = df_d["High"].diff()
    down = -df_d["Low"].diff()

    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)

    tr = pd.concat([
        df_d["High"] - df_d["Low"],
        abs(df_d["High"] - close_d.shift()),
        abs(df_d["Low"] - close_d.shift())
    ], axis=1).max(axis=1)

    atr = tr.rolling(14).sum()
    
    # CORREÇÃO DO ERRO DE DIMENSÃO (.flatten() e index)
    di_plus = 100 * pd.Series(plus_dm.flatten(), index=df_d.index).rolling(14).sum() / atr
    di_minus = 100 * pd.Series(minus_dm.flatten(), index=df_d.index).rolling(14).sum() / atr

    # ======================
    # REGRAS ORIGINAIS
    # ======================

    # SEMANAL AUTORIZA
    semanal_ok = float(close_w.iloc[-1]) > float(ema69_w.iloc[-1])

    # DIÁRIO ENTRA
    diario_ok = (
        float(close_d.iloc[-1]) > float(ema69_d.iloc[-1]) and
        float(di_plus.iloc[-1]) > float(di_minus.iloc[-1]) and
        float(stoch_d.iloc[-1]) < 80 and
        float(close_d.iloc[-1]) > float(df_d["High"].iloc[-2])
    )

    if semanal_ok and diario_ok:
        resultados.append({
            "Ativo": ativo.replace(".SA", ""),
            "Fechamento": round(float(close_d.iloc[-1]), 2)
        })

# ======================
# RESULTADO
# ======================
if resultados:
    df_resultado = pd.DataFrame(resultados)
    st.success(f"{len(df_resultado)} ativos aprovados pelo Setup VIP GOLD")
    st.dataframe(df_resultado, use_container_width=True)
else:
    st.warning("Nenhum ativo passou pelo filtro hoje. Mercado sem autorização técnica.")
