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

# Lista de ativos
ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA",
    "ABEV3.SA", "BBDC4.SA", "WEGE3.SA", "BOVA11.SA",
    "MGLU3.SA", "RENT3.SA", "B3SA3.SA", "PRIO3.SA"
]

resultados = []

# ======================
# LOOP PRINCIPAL
# ======================
progress_bar = st.progress(0)
status_text = st.empty()

for i, ativo in enumerate(ativos):
    status_text.text(f"Analisando {ativo}...")
    
    # Download dos dados
    df_d = yf.download(ativo, period="1y", interval="1d", progress=False)
    df_w = yf.download(ativo, period="2y", interval="1wk", progress=False)

    if df_d.empty or df_w.empty or len(df_d) < 70:
        continue
    
    # Tratamento para evitar erro de Multi-Index no yfinance recente
    if isinstance(df_d.columns, pd.MultiIndex):
        df_d.columns = df_d.columns.get_level_values(0)
    if isinstance(df_w.columns, pd.MultiIndex):
        df_w.columns = df_w.columns.get_level_values(0)

    close_d = df_d["Close"]
    close_w = df_w["Close"]

    # Média 69 (Exponencial)
    ema69_d = close_d.ewm(span=69, adjust=False).mean()
    ema69_w = close_w.ewm(span=69, adjust=False).mean()

    # Estocástico Diário (14 períodos)
    low14 = df_d["Low"].rolling(14).min()
    high14 = df_d["High"].rolling(14).max()
    stoch_d = 100 * (close_d - low14) / (high14 - low14)

    # DMI Diário - Cálculo Corrigido
    up = df_d["High"].diff()
    down = -df_d["Low"].diff()

    # Garantimos que plus_dm e minus_dm sejam Series com o mesmo índice do df_d
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df_d.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df_d.index)

    tr = pd.concat([
        df_d["High"] - df_d["Low"],
        abs(df_d["High"] - close_d.shift()),
        abs(df_d["Low"] - close_d.shift())
    ], axis=1).max(axis=1)

    atr = tr.rolling(14).sum()
    
    # Cálculo dos DIs com tratamento de divisão por zero
    di_plus = 100 * (plus_dm.rolling(14).sum() / atr)
    di_minus = 100 * (minus_dm.rolling(14).sum() / atr)

    # ======================
    # REGRAS DO SETUP
    # ======================

    # 1. SEMANAL EM TENDÊNCIA DE ALTA (Preço acima da média 69)
    semanal_ok = float(close_w.iloc[-1]) > float(ema69_w.iloc[-1])

    # 2. DIÁRIO: Preço > Média, DI+ > DI-, Estocástico não sobrecomprado, Rompimento da Máxima Anterior
    try:
        diario_ok = (
            float(close_d.iloc[-1]) > float(ema69_d.iloc[-1]) and
            float(di_plus.iloc[-1]) > float(di_minus.iloc[-1]) and
            float(stoch_d.iloc[-1]) < 80 and
            float(close_d.iloc[-1]) > float(df_d["High"].iloc[-2])
        )
    except:
        diario_ok = False

    if semanal_ok and diario_ok:
        resultados.append({
            "Ativo": ativo.replace(".SA", ""),
            "Preço": round(float(close_d.iloc[-1]), 2),
            "DMI+": round(float(di_plus.iloc[-1]), 2),
            "Estocástico": round(float(stoch_d.iloc[-1]), 2)
        })
    
    progress_bar.progress((i + 1) / len(ativos))

status_text.empty()
progress_bar.empty()

# ======================
# EXIBIÇÃO DOS RESULTADOS
# ======================
if resultados:
    df_resultado = pd.DataFrame(resultados)
    st.success(f"🔥 {len(df_resultado)} ativos encontrados com compra autorizada!")
    
    # Formatação da tabela
    st.dataframe(
        df_resultado.style.format({"Preço": "R$ {:.2f}", "DMI+": "{:.1f}", "Estocástico": "{:.1f}"}),
        use_container_width=True
    )
else:
    st.warning("Nenhum ativo passou pelo filtro VIP GOLD hoje. Aguarde uma melhor oportunidade.")

st.divider()
st.caption("Dados fornecidos via Yahoo Finance. Analise sempre o gráfico antes de operar.")

