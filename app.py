import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Configuração de página
st.set_page_config(page_title="B3 VIP GOLD", layout="wide")

# 2. LOGIN
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acesso Restrito")
    senha = st.text_input("Senha de acesso", type="password")
    if st.button("Entrar"):
        if senha == "mestre10":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# 3. INTERFACE
st.title("Scanner B3 VIP GOLD - Alta Performance")

# LISTA MESTRA (260 ATIVOS)
@st.cache_data
def get_lista_vip():
    lista = [
        "RRRP3.SA", "ALOS3.SA", "ALPA4.SA", "ABEV3.SA", "ARZZ3.SA", "ASAI3.SA", "AZUL4.SA", "B3SA3.SA", 
        "BBAS3.SA", "BBDC3.SA", "BBDC4.SA", "BBSE3.SA", "BEEF3.SA", "BPAC11.SA", "BRAP4.SA", "BRFS3.SA", 
        "BRKM5.SA", "CCRO3.SA", "CIEL3.SA", "CMIG4.SA", "CMIN3.SA", "COGN3.SA", "CPFE3.SA", "CPLE6.SA", 
        "CRFB3.SA", "CSAN3.SA", "CSNA3.SA", "CVCB3.SA", "CYRE3.SA", "DXCO3.SA", "ELET3.SA", "ELET6.SA", 
        "EMBR3.SA", "ENGI11.SA", "ENEV3.SA", "EGIE3.SA", "EQTL3.SA", "EZTC3.SA", "FLRY3.SA", "GGBR4.SA", 
        "GOAU4.SA", "HAPV3.SA", "HYPE3.SA", "ITSA4.SA", "ITUB4.SA", "JBSS3.SA", "KLBN11.SA", "LREN3.SA", 
        "LWSA3.SA", "MGLU3.SA", "MRFG3.SA", "MRVE3.SA", "MULT3.SA", "NTCO3.SA", "PETR3.SA", "PETR4.SA", 
        "PRIO3.SA", "PETZ3.SA", "RADL3.SA", "RAIZ4.SA", "RDOR3.SA", "RENT3.SA", "RAIL3.SA", "SBSP3.SA", 
        "SANB11.SA", "SMTO3.SA", "SUZB3.SA", "TAEE11.SA", "TIMS3.SA", "TOTS3.SA", "UGPA3.SA", "USIM5.SA", 
        "VALE3.SA", "VAMO3.SA", "VBBR3.SA", "VIVT3.SA", "WEGE3.SA", "YDUQ3.SA", "POMO4.SA", "TEND3.SA",
        "SLCE3.SA", "MOVI3.SA", "STBP3.SA", "SOMA3.SA", "PSSA3.SA", "RAPT4.SA", "RECV3.SA", "SIMH3.SA",
        "VULC3.SA", "AURE3.SA", "DIRR3.SA", "JHSF3.SA", "KEPL3.SA", "LEVE3.SA", "MDIA3.SA", "MYPK3.SA",
        "AMER3.SA", "GRND3.SA", "QUAL3.SA", "SMFT3.SA", "TASA4.SA", "TRIS3.SA", "WIZC3.SA", "ZAMP3.SA",
        "BOVA11.SA", "IVVB11.SA", "SMAL11.SA", "HASH11.SA", "QBTC11.SA", "GOLD11.SA", "XINA11.SA",
        "DIVO11.SA", "MATB11.SA", "IFRA11.SA", "TEKB11.SA", "BOVS11.SA", "SPXI11.SA", "EURP11.SA",
        "NASD11.SA", "BBSD11.SA", "ECOO11.SA", "FIND11.SA", "GOVE11.SA", "AAPL34.SA", "AMZO34.SA", 
        "GOGL34.SA", "MSFT34.SA", "TSLA34.SA", "META34.SA", "NVDC34.SA", "DISB34.SA", "NFLX34.SA", 
        "BABA34.SA", "NIKE34.SA", "PYPL34.SA", "JPMC34.SA", "COCA34.SA", "PEP34.SA", "MCDC34.SA", 
        "BERK34.SA", "JNJB34.SA", "PFIZ34.SA", "WALM34.SA", "XOMP34.SA", "ADBE34.SA", "AVGO34.SA", 
        "QCOM34.SA", "TXSA34.SA", "AMDZ34.SA", "ASML34.SA", "COST34.SA"
    ]
    return sorted(list(set(lista)))

ativos = get_lista_vip()

if st.button(f"🚀 INICIAR VARREDURA ({len(ativos)} ATIVOS)", use_container_width=True):
    resultados = []
    progresso = st.progress(0)
    status_msg = st.empty()
    
    for i, ativo in enumerate(ativos):
        try:
            status_msg.text(f"Analisando: {ativo} ({i+1}/{len(ativos)})")
            
            # Download reduzido para estabilidade
            df_d = yf.download(ativo, period="100d", interval="1d", progress=False)
            df_w = yf.download(ativo, period="2y", interval="1wk", progress=False)

            if len(df_d) < 70 or df_d['Close'].isnull().all(): continue
            if isinstance(df_d.columns, pd.MultiIndex): df_d.columns = df_d.columns.get_level_values(0)
            if isinstance(df_w.columns, pd.MultiIndex): df_w.columns = df_w.columns.get_level_values(0)

            # Indicadores
            close = df_d["Close"]
            ema69_d = close.ewm(span=69, adjust=False).mean()
            ema69_w = df_w["Close"].ewm(span=69, adjust=False).mean()

            l14, h14 = df_d["Low"].rolling(14).min(), df_d["High"].rolling(14).max()
            stoch = 100 * (close - l14) / (h14 - l14)

            up, dw = df_d["High"].diff(), -df_d["Low"].diff()
            tr = pd.concat([df_d["High"]-df_d["Low"], abs(df_d["High"]-close.shift()), abs(df_d["Low"]-close.shift())], axis=1).max(axis=1)
            atr = tr.rolling(14).sum()
            pi = 100 * pd.Series(np.where((up>dw)&(up>0), up, 0), index=df_d.index).rolling(14).sum() / atr
            mi = 100 * pd.Series(np.where((dw>up)&(dw>0), dw, 0), index=df_d.index).rolling(14).sum() / atr

            v_p = float(close.iloc[-1])
            max_o = float(df_d["High"].iloc[-2])

            # Filtros Rigorosos VIP GOLD
            if (v_p > float(ema69_w.iloc[-1]) and v_p > float(ema69_d.iloc[-1]) and 
                float(pi.iloc[-1]) > float(mi.iloc[-1]) and float(stoch.iloc[-1]) < 80.0 and v_p > max_o):
                
                if "34" in ativo: cl, pl, pg = "BDR", 4, 6
                elif "11" in ativo: cl, pl, pg = "ETF", 3, 4.5
                else: cl, pl, pg = "Ação", 5, 7.5

                sl, sg = round(v_p*(1-pl/100),2), round(v_p*(1+pg/100),2)

                # Salva dados do gráfico para gerar depois da varredura (evita travar)
                resultados.append({
                    "Ativo": ativo, "Classe": cl, "Entrada (R$)": round(v_p, 2),
                    "Stop Loss": sl, "% Loss": f"-{pl}%", "Stop Gain": sg, "% Gain": f"+{pg}%",
                    "Máx Ontem": round(max_o, 2), "df": df_d.tail(40), "ema": ema69_d.tail(40)
                })

        except Exception as e:
            continue
        
        progresso.progress((i + 1) / len(ativos))

    status_msg.empty()
    progresso.empty()

    if resultados:
        st.success(f"🔥 {len(resultados)} Oportunidades Encontradas!")
        
        # Tabela sem os dados brutos do gráfico
        df_table = pd.DataFrame(resultados).drop(columns=['df', 'ema'])
        st.table(df_table)
        
        st.divider()
        st.subheader("Gráficos Técnicos de Entrada")
        
        # Gera os gráficos um por um após a varredura
        for res in resultados:
            df_g = res['df']
