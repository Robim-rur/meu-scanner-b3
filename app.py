from datetime import datetime, timedelta
import sys
import pandas as pd
import yfinance as yf
from ta.momentum import StochasticOscillator
from ta.trend import ADXIndicator

# ==================================================
# 1) CONTROLE DE ACESSO – 30 DIAS
# ==================================================

def validar_senha():
    senha = input("Digite sua senha de acesso: ").strip()

    try:
        prefixo, data_str, _ = senha.split("-")
        if prefixo != "CRUVI":
            raise ValueError

        inicio = datetime.strptime(data_str, "%Y-%m-%d")
        validade = inicio + timedelta(days=30)

        if datetime.now() > validade:
            print("❌ Licença expirada.")
            sys.exit()

        print(f"✅ Acesso liberado até {validade.strftime('%d/%m/%Y')}")
    except:
        print("❌ Senha inválida.")
        sys.exit()

# ==================================================
# 2) LISTA FIXA – ATIVOS MAIS LÍQUIDOS DA B3 (~200)
# ==================================================

ATIVOS = [
    # BANCOS / FINANCEIRO
    "ITUB4.SA","BBDC4.SA","BBAS3.SA","SANB11.SA","BPAC11.SA",

    # PETRÓLEO / MINERAÇÃO
    "PETR4.SA","PETR3.SA","VALE3.SA","PRIO3.SA","RRRP3.SA",

    # CONSUMO / VAREJO
    "ABEV3.SA","MGLU3.SA","ASAI3.SA","LREN3.SA","AMER3.SA",
    "RAIL3.SA","HYPE3.SA","PCAR3.SA",

    # INDÚSTRIA / UTILITIES
    "WEGE3.SA","EGIE3.SA","ELET3.SA","ELET6.SA","CPLE6.SA",
    "TAEE11.SA","ENGI11.SA","CMIG4.SA",

    # TECNOLOGIA / SERVIÇOS
    "TOTS3.SA","LWSA3.SA","POSI3.SA","CASH3.SA",

    # SAÚDE
    "RADL3.SA","HAPV3.SA","FLRY3.SA","QUAL3.SA",

    # SIDERURGIA
    "GGBR4.SA","USIM5.SA","CSNA3.SA",

    # TRANSPORTE / LOGÍSTICA
    "RAIL3.SA","ECOR3.SA","STBP3.SA",

    # SEGURADORAS
    "BBSE3.SA","PSSA3.SA","IRBR3.SA",

    # ETFs
    "BOVA11.SA","SMAL11.SA","IVVB11.SA","DIVO11.SA",

    # (lista reduzida aqui por limite de mensagem,
    # mas tecnicamente você pode colocar 200 sem mudar NADA no código)
]

# ==================================================
# 3) SETUP REAL – SEMANAL + DIÁRIO
# ==================================================

def analisar_ativo(ticker):
    df = yf.download(ticker, period="1y", interval="1d", progress=False)

    if df.empty or len(df) < 100:
        return None

    # ---------- ESTOCÁSTICO DIÁRIO ----------
    estoc_d = StochasticOscillator(
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        window=14,
        smooth_window=3
    )

    df["k_d"] = estoc_d.stoch()
    df["d_d"] = estoc_d.stoch_signal()

    # ---------- ADX ----------
    adx = ADXIndicator(df["High"], df["Low"], df["Close"], window=14)
    df["adx"] = adx.adx()

    # ---------- SEMANAL ----------
    semanal = df.resample("W").last()

    estoc_s = StochasticOscillator(
        high=semanal["High"],
        low=semanal["Low"],
        close=semanal["Close"],
        window=14,
        smooth_window=3
    )

    semanal["k_s"] = estoc_s.stoch()
    semanal["d_s"] = estoc_s.stoch_signal()

    # ---------- CONDIÇÕES ----------
    if not (
        semanal["k_s"].iloc[-1] > semanal["d_s"].iloc[-1] and
        df["k_d"].iloc[-1] > df["d_d"].iloc[-1] and
        df["adx"].iloc[-1] > 15
    ):
        return None

    preco = round(df["Close"].iloc[-1], 2)

    # ---------- CLASSE / RISCO ----------
    if ticker.endswith("11.SA"):
        stop = 0.03
        gain = 0.05
    else:
        stop = 0.05
        gain = 0.08

    # ---------- RELAÇÃO R/R ----------
    if gain / stop < 1.5:
        return None

    return {
        "Ativo": ticker.replace(".SA", ""),
        "Entrada": preco,
        "Stop (%)": stop * 100,
        "Gain (%)": gain * 100
    }

# ==================================================
# 4) EXECUÇÃO
# ==================================================

def executar_scanner():
    resultados = []

    for ativo in ATIVOS:
        try:
            r = analisar_ativo(ativo)
            if r:
                resultados.append(r)
        except:
            pass

    return pd.DataFrame(resultados)

if __name__ == "__main__":
    validar_senha()
    tabela = executar_scanner()
    print("\nATIVOS COM ENTRADA NO DIA:\n")
    print(tabela if not tabela.empty else "Nenhum ativo encontrado.")
