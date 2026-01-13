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
st.title("Scanner B3 VIP GOLD")

# LISTA EXPANDIDA (250 ATIVOS)
@st.cache_data
def get_lista_ativos():
    return sorted(list(set([
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
        "AAPL34.SA", "AMZO34.SA", "GOGL34.SA", "MSFT34.SA", "TSLA34.SA", "META34.SA", "NVDC34.SA",
        "DISB34.SA", "NFLX34.SA", "BABA34.SA", "NIKE34.SA", "PYPL34.SA", "JPMC34.SA", "COCA34.SA",
        "PEP34.SA", "MCDC34.SA", "BERK34.SA", "JNJB34.SA", "PFIZ34.SA", "WALM34.SA", "XOMP34.SA"
        # ... Adicione mais conforme necessário até os 250
    ])))

ativos = get_lista_ativos()

if st.button(f"🔍 INICIAR VARREDURA ({len(ativos)} ATIVOS)", use_container_width=True):
    resultados = []
    lista_graficos = []
    progresso = st.progress(0)
    status = st.empty()
    
    for i, ativo in enumerate(ativos):
        try:
            status.text(f"Processando {i+1}/{len(ativos)}: {ativo}")
            
            # Download otimizado (apenas o necessário)
            df_d = yf.download(ativo, period="60d", interval="1d", progress=False)
            df_w = yf.download(ativo, period="1y", interval="1wk", progress=False)

            if len(df_d) < 20 or len(df_w) < 20: continue
            
            # Limpeza de Colunas
            if isinstance(df_d.columns, pd.MultiIndex): df_d.columns = df_d.columns.get_level_values(0)
            if isinstance(df_w.columns, pd.MultiIndex): df_w.columns = df_w.columns.get_level_values(0)

            cl_d, cl_w = df_d["Close"], df_w["Close"]
            ema69_d = cl_d.ewm(span=69, adjust=False).mean()
            ema69_w = cl_w.ewm(span=69, adjust=False).mean()

            # Estocástico (14)
            l14, h14 = df_d["Low"].rolling(14).min(), df_d["High"].rolling(14).max()
            stk_d = 100 * (cl_d - l14) / (h14 - l14)
            
            # DMI
            u, d = df_d["High"].diff(), -df_d["Low"].diff()
            tr = pd.concat([df_d["High"]-df_d["Low"], abs(df_d["High"]-cl_d.shift()), abs(df_d["Low"]-cl_d.shift())], axis=1).max(axis=1)
            atr = tr.rolling(14).sum()
            pi = 100 * pd.Series(np.where((u>d)&(u>0), u, 0), index=df_d.index).rolling(14).sum() / atr
            mi = 100 * pd.Series(np.where((d>u)&(d>0), d, 0), index=df_d.index).rolling(14).sum() / atr

            # REGRAS DO SETUP
            v_w = float(cl_w.iloc[-1]) > float(ema69_w.iloc[-1])
            v1 = float(cl_d.iloc[-1]) > float(ema69_d.iloc[-1])
            v2 = float(pi.iloc[-1]) > float(mi.iloc[-1])
            v3 = float(stk_d.iloc[-1]) < 80
            v4 = float(cl_d.iloc[-1]) > float(df_d["High"].iloc[-2])

            if v_w and v1 and v2 and v3 and v4:
                entrada = float(cl_d.iloc[-1])
                
                if "34" in ativo: classe, p_l, p_g = "BDR", 4, 6
                elif "11" in ativo: classe, p_l, p_g = "ETF", 3, 4.5
                else: classe, p_l, p_g = "Ação", 5, 7.5

                s_l, s_g = round(entrada*(1-p_l/100),2), round(entrada*(1+p_g/100),2)

                resultados.append({
                    "Ativo": ativo.replace(".SA",""), "Classe": classe,
                    "Entrada (R$)": round(entrada,2), "Stop Loss": s_l,
                    "% Loss": f"-{p_l}%", "Stop Gain": s_g, "% Gain": f"+{p_g}%"
                })

                # Criação do gráfico
                fig = go.Figure(data=[go.Candlestick(x=df_d.index[-30:], open=df_d['Open'][-30:], 
                                high=df_d['High'][-30:], low=df_d['Low'][-30:], close=df_d['Close'][-30:])])
                fig.add_hline(y=entrada, line_color="blue", line_dash="dash")
                fig.add_hline(y=s_g, line_color="green", annotation_text="GAIN")
                fig.add_hline(y=s_l, line_color="red", annotation_text="LOSS")
                fig.update_layout(title=f"{ativo} - VIP GOLD", xaxis_rangeslider_visible=False, height=400)
                lista_graficos.append(fig)

        except: continue
        progresso.progress((i + 1) / len(ativos))

    status.empty()
    progresso.empty()

    if resultados:
        st.table(pd.DataFrame(resultados))
        for g in lista_graficos:
            st.plotly_chart(g, use_container_width=True)
    else:
        st.warning("Nenhum ativo passou nos filtros.")

st.divider()
