import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÕES TÉCNICAS (SETUP OCULTO)
# =============================================================================
st.set_page_config(page_title="Scanner B3 - Sinais", layout="wide")

def calcular_indicadores_secretos(df):
    """Cálculos do Setup: Estocástico 14,3,3 e ADX 14"""
    # Garante que as colunas sejam float e limpa dados nulos
    for col in ['High', 'Low', 'Close']:
        df[col] = df[col].astype(float)
    
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    return pd.concat([df, stoch, adx], axis=1)

def obter_gerenciamento(ticker):
    """Define Stop Loss, Gain e Tipo"""
    t = ticker.upper()
    if "34.SA" in t: 
        return 0.04, 0.06, "BDR"
    elif "11.SA" in t: 
        return 0.03, 0.05, "ETF"
    else: 
        return 0.05, 0.08, "AÇÃO"

# =============================================================================
# 2. MOTOR DE ANÁLISE (SEMANAL + DIÁRIO)
# =============================================================================
def analisar_ativo(ticker):
    try:
        # Puxa histórico longo para MM200
        df = yf.download(ticker, period="2y", interval="1d", progress=False)
        if df is None or len(df) < 200: 
            return None
        
        # FILTRO SEMANAL
        df_w = df.resample('W').last()
        df_w = calcular_indicadores_secretos(df_w)
        df_w['SMA200'] = ta.sma(df_w['Close'], length=200)
        
        # Regra: Preço > MM200 e Estocástico %K > %D
        semanal_ok = (df_w['STOCHk_14_3_3'].iloc[-1] > df_w['STOCHd_14_3_3'].iloc[-1]) and \
                     (df_w['Close'].iloc[-1] > df_w['SMA200'].iloc[-1])
        
        if not semanal_ok: 
            return None

        # FILTRO DIÁRIO
        df_d = calcular_indicadores_secretos(df)
        # Regra: Estocástico %K > %D e ADX > 15
        diario_ok = (df_d['STOCHk_14_3_3'].iloc[-1] > df_d['STOCHd_14_3_3'].iloc[-1]) and \
                    (df_d['ADX_14'].iloc[-1] > 15)
        
        if diario_ok:
            return float(df_d['Close'].iloc[-1])
        return None
    except:
        return None

# =============================================================================
# 3. LISTA DE ATIVOS E EXECUÇÃO
# =============================================================================
def main():
    st.title("🎯 Scanner de Oportunidades Profissional")
    
    # Lista organizada em bloco único para evitar quebras de aspas
    ativos_brutos = [
        "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "BBAS3.SA", "JBSS3.SA", "ELET3.SA", "WEGE3.SA", "RENT3.SA",
        "ITSA4.SA", "HAPV3.SA", "GGBR4.SA", "SUZB3.SA", "B3SA3.SA", "MGLU3.SA", "LREN3.SA", "EQTL3.SA", "CSAN3.SA", "RDOR3.SA",
        "RAIL3.SA", "PRIO3.SA", "VIBR3.SA", "UGPA3.SA", "SBSP3.SA", "ASAI3.SA", "CCRO3.SA", "RADL3.SA", "CMIG4.SA", "CPLE6.SA",
        "TOTS3.SA", "CPFE3.SA", "ENEV3.SA", "EMBR3.SA", "BRFS3.SA", "CRFB3.SA", "MULT3.SA", "CSNA3.SA", "GOAU4.SA", "USIM5.SA",
        "CYRE3.SA", "MRVE3.SA", "EZTC3.SA", "DIRR3.SA", "QUAL3.SA", "ALPA4.SA", "YDUQ3.SA", "COGN3.SA", "CVCB3.SA", "AZUL4.SA",
        "AAPL34.SA", "AMZO34.SA", "GOGL34.SA", "MSFT34.SA", "TSLA34.SA", "META34.SA", "NFLX34.SA", "NVDC34.SA", "MELI34.SA", "BABA34.SA",
        "DISB34.SA", "PYPL34.SA", "JNJB34.SA", "PGCO34.SA", "HOME34.SA", "COCA34.SA", "MCDC34.SA", "NIKE34.SA", "NUBR33.SA", "VZBO34.SA",
        "BOVA11.SA", "IVVB11.SA", "SMAL11.SA", "XINA11.SA", "NASD11.SA", "HASH11.SA", "QBTC11.SA", "BITH11.SA", "ETHE11.SA", "SPXI11.SA",
        "PSSA3.SA", "BBSE3.SA", "IRBR3.SA", "CIEL3.SA", "JHSF3.SA", "TEND3.SA", "HBOR3.SA", "EVEN3.SA", "MOVI3.SA", "STBP3.SA",
        "ARZZ3.SA", "CEAB3.SA", "AMAR3.SA", "GRND3.SA", "VIVA3.SA", "ZAMP3.SA", "PETR3.SA", "BBDC3.SA", "ITUB3.SA", "ELET6.SA",
        "SANB11.SA", "BPAC11.SA", "KLBN11.SA", "TAEE11.SA", "TRPL4.SA", "ALUP11.SA", "AESB3.SA", "EGIE3.SA", "AURE3.SA", "CMIN3.SA",
        "BRAP4.SA", "CSMG3.SA", "SAPR11.SA", "SIMH3.SA", "JALL3.SA", "HYPE3.SA", "FLRY3.SA", "ODPV3.SA", "PARD3.SA", "BLAU3.SA",
        "PNVL3.SA", "SLCE3.SA", "SMTO3.SA", "AGRO3.SA", "BEEF3.SA", "MRFG3.SA", "MDIA3.SA", "CAML3.SA", "RAPT4.SA", "TUPY3.SA",
        "KEPL3.SA", "SHUL4.SA", "POMO4.SA", "WIZS3.SA", "CASH3.SA", "LWSA3.SA", "POSI3.SA", "INTB3.SA", "ROMI3.SA", "RANI3.SA",
        "DXCO3.SA", "UNIP6.SA", "AERI3.SA", "LOGN3.SA", "VLID3.SA", "PFRM3.SA", "SOJA3.SA", "ORVR3.SA", "GMAT3.SA", "SOMA3.SA",
        "TIMS3.SA", "VIVT3.SA", "GOLL4.SA", "MYPK3.SA", "LJQQ3.SA", "OPCT3.SA", "LVTC3.SA", "IFCM3.SA", "CLSA3.SA", "NINJ3.SA",
        "SBFG3.SA", "PORT3.SA", "BRML3.SA", "LCAM3.SA", "BKBR3.SA", "CPLE3.SA", "CMIG3.SA", "BMEB4.SA", "BNBR3.SA", "BPNM4.SA"
    ]
    
    # Remove duplicatas e limpa espaços
    ativos = sorted(list(set([a.strip() for a in ativos_brutos])))

    st.subheader(f"📋 Monitorando {len(ativos)} ativos selecionados")
    
    hits = []
    barra = st.progress(0)
    status = st.empty()
    
    for i, t in enumerate(ativos):
        nome = t.replace(".SA", "")
        status.text(f"🔍 Analisando: {nome}...")
        
        preco = analisar_ativo(t)
        if preco:
            l_p, g_p, tipo = obter_gerenciamento(t)
            hits.append({
                "ATIVO": nome,
                "TIPO": tipo,
                "ENTRADA": round(preco, 2),
                "STOP LOSS": round(preco * (1 - l_p), 2),
                "LOSS (%)": f"{l_p*100:.0f}%",
                "STOP GAIN": round(preco * (1 + g_p), 2),
                "GAIN (%)": f"{g_p*100:.1f}%"
            })
        barra.progress((i + 1) / len(ativos))

    status.text("Varredura concluída!")
    
    if hits:
        st.subheader("🚀 Oportunidades Identificadas:")
