import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="SISTEMA B3 VIP GOLD", layout="wide")

# =========================
# LOGIN SIMPLES (SEM ERRO)
# =========================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 ACESSO RESTRITO</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        senha = st.text_input("Digite a Senha:", type="password")
        if st.button("ENTRAR", use_container_width=True):
            if senha == "mestre10":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Senha incorreta")
    st.stop()

# =========================
# LISTA DE ATIVOS (EXEMPLO)
# =========================
ATIVOS = [
    "PETR4", "VALE3", "ITUB4", "BBAS3", "BOVA11", "AAPL34"
]

def analisar(ativo):
    try:
        df = yf.download(f"{ativo}.SA", period="120d", progress=False)
        if df.empty or len(df) < 70:
            return None

        close = df["Close"]
        ema69 = close.ewm(span=69).mean()

        if close.iloc[-1] > ema69.iloc[-1]:
            preco = round(close.iloc[-1], 2)
            loss = round(preco * 0.95, 2)
            gain = round(preco * 1.08, 2)

            return {
                "ATIVO": ativo,
                "PREÇO": preco,
                "STOP (-5%)": loss,
                "ALVO (+8%)": gain
            }
    except:
        pass
    return None

st.title("🛡️ Scanner B3 VIP GOLD")

if st.button("BUSCAR OPORTUNIDADES", use_container_width=True):
    resultados = []
    for ativo in ATIVOS:
        r = analisar(ativo)
        if r:
            resultados.append(r)

    if resultados:
        df = pd.DataFrame(resultados)
        st.subheader("Ativos que passaram no filtro")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum ativo passou no filtro hoje.")

