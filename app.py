import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÕES TÉCNICAS E INTERFACE (LINHAS 1-25)
# =============================================================================
st.set_page_config(page_title="Scanner B3 - Setup Profissional", layout="wide")

def obter_indicadores(df):
    """Calcula Estocástico 14,3,3 e ADX 14 necessários para o setup"""
    # Estocástico %K e %D (Usando a biblioteca pandas_ta)
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    # ADX (Average Directional Index)
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    return pd.concat([df, stoch, adx], axis=1)

# =============================================================================
# 2. IDENTIFICAÇÃO DE CLASSE E GERENCIAMENTO (LINHAS 26-60)
# =============================================================================
def definir_parametros_risco(ticker):
    """Retorna Stop Loss e Gain baseados na classe e valida R/R >= 1.5"""
    t = ticker.upper()
    # Ações: L 5%, G 7.5% (R/R 1.5) | BDRs: L 4%, G 6% (R/R 1.5) | ETFs: L 3%, G 4.5% (R/R 1.5)
    if t.endswith('34.SA'): 
        return 0.04, 0.06, "BDR"
    elif t.endswith('11.SA'): 
        return 0.03, 0.045, "ETF"
    else: 
        return 0.05, 0.075, "AÇÃO"

# =============================================================================
# 3. FILTRO DO SETUP SECRETO (SEMANAL + DIÁRIO) (LINHAS 61-95)
# =============================================================================
def analisar_setup(ticker):
    """Executa o scanner seguindo a risca o setup operacional"""
    try:
        # Puxa 2 anos de dados para ter MM200 semanal estável
        dados = yf.download(ticker, period="2y", interval="1d", progress=False)
        if len(dados) < 200: return None
        
        # --- FILTRO 01: SEMANAL (Resampling para converter dias em semanas) ---
        df_w = dados.resample('W').last()
        df_w = obter_indicadores(df_w)
        df_w['SMA200'] = ta.sma(df_w['Close'], length=200)
        
        # Condição Semanal: %K > %D e Preço > MM200 (Tendência Primária de Alta)
        autoriza_w = (df_w['STOCHk_14_3_3'].iloc[-1] > df_w['STOCHd_14_3_3'].iloc[-1]) and \
                     (df_w['Close'].iloc[-1] > df_w['SMA200'].iloc[-1])
        
        if not autoriza_w: return None

        # --- FILTRO 02: DIÁRIO ---
        df_d = obter_indicadores(dados)
        # Condição Diária: %K > %D e ADX > 15
        autoriza_d = (df_d['STOCHk_14_3_3'].iloc[-1] > df_d['STOCHd_14_3_3'].iloc[-1]) and \
                      (df_d['ADX_14'].iloc[-1] > 15)
        
        if autoriza_d:
            return df_d.iloc[-1]['Close']
        return None
    except Exception:
        return None

# =============================================================================
# 4. PROCESSAMENTO E EXIBIÇÃO PARA O CLIENTE (LINHAS 96-115)
# =============================================================================
def main():
    st.title("🔍 Scanner B3 - Setup de Alta Liquidez")
    st.write("Ativos filtrados pelo Setup Estocástico (S/D) + ADX + Tendência Primária.")

    # Lista de ativos monitorados (Principais da B3 para teste)
    ativos = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "IVVB11.SA", "AAPL34.SA", "BOVA11.SA"]
    
    hits = []
    with st.spinner('Escaneando mercado...'):
        for t in ativos:
            preco_entrada = analisar_setup(t)
            if preco_entrada:
                loss_p, gain_p, classe = definir_parametros_risco(t)
                rr = gain_p / loss_p # Validação da relação mínima de 1.5
                
                if rr >= 1.5:
                    hits.append({
                        "ATIVO": t.replace(".SA", ""),
                        "ENTRADA (R$)": round(preco_entrada, 2),
                        "STOP LOSS": round(preco_entrada * (1 - loss_p), 2),
                        "LOSS (%)": f"{loss_p*100:.0f}%",
                        "STOP GAIN": round(preco_entrada * (1 + gain_p), 2),
                        "GAIN (%)": f"{gain_p*100:.1f}%"
                    })

    if hits:
        st.table(pd.DataFrame(hits))
    else:
        st.info("Nenhum ativo preencheu todos os critérios técnicos (Semanal + Diário) hoje.")

# =============================================================================
# 5. INICIALIZAÇÃO DO SISTEMA (LINHAS 116-132)
# =============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erro na execução: {e}")
# Fim do código com 132 linhas totais.
