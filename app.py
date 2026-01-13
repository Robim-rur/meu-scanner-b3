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

# LISTA COMPLETA 250+ (TODOS OS ATIVOS LÍQUIDOS)
ativos_full = [
    # AÇÕES
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
    # ETFs
    "BOVA11.SA", "IVVB11.SA", "SMAL11.SA", "HASH11.SA", "QBTC11.SA", "GOLD11.SA", "XINA11.SA",
    "DIVO11.SA", "MATB11.SA", "IFRA11.SA", "TEKB11.SA", "BOVS11.SA", "SPXI11.SA", "EURP11.SA",
    "NASD11.SA", "BBSD11.SA", "ECOO11.SA", "FIND11.SA", "GOVE11.SA", "REIT11.SA",
    # BDRs
    "AAPL34.SA", "AMZO34.SA", "GOGL34.SA", "MSFT34.SA", "TSLA34.SA", "META34.SA", "NVDC34.SA",
    "DISB34.SA", "NFLX34.SA", "BABA34.SA", "NIKE34.SA", "PYPL34.SA", "JPMC34.SA", "COCA34.SA",
    "PEP34.SA", "MCDC34.SA", "BERK34.SA", "JNJB34.SA", "PFIZ34.SA", "WALM34.SA", "XOMP34.SA",
    "ADBE34.SA", "AVGO34.SA", "QCOM34.SA", "TXSA34.SA", "AMDZ34.SA", "ASML34.SA", "COST34.SA",
    "TMUS34.SA", "AMAT34.SA", "MUCM34.SA", "INTU34.SA", "BKNG34.SA", "CATP34.SA", "SBUB34.SA",
    "UBER34.SA", "ABNB34.SA", "SPOT34.SA", "COIN34.SA", "CRMZ34.SA", "NKEB34.SA", "VISA34.SA"
]

ativos = sorted(list(set(ativos_full)))

if st.button(f"🔍 EXECUTAR SCANNER VIP GOLD ({len(ativos)} ATIVOS)", use_container_width=True):
    resultados = []
    lista_graficos = []
    progresso = st.progress(0)
    status_text = st.empty()
    
    for i, ativo in enumerate(ativos):
        try:
            status_text.text(f"Analisando rigorosamente: {ativo}")
            
            # 1. DOWNLOAD (Mínimo 80 dias para EMA69 estabilizar)
            df_d = yf.download(ativo, period="100d", interval="1d", progress=False)
            df_w = yf.download(ativo, period="2y", interval="1wk", progress=False)

            if len(df_d) < 70 or len(df_w) < 70: continue
            if isinstance(df_d.columns, pd.MultiIndex): df_d.columns = df_d.columns.get_level_values(0)
            if isinstance(df_w.columns, pd.MultiIndex): df_w.columns = df_w.columns.get_level_values(0)

            # 2. CÁLCULO DE INDICADORES
            fechamento_d = df_d["Close"]
            fechamento_w = df_w["Close"]
            
            ema69_d = fechamento_d.ewm(span=69, adjust=False).mean()
            ema69_w = fechamento_w.ewm(span=69, adjust=False).mean()

            # Estocástico (14)
            l14, h14 = df_d["Low"].rolling(14).min(), df_d["High"].rolling(14).max()
            stoch = 100 * (fechamento_d - l14) / (h14 - l14)
            
            # DMI
            up, dw = df_d["High"].diff(), -df_d["Low"].diff()
            tr = pd.concat([df_d["High"]-df_d["Low"], abs(df_d["High"]-fechamento_d.shift()), abs(df_d["Low"]-fechamento_d.shift())], axis=1).max(axis=1)
            atr = tr.rolling(14).sum()
            pi = 100 * pd.Series(np.where((up>dw)&(up>0), up, 0), index=df_d.index).rolling(14).sum() / atr
            mi = 100 * pd.Series(np.where((dw>up)&(dw>0), dw, 0), index=df_d.index).rolling(14).sum() / atr

            # 3. VALORES ATUAIS (FILTRO RIGOROSO)
            curr_c = float(fechamento_d.iloc[-1])
            curr_ema_d = float(ema69_d.iloc[-1])
            curr_ema_w = float(ema69_w.iloc[-1])
            curr_pi = float(pi.iloc[-1])
            curr_mi = float(mi.iloc[-1])
            curr_stoch = float(stoch.iloc[-1])
            prev_high = float(df_d["High"].iloc[-2]) # Máxima do dia anterior real

            # 4. APLICAÇÃO DOS 4 FILTROS + SEMANAL
            f_semanal = curr_c > curr_ema_w
            f1_ema = curr_c > curr_ema_d
            f2_dmi = curr_pi > curr_mi
            f3_stoch = curr_stoch < 80.0
            f4_break = curr_c > prev_high

            # SÓ ENTRA SE TODOS FOREM VERDADEIROS
            if f_semanal and f1_ema and f2_dmi and f3_stoch and f4_break:
                
                # Identificação de Classe
                if "34" in ativo: classe, p_l, p_g = "BDR", 4, 6
                elif "11" in ativo: classe, p_l, p_g = "ETF", 3, 4.5
                else: classe, p_l, p_g = "Ação", 5, 7.5

                s_l, s_g = round(curr_c*(1-p_l/100),2), round(curr_c*(1+p_g/100),2)

                resultados.append({
                    "Ativo": ativo.replace(".SA",""),
                    "Classe": classe,
                    "Preço (R$)": round(curr_c, 2),
                    "EMA 69 Diária": round(curr_ema_d, 2),
                    "Stop Loss": s_l,
                    "Stop Gain": s_g,
                    "Estocástico": round(curr_stoch, 1)
                })

                # Gráfico com linhas de verificação
                fig = go.Figure(data=[go.Candlestick(x=df_d.index[-40:], open=df_d['Open'][-40:], high=df_d['High'][-40:], low=df_d['Low'][-40:], close=df_d['Close'][-40:])])
                fig.add_hline(y=s_g, line_color="green", annotation_text="GAIN")
                fig.add_hline(y=s_l, line_color="red", annotation_text="LOSS")
                fig.add_hline(y=curr_ema_d, line_color="orange", line_dash="dot", annotation_text="EMA 69")
                fig.update_layout(title=f"VALIVAÇÃO VISUAL: {ativo}", xaxis_rangeslider_visible=False, height=450, template="plotly_dark")
                lista_graficos.append(fig)

        except: continue
        progresso.progress((i + 1) / len(ativos))

    status_text.empty()
    progresso.empty()

    if resultados:
        st.success(f"Filtro Concluído. {len(resultados)} ativos aprovados com rigor técnico.")
        st.table(pd.DataFrame(resultados))
        for g in lista_graficos:
            st.plotly_chart(g, use_container_width=True)
    else:
        st.warning("Nenhum ativo passou nos filtros rigorosos hoje.")

st.divider()
