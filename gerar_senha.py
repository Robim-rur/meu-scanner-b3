from datetime import datetime
import random
import string

def gerar_senha():
    hoje = datetime.now().strftime("%Y-%m-%d")
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"CRUVI-{hoje}-{codigo}"

if __name__ == "__main__":
    print("Senha gerada:")
    print(gerar_senha())
