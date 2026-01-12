import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(page_title="SCANNER B3 VIP GOLD", layout="wide")

# LISTA DE ATIVOS (+200)
LISTA_TOTAL_B3 = [
    "RRRP3", "ALOS3", "ALPA4", "ABEV3", "ARZZ3", "ASAI3", "AZUL4", "B3SA3", "BBAS3", "BBDC3", "BBDC4", "BBSE3", "BEEF3", "BPAC11", "BRAP4", "BRFS3", "BRKM5", "CCRO3", "CIEL3", "CMIG4", "CMIN3", "COGN3", "CPFE3", "CPLE6", "CSAN3", "CSNA3", "CVCB3", "CYRE3", "DXCO3", "ELET3", "ELET6", "EMBR3", "ENGI11", "ENEV3", "EGIE3", "EQTL3", "EZTC3", "FLRY3", "GGBR4", "GOAU4", "GOLL4", "HAPV3", "HYPE3", "IGTI11", "ITSA4", "ITUB4", "JBSS3", "KLBN11", "LREN3", "LWSA3", "MGLU3", "MRFG3", "MRVE3", "MULT3", "NTCO3", "PETR3", "PETR4", "RECV3", "PRIO3", "PETZ3", "RADL3", "RAIZ4", "RENT3", "RAIL3", "RDOR3", "SANB11", "SBSP3", "SMTO3", "SUZB3", "TAEE11", "TIMS3", "TOTS3", "TRPL4", "UGPA3", "USIM5", "VALE3", "VBBR3", "VIVT3", "WEGE3", "YDUQ3", "POMO4", "MOVI3", "STBP3", "PSSA11", "TEND3", "JHSF3", "GRND3", "ODPV3", "SLCE3", "MDIA3", "BRSR6", "TRIS3", "LEVE3", "UNIP6", "VULC3", "SIMH3", "KEPL3", "MYPK3", "CAML3", "RANI3", "AMER3", "AERI3", "ZAMP3", "LJQQ3", "AESB3", "MEAL3", "SOJA3", "ROMI3", "RAPT4", "ESPA3", "MILS3", "VIVA3", "PORT3", "GMAT3", "CURY3", "LAVV3", "DIRR3", "ORVR3", "OPCT3", "IFCM3", "CLSA3", "VITT3", "MATD3", "FIQE3", "TFCO4", "INTB3", "AMBP3", "CBAV3", "CXSE3", "GGPS3", "TTEN3", "AGXY3", "BRBI11", "MLAS3", "NUBR33", "PINE4", "RNI3", "RSID3", "SHOW3", "TECN3", "UCAS3",
    "BOVA11", "IVVB11", "SMAL11", "HASH11", "XINA11", "NASD11", "EURP11", "USTK11", "QBTC11", "ETHE11", "GOLD11", "SPXI11", "DIVO11", "BOVV11",
    "AAPL34", "AMZO34", "GOGL34", "MSFT34", "TSLA34", "NVDC34", "META34", "NFLX34", "DISB34", "BABA34", "NIKE34", "PYPL34", "JPMB34", "VIVB34", "COCA34", "PEP34", "MCDC34", "ABTT34", "ADBE34", "AMD34", "AXPB34", "BAHI34", "BERK34", "BKNG34", "CATP34", "COST34", "CRMZ34", "CSCO34", "CVSH34", "EBAY34", "GEPA34", "GILD34", "GSGI34", "HDLU34", "HONB34", "IBMJ34", "INTC34", "ISFE34", "ITUB34", "JNJB34", "LILL34", "LINB34", "LOWC34", "MAEL34", "MMM_34", "MOOO34", "MRCK34", "MSCD34", "ORCL34", "PFIZ34", "PGCO34", "PMAM34", "QCOM34", "SBUX34", "TGTB34", "TMOS34", "TXSA34", "UNHH34", "UPSS34", "USB_34", "VZIO34", "WDPZ34", "WFCO34", "WMTB34", "XOMX34"
]

def calcular_dados(ticker):
    try:
        simbolo = f"{ticker}.SA" if not ticker.endswith(".SA") else ticker
        df = yf.download(simbolo, period="1y", progress=False)
        if df.empty or len(df) < 70: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        cl = df['Close']
        hi = df['High']
        lo = df['Low']
        
        # Indicadores
        m69 = cl.ewm(span=69, adjust=False).mean()
        l14, h14 = lo.rolling(14).min(), hi.rolling(14).max()
        stk = 100 * ((cl - l14) / (h14 - l14)).rolling(3).mean()
        
        up, dw = hi.diff(), -lo.diff()
        tr = pd.concat([hi-lo, abs(hi-cl.shift()), abs(lo-cl.shift())], axis=1).max(axis=1)
        atr_s = tr.rolling(14).sum()
        pi = 100 * (pd.Series(np.where((up>dw)&(up>0), up, 0)).rolling(14).sum().values / atr_s.values)
        mi = 100 * (pd.Series(np.where((dw>up)&(dw>0), dw, 0)).rolling(14).sum().values / atr_s.values)

        # Mapear Sinais Históricos
        sinais_x, sinais_y = [], []
        for i in range(1, len(df)):
            v1 = cl.iloc[i] > m69.iloc[i]
            v2 = pi[i] > mi[i]
            v3 = stk.iloc[i] < 80
            v4 = cl.iloc[i] > hi.iloc[i-1]
            if v1 and v2 and v3 and v4:
                sinais_x.append(df.index[i])
                sinais_y.append(cl.iloc[i])
        
        return df, m69, sinais_x, sinais_y
    except: return None

# --- INTERFACE ---
st.title("🛡️ SCANNER B3 VIP GOLD + GRÁFICOS")

if "resultados" not in st.session_state: st.session_state.resultados = []

if st.button("BUSCAR OPORTUNIDADES AGORA", use_container_width=True):
    deteccoes = []
    progresso = st.progress(0)
    status = st.empty()
    for i, t in enumerate(LISTA_TOTAL_B3):
        status.text(f"Analisando: {t}")
        # Simplificado para o scanner ser rápido
        res_data = calcular_dados(t)
        if res_data:
            df, m69, sx, sy = res_data
            # Verifica se o último dia deu sinal
            if len(sx) > 0 and sx[-1] == df.index[-1]:
                if t.endswith('34'): sl = 0.04
                elif t.endswith('11'): sl = 0.03
                else: sl = 0.05
                preco = float(df['Close'].iloc[-1])
                deteccoes.append({"ATIVO": t, "PREÇO": round(preco, 2), "STOP LOSS": round(preco*(1-sl), 2)})
        progresso.progress((i + 1) / len(LISTA_TOTAL_B3))
    st.session_state.resultados = deteccoes
    status.success(f"Fim! {len(deteccoes)} ativos com sinal.")
    progresso.empty()

if st.session_state.resultados:
    st.table(pd.DataFrame(st.session_state.resultados))
    st.divider()
    
    # SELETOR PARA O GRÁFICO
    ativo_sel = st.selectbox("Escolha um ativo para ver os sinais no gráfico:", [r['ATIVO'] for r in st.session_state.resultados])
    
    if ativo_sel:
        df, m69, sx, sy = calcular_dados(ativo_sel)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.tail(100).index, y=df['Close'].tail(100), name="Preço", line=dict(color="#00FF00")))
        fig.add_trace(go.Scatter(x=df.tail(100).index, y=m69.tail(100), name="EMA 69", line=dict(color="orange", dash="dot")))
        
        # Mostrar os últimos 2 sinais (ou quantos houver no período do gráfico)
        ultimos_sx = sx[-2:] if len(sx) >= 2 else sx
        ultimos_sy = sy[-2:] if len(sy) >= 2 else sy
        
        fig.add_trace(go.Scatter(x=ultimos_sx, y=ultimos_sy, mode='markers', name='Sinal GOLD',
                                 marker=dict(symbol='triangle-up', size=12, color='white', line=dict(width=2, color='green'))))
        
        fig.update_layout(template="plotly_dark", title=f"Sinais Recentes em {ativo_sel}", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
