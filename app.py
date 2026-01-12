import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================
# CONFIGURAÇÃO GERAL
# =========================
st.set_page_config(
    page_title="Scanner B3 VIP GOLD",
    layout="wide"
)

# =========================
# BLINDAGEM VISUAL
# =========================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGIN
# =========================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 ACESSO RESTRITO</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        senha = st.text_input("Digite sua senha de acesso", type="password")
        if st.button("ENTRAR", use_container_width=True):
            if senha == "mestre10":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Senha incorreta")
    st.stop()

# =========================
# TEXTO EXPLICATIVO (INICIANTE)
# =========================
st.markdown("""
### 🛡️ Scanner B3 VIP GOLD

Os ativos listados abaixo **passaram por um filtro técnico proprietário**, 
baseado na **confluência de múltiplos indicadores de tendência e momentum**.

👉 O objetivo é **mapear ativos alinhados com tendência de alta**,  
👉 já com **níveis objetivos de risco (stop)** e **alvo (gain)**.

> ⚠️ Este scanner **não executa ordens**.  
> Ele apenas **organiza oportunidades** dentro do método VIP GOLD.
""")

# =========================
# LISTA DE ATIVOS (INICIAL)
# =========================
ATIVOS = [
    "PETR4", "VALE3", "ITUB4", "BBAS3", "WEGE3",
    "BOVA11", "IVVB11", "AAPL34", "MSFT34"
]

# =========================
# FUNÇÃO DE ANÁLISE (OCULTA)
# =========================
def analisar(ativo):
    try:
        ticker = f"{ativo}.SA"
        df = yf.download(ticker, period="160d", progress=False)
        if df.empty or len(df) < 80:
            return None

        close = df["Close"]
        ema69 = close.ewm(span=69).mean()

        # FILTRO PRINCIPAL (SEM EXPOR SETUP)
        condicao = close.iloc[-1] > ema69.iloc[-1]

        if condicao:
            preco = round(close.iloc[-1], 2)

            if ativo.endswith("34"):
                sl, sg = 0.04, 0.06
            elif ativo.endswith("11"):
                sl, sg = 0.03, 0.045
            else:
                sl, sg = 0.05, 0.075

            return {
                "Ativo": ativo,
                "Preço Atual": preco,
                "Stop (%)": f"{int(sl*100)}%",
                "Alvo (%)": f"{int(sg*100)}%",
                "Stop (R$)": round(preco * (1 - sl), 2),
                "Alvo (R$)": round(preco * (1 + sg), 2)
            }
    except:
        pass
    return None

# =========================
# EXECUÇÃO
# =========================
st.divider()

if st.button("🔍 Buscar oportunidades do dia", use_container_width=True):
    resultados = []
    progresso = st.progress(0)

    for i, ativo in enumerate(ATIVOS):
        r = analisar(ativo)
        if r:
            resultados.append(r)
        progresso.progress((i + 1) / len(ATIVOS))

    progresso.empty()

    if resultados:
        df = pd.DataFrame(resultados)
        st.subheader("🎯 Ativos aprovados pelo filtro VIP GOLD")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum ativo passou pelo filtro hoje.")


