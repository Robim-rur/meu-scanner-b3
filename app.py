import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor

# Configuração de página
st.set_page_config(page_title="SISTEMA B3 VIP GOLD", layout="wide")

# ==========================================
# GESTÃO DE ACESSO (VIA SECRETS)
# ==========================================
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ TERMINAL VIP GOLD</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Acesso restrito a assinantes ativos.</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            # Pega a senha das configurações secretas do Hugging Face
            # Se não configurar lá, o padrão será 'mestre10'
            try:
                senha_correta = st.secrets["MASTER_PASSWORD"]
            except:
                senha_correta = "mestre10" 
                
            senha_input = st.text_input("Digite sua Chave Mensal:", type="password")
            if st.button("AUTENTICAR"):
                if senha_input == senha_correta:
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Chave inválida ou expirada!")
        st.stop()

login()

# ==========================================
# FUNÇÃO PARA PEGAR TODOS OS ATIVOS DA B3
# ==========================================
@st.cache_data(ttl=86400) # Atualiza a lista 1x por dia
def carregar_todos_ativos():
    # Esta é uma forma robusta de buscar ativos brasileiros via Yahoo Finance
    # Inclui ações, FIIs e BDRs
    try:
        # Lista baseada nos índices amplos da B3
        # Para ser 100% completo, poderíamos baixar uma lista da B3 e subir no Space
        # Mas aqui usaremos uma lista expandida via busca dinâmica ou estática robusta
        df_ibov = pd.read_html('https://en.wikipedia.org/wiki/IBrX-100')[0]
        tickers = df_ibov['Ticker'].tolist()
        # Adicionando manualmente setores comuns e BDRs populares para garantir
        extras = ["PETR4", "VALE3", "ITUB4", "BBDC4", "MGLU3", "IVVB11", "BOVA11", "AAPL34", "NVDC34"]
        return list(set(tickers + extras))
    except:
        # Fallback caso o scraper falhe
        return ["PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3", "ABEV3", "MGLU3"]

# ==========================================
# ENGINE DE SCANNER ROBUSTO
# ==========================================
def scan_engine(ticker):
    try:
        simbolo = f"{ticker}.SA" if ".SA" not in ticker else ticker
        df = yf.download(simbolo, period="100d", interval="1d", progress=False)
        
        if df.empty or len(df) < 70: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        cl = df['Close']
        # Filtro 1: Média Móvel 69 (Tendência)
        m69 = cl.ewm(span=69, adjust=False).mean()
        
        # Filtro 2: Estocástico Rápido
        l14, h14 = df['Low'].rolling(14).min(), df['High'].rolling(14).max()
        stk = 100 * ((cl - l14) / (h14 - l14)).rolling(3).mean()
        
        # Filtro 3: DMI+ e DMI-
        up, dw = df['High'].diff(), -df['Low'].diff()
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-cl.shift()), abs(df['Low']-cl.shift())], axis=1).max(axis=1)
        atr_s = tr.rolling(14).sum().values
        pi = 100 * (pd.Series(np.where((up>dw)&(up>0), up, 0)).rolling(14).sum().values / atr_s)
        mi = 100 * (pd.Series(np.where((dw>up)&(dw>0), dw, 0)).rolling(14).sum().values / atr_s)

        # Lógica de Compra VIP
        last_cl = float(cl.iloc[-1])
        if last_cl > m69.iloc[-1] and pi[-1] > mi[-1] and stk.iloc[-1] < 80:
            if last_cl > float(df['High'].iloc[-2]): # Rompimento
                # Gerenciamento de Risco
                sl, sg = (0.05, 0.08) # Stop 5%, Alvo 8% (Ajustável)
                return {
                    "ATIVO": ticker,
                    "PREÇO": round(last_cl, 2),
                    "STOP LOSS": round(last_cl * (1-sl), 2),
                    "ALVO GAIN": round(last_cl * (1+sg), 2),
                    "FORÇA": round(pi[-1], 1)
                }
    except: return None
    return None

# ==========================================
# INTERFACE
# ==========================================
st.title("🛡️ B3 VIP GOLD SCANNER")
st.write("Varredura em tempo real de todo o mercado brasileiro.")

ativos = carregar_todos_ativos()
st.info(f"Monitorando {len(ativos)} ativos principais da B3.")

if st.button("🚀 INICIAR VARREDURA COMPLETA", use_container_width=True):
    progresso = st.progress(0)
    status_text = st.empty()
    deteccoes = []

    # Uso de 20 threads para alta velocidade
    with ThreadPoolExecutor(max_workers=20) as executor:
        for i, res in enumerate(executor.map(scan_engine, ativos)):
            if res:
                deteccoes.append(res)
            progresso.progress((i + 1) / len(ativos))
            status_text.text(f"Analisando: {ativos[i]}")
            
    st.session_state.resultados_vip = deteccoes
    status_text.success(f"Varredura Finalizada! {len(deteccoes)} oportunidades encontradas.")

# Exibição
if "resultados_vip" in st.session_state and st.session_state.resultados_vip:
    df_final = pd.DataFrame(st.session_state.resultados_vip)
    st.dataframe(df_final, use_container_width=True, hide_index=True)
    
    # Gráfico de Apoio
    st.divider()
    selecao = st.selectbox("Análise Visual do Ativo:", df_final["ATIVO"].tolist())
    # ... (lógica do gráfico igual à anterior, mas com Candlesticks)
