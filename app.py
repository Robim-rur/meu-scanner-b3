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
    if st.button("Entrar", use_container_width=True):
        if senha == SENHA:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# ======================
# INTERFACE
# ======================
st.title("📊 Scanner B3 VIP GOLD - Sincronizado")

ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "BBDC4.SA", 
    "ABEV3.SA", "WEGE3.SA", "MGLU3.SA", "RENT3.SA", "PRIO3.SA",
    "B3SA3.SA", "GOAU4.SA", "GGBR4.SA", "CSNA3.SA", "BOVA11.SA"
]

if st.button("🔍 EXECUTAR VARREDURA", use_container_width=True):
    resultados = []
    progresso = st.progress(0)
    
    for i, ticker in enumerate(ativos):
        try:
            # Baixamos apenas o Diário (mais estável)
            df = yf.download(ticker, period="2y", interval="1d", progress=False)
            if df.empty or len(df) < 100: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

            # --- CONSTRUÇÃO DO SEMANAL (A partir do Diário) ---
            # Isso garante que o Scanner veja o MESMO que o seu gráfico
            df_w = df.resample('W').last()
            
            # --- CÁLCULOS SEMANAIS ---
            cl_w = df_w["Close"]
            m69_w = cl_w.ewm(span=69, adjust=False).mean()
            lo_w, hi_w = df_w["Low"], df_w["High"]
            stk_w = 100 * ((cl_w - lo_w.rolling(14).min()) / (hi_w.rolling(14).max() - lo_w.rolling(14).min())).rolling(3).mean()
            
            # FILTRO 1: SEMANAL (M69 + Estocástico não caindo)
            ok_w = (float(cl_w.iloc[-1]) > float(m69_w.iloc[-1])) and (float(stk_w.iloc[-1]) >= float(stk_w.iloc[-2]))

            if ok_w:
                # --- CÁLCULOS DIÁRIOS ---
                cl_d = df["Close"]
                m69_d = cl_d.ewm(span=69, adjust=False).mean()
                lo_d, hi_d = df["Low"], df["High"]
                
                # Estocástico Diário (K e D)
                stk_d_k = 100 * ((cl_d - lo_d.rolling(14).min()) / (hi_d.rolling(14).max() - lo_d.rolling(14).min())).rolling(3).mean()
                stk_d_d = stk_d_k.rolling(3).mean()
                
                # DMI Diário
                u, d = hi_d.diff(), -lo_d.diff()
                tr = pd.concat([hi_d-lo_d, abs(hi_d-cl_d.shift()), abs(lo_d-cl_d.shift())], axis=1).max(axis=1)
                at = tr.rolling(14).sum()
                pi = 100 * (pd.Series(np.where((u>d)&(u>0), u, 0)).rolling(14).sum().values / at.values)
                mi = 100 * (pd.Series(np.where((d>u)&(d>0), d, 0)).rolling(14).sum().values / at.values)

                # GATILHOS DIÁRIOS (Conforme seu setup colado)
                v1 = float(cl_d.iloc[-1]) > float(m69_d.iloc[-1])  # Preço > M69
                v2 = float(pi[-1]) > float(mi[-1])                # D+ > D-
                v3 = float(stk_d_k.iloc[-1]) > float(stk_d_d.iloc[-1]) # %K > %D
                v4 = float(cl_d.iloc[-1]) > float(hi_d.iloc[-2])  # Rompeu máxima anterior

                if v1 and v2 and v3 and v4:
                    resultados.append({
                        "ATIVO": ticker.replace(".SA", ""),
                        "FECHAMENTO": f"R$ {float(cl_d.iloc[-1]):.2f}",
                        "SINAL": "VIP GOLD COMPRA 🚀"
                    })

        except: continue
        progresso.progress((i + 1) / len(ativos))

    if resultados:
        st.success(f"Encontrados {len(resultados)} ativos!")
        st.table(pd.DataFrame(resultados))
    else:
        st.warning("Nenhum ativo passou hoje. Verifique se o ativo que você esperava rompeu a máxima de ontem.")

st.divider()
st.caption("Dica: Se um ativo não passou, verifique se o Estocástico Semanal dele não está levemente inclinado para baixo.")
