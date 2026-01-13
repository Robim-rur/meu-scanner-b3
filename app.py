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
st.title("📊 Scanner B3 VIP GOLD - Rígido")
st.markdown("---")

ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "BBDC4.SA", 
    "ABEV3.SA", "WEGE3.SA", "MGLU3.SA", "RENT3.SA", "PRIO3.SA",
    "B3SA3.SA", "GOAU4.SA", "GGBR4.SA", "CSNA3.SA", "BOVA11.SA",
    "IVVB11.SA", "AAPL34.SA", "ELET3.SA", "VBBR3.SA", "RAIZ4.SA"
]

if st.button("🔍 INICIAR VARREDURA RÍGIDA", use_container_width=True):
    resultados = []
    progresso = st.progress(0)
    status_placeholder = st.empty()
    
    for i, ticker in enumerate(ativos):
        try:
            status_placeholder.text(f"Analisando {ticker}...")
            
            df_d = yf.download(ticker, period="1y", interval="1d", progress=False)
            df_w = yf.download(ticker, period="2y", interval="1wk", progress=False)

            if df_d.empty or df_w.empty: continue
            if isinstance(df_d.columns, pd.MultiIndex): df_d.columns = df_d.columns.get_level_values(0)
            if isinstance(df_w.columns, pd.MultiIndex): df_w.columns = df_w.columns.get_level_values(0)

            # ==========================================
            # 1. FILTRO DE AUTORIZAÇÃO (SEMANAL) - RÍGIDO
            # ==========================================
            cl_w = df_w["Close"]
            m69_w = cl_w.ewm(span=69, adjust=False).mean() # A Média 69 é o filtro mestre
            
            # Estocástico Semanal (14,3,3)
            low_w14 = df_w["Low"].rolling(14).min()
            high_w14 = df_w["High"].rolling(14).max()
            stk_w = 100 * ((cl_w - low_w14) / (high_w14 - low_w14)).rolling(3).mean()

            # CONDIÇÕES SEMANAIS
            cond_w1 = float(cl_w.iloc[-1]) > float(m69_w.iloc[-1]) # Preço ACIMA da média
            cond_w2 = float(stk_w.iloc[-1]) >= float(stk_w.iloc[-2]) # Estocástico SUBINDO ou LATERAL
            
            # DMI Semanal
            up_w, dw_w = df_w["High"].diff(), -df_w["Low"].diff()
            tr_w = pd.concat([df_w["High"]-df_w["Low"], abs(df_w["High"]-cl_w.shift()), abs(df_w["Low"]-cl_w.shift())], axis=1).max(axis=1)
            atr_w = tr_w.rolling(14).sum()
            plus_w = 100 * (pd.Series(np.where((up_w>dw_w)&(up_w>0), up_w, 0)).rolling(14).sum().values / atr_w.values)
            minus_w = 100 * (pd.Series(np.where((dw_w>up_w)&(dw_w>0), dw_w, 0)).rolling(14).sum().values / atr_w.values)
            cond_w3 = float(plus_w[-1]) > float(minus_w[-1]) # DMI+ > DMI-

            if cond_w1 and cond_w2 and cond_w3:
                
                # ==========================================
                # 2. GATILHO DE ENTRADA (DIÁRIO) - RÍGIDO
                # ==========================================
                cl_d = df_d["Close"]
                m69_d = cl_d.ewm(span=69, adjust=False).mean()
                
                # Estocástico Diário (14,3,3)
                low_d14 = df_d["Low"].rolling(14).min()
                high_d14 = df_d["High"].rolling(14).max()
                k_d = 100 * ((cl_d - low_d14) / (high_d14 - low_d14)).rolling(3).mean()
                d_d = k_d.rolling(3).mean()

                # DMI Diário
                up_d, dw_d = df_d["High"].diff(), -df_d["Low"].diff()
                tr_d = pd.concat([df_d["High"]-df_d["Low"], abs(df_d["High"]-cl_d.shift()), abs(df_d["Low"]-cl_d.shift())], axis=1).max(axis=1)
                atr_d = tr_d.rolling(14).sum()
                plus_d = 100 * (pd.Series(np.where((up_d>dw_d)&(up_d>0), up_d, 0)).rolling(14).sum().values / atr_d.values)
                minus_d = 100 * (pd.Series(np.where((dw_d>up_d)&(dw_d>0), dw_d, 0)).rolling(14).sum().values / atr_d.values)

                # CONDIÇÕES DIÁRIAS
                cond_d1 = float(cl_d.iloc[-1]) > float(m69_d.iloc[-1]) # Preço > M69 no Diário
                cond_d2 = float(plus_d[-1]) > float(minus_d[-1])      # D+ > D- no Diário
                cond_d3 = float(k_d.iloc[-1]) > float(d_d.iloc[-1])   # %K > %D (Cruzamento)
                cond_d4 = float(cl_d.iloc[-1]) > float(df_d["High"].iloc[-2]) # Rompimento da Máxima anterior

                if cond_d1 and cond_d2 and cond_d3 and cond_d4:
                    resultados.append({
                        "Ativo": ticker.replace(".SA", ""),
                        "Preço": f"R$ {float(cl_d.iloc[-1]):.2f}",
                        "Filtro Semanal": "✅ OK",
                        "Média 69": "✅ ACIMA"
                    })

        except: continue
        progresso.progress((i + 1) / len(ativos))

    status_placeholder.empty()
    progresso.empty()

    if resultados:
        st.success(f"Foram encontrados {len(resultados)} ativos que passaram no filtro ultra-rígido!")
        st.table(pd.DataFrame(resultados))
    else:
        st.warning("Nenhum ativo passou nos filtros rigorosos hoje.")

st.info("Este scanner usa: Preço > M69 (S/D), Estocástico Subindo (S), %K > %D (D), D+ > D- (S/D) e Rompimento de Máxima (D).")
