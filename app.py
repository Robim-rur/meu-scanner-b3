import pandas as pd
import numpy as np
import sys

def inicializar_sistema():
    try:
        # 1. Simulação/Carregamento de Dados (Ajuste para seu arquivo se necessário)
        # Se você estiver usando um arquivo real, use: df = pd.read_csv('seu_arquivo.csv')
        data = {
            'id': range(1, 6),
            'valor': [100, -50, 200, 0, 300],
            'categoria': ['A', 'B', 'A', 'C', 'B']
        }
        df = pd.DataFrame(data)

        # 2. Processamento (Onde o erro de "tela branca" costuma ocorrer)
        if df.empty:
            print("Atenção: O DataFrame está vazio.")
            return

        # Normalização de colunas
        df.columns = df.columns.str.strip().str.lower()

        # Lógica de Status
        df['status'] = np.where(df['valor'] > 0, 'Ativo', 'Inativo')

        # 3. GARANTINDO A EXIBIÇÃO (Para não ficar branco)
        print("-" * 30)
        print("DADOS PROCESSADOS:")
        print(df) 
        print("-" * 30)
        
        # Agrupamento para resumo
        resumo = df.groupby('status').agg({'valor': 'sum', 'id': 'count'}).reset_index()
        
        print("RESUMO FINAL:")
        print(resumo)
        return resumo

    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")

if __name__ == "__main__":
    # Força a saída no console para evitar que o buffer segure a informação
    resultado = inicializar_sistema()
    sys.stdout.flush()
