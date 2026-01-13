from datetime import datetime
import random
import string

def gerar():
    hoje = datetime.now().strftime("%Y-%m-%d")
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    print(f"CRUVI-{hoje}-{codigo}")

if __name__ == "__main__":
    gerar()
