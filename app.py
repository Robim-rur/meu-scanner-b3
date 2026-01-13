import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# ===============================
# CONFIGURAÇÕES
# ===============================
QTDE_ATIVOS = 200
RR_MINIMO = 1.5

STOP_LOSS = {
    "ACAO": 0.05,
    "BDR": 0.04,
    "ETF": 0.03
}

STOP_GAIN = {
    "ACAO": 0.08,
    "BDR": 0.06,
    "ETF": 0.05
}

# ===============================
# LISTA BASE DE ATIVOS B3
# (você pode ampliar depois)
# ===============================
ATIVOS_B3 = [
    "PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA","ABEV3.SA",
    "WEGE3.SA","PRIO3.SA","RADL3.SA","RENT3.SA","SUZB3.SA","JBSS3.SA",
    "BOVA11.SA","IVVB11.SA","SMAL11.SA"
]

# ===============================
# FUNÇÕES AUXILIARES
# ===============================
def classificar_ativo(ticker):
    if ticker.endswith("11.SA"):
        return "ETF"
    elif ticker.endswith("34.SA"):
        return "BDR"
    else:
        return "ACAO"

def calcular_liquidez(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        df["Financeiro"] = df["Close"] * df["Volume"]
        return df["Financeiro"].mean()
    except:
        return 0

def top_ativos_liquidos(lista, qtd):
    liquidez = []
    for ativo in lista:
        liquidez.append((ativo, calcular_liquidez(ativo)))
    liquidez.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in liquidez[:qtd]]

# ===============================
# TENDÊNCIA PRIMÁRIA
# ===============================
def tendencia_alta_semanal(df):
    df["MM200"] = ta.sma(df["Close"], length=200)
    return df["Close"].iloc[-1] > df["MM200"].iloc[-1]

# ===============================
# FILTRO SEMANAL
# ===============================
def filtro_semanal(ticker):
    df = yf.download(ticker, period="2y", interval="1wk", progress=False)
    if len(df) < 50:
        return False

    stoch = ta.stoch(df["High"], df["Low"], df["Close"])
    df = pd.concat([df, stoch], axis=1)

    return (
        df["STOCHk_14_3_3"].iloc[-1] > df["STOCHd_14_3_3"].iloc[-1]
        and tendencia_alta_semanal(df)
    )

# ===============================
# FILTRO DIÁRIO
# ===============================
def filtro_diario(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    if len(df) < 50:
        return None

    stoch = ta.stoch(df["High"], df["Low"], df["Close"])
    adx = ta.adx(df["High"], df["Low"], df["Close"])

    df = pd.concat([df, stoch, adx], axis=1)

    if (
        df["STOCHk_14_3_3"].iloc[-1] > df["STOCHd_14_3_3"].iloc[-1]
        and df["ADX_14"].iloc[-1] > 15
    ):
        return df

    return None

# ===============================
# CÁLCULO DO TRADE
# ===============================
def calcular_trade(df, ticker):
    classe = classificar_ativo(ticker)
    entrada = df["Close"].iloc[-1]

    stop = entrada * (1 - STOP_LOSS[classe])
    gain = entrada * (1 + STOP_GAIN[classe])

    risco = entrada - stop
    retorno = gain - entrada
    rr = retorno / risco

    if rr < RR_MINIMO:
        return None

    return {
        "Ativo": ticker.replace(".SA",""),
        "Classe": classe,
        "Entrada": round(entrada,2),
        "Stop": round(stop,2),
        "Gain": round(gain,2),
        "Loss %": -STOP_LOSS[classe]*100,
        "Gain %": STOP_GAIN[classe]*100,
        "R/R": round(rr,2)
    }

# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================
def executar_scanner():
    ativos = top_ativos_liquidos(ATIVOS_B3, QTDE_ATIVOS)
    resultados = []

    for ativo in ativos:
        try:
            if filtro_semanal(ativo):
                df_diario = filtro_diario(ativo)
                if df_diario is not None:
                    trade = calcular_trade(df_diario, ativo)
                    if trade:
                        resultados.append(trade)
        except:
            continue

    df_final = pd.DataFrame(resultados)
    df_final["Data"] = datetime.now().strftime("%Y-%m-%d")
    return df_final

# ===============================
# RODAR
# ===============================
if __name__ == "__main__":
    tabela = executar_scanner()
    print("\nATIVOS COM ENTRADA NO DIA:\n")
    print(tabela)
