import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# CONFIGURAÇÃO GERAL
# =========================
st.set_page_config(page_title="Scanner B3 VIP GOLD", layout="wide")

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
# TEXTO DIDÁTICO
# =========================
st.markdown("""
### 🛡️ Scanner B3 VIP GOLD

Os ativos abaixo passaram por um **filtro técnico proprietário**,  
alinhado ao método VIP GOLD, respeitando:

- Tendência de alta
- Confirmação no semanal
- Força direcional
- Momento adequado

Cada ativo já vem com **stop e alvo objetivos**.
""")

# =========================
# LISTA INICIAL (CONTROLADA)
# =========================
ATIVOS = [
    "ABEV3","BBAS3","BBDC4","ITUB4","PETR4","VALE3","WEGE3","SUZB3",
    "BOVA11","IVVB11",
    "AAPL34","MSFT34","GOGL34"
]

# =========================
# FUNÇÕES
# =========================
def calcular_dmi(df, n=14):
    high, low, close = df["High"], df["Low"], df["Close"]
    up = high.diff()
    down = -low.diff()
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(n).sum()
    plus_dm = np.where((up > down) & (up > 0), up, 0)
    minus_dm = np.where((down > up) & (down > 0), down, 0)

    plus_di = 100 * pd.Series(plus_dm).rolling(n).sum() / atr
    minus_di = 100 * pd.Series(minus_dm).rolling(n).sum() / atr

    return plus_di, minus_di

def criar_semanal(df_diario):
    semanal = df_diario.resample("W").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }).dropna()
    return semanal

# =========================
# ANÁLISE PRINCIPAL
# =========================
def analisar_ativo(ativo):
    try:
        ticker = f"{ativo}.SA"
        df = yf.download(ticker, period="300d", progress=False)
        if df.empty or len(df) < 120:
            return None

        df_w = criar_semanal(df)

        close_d = df["Close"]
        close_w = df_w["Close"]

        ema69_d = close_d.ewm(span=69).mean()
        ema69_w = close_w.ewm(span=69).mean()

        # CONFIRMAÇÃO SEMANAL
        if close_w.iloc[-1] <= ema69_w.iloc[-1]:
            return None

        # TENDÊNCIA DIÁRIA
        if close_d.iloc[-1] <= ema69_d.iloc[-1]:
            return None

        # DMI
        di_plus, di_minus = calcular_dmi(df)
        if di_plus.iloc[-1] <= di_minus.iloc[-1]:
            return None

        # ESTOCÁSTICO (NÃO EXTREMO)
        low14 = df["Low"].rolling(14).min()
        high14 = df["High"].rolling(14).max()
        stoch_k = 100 * (close_d - low14) / (high14 - low14)
        stoch_k = stoch_k.rolling(3).mean()

        if stoch_k.iloc[-1] > 90:
            return None

        preco = round(close_d.iloc[-1], 2)

        if ativo.endswith("34"):
            sl, sg, tipo = 0.04, 0.06, "BDR"
        elif ativo.endswith("11"):
            sl, sg, tipo = 0.03, 0.045, "ETF"
        else:
            sl, sg, tipo = 0.05, 0.075, "AÇÃO"

        return {
            "Ativo": ativo,
            "Tipo": tipo,
            "Preço": preco,
            "Stop (%)": f"{int(sl*100)}%",
            "Alvo (%)": f"{round(sg*100,1)}%",
            "Stop (R$)": round(preco * (1 - sl), 2),
            "Alvo (R$)": round(preco * (1 + sg), 2)
        }

    except:
        return None

# =========================
# EXECUÇÃO
# =========================
st.divider()

if st.button("🔍 Buscar oportunidades do dia", use_container_width=True):
    resultados = []
    progresso = st.progress(0)

    for i, ativo in enumerate(ATIVOS):
        r = analisar_ativo(ativo)
        if r:
            resultados.append(r)
        progresso.progress((i + 1) / len(ATIVOS))

    progresso.empty()

    if resultados:
        df = pd.DataFrame(resultados)
        st.subheader("🎯 Ativos aprovados pelo método VIP GOLD")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum ativo atendeu a todos os critérios hoje.")
