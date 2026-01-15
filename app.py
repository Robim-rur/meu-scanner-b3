import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

# =============================================================================
# 1. CONFIGURAÇÕES DE INTERFACE
# =============================================================================
st.set_page_config(page_title="Scanner de Tendência - B3", layout="wide")

def calcular_indicadores(df):
    """Cálculos de Estocástico e DMI (ADX)"""
    # Estocástico 14,3,3
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    # DMI/ADX 14
    adx_df = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    return pd.concat([df, stoch, adx_df], axis=1)

# =============================================================================
# 2. MOTOR DE ANÁLISE COM SEUS PARÂMETROS EXATOS
# =============================================================================
def analisar_ativo(ticker):
    try:
        # Download dos dados
        df_diario = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df_diario is None or len(df_diario) < 50: return None
        
        # Limpeza de multi-index se necessário
        df_diario.columns = [col[0] if isinstance(col, tuple) else col for col in df_diario.columns]
        
        # --- ANÁLISE SEMANAL (CONFIRMAÇÃO) ---
        df_semanal = df_diario.resample('W').last()
        df_s = calcular_indicadores(df_semanal)
        df_s['SMA200'] = ta.sma(df_s['Close'], length=200) # Para tendência de alta
        
        s = df_s.iloc[-1]
        
        # Regras Semanal: Preço > SMA200 + K > D + D+ > D- + ADX > 15
        semanal_ok = (s['Close'] > s['SMA200']) and \
                     (s['STOCHk_14_3_3'] > s['STOCHd_14_3_3']) and \
                     (s['DMP_14'] > s['DMN_14']) and \
                     (s['ADX_14'] > 15)
        
        if not semanal_ok: return None

        # --- ANÁLISE DIÁRIA (ENTRADA) ---
        df_d = calcular_indicadores(df_diario)
        d_atual = df_d.iloc[-1]
        d_anterior = df_d.iloc[-2]
        
        # Regras Diário:
        # 1. DMI: D+ > D- e ADX > 15
        dmi_diario_ok = (d_atual['DMP_14'] > d_atual['DMN_14']) and (d_atual['ADX_14'] > 15)
        
        # 2. Estocástico: K > D E cruzamento recente (K era menor que D) 
        # E o cruzamento (valor de K) deve estar abaixo ou igual a 35
        cruzamento_up = (d_atual['STOCHk_14_3_3'] > d_atual['STOCHd_14_3_3']) and \
                        (d_anterior['STOCHk_14_3_3'] <= d_anterior['STOCHd_14_3_3'])
        
        estocastico_diario_ok = cruzamento_up and (d_atual['STOCHk_14_3_3'] <= 35)

        if dmi_diario_ok and estocastico_diario_ok:
            return round(float(d_atual['Close']), 2)
            
        return None
    except:
        return None

# =============================================================================
# 3. LISTA DOS 100 ATIVOS MAIS NEGOCIADOS E EXECUÇÃO
# =============================================================================
def main():
    st.title("🎯 Scanner Estratégico B3")
    st.write("Filtro: Semanal (Tendência) + Diário (Gatilho Estocástico < 35)")

    top_100 = [
        "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "ABEV3.SA", "JBSS3.SA", "ELET3.SA", "WEGE3.SA", "RENT3.SA",
        "ITSA4.SA", "HAPV3.SA", "GGBR4.SA", "SUZB3.SA", "B3SA3.SA", "MGLU3.SA", "LREN3.SA", "EQTL3.SA", "CSAN3.SA", "RDOR3.SA",
        "RAIL3.SA", "PRIO3.SA", "VIBR3.SA", "UGPA3.SA", "SBSP3.SA", "ASAI3.SA", "CCRO3.SA", "RADL3.SA", "CMIG4.SA", "CPLE6.SA",
        "TOTS3.SA", "CPFE3.SA", "ENEV3.SA", "EMBR3.SA", "BRFS3.SA", "CRFB3.SA", "MULT3.SA", "CSNA3.SA", "GOAU4.SA", "USIM5.SA",
        "HYPE3.SA", "FLRY3.SA", "EGIE3.SA", "TAEE11.SA", "TRPL4.SA", "KLBN11.SA", "BPAC11.SA", "SANB11.SA", "PSSA3.SA", "BBSE3.SA",
        "MRVE3.SA", "CYRE3.SA", "EZTC3.SA", "DIRR3.SA", "ALPA4.SA", "YDUQ3.SA", "COGN3.SA", "AZUL4.SA", "GOLL4.SA", "CVCB3.SA",
        "TIMS3.SA", "VIVT3.SA", "BRAP4.SA", "CMIN3.SA", "CSMG3.SA", "SAPR11.SA", "ALUP11.SA", "AURE3.SA", "SMTO3.SA", "SLCE3.SA",
        "BEEF3.SA", "MRFG3.SA", "MDIA3.SA", "STBP3.SA", "ARZZ3.SA", "VIVA3.SA", "SOMA3.SA", "GMAT3.SA", "LWSA3.SA", "CASH3.SA",
        "POSI3.SA", "INTB3.SA", "RECV3.SA", "BRKM5.SA", "DXCO3.SA", "POMO4.SA", "TUPY3.SA", "KEPL3.SA", "RANI3.SA", "UNIP6.SA",
        "BOVA11.SA", "IVVB11.SA", "SMAL11.SA", "IFNC11.SA", "XINA11.SA", "HASH11.SA", "GOAU4.SA", "USIM5.SA", "PETR3.SA", "BBDC3.SA"
    ]

    if st.button('🔍 Iniciar Varredura de Precisão'):
        hits = []
        barra = st.progress(0)
        status = st.empty()
        
        for i, ticker in enumerate(top_100):
            nome = ticker.replace(".SA", "")
            status.text(f"Processando {nome}...")
            preco = analisar_ativo(ticker)
            
            if preco:
                hits.append({
                    "ATIVO": nome,
                    "ENTRADA (R$)": preco,
                    "STOP LOSS": round(preco * 0.94, 2),
                    "ALVO": round(preco * 1.10, 2)
                })
            barra.progress((i + 1) / len(top_100))
        
        status.success("Varredura finalizada!")
        
        if hits:
            st.table(pd.DataFrame(hits))
        else:
            st.info("Nenhum ativo cumpre rigorosamente todos os critérios de entrada hoje.")

if __name__ == "__main__":
    main()
