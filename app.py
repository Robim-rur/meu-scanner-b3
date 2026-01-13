import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. Configuração Inicial (DEVE ser a primeira linha de comando Streamlit)
st.set_page_config(page_title="B3 VIP GOLD", layout="wide")

# 2. SISTEMA DE LOGIN (Bloqueia tudo abaixo)
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 ACESSO RESTRITO</h2>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1,1,1])
    with col_c:
        senha = st.text_input("Digite a Senha", type="password")
        if st.button("LIBERAR SCANNER", use_container_width=True):
            if senha == "mestre10":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Senha Incorreta")
    st.stop()

# 3. INTERFACE APÓS LOGIN
st.title("📈 SCANNER B3 VIP GOLD")
st.markdown("---")

# Lista de ativos para busca
ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "BBDC4.SA", 
    "ABEV3.SA", "WEGE3.SA", "MGLU3.SA", "RENT3.SA", "PRIO3.SA",
    "B3SA3.SA", "GOAU4.SA", "GGBR4.SA", "CSNA3.SA", "RAIZ4.SA",
    "BOVA11.SA", "IVVB11.SA", "SMALL11.SA", "AAPL34.SA", "AMZO34.SA"
]

if st.button("🚀 INICIAR VARREDURA AGORA", use_container_width=True):
    resultados = []
    progresso = st.progress(0)
    status = st.empty()

    for i, ticker_sa in enumerate(ativos):
        try:
            status.text(f"Analisando {ticker_sa}...")
            
            # Download de dados
            df_d = yf.download(ticker_sa, period="1y", interval="1d", progress=False)
            df_w = yf.download(ticker_sa, period="2y", interval="1wk", progress=False)

            if df_d.empty or df_w.empty:
                continue

            # Ajuste de Colunas (yfinance fix)
            if isinstance(df_d.columns, pd.MultiIndex): df_d.columns = df_d.columns.get_level_values(0)
            if isinstance(df_w.columns, pd.MultiIndex): df_w.columns = df_w.columns.get_level_values(0)

            # --- LÓGICA SEMANAL ---
            cl_w = df_w['Close']
            m69_w = cl_w.ewm(span=69, adjust=False).mean()
            
            # Estocástico Semanal
            low_w, high_w = df_w['Low'].rolling(14).min(), df_w['High'].rolling(14).max()
            stk_w = 100 * ((cl_w - low_w) / (high_w - low_w)).rolling(3).mean()

            # Filtros Semanais
            ok_m69_w = float(cl_w.iloc[-1]) > float(m69_w.iloc[-1])
            # Se o estocástico estiver caindo muito forte (diferença > 2 pontos), bloqueia
            stoch_caindo = float(stk_w.iloc[-1]) < (float(stk_w.iloc[-2]) - 2.0)

            if ok_m69_w and not stoch_caindo:
                
                # --- LÓGICA DIÁRIA (GATILHO) ---
                cl_d = df_d['Close']
                m69_d = cl_d.ewm(span=69, adjust=False).mean()
                
                # Estocástico Diário
                low_d, high_d = df_d['Low'].rolling(14).min(), df_d['High'].rolling(14).max()
                stk_d = 100 * ((cl_d - low_d) / (high_d - low_d)).rolling(3).mean()

                # DMI Diário
                u, d = df_d['High'].diff(), -df_d['Low'].diff()
                tr = pd.concat([df_d['High']-df_d['Low'], abs(df_d['High']-cl_d.shift()), abs(df_d['Low']-cl_d.shift())], axis=1).max(axis=1)
                at_sum = tr.rolling(14).sum()
                pi = 100 * (pd.Series(np.where((u>d)&(u>0), u, 0)).rolling(14).sum().values / at_sum.values)
                mi = 100 * (pd.Series(np.where((d>u)&(d>0), d, 0)).rolling(14).sum().values / at_sum.values)

                # OS 4 PILARES DO GATILHO
                v1 = float(cl_d.iloc[-1]) > float(m69_d.iloc[-1])
                v2 = float(pi[-1]) > float(mi[-1])
                v3 = float(stk_d.iloc[-1]) < 80
                v4 = float(cl_d.iloc[-1]) > float(df_d['High'].iloc[-2])

                if v1 and v2 and v3 and v4:
                    # Cálculo de Stop
                    ticker = ticker_sa.replace(".SA", "")
                    s_loss = 0.04 if ticker.endswith('34') else 0.05
                    
                    resultados.append({
                        "ATIVO": ticker,
                        "PREÇO": f"R$ {float(cl_d.iloc[-1]):.2f}",
                        "STOP LOSS": f"R$ {float(cl_d.iloc[-1])*(1-s_loss):.2f}",
                        "ALVO (GAIN)": f"R$ {float(cl_d.iloc[-1])*(1+(s_loss*1.5)):.2f}"
                    })

        except:
            continue
        
        progresso.progress((i + 1) / len(ativos))

    status.empty()
    progresso.empty()

    if resultados:
        st.success(f"Sinal de Compra Confirmado em {len(resultados)} ativos!")
        st.dataframe(pd.DataFrame(resultados), use_container_width=True)
    else:
        st.warning("Nenhum ativo passou nos filtros hoje. O mercado pode estar em correção.")

st.sidebar.write("### Critérios VIP GOLD")
st.sidebar.write("- Semanal acima da M69")
st.sidebar.write("- Estocástico Semanal estável/subindo")
st.sidebar.write("- Gatilhos técnicos no Diário")
