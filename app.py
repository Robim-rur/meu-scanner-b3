import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="SISTEMA B3 VIP GOLD",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Oculta menus e rodapé (proteção visual)
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =========================
# SISTEMA DE LOGIN (SEGURO)
# =========================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>🔐 ACESSO RESTRITO</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try:
            SENHA_MESTRA = os.environ["MASTER_PASSWORD"]
        except KeyError:
            st.error("Senha do sistema não configurada.")
            st.stop()

        senha = st.text_input("Digite a senha de acesso:", type="password")
        if st.button("ENTRAR NO SISTEMA", use_container_width=True):
            if senha == SENHA_MESTRA:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Senha incorreta.")

    st.stop()

# =========================
# TÍTULO
# =========================
st.title("🛡️ SCANNER B3 – VIP GOLD")

# =========================
# BOX EXPLICATIVO (INICIANTE)
# =========================
st.info("""
🟨 **Filtro Proprietário – Setup VIP GOLD**

Os ativos exibidos abaixo passaram por um filtro técnico proprietário,
baseado na convergência de múltiplos indicadores de tendência e momentum,
com foco exclusivo em operações compradas (swing trade).

Este scanner tem como objetivo reduzir ruído operacional e apresentar
somente ativos tecnicamente alinhados à tendência principal.
""")

# =========================
# LISTA DE ATIVOS (CURADA)
# =========================
LISTA_TOTAL_B3 = [
    "ABEV3","ALPA4","ARZZ3","ASAI3","AZUL4","B3SA3","BBAS3","BBDC4","BBSE3",
    "BEEF3","BPAC11","BRFS3","CCRO3","CMIG4","CPFE3","CSAN3","CSNA3","CYRE3",
    "ELET3","ELET6","EMBR3","ENGI11","ENEV3","EGIE3","EQTL3","FLRY3","GGBR4",
    "GOAU4","HYPE3","ITSA4","ITUB4","JBSS3","KLBN11","LREN3","MGLU3","MULT3",
    "NTCO3","PETR4","PRIO3","RADL3","RAIL3","RENT3","SBSP3","SUZB3","TAEE11",
    "TOTS3","UGPA3","USIM5","VALE3","VIVT3","WEGE3","YDUQ3",
    "BOVA11","IVVB11","SMAL11","DIVO11",
    "AAPL34","AMZO34","GOGL34","MSFT34","META34","NVDC34","TSLA34"
]

# =========================
# FUNÇÃO DE ANÁLISE (BLINDADA)
# =========================
def analisar_ativo(ticker):
    try:
        simbolo = f"{ticker}.SA"
        df = yf.download(simbolo, period="150d", progress=False)
        if df.empty or len(df) < 70:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df["Close"]
        high = df["High"]
        low = df["Low"]

        ema69 = close.ewm(span=69, adjust=False).mean()

        l14 = low.rolling(14).min()
        h14 = high.rolling(14).max()
        estoc = 100 * ((close - l14) / (h14 - l14))
        estoc = estoc.rolling(3).mean()

        up = high.diff()
        down = -low.diff()
        tr = pd.concat(
            [high - low, abs(high - close.shift()), abs(low - close.shift())],
            axis=1
        ).max(axis=1)

        atr = tr.rolling(14).sum()
        plus_dm = np.where((up > down) & (up > 0), up, 0)
        minus_dm = np.where((down > up) & (down > 0), down, 0)

        di_plus = 100 * (pd.Series(plus_dm).rolling(14).sum() / atr)
        di_minus = 100 * (pd.Series(minus_dm).rolling(14).sum() / atr)

        cond1 = close.iloc[-1] > ema69.iloc[-1]
        cond2 = di_plus.iloc[-1] > di_minus.iloc[-1]
        cond3 = estoc.iloc[-1] < 80
        cond4 = close.iloc[-1] > high.iloc[-2]

        if cond1 and cond2 and cond3 and cond4:
            if ticker.endswith("34"):
                sl, sg = 0.04, 0.06
            elif ticker.endswith("11"):
                sl, sg = 0.03, 0.045
            else:
                sl, sg = 0.05, 0.075

            preco = round(close.iloc[-1], 2)

            return {
                "ATIVO": ticker,
                "PREÇO": preco,
                "STOP": round(preco * (1 - sl), 2),
                "STOP (%)": f"{sl*100:.1f}%",
                "GAIN": round(preco * (1 + sg), 2),
                "GAIN (%)": f"{sg*100:.1f}%"
            }

    except:
        return None

    return None

# =========================
# BOTÃO DE BUSCA
# =========================
if "resultados" not in st.session_state:
    st.session_state.resultados = []

if st.button("🔍 BUSCAR ATIVOS APROVADOS", use_container_width=True):
    aprovados = []
    barra = st.progress(0)

    for i, ativo in enumerate(LISTA_TOTAL_B3):
        res = analisar_ativo(ativo)
        if res:
            aprovados.append(res)
        barra.progress((i + 1) / len(LISTA_TOTAL_B3))

    st.session_state.resultados = aprovados
    barra.empty()

# =========================
# RESULTADOS
# =========================
if st.session_state.resultados:
    st.subheader("🎯 Ativos Aprovados pelo Filtro")

    df = pd.DataFrame(st.session_state.resultados)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    ativo_sel = st.selectbox(
        "Visualizar gráfico do ativo:",
        df["ATIVO"].tolist()
    )

    dados = df[df["ATIVO"] == ativo_sel].iloc[0]

    df_plot = yf.download(f"{ativo_sel}.SA", period="60d", progress=False)
    if isinstance(df_plot.columns, pd.MultiIndex):
        df_plot.columns = df_plot.columns.get_level_values(0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot.index,
        y=df_plot["Close"],
        name="Preço",
        line=dict(color="#00ff99")
    ))

    fig.add_hline(
        y=dados["GAIN"],
        line_dash="dash",
        line_color="cyan",
        annotation_text="GAIN"
    )

    fig.add_hline(
        y=dados["STOP"],
        line_dash="dash",
        line_color="red",
        annotation_text="STOP"
    )

    fig.update_layout(
        template="plotly_dark",
        height=450,
        showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

