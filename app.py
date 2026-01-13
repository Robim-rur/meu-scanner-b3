import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. Configuração de página
st.set_page_config(page_title="B3 VIP GOLD - 100 Ativos", layout="wide")

# 2. LOGIN
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acesso Restrito")
    senha = st.text_input("Senha de acesso", type="password")
    if st.button("Entrar"):
        if senha == "mestre10":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# 3. INTERFACE
st.title("📊 Scanner B3 VIP GOLD - Top 100")

# Lista expandida para ~100 ativos
ativos = [
    "RRRP3.SA", "ALOS3.SA", "ALPA4.SA", "ABEV3.SA", "ARZZ3.SA", "ASAI3.SA", "AZUL4.SA", "B3SA3.SA", 
    "BBAS3.SA", "BBDC3.SA", "BBDC4.SA", "BBSE3.SA", "BEEF3.SA", "BPAC11.SA", "BRAP4.SA", "BRFS3.SA", 
    "BRKM5.SA", "CCRO3.SA", "CIEL3.SA", "CMIG4.SA", "CMIN3.SA", "COGN3.SA", "CPFE3.SA", "CPLE6.SA", 
    "CRFB3.SA", "CSAN3.SA", "CSNA3.SA", "CVCB3.SA", "CYRE3.SA", "DXCO3.SA", "ELET3.SA", "ELET6.SA", 
    "EMBR3.SA", "ENGI11.SA", "ENEV3.SA", "EGIE3.SA", "EQTL3.SA", "EZTC3.SA", "FLRY3.SA", "GGBR4.SA", 
    "GOAU4.SA", "GOLL4.SA", "HAPV3.SA", "HYPE3.SA", "ITSA4.SA", "ITUB4.SA", "JBSS3.SA", "KLBN11.SA", 
    "KROT3.SA", "LREN3.SA", "LWSA3.SA", "MGLU3.SA", "MRFG3.SA", "MRVE3.SA", "MULT3.SA", "NTCO3.SA", 
    "PETR3.SA", "PETR4.SA", "PRIO3.SA", "PETZ3.SA", "RADL3.SA", "RAIZ4.SA", "RDOR3.SA", "RENT3.SA", 
    "RAIL3.SA", "SBSP3.SA", "SANB11.SA", "SMTO3.SA", "SULA11.SA", "SUZB3.SA", "TAEE11.SA", "TALT3.SA", 
    "TIMS3.SA", "TOTS3.SA", "UGPA3.SA", "USIM5.SA", "VALE3.SA", "VAMO3.SA", "VBBR3.SA", "VIVT3.SA", 
    "WEGE3.SA", "YDUQ3.SA", "BOVA11.SA", "IVVB11.SA", "SMALL11.SA", "SMAL11.SA"
]

if st.button("🚀 INICIAR VARREDURA COMPLETA (100 ATIVOS)"):
    resultados = []
    progresso = st.progress(0)
    total = len(ativos)
    
    for i, ativo in enumerate(ativos):
        try:
            df_d = yf.download(ativo, period="1y", interval="1d", progress=False)
            df_w = yf.download(ativo, period="2y", interval="1wk", progress=False)

            if df_d.empty or df_w.empty:
                continue

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
            
            di_plus = 100 * pd.Series(plus_dm.flatten(), index=df_d.index).rolling(14).sum() / atr
            di_minus = 100 * pd.Series(minus_dm.flatten(), index=df_d.index).rolling(14).sum() / atr

            # REGRAS
            # 1. Semanal: Acima EMA 69
            semanal_ok = float(close_w.iloc[-1]) > float(ema69_w.iloc[-1])

            # 2. Diário: Acima EMA 69 + DMI + Estocástico < 80
            diario_ok = (
                float(close_d.iloc[-1]) > float(ema69_d.iloc[-1]) and
                float(di_plus.iloc[-1]) > float(di_minus.iloc[-1]) and
                float(stoch_d.iloc[-1]) < 80
            )

            if semanal_ok and diario_ok:
                resultados.append({
                    "Ativo": ativo.replace(".SA", ""),
                    "Preço": round(float(close_d.iloc[-1]), 2),
                    "Estocástico": round(float(stoch_d.iloc[-1]), 2)
                })
        except:
            continue
        
        progresso.progress((i + 1) / total)

    if resultados:
        df_resultado = pd.DataFrame(resultados)
        st.success(f"Filtro finalizado! {len(df_resultado)} ativos encontrados.")
        st.dataframe(df_resultado, use_container_width=True)
    else:
        st.warning("Nenhum ativo dos 100 analisados passou nos critérios hoje.")

st.divider()
