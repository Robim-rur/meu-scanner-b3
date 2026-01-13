import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÕES DE INTERFACE (LINHAS 1-25)
# =============================================================================
st.set_page_config(page_title="Scanner de Sinais B3", layout="wide")

def obter_indicadores_internos(df):
    """Cálculos proprietários do setup (ocultos do cliente)"""
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    return pd.concat([df, stoch, adx], axis=1)

# =============================================================================
# 2. PARÂMETROS DE RISCO E CLASSIFICAÇÃO (LINHAS 26-60)
# =============================================================================
def definir_alvos(ticker):
    """Define Stop Loss e Gain conforme a classe do ativo"""
    t = ticker.upper()
    # Ações: L 5%, G 7.5% | BDRs: L 4%, G 6% | ETFs: L 3%, G 4.5%
    if t.endswith('34.SA'): 
        return 0.04, 0.06, "BDR"
    elif t.endswith('11.SA'): 
        return 0.03, 0.045, "ETF"
    else: 
        return 0.05, 0.075, "AÇÃO"

# =============================================================================
# 3. MOTOR DE VARREDURA PRIVADO (LINHAS 61-90)
# =============================================================================
def processar_rastreio(ticker):
    """Executa a lógica de filtragem sem expor os critérios na tela"""
    try:
        dados = yf.download(ticker, period="2y", interval="1d", progress=False)
        if len(dados) < 200: return None
        
        # Análise Semanal (Oculta)
        df_w = dados.resample('W').last()
        df_w = obter_indicadores_internos(df_w)
        df_w['SMA200'] = ta.sma(df_w['Close'], length=200)
        
        autoriza_semanal = (df_w['STOCHk_14_3_3'].iloc[-1] > df_w['STOCHd_14_3_3'].iloc[-1]) and \
                           (df_w['Close'].iloc[-1] > df_w['SMA200'].iloc[-1])
        
        if not autoriza_semanal: return None

        # Análise Diária (Oculta)
        df_d = obter_indicadores_internos(dados)
        autoriza_diario = (df_d['STOCHk_14_3_3'].iloc[-1] > df_d['STOCHd_14_3_3'].iloc[-1]) and \
                          (df_d['ADX_14'].iloc[-1] > 15)
        
        if autoriza_diario:
            return df_d.iloc[-1]['Close']
        return None
    except Exception:
        return None

# =============================================================================
# 4. EXIBIÇÃO PARA O CLIENTE (LINHAS 91-115)
# =============================================================================
def main():
    st.title("🎯 Oportunidades Identificadas - B3")
    st.write("Ativos que atingiram os critérios de entrada para operação hoje.")

    # Lista organizada verticalmente para evitar erros de sintaxe (SyntaxError)
    lista_ativos = [
        "PETR4.SA", 
        "VALE3.SA", 
        "ITUB4.SA", 
        "BBDC4.SA", 
        "ABEV3.SA", 
        "BBAS3.SA", 
        "AAPL34.SA", 
        "GOGL34.SA", 
        "AMZO34.SA", 
        "MSFT34.SA", 
        "BOVA11.SA", 
        "IVVB11.SA",
        "WEGE3.SA", 
        "RENT3.SA", 
        "SUZB3.SA", 
        "MGLU3.SA", 
        "B3SA3.SA", 
        "LREN3.SA"
    ]
    
    hits = []
    progresso = st.progress(0)
    
    for i, t in enumerate(lista_ativos):
        preco_entrada = processar_rastreio(t)
        if preco_entrada is not None:
            loss_p, gain_p, classe = definir_alvos(t)
            hits.append({
                "ATIVO": t.replace(".SA", ""),
                "TIPO": classe,
                "ENTRADA (R$)": round(float(preco_entrada), 2),
                "STOP LOSS (R$)": round(float(preco_entrada * (1 - loss_p)), 2),
                "LOSS (%)": f"{loss_p*100:.0f}%",
                "STOP GAIN (R$)": round(float(preco_entrada * (1 + gain_p)), 2),
                "GAIN (%)": f"{gain_p*100:.1f}%"
            })
        progresso.progress((i + 1) / len(lista_ativos))

    if hits:
        st.table(pd.DataFrame(hits))
    else:
        st.info("Nenhuma nova entrada identificada para os ativos monitorados nesta sessão.")

# =============================================================================
# 5. INICIALIZAÇÃO (LINHAS 116-132)
# =============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("Sistema em atualização. Por favor, aguarde alguns instantes.")
