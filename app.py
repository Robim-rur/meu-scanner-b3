import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÕES TÉCNICAS E INTERFACE (LINHAS 1-25)
# =============================================================================
st.set_page_config(page_title="Scanner de Setup Exclusivo", layout="wide")

def obter_indicadores(df):
    """Calcula Estocástico 14,3,3 e ADX 14"""
    # Estocástico %K e %D
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    # ADX
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    return pd.concat([df, stoch, adx], axis=1)

# =============================================================================
# 2. IDENTIFICAÇÃO DE CLASSE E GERENCIAMENTO (LINHAS 26-60)
# =============================================================================
def definir_parametros_risco(ticker):
    """Retorna Stop Loss e Gain baseados na classe do ativo"""
    t = ticker.upper()
    # Critérios definidos: Ações (L:5% G:7-8%), BDRs (L:4% G:6%), ETFs (L:3% G:4-5%)
    if t.endswith('34.SA'): # BDRs costumam terminar em 34
        return 0.04, 0.06, "BDR"
    elif t.endswith('11.SA'): # ETFs (Ex: BOVA11, IVVB11)
        return 0.03, 0.045, "ETF"
    else: # Ações (Padrão)
        return 0.05, 0.075, "AÇÃO"

# =============================================================================
# 3. FILTRO DO SETUP (SEMANAL + DIÁRIO) (LINHAS 61-95)
# =============================================================================
def scanner_setup(ticker):
    try:
        # Puxa dados diários para converter em semanal também
        dados = yf.download(ticker, period="2y", interval="1d", progress=False)
        if len(dados) < 200: return None
        
        # --- FILTRO SEMANAL ---
        df_w = dados.resample('W').last()
        df_w = obter_indicadores(df_w)
        df_w['SMA200'] = ta.sma(df_w['Close'], length=200)
        
        # Setup Semanal: %K > %D e Tendência Primária de Alta (Preço > MM200)
        autoriza_w = (df_w['STOCHk_14_3_3'].iloc[-1] > df_w['STOCHd_14_3_3'].iloc[-1]) and \
                     (df_w['Close'].iloc[-1] > df_w['SMA200'].iloc[-1])
        
        if not autoriza_w: return None

        # --- FILTRO DIÁRIO ---
        df_d = obter_indicadores(dados)
        # Setup Diário: %K > %D e ADX > 15
        autoriza_d = (df_d['STOCHk_14_3_3'].iloc[-1] > df_d['STOCHd_14_3_3'].iloc[-1]) and \
                     (df_d['ADX_14'].iloc[-1] > 15)
        
        if autoriza_d:
            return df_d.iloc[-1]['Close']
        return None
    except:
        return None

# =============================================================================
# 4. PROCESSAMENTO E FILTRO R/R (LINHAS 96-115)
# =============================================================================
def main():
    st.title("🚀 Scanner Swing Trade - B3")
    st.write("Filtro: Estocástico (S/D) + ADX + Tendência + R/R Mínimo 1.5")

    # Lista de exemplo (Em produção, aqui entrariam os 200 ativos mais líquidos)
    tickers = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "IVVB11.SA", "AAPL34.SA", "BOVA11.SA"]
    
    tabela_final = []
    with st.spinner('Analisando setups...'):
        for t in tickers:
            preco_fech = scanner_setup(t)
            if preco_fech:
                loss_p, gain_p, classe = definir_parametros_risco(t)
                
                # Cálculo de Risco/Retorno
                rr_atual = gain_p / loss_p
                
                # Validação Final: R/R >= 1.5
                if rr_atual >= 1.5:
                    tabela_final.append({
                        "ATIVO": t.replace(".SA", ""),
                        "CLASSE": classe,
                        "ENTRADA (R$)": round(preco_fech, 2),
                        "STOP LOSS (R$)": round(preco_fech * (1 - loss_p), 2),
                        "LOSS (%)": f"{loss_p*100:.0f}%",
                        "STOP GAIN (R$)": round(preco_fech * (1 + gain_p), 2),
                        "GAIN (%)": f"{gain_p*100:.1f}%",
                        "R/R": round(rr_atual, 2)
                    })

    if tabela_final:
        st.table(pd.DataFrame(tabela_final))
    else:
        st.info("Nenhum ativo preencheu todos os critérios do setup até o momento.")

# =============================================================================
# 5. INICIALIZAÇÃO (LINHAS 116-132)
# =============================================================================
if __name__ == "__main__":
    main()
