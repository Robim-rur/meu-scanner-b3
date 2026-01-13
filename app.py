from datetime import datetime, timedelta
import sys
import pandas as pd
import yfinance as yf
import numpy as np
from ta.momentum import StochasticOscillator
from ta.trend import ADXIndicator

# =====================================
# VALIDAÇÃO DE SENHA (30 DIAS)
# =====================================

def validar_senha():
    senha = input("Digite sua senha de acesso: ").strip()

    try:
        prefixo, data_str, _ = senha.split("-")

        if prefixo != "CRUVI":
            raise ValueError

        data_inicio = datetime.strptime(data_str, "%Y-%m-%d")
        validade = data_inicio + timedelta(days=30)

        if datetime.now() > validade:
            print("Licença expirada.")
            sys.exit()

        print(f"Acesso liberado até {validade.strftime('%d/%m/%Y')}")

    except:
        print("Senha inválida.")
        sys.exit()

# =====================================
# LISTA DE ATIVOS (EXEMPLO – 200 MAIORES)
# =====================================

ATIVOS = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA",
    "ABEV3.SA", "BBAS3.SA", "WEGE3.SA"
]

# =====================================
# SCANNER COM SEU SETUP
# =====================================

def analisar_ativo(ticker):
    df = yf.download(ticker, period="1y", interval="1d", progress=False)

    if len(df) < 200:
        return None

    # --------- ESTOCÁSTICO DIÁRIO ---------
    estoc_d = StochasticOscillator(
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        window=14,
        smooth_window=3
    )

    df["k_d"] = estoc_d.stoch()
    df["d_d"] = estoc_d.stoch_signal()

    # --------- ADX ---------
    adx = ADXIndicator(df["High"], df["Low"], df["Close"], window=14)
    df["adx"] = adx.adx()

    # --------- ESTOCÁSTICO SEMANAL ---------
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

    # --------- CONDIÇÕES DO SETUP ---------
    if not (
        semanal["k_s"].iloc[-1] > semanal["d_s"].iloc[-1] and
        df["k_d"].iloc[-1] > df["d_d"].iloc[-1] and
        df["adx"].iloc[-1] > 15
    ):
        return None

    preco = df["Close"].iloc[-1]

    # --------- CLASSIFICAÇÃO SIMPLES ---------
    if "ETF" in ticker:
        stop = 0.03
        gain = 0.05
    elif "BDR" in ticker:
        stop = 0.04
        gain = 0.06
    else:
        stop = 0.05
        gain = 0.08

    return {
        "Ativo": ticker.replace(".SA", ""),
        "Entrada": round(preco, 2),
        "Stop (%)": stop * 100,
        "Gain (%)": gain * 100
    }

# =====================================
# EXECUÇÃO
# =====================================

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
