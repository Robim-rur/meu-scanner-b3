import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(page_title="B3 VIP GOLD - SCANNER", layout="wide")

# ======================
# LOGIN
# ======================
SENHA = "mestre10"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 ACESSO RESTRITO</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha...", label_visibility="collapsed")
    if st.button("DESBLOQUEAR SISTEMA", use_container_width=True):
        if senha == SENHA:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ======================
# INTERFACE E LISTA
# ======================
st.title("📊 Scanner B3 VIP GOLD (V2 - High Performance)")
st.info("Filtros: Tendência Semanal (M69) + Inclinação do Estocástico Semanal + Gatilho Diário.")

# Lista de ativos
ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "BBDC4.SA", 
    "ABEV3.SA", "WEGE3.SA", "MGLU3.SA", "RENT3.SA", "PRIO3.SA",
    "B3SA3.SA", "GOAU4.SA", "GGBR4.SA", "CSNA3.SA", "RAIZ4.SA",
    "BOVA11.SA", "IVVB11.SA", "SMALL11.SA", "AAPL34.SA", "AMZO34.SA",
    "ELET3.SA", "SUZB3.SA", "LREN3.SA", "HYPE3.SA", "RADL3.SA"
]

if st.button("🔍 INICIAR VARREDURA COMPLETA"):
    resultados = []
    progresso = st.progress(0)
    status = st.empty()

    for i, ticker_sa in enumerate(ativos):
        try:
            status.text(f"Analisando {ticker_sa}...")
            
            # Download Diário e Semanal
            df_d = yf.download(ticker_sa, period="1y", interval="1d", progress=False)
            df_w = yf.download(ticker_sa, period="2y", interval="1wk", progress=False)

            if df_d.empty or df_w.empty or len(df_w) < 70:
                continue

            # Limpeza MultiIndex
            if isinstance(df_d.columns, pd.MultiIndex): df_d.columns = df_d.columns.get_level_values(0)
            if isinstance(df_w.columns, pd.MultiIndex): df_w.columns = df_w.columns.get_level_values(0)

            # --- 1. CÁLCULOS SEMANAIS ---
            cl_w = df_w['Close']
            m69_w = cl_w.ewm(span=69, adjust=False).mean()
            
            # Estocástico Semanal
            low14_w, high14_w = df_w['Low'].rolling(14).min(), df_w['High'].rolling(14).max()
            stk_w = 100 * ((cl_w - low14_w) / (high14_w - low14_w)).rolling(3).mean()

            # FILTRO SEMANAL 01: Preço acima da M69
            semanal_tendencia = float(cl_w.iloc[-1]) > float(m69_w.iloc[-1])
            
            # FILTRO SEMANAL 02: Estocástico não pode estar inclinado para baixo
            # (Valor atual >= Valor da semana anterior)
            semanal_stoch_up = float(stk_w.iloc[-1]) >= float(stk_w.iloc[-2])

            if semanal_tendencia and semanal_stoch_up:
                
                # --- 2. CÁLCULOS DIÁRIOS (GATILHO) ---
                cl_d = df_d['Close']
                m69_d = cl_d.ewm(span=69, adjust=False).mean()

                # Estocástico Diário
                l14_d, h14_d = df_d['Low'].rolling(14).min(), df_d['High'].rolling(14).max()
                stk_d = 100 * ((cl_d - l14_d) / (h14_d - l14_d)).rolling(3).mean()

                # DMI Diário
                u, d = df_d['High'].diff(), -df_d['Low'].diff()
                tr = pd.concat([df_d['High']-df_d['Low'], abs(df_d['High']-cl_d.shift()), abs(df_d['Low']-cl_d.shift())], axis=1).max(axis=1)
                at_sum = tr.rolling(14).sum()
                pi = 100 * (pd.Series(np.where((u>d)&(u>0), u, 0)).rolling(14).sum().values / at_sum.values)
                mi = 100 * (pd.Series(np.where((d>u)&(d>0), d, 0)).rolling(14).sum().values / at_sum.values)

                # VALIDAÇÃO DOS 4 GATILHOS DIÁRIOS
                v1 = float(cl_d.iloc[-1]) > float(m69_d.iloc[-1])         # Preço > M69
                v2 = float(pi[-1]) > float(mi[-1])                       # DMI+ > DMI-
                v3 = float(stk_d.iloc[-1]) < 80                          # Não sobrecomprado
                v4 = float(cl_d.iloc[-1]) > float(df_d['High'].iloc[-2]) # Rompeu máxima anterior

                if v1 and v2 and v3 and v4:
                    ticker = ticker_sa.replace(".SA", "")
                    
                    # Definição de Stop por perfil de ativo
                    if ticker.endswith('34'): s_loss, s_gain = 0.04, 0.06
                    elif ticker.endswith('11') and ticker not in ['PSSA11', 'KLBN11', 'SULA11']: s_loss, s_gain = 0.03, 0.045
                    else: s_loss, s_gain = 0.05, 0.075

                    preço_atual = float(cl_d.iloc[-1])
                    resultados.append({
                        "Ativo": ticker,
                        "Sinal": "COMPRA VIP GOLD 🚀",
                        "Preço": f"R$ {preço_atual:.2f}",
                        "Stop Loss": f"R$ {preço_atual*(1-s_loss):.2f}",
                        "Stop Gain": f"R$ {preço_atual*(1+s_gain):.2f}",
                        "Estoc. Semanal": "📈 Subindo" if float(stk_w.iloc[-1]) > float(stk_w.iloc[-2]) else "➡️ Estável"
                    })

        except Exception as e:
            continue
        
        progresso.progress((i + 1) / len(ativos))

    status.empty()
    progresso.empty()

    # EXIBIÇÃO
    if resultados:
        st.success(f"🔥 {len(resultados)} ativos filtrados com sucesso!")
        st.table(pd.DataFrame(resultados))
    else:
        st.warning("Nenhum ativo passou por todos os filtros (Semanal + Diário) hoje.")

st.divider()
st.markdown("""
**Regras de Ouro aplicadas:**
- **Filtro Semanal:** Preço acima da Média 69 + Estocástico Semanal NÃO pode estar caindo.
- **Gatilho Diário:** Preço > M69 + DMI+ > DMI- + Estocástico < 80 + Rompimento da Máxima de ontem.
""")
