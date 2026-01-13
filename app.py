import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÕES DE INTERFACE
# =============================================================================
st.set_page_config(page_title="Scanner B3 - Sinais de Entrada", layout="wide")

def obter_indicadores_secretos(df):
    """Cálculos do Setup: Estocástico 14,3,3 e ADX 14 (Oculto)"""
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    return pd.concat([df, stoch, adx], axis=1)

# =============================================================================
# 2. DEFINIÇÃO DE ALVOS E RISCO/RETORNO
# =============================================================================
def obter_gerenciamento(ticker):
    """Define Stop Loss, Gain e Classe"""
    t = ticker.upper()
    if t.endswith('34.SA'): 
        return 0.04, 0.06, "BDR"
    elif t.endswith('11.SA'): 
        return 0.03, 0.05, "ETF"
    else: 
        return 0.05, 0.08, "AÇÃO"

# =============================================================================
# 3. MOTOR DE VARREDURA (SEMANAL + DIÁRIO)
# =============================================================================
def analisar_ativo(ticker):
    try:
        df = yf.download(ticker, period="2y", interval="1d", progress=False)
        if len(df) < 200: return None
        
        # FILTRO SEMANAL: Tendência de Alta (Preço > MM200) e Estocástico %K > %D
        df_w = df.resample('W').last()
        df_w = obter_indicadores_secretos(df_w)
        df_w['SMA200'] = ta.sma(df_w['Close'], length=200)
        
        semanal_ok = (df_w['STOCHk_14_3_3'].iloc[-1] > df_w['STOCHd_14_3_3'].iloc[-1]) and \
                     (df_w['Close'].iloc[-1] > df_w['SMA200'].iloc[-1])
        if not semanal_ok: return None

        # FILTRO DIÁRIO: Estocástico %K > %D e ADX > 15
        df_d = obter_indicadores_secretos(df)
        diario_ok = (df_d['STOCHk_14_3_3'].iloc[-1] > df_d['STOCHd_14_3_3'].iloc[-1]) and \
                    (df_d['ADX_14'].iloc[-1] > 15)
        
        if diario_ok:
            return df_d.iloc[-1]['Close']
        return None
    except:
        return None

# =============================================================================
# 4. LISTA BLINDADA DE 200 ATIVOS
# =============================================================================
def main():
    st.title("🎯 Scanner de Oportunidades Profissional")
    
    # Texto multilinhas blindado contra SyntaxError
    raw_tickers = """
    PETR4.SA VALE3.SA ITUB4.SA BBDC4.SA ABEV3.SA BBAS3.SA JBSS3.SA ELET3.SA WEGE3.SA RENT3.SA
    ITSA4.SA HAPV3.SA GGBR4.SA SUZB3.SA B3SA3.SA MGLU3.SA LREN3.SA EQTL3.SA CSAN3.SA RDOR3.SA
    RAIL3.SA PRIO3.SA VIBR3.SA UGPA3.SA SBSP3.SA ASAI3.SA CCRO3.SA RADL3.SA CMIG4.SA CPLE6.SA
    TOTS3.SA CPFE3.SA ENEV3.SA EMBR3.SA BRFS3.SA CRFB3.SA MULT3.SA CSNA3.SA GOAU4.SA USIM
