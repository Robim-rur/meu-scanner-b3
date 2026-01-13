import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(page_title="B3 VIP GOLD", layout="wide")

# ======================
# LOGIN
# ======================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 ACESSO RESTRITO</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha...", label_visibility="collapsed")
    if st.button("DESBLOQUEAR SISTEMA", use_container_width=True):
        if senha == "mestre10":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ======================
# INTERFACE
# ======================
st.title("📈 SISTEMA B3 VIP - GOLD")

ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "BBDC4.SA", 
    "ABEV3.SA", "WEGE3.SA", "MGLU3.SA", "RENT3.SA", "PRIO3.SA",
    "B3SA3.SA", "GOAU4.SA", "GGBR4.SA", "CSNA3.SA", "RAIZ4.SA",
    "BOVA11.SA", "IVVB11.SA", "SMALL11.SA", "AAPL34.SA", "AMZO34.SA"
]

if st.button("EXECUTAR ANÁLISE DE MERCADO", use_container_width=True):
    resultados = []
    progresso = st.progress(0)
    
    for i, ticker in enumerate(ativos):
        try:
            df_d = yf.download(ticker, period="1y", interval="1d", progress=False)
            df_w = yf.download(ticker, period="2y", interval="1wk", progress=False)

            if df_d.empty or df_w.empty:
                continue

            if isinstance(df_d.columns, pd.MultiIndex):
                df_d.columns = df_d.columns.get_level_values(0)
            if isinstance(df_w.columns, pd.MultiIndex):
                df_w.columns = df_w.columns.get_level_values(0)

            # --- CÁLCULOS ---
            cl_w = df_w['Close']
            m69_w = cl_w.ewm(span=69, adjust=False).mean()
            
            cl_d = df_d['Close']
            m69_d = cl_d.ewm(span=69, adjust=False).mean()
            
            l14, h14 = df_d['Low'].rolling(14).min(), df_d['High'].rolling(14).max()
            stk = 100 * ((cl_d - l14) / (h14 - l14)).rolling(3).mean()
            
            u, d = df_d['High'].diff(), -df_d['Low'].diff()
            tr = pd.concat([df_d['High']-df_d['Low'], abs(df_d['High']-cl_d.shift()), abs(df_d['Low']-cl_d.shift())], axis=1).max(axis=1)
            at_sum = tr.rolling(14).sum()
            pi = 100 * (pd.Series(np.where((u>d)&(u>0), u, 0)).rolling(14).sum().values / at_sum.values)
            mi = 100 * (pd.Series(np.where((d>u)&(d>0), d, 0)).rolling(14).sum().values / at_sum.values)

            # --- REGRAS (REDUZIDAS) ---
            v_w = float(cl_w.iloc[-1]) > float(m69_w.iloc[-1])
            v1 = float(cl_d.iloc[-1]) > float(m69_d.iloc[-1])
            v2 = float(pi[-1]) > float(mi[-1])
            v3 = float(stk.iloc[-1]) < 80

            if v_w and v1 and v2 and v3:
                resultados.append({
                    "Ativo": ticker.replace(".SA", ""),
                    "Preço": f"R$ {float(cl_d.iloc[-1]):.2f}",
                    "Sinal": "COMPRA 🚀"
                })

        except:
            continue
        
        progresso.progress((i + 1) / len(ativos))

    progresso.empty()

    if resultados:
        st.table(pd.DataFrame(resultados))
    else:
        st.warning("Nenhum ativo encontrado.")

st.divider()
