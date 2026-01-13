import pandas as pd
import numpy as np

def processar_dados(caminho_arquivo):
    try:
        # Carregamento otimizado
        df = pd.read_csv(caminho_arquivo)
        
        # Limpeza de colunas desnecessárias que inflavam o código anterior
        df.columns = df.columns.str.strip().str.lower()
        
        # Lógica central: Filtro e Cálculo
        # Em vez de 50 linhas de IFs, usamos mapeamento
        df['status'] = np.where(df['valor'] > 0, 'Ativo', 'Inativo')
        
        # Agrupamento simplificado
        resultado = df.groupby('status').agg({
            'valor': 'sum',
            'id': 'count'
        }).reset_index()
        
        print("Processamento concluído com sucesso.")
        return resultado

    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Execução
if __name__ == "__main__":
    arquivo = "dados_vendas.csv"  # Altere para o seu arquivo
    final_df = processar_dados(arquivo)
    if final_df is not None:
        print(final_df)
