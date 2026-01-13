import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da Página
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
# INTERFACE
# ======================
st.title("📊 Scanner B3 VIP GOLD - Sincronia Semanal")
st.markdown("---")

ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "BBDC4.SA", 
    "ABEV3.SA", "WEGE3.SA", "MGLU3.SA", "RENT3.SA", "PRIO3.SA",
    "B3SA3.SA", "GOAU4.SA", "GGBR4.SA", "CSNA3.SA", "BOVA11.SA"
]

if st.button("🚀 INICIAR VARREDURA"):
    resultados = []
    progresso = st.progress(0)
    status_placeholder = st.empty()
    
    for i, ticker in enumerate(ativos):
        try:
            status_placeholder.text(f"Analisando {ticker}...")
            
            # Download de dados
            df_d = yf.download(ticker, period="1y", interval="1d", progress=False)
            df_w = yf.download(ticker, period="2y", interval="1wk", progress=False)

            if df_d.empty or df_w.empty: continue
            if isinstance(df_d.columns, pd.MultiIndex): df_d.columns = df_d.columns.get_level_values(0)
            if isinstance(df_w.columns, pd.MultiIndex): df_w.columns = df_w.columns.get_level_values(0)

            # --- 1. FILTRO SEMANAL (REGRAS DESCOBERTAS) ---
            cl_w = df_w["Close"]
            hi_w, lo_w = df_w["High"], df_w["Low"]
            m69_w = cl_w.ewm(span=69, adjust=False).mean()

            # Estocástico Semanal (14,3,3)
            stk_w_raw = 100 * ((cl_w - lo_w.rolling(14).min()) / (hi_w.rolling(14).max() - lo_w.rolling(14).min()))
            k_w = stk_w_raw.rolling(3).mean() # %K
            d_w = k_w.rolling(3).mean()       # %D

            # DMI Semanal
            up_w, dw_w = hi_w.diff(), -lo_w.diff()
            tr_w = pd.concat([hi_w-lo_w, abs(hi_w-cl_w.shift()), abs(lo_w-cl_w.shift())], axis=1).max(axis=1)
            atr_w = tr_w.rolling(14).sum()
            plus_w = 100 * (pd.Series(np.where((up_w>dw_w)&(up_w>0), up_w, 0)).rolling(14).sum().values / atr_w.values)
            minus_w = 100 * (pd.Series(np.where((dw_w>up_w)&(dw_w>0), dw_w, 0)).rolling(14).sum().values / atr_w.values)

            # VALIDAÇÃO SEMANAL
            ok_semanal = (
                float(cl_w.iloc[-1]) > float(m69_w.iloc[-1]) and     # Tendência Alta
                float(k_w.iloc[-1]) >= float(k_w.iloc[-2]) and       # Não inclinado para baixo
                float(k_w.iloc[-1]) > float(d_w.iloc[-1]) and        # %K > %D
                float(plus_w[-1]) > float(minus_w[-1])               # D+ > D-
            )

            if ok_semanal:
                # --- 2. GATILHO DIÁRIO ---
                cl_d = df_d["Close"]
                hi_d, lo_d = df_d["High"], df_d["Low"]
                m69_d = cl_d.ewm(span=69, adjust=False).mean()
                
                # Estocástico Diário (14,3,3)
                stk_d_raw = 100 * ((cl_d - lo_d.rolling(14).min()) / (hi_d.rolling(14).max() - lo_d.rolling(14).min()))
                k_d = stk_d_raw.rolling(3).mean()
                d_d = k_d.rolling(3).mean()

                # DMI Diário
                up_d, dw_d = hi_d.diff(), -lo_d.diff()
                tr_d = pd.concat([hi_d-lo_d, abs(hi_d-cl_d.shift()), abs(lo_d-cl_d.shift())], axis=1).max(axis=1)
                atr_d = tr_d.rolling(14).sum()
                plus_d = 100 * (pd.Series(np.where((up_d>dw_d)&(up_d>0), up_d, 0)).rolling(14).sum().values / atr_d.values)
                minus_d = 100 * (pd.Series(np.where((dw_d>up_d)&(dw_d>0), dw_d, 0)).rolling(14).sum().values / atr_d.values)

                # VALIDAÇÃO DIÁRIA
                ok_diario = (
                    float(cl_d.iloc[-1]) > float(m69_d.iloc[-1]) and
                    float(plus_d[-1]) > float(minus_d[-1]) and
                    float(k_d.iloc[-1]) > float(d_d.iloc[-1]) and
                    float(cl_d.iloc[-1]) > float(hi_d.iloc[-2]) # Rompimento da máxima anterior
                )

                if ok_diario:
                    resultados.append({
                        "Ativo": ticker.replace(".SA", ""),
                        "Preço": f"R$ {float(cl_d.iloc[-1]):.2f}",
                        "Sinal": "COMPRA LIBERADA 🚀"
                    })

        except: continue
        progresso.progress((i + 1) / len(ativos))

    status_placeholder.empty()
    progresso.empty()

    if resultados:
        st.success(f"Encontrados {len(resultados)} ativos com autorização completa!")
        st.table(pd.DataFrame(resultados))
    else:
        st.warning("Nenhum ativo passou nos filtros de autorização semanal e diária hoje.")

st.info("Filtro Semanal: Tendência Alta + Estocástico (%K >= Ant. e %K > %D) + DMI+ > DMI-.")
