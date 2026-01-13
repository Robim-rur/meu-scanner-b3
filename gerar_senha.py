from datetime import datetime
import random
import string

PREFIXO = "CRUVI"

def gerar_senha():
    hoje = datetime.now().strftime("%Y-%m-%d")
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{PREFIXO}-{hoje}-{codigo}"

if __name__ == "__main__":
    print("\nSENHA GERADA:")
    print(gerar_senha())
