from datetime import datetime, timedelta
import sys
import pandas as pd
import yfinance as yf
from ta.momentum import StochasticOscillator
from ta.trend import ADXIndicator

# ==================================================
# CONTROLE DE ACESSO – SENHA VÁLIDA POR 30 DIAS
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
# LISTA FIXA DE ATIVOS MAIS LÍQUIDOS DA B3 (~200)
# ==================================================

ATIVOS = [
"ABEV3.SA","ALPA4.SA","AMER3.SA","ARZZ3.SA","ASAI3.SA","AZUL4.SA",
"B3SA3.SA","BBAS3.SA","BBDC3.SA","BBDC4.SA","BBSE3.SA","BPAC11.SA",
"BRAP
