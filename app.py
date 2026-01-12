import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(page_title="SCANNER B3 VIP GOLD", layout="wide")

# =========================================================
# LISTA DE ALTA LIQUIDEZ (+200 ATIVOS)
# =========================================================
LISTA_TOTAL_B3 = [
    # AÇÕES PRINCIPAIS (IBOVESPA + IGC)
    "RRRP3", "ALOS3", "ALPA4", "ABEV3", "ARZZ3", "ASAI3", "AZUL4", "B3SA3", "BBAS3", "BBDC3", "BBDC4", "BBSE3", "BEEF3", "BPAC11", "BRAP4", "BRFS3", "BRKM5", "CCRO3", "CIEL3", "CMIG4", "CMIN3", "COGN3", "CPFE3", "CPLE6", "CSAN3", "CSNA3", "CVCB3", "CYRE3", "DXCO3", "ELET3", "ELET6", "EMBR3", "ENGI11", "ENEV3", "EGIE3", "EQTL3", "EZTC3", "FLRY3", "GGBR4", "GOAU4", "GOLL4", "HAPV3", "HYPE3", "IGTI11", "ITSA4", "ITUB4", "JBSS3", "KLBN11", "LREN3", "LWSA3", "MGLU3", "MRFG3", "MRVE3", "MULT3", "NTCO3", "PETR3", "PETR4", "RECV3", "PRIO3", "PETZ3", "RADL3", "RAIZ4", "RENT3", "RAIL3", "RDOR3", "SANB11", "SBSP3", "SMTO3", "SUZB3", "TAEE11", "TIMS3", "TOTS3", "TRPL4", "UGPA3", "USIM5", "VALE3", "VBBR3", "VIVT3", "WEGE3", "YDUQ3", "POMO4", "MOVI3", "STBP3", "SULA11", "PSSA11", "TEND3", "JHSF3", "GRND3", "ODPV3", "SLCE3", "MDIA3", "BBDC4", "BRSR6", "TRIS3", "LEVE3", "UNIP6", "VULC3", "SIMH3", "KEPL3", "MYPK3", "CAML3", "RANI3", "AMER3", "AERI3", "ZAMP3", "LJQQ3", "AESB3", "MEAL3", "SOJA3", "ROMI3", "RAPT4", "GOLL4", "ESPA3", "MILS3", "VIVA3", "PORT3", "GMAT3", "CURY3", "LAVV3", "DIRR3", "ORVR3", "OPCT3", "IFCM3", "CLSA3", "VITT3", "MATD3", "FIQE3", "TFCO4", "INTB3", "AMBP3", "CBAV3", "CXSE3", "GGPS3", "TTEN3", "AGXY3", "RECV3", "BRBI11", "MODL3", "MLAS3", "NUBR33", "PINE4", "RNI3", "RSID3", "SHOW3", "TECN3", "UCAS3",
    # ETFs
    "BOVA11", "IVVB11", "SMAL11", "HASH11", "XINA11", "NASD11", "EURP11", "USTK11", "QBTC11", "ETHE11", "GOLD11", "SPXI11", "DIVO11", "BOVV11",
    # BDRs (MAIS LÍQUIDOS)
    "AAPL34", "AMZO34", "GOGL34", "MSFT34", "TSLA34", "NVDC34", "META34", "NFLX34", "DISB34", "BABA34", "NIKE34", "PYPL34", "JPMB34", "VIVB34", "COCA34", "PEP34", "MCDC34", "ABTT34", "ADBE34", "AMD34", "AXPB34", "BAHI34", "BERK34", "BKNG34", "CATP34", "COST34", "CRMZ34", "CSCO34", "CVSH34", "EBAY34", "GEPA34", "GILD34", "GSGI34", "HDLU34", "HONB34", "IBMJ34", "INTC34", "ISFE34", "ITUB34", "JNJB34", "LILL34", "LINB34", "LOWC34", "MAEL34", "MMM_34", "MOOO34", "MRCK34", "MSCD34", "ORCL34", "PFIZ34", "PGCO34", "PMAM34", "QCOM34", "SBUX34", "TGTB34", "TMOS34", "TXSA34", "UNHH34", "UPSS34", "USB_34", "VZIO34", "WDPZ34", "WFCO34", "WMTB34", "XOMX34"
]

def analisar_ativo(ticker):
    try:
        simbolo = f"{ticker}.SA" if not ticker.endswith(".SA") else ticker
        df = yf.download(simbolo, period="150d", progress=False, threads=True)
        
        if df.empty or len(df) < 70:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # INDICADORES
        ema69 = close.ewm(span=69, adjust=False).mean()
        l14, h14 = low.rolling(14).min(), high.rolling(14).max()
        stoch = 100 * ((close - l14) / (h14 - l14)).rolling(3).mean()
        
        up, dw = high.diff(), -low.diff()
        tr = pd.concat([high-low, abs(high-close.shift()), abs(low-close.shift())], axis=1).max(axis=1)
        atr_sum = tr.rolling(14).sum()
        p_di = 100 * (pd.Series(np.where((up>dw)&(up>0), up, 0)).rolling(14).sum().values / atr_sum.values)
        m_di = 100 * (pd.Series(np.where((dw>up)&(dw>0), dw, 0)).rolling(14).sum().values / atr_sum.values)

        # REGRAS DE STOP
        if ticker.endswith('34'): s_loss, s_gain = 0.04, 0.06
        elif ticker.endswith('11'): s_loss, s_gain = 0.03, 0.045
        else: s_loss, s_gain = 0.05, 0.075

        # SETUP GOLD (AS 4 REGRAS)
        c1 = close.iloc[-1] > ema69.iloc[-1]
        c2 = p_di[-1] > m_di[-1]
        c3 = stoch.iloc[-1] < 80
        c4 = close.iloc[-1] > high.iloc[-2]

        if c1 and c2 and c3 and c4:
            preco_fechamento = float(close.iloc[-1])
            return {
                "ATIVO": ticker,
                "PREÇO": round(preco_fechamento, 2),
                "STOP LOSS": round(preco_fechamento * (1 - s_loss), 2),
                "STOP GAIN": round(preco_fechamento * (1 + s_gain), 2),
                "STATUS": "🚀 COMPRA"
            }
    except: return None
    return None

# --- INTERFACE ---
st.title("🛡️ SCANNER B3 VIP GOLD - LIQUIDEZ TOTAL")
st.write(f"Analisando os **{len(LISTA_TOTAL_B3)}** ativos mais importantes do mercado.")

if st.button("BUSCAR OPORTUNIDADES AGORA", use_container_width=True):
    lista_deteccoes = []
    progresso = st.progress(0)
    status_bar = st.empty()
    
    total = len(LISTA_TOTAL_B3)
    
    for i, ticker in enumerate(LISTA_TOTAL_B3):
        status_bar.text(f"Varrendo: {ticker} ({i+1}/{total})")
        resultado = analisar_ativo(ticker)
        if resultado:
            lista_deteccoes.append(resultado)
        progresso.progress((i + 1) / total)
    
    status_bar.success(f"Análise Completa! Foram encontrados {len(lista_deteccoes)} sinais.")
    progresso.empty()

    if lista_deteccoes:
        df_final = pd.DataFrame(lista_deteccoes)
        st.subheader("🎯 LISTA DE ENTRADA - SETUP GOLD")
        st.table(df_final)
    else:
        st.warning("Nenhum ativo de alta liquidez deu sinal de compra no momento.")
