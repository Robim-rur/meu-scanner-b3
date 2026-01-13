import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(page_title="B3 VIP GOLD", layout="wide")

# ======================
# SISTEMA DE LOGIN
# ======================
SENHA = "mestre10"
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acesso Restrito")
    senha = st.text_input("Senha de acesso", type="password")
    if st.button("Entrar", use_container_width=True):
        if senha == SENHA:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# ======================
# INTERFACE PRINCIPAL
# ======================
st.title("📊 Scanner B3 VIP GOLD")
st.markdown("---")

# Lista de ativos (Aumentei a lista para garantir que encontre sinais com filtros rigorosos)
ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "BBDC4.SA", 
    "ABEV3.SA", "WEGE3.SA", "MGLU3.SA", "RENT3.SA", "PRIO3.SA",
    "B3SA3.SA", "GOAU4.SA", "GGBR4.SA", "CSNA3.SA", "BOVA11.SA",
    "IVVB11.SA", "AAPL34.SA", "ELET3.SA", "VBBR3.SA", "RAIZ4.SA"
]

if st.button("🔍 INICIAR VARREDURA (SEMANAL -> DIÁRIO)", use_container_width=True):
    resultados = []
    progresso = st.progress(0)
    status_placeholder = st.empty()
    
    for i, ticker in enumerate(ativos):
        try:
            status_placeholder.text(f"Analisando tendência de {ticker}...")
            
            # Download de dados
            df_d = yf.download(ticker, period="1y", interval="1d", progress=False)
            df_w = yf.download(ticker, period="2y", interval="1wk", progress=False)

            if df_d.empty or df_w.empty: continue
            if isinstance(df_d.columns, pd.MultiIndex): df_d.columns = df_d.columns.get_level_values(0)
            if isinstance(df_w.columns, pd.MultiIndex): df_w.columns = df_w.columns.get_level_values(0)

            # ==========================================
            # 1. FILTRO DE AUTORIZAÇÃO (SEMANAL)
            # ==========================================
            cl_w = df_w["Close"]
            hi_w, lo_w = df_w["High"], df_w["Low"]
            
            # Estocástico Semanal (14,3,3)
            stk_w_raw = 100 * ((cl_w - lo_w.rolling(14).min()) / (hi_w.rolling(14).max() - lo_w.rolling(14).min()))
            k_w = stk_w_raw.rolling(3).mean()
            
            # DMI Semanal
            up_w, dw_w = hi_w.diff(), -lo_w.diff()
            tr_w = pd.concat([hi_w-lo_w, abs(hi_w-cl_w.shift()), abs(lo_w-cl_w.shift())], axis=1).max(axis=1)
            atr_w = tr_w.rolling(14).sum()
            plus_w = 100 * (pd.Series(np.where((up_w>dw_w)&(up_w>0), up_w, 0)).rolling(14).sum().values / atr_w.values)
            minus_w = 100 * (pd.Series(np.where((dw_w>up_w)&(dw_w>0), dw_w, 0)).rolling(14).sum().values / atr_w.values)

            # Verificação do Filtro Semanal
            stoch_w_ok = float(k_w.iloc[-1]) >= float(k_w.iloc[-2]) # Inclinado para cima ou lateral
            dmi_w_ok = float(plus_w[-1]) > float(minus_w[-1])      # D+ > D-

            # SÓ CONTINUA SE O SEMANAL AUTORIZAR
            if stoch_w_ok and dmi_w_ok:
                
                status_placeholder.text(f"✅ {ticker} Autorizado no Semanal! Checando gatilho diário...")
                
                # ==========================================
                # 2. GATILHO DE ENTRADA (DIÁRIO)
                # ==========================================
                cl_d = df_d["Close"]
                hi_d, lo_d = df_d["High"], df_d["Low"]
                
                # Estocástico Diário (14,3,3)
                stk_d_raw = 100 * ((cl_d - lo_d.rolling(14).min()) / (hi_d.rolling(14).max() - lo_d.rolling(14).min()))
                k_d = stk_d_raw.rolling(3).mean() # %K
                d_d = k_d.rolling(3).mean()       # %D

                # DMI Diário
                up_d, dw_d = hi_d.diff(), -lo_d.diff()
                tr_d = pd.concat([hi_d-lo_d, abs(hi_d-cl_d.shift()), abs(lo_d-cl_d.shift())], axis=1).max(axis=1)
                atr_d = tr_d.rolling(14).sum()
                plus_d = 100 * (pd.Series(np.where((up_d>dw_d)&(up_d>0), up_d, 0)).rolling(14).sum().values / atr_d.values)
                minus_d = 100 * (pd.Series(np.where((dw_d>up_d)&(dw_d>0), dw_d, 0)).rolling(14).sum().values / atr_d.values)

                # Verificação do Gatilho Diário
                k_acima_d = float(k_d.iloc[-1]) > float(d_d.iloc[-1]) # %K acima de %D
                dmi_d_ok = float(plus_d[-1]) > float(minus_d[-1])    # D+ acima de D-

                if k_acima_d and dmi_d_ok:
                    resultados.append({
                        "Ativo": ticker.replace(".SA", ""),
                        "Preço": f"R$ {float(cl_d.iloc[-1]):.2f}",
                        "Filtro Semanal": "AUTORIZADO",
                        "Gatilho Diário": "CONFIRMADO"
                    })

        except: continue
        progresso.progress((i + 1) / len(ativos))

    status_placeholder.empty()
    progresso.empty()

    if resultados:
        st.success(f"Sinal de Compra VIP GOLD detectado em {len(resultados)} ativos!")
        st.dataframe(pd.DataFrame(resultados), use_container_width=True)
    else:
        st.warning("Varredura concluída: Nenhum ativo passou pela sincronia Semanal -> Diário hoje.")

st.divider()
st.caption("A varredura respeita a hierarquia de tempos gráficos: Primeiro a tendência no semanal, depois o gatilho no diário.")
