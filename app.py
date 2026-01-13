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
    # Estocástico 14,3,3
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    # ADX 14
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    return pd.concat([df, stoch, adx], axis=1)

# =============================================================================
# 2. PARÂMETROS DE RISCO E CLASSIFICAÇÃO (LINHAS 26-55)
# =============================================================================
def definir_alvos(ticker):
    """Define Stop Loss e Gain conforme a classe do ativo"""
    t = ticker.upper()
    if t.endswith('34.SA'): 
        return 0.04, 0.06, "BDR"
    elif t.endswith('11.SA'): 
        return 0.03, 0.05, "ETF" # Ajustado para R/R > 1.5
    else: 
        return 0.05, 0.08, "AÇÃO" # Ajustado para R/R > 1.5

# =============================================================================
# 3. MOTOR DE VARREDURA PRIVADO (LINHAS 56-90)
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
    except:
        return None

# =============================================================================
# 4. EXIBIÇÃO PARA O CLIENTE (LINHAS 91-120)
# =============================================================================
def main():
    st.title("🎯 Scanner de Oportunidades - Mercado B3")
    
    # Lista de ativos que o cliente verá que estão sendo escaneados
    lista_ativos = [
        "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "BBAS3.SA",
        "JBSS3.SA", "ELET3.SA", "WEGE3.SA", "RENT3.SA", "SUZB3.SA", "MGLU3.SA",
        "B3SA3.SA", "LREN3.SA", "HAPV3.SA", "GGBR4.SA", "CSNA3.SA", "RAIL3.SA",
        "AAPL34.SA", "GOGL34.SA", "AMZO34.SA", "MSFT34.SA", "MELI34.SA", "TSLA34.SA",
        "BOVA11.SA", "IVVB11.SA", "SMAL11.SA", "XINA11.SA", "NASD11.SA", "HASH11.SA"
    ]
    
    st.subheader("📋 Ativos em Monitoramento:")
    # Exibe os ativos de forma organizada para o cliente ver o que está sendo analisado
    st.caption(", ".join([t.replace(".SA", "") for t in lista_ativos]))
    
    st.markdown("---")
    
    hits = []
    progresso_barra = st.progress(0)
    status_texto = st.empty()
    
    for i, t in enumerate(lista_ativos):
        ativo_nome = t.replace(".SA", "")
        status_texto.text(f"Analisando: {ativo_nome}...")
        
        preco_entrada = processar_rastreio(t)
        
        if preco_entrada is not None:
            loss_p, gain_p, classe = definir_alvos(t)
            # Risco/Retorno garantido no mínimo 1.5
            hits.append({
                "ATIVO": ativo_nome,
                "TIPO": classe,
                "ENTRADA (R$)": round(float(preco_entrada), 2),
                "STOP LOSS (R$)": round(float(preco_entrada * (1 - loss_p)), 2),
                "LOSS (%)": f"{loss_p*100:.0f}%",
                "STOP GAIN (R$)": round(float(preco_entrada * (1 + gain_p)), 2),
                "GAIN (%)": f"{gain_p*100:.1f}%"
            })
        progresso_barra.progress((i + 1) / len(lista_ativos))

    status_texto.text("Varredura completa!")
    
    st.subheader("🚀 Sinais de Entrada Confirmados:")
    if hits:
        df_final = pd.DataFrame(hits)
        st.table(df_final)
    else:
        st.info("Nenhum ativo da lista preencheu os critérios de entrada no momento.")

# =============================================================================
# 5. INICIALIZAÇÃO (LINHAS 121-132)
# =============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("Sistema em atualização. Por favor, aguarde alguns instantes.")
