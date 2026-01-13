import pandas as pd
import numpy as np
import os
import sys
import datetime

# =============================================================================
# CONFIGURAÇÕES DE EXIBIÇÃO
# =============================================================================
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

def configurar_ambiente():
    print(f"Processamento iniciado em: {datetime.datetime.now()}")
    print("-" * 50)

# =============================================================================
# FUNÇÕES DE TRATAMENTO DE DADOS
# =============================================================================
def tratar_dados(df):
    # Padronização de colunas para maiúsculo
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Verificação de colunas obrigatórias
    colunas_obrigatorias = ['ID', 'VALOR', 'PRODUTO', 'CATEGORIA']
    for col in colunas_obrigatorias:
        if col not in df.columns:
            df[col] = 0
            
    # Conversão do campo VALOR para numérico
    df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)
    
    # Cálculos de impostos e valores líquidos
    df['IMPOSTO'] = df['VALOR'] * 0.10
    df['LIQUIDO'] = df['VALOR'] - df['IMPOSTO']
    
    return df

def gerar_categorias(df):
    # Lógica de classificação baseada nos valores
    condicoes = [
        (df['VALOR'] >= 1000),
        (df['VALOR'] >= 500) & (df['VALOR'] < 1000),
        (df['VALOR'] < 500)
    ]
    valores = ['PREMIUM', 'PADRÃO', 'ECONÔMICO']
    df['STATUS_VENDA'] = np.select(condicoes, valores, default='N/A')
    return df

# =============================================================================
# RELATÓRIOS E SAÍDA
# =============================================================================
def imprimir_relatorio(df):
    print("\n>>> LISTAGEM DE VENDAS PROCESSADAS:")
    print(df.head(20))
    
    print("\n>>> RESUMO POR STATUS DE VENDA:")
    resumo = df.groupby('STATUS_VENDA').agg({
        'VALOR': 'sum',
        'LIQUIDO': 'mean',
        'ID': 'count'
    })
    print(resumo)

# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================
def main():
    configurar_ambiente()
    
    arquivo = 'dados_vendas.csv'
    
    if os.path.exists(arquivo):
        try:
            # Tenta ler o arquivo original
            df = pd.read_csv(arquivo, sep=',', encoding='utf-8')
        except:
            # Fallback para outro encoding se necessário
            df = pd.read_csv(arquivo, sep=';', encoding='latin1')
            
        # Execução das funções na ordem original
        df_tratado = tratar_dados(df)
        df_final = gerar_categorias(df_tratado)
        
        imprimir_relatorio(df_final)
        
    else:
        print(f"Erro: O arquivo {arquivo} não foi encontrado no diretório.")
        print("Certifique-se de que o arquivo CSV está na mesma pasta do script.")

if __name__ == "__main__":
    main()
    print("\n" + "="*50)
    input("Pressione qualquer tecla para sair...")
