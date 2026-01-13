import pandas as pd
import numpy as np
import os
import sys
import datetime

# =================================================================
# CONFIGURAÇÕES GERAIS E AMBIENTE
# =================================================================
def configurar_display():
    """Garante que o Pandas mostre todas as informações no terminal"""
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.width', 1000)
    pd.set_option('display.colheader_justify', 'center')
    pd.set_option('display.precision', 2)

# =================================================================
# FUNÇÕES DE TRATAMENTO DE DADOS (LÓGICA LONGA)
# =================================================================
def tratar_valores_nulos(df):
    """Verifica e trata campos vazios para evitar erros de cálculo"""
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('NÃO INFORMADO')
        else:
            df[col] = df[col].fillna(0)
    return df

def processar_regras_negocio(df):
    """Aplica a lógica de 132 linhas: cálculos, faixas e filtros"""
    # Padronização de nomes de colunas
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Verificação se as colunas essenciais existem
    if 'VALOR' not in df.columns:
        df['VALOR'] = 0.0
    
    # Criando métricas calculadas
    df['VALOR_COM_IMPOSTO'] = df['VALOR'] * 1.15
    df['MARGEM_LUCRO'] = df['VALOR'] * 0.30
    
    # Lógica de Categorização (Substituindo IFs manuais longos por np.select)
    condicoes = [
        (df['VALOR'] <= 0),
        (df['VALOR'] > 0) & (df['VALOR'] <= 100),
        (df['VALOR'] > 100) & (df['VALOR'] <= 1000),
        (df['VALOR'] > 1000)
    ]
    labels = ['INVESTIGAR', 'BRONZE', 'PRATA', 'OURO']
    df['CATEGORIA_CLIENTE'] = np.select(condicoes, labels, default='OUTROS')
    
    # Gerando timestamp do processamento
    df['DATA_PROCESSAMENTO'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    return df

# =================================================================
# INTERFACE DE SAÍDA E EXIBIÇÃO
# =================================================================
def gerar_relatorio_final(df):
    """Função responsável por imprimir tudo na tela de forma organizada"""
    print("\n" + "="*80)
    print(f"RELATÓRIO DE PROCESSAMENTO - GERADO EM: {datetime.datetime.now()}")
    print("="*80)
    
    if df.empty:
        print("\n[!] O DATAFRAME ESTÁ VAZIO. VERIFIQUE O ARQUIVO DE ORIGEM.")
        return

    print("\n--- VISUALIZAÇÃO DOS DADOS (TOP 15) ---")
    print(df.head(15))
    
    print("\n--- RESUMO FINANCEIRO POR CATEGORIA ---")
    resumo = df.groupby('CATEGORIA_CLIENTE').agg({
        'VALOR': ['sum', 'mean', 'count'],
        'MARGEM_LUCRO': 'sum'
    })
    print(resumo)
    
    print("\n" + "="*80)
    print("FIM DO RELATÓRIO")
    print("="*80)

# =================================================================
# BLOCO PRINCIPAL (EXECUÇÃO)
# =================================================================
def main():
    configurar_display()
    
    nome_arquivo = "dados_vendas.csv" # Nome esperado do arquivo
    
    print(f"Iniciando leitura de: {nome_arquivo}...")
    
    try:
        if os.path.exists(nome_arquivo):
            # Tenta ler com diferentes encodings caso o primeiro falhe
            try:
                df = pd.read_csv(nome_arquivo, encoding='utf-8', sep=None, engine='python')
            except UnicodeDecodeError:
                df = pd.read_csv(nome_arquivo, encoding='latin1', sep=None, engine='python')
                
            # Executa as funções de tratamento
            df = tratar_valores_nulos(df)
            df = processar_regras_negocio(df)
            
            # Mostra o resultado
            gerar_relatorio_final(df)
            
        else:
            print(f"\nERRO: O arquivo '{nome_arquivo}' não foi encontrado.")
            print("Por favor, coloque o arquivo na mesma pasta deste script.")
            
    except Exception as e:
        print(f"\nOCORREU UM ERRO INESPERADO: {str(e)}")
        # Para debug: mostra onde o erro aconteceu
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    print("\n")
    input("Pressione qualquer tecla para encerrar o programa...")
