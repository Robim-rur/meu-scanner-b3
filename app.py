import pandas as pd
import numpy as np
import os
import sys
import time
import datetime

# =============================================================================
# CONFIGURAÇÕES DE AMBIENTE E INTERFACE
# =============================================================================
def configurar_sistema():
    """Define como os dados serão exibidos no console para evitar cortes"""
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.width', 1000)
    pd.set_option('display.expand_frame_repr', False)
    print(f"[{datetime.datetime.now()}] Sistema inicializado com sucesso.")

# =============================================================================
# BLOCO DE FUNÇÕES DE PROCESSAMENTO (LÓGICA ORIGINAL)
# =============================================================================
def validar_colunas(df):
    """Verifica a integridade das colunas do arquivo original"""
    colunas_esperadas = ['ID', 'DATA', 'PRODUTO', 'VALOR', 'CATEGORIA', 'VENDEDOR']
    colunas_atuais = [c.upper() for c in df.columns]
    df.columns = colunas_atuais
    
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = np.nan
            print(f"Aviso: Coluna {col} não encontrada. Criando coluna vazia.")
    return df

def aplicar_tratamento_financeiro(df):
    """Aplica as regras de cálculo e impostos que estavam no código inicial"""
    print("Iniciando tratamento financeiro...")
    
    # Garantir que VALOR seja numérico
    df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)
    
    # Cálculo de impostos e margens (Lógica do Código 1)
    df['IMPOSTO_TAXA'] = 0.05
    df['VALOR_IMPOSTO'] = df['VALOR'] * df['IMPOSTO_TAXA']
    df['VALOR_LIQUIDO'] = df['VALOR'] - df['VALOR_IMPOSTO']
    
    # Categorização de performance
    df['PERFORMANCE'] = 'NORMAL'
    df.loc[df['VALOR'] > 1000, 'PERFORMANCE'] = 'ALTO IMPACTO'
    df.loc[df['VALOR'] < 100, 'PERFORMANCE'] = 'BAIXO IMPACTO'
    
    return df

def realizar_agrupamentos(df):
    """Gera os resumos que eram exibidos no final do primeiro código"""
    print("Gerando resumos consolidados...")
    resumo_vendas = df.groupby('PERFORMANCE').agg({
        'VALOR': 'sum',
        'VALOR_LIQUIDO': 'mean',
        'ID': 'count'
    }).rename(columns={'ID': 'QTD_VENDAS'})
    
    return resumo_vendas

# =============================================================================
# EXIBIÇÃO E SAÍDA DE DADOS
# =============================================================================
def mostrar_dashboard(df, resumo):
    """Função de impressão longa para garantir que nada fique em branco"""
    print("\n" + "="*100)
    print(f"{'DASHBOARD DE VENDAS - RELATÓRIO COMPLETO':^100}")
    print("="*100)
    
    print("\n>>> VISUALIZAÇÃO DOS REGISTROS (HEAD):")
    print(df.head(30))
    
    print("\n" + "-"*100)
    print(">>> RESUMO POR PERFORMANCE:")
    print(resumo)
    print("-"*100)
    
    print(f"\nProcessamento concluído em: {datetime.datetime.now()}")
    print("="*100)

# =============================================================================
# FLUXO PRINCIPAL (MAIN)
# =============================================================================
def executar():
    configurar_sistema()
    
    arquivo = "dados_vendas.csv"
    
    # Verificação de existência para evitar travamento em branco
    if not os.path.exists(arquivo):
        print(f"\nCRITICAL ERROR: O arquivo '{arquivo}' não foi encontrado.")
        print(f"Diretório atual: {os.getcwd()}")
        return

    try:
        # Carregamento com tratamento de encoding original
        print(f"Lendo arquivo: {arquivo}...")
        try:
            df_bruto = pd.read_csv(arquivo, sep=None, engine='python', encoding='utf-8')
        except UnicodeDecodeError:
            df_bruto = pd.read_csv(arquivo, sep=None, engine='python', encoding='latin1')

        # Sequência de funções
        df_validado = validar_colunas(df_bruto)
        df_processado = aplicar_tratamento_financeiro(df_validado)
        resumo_final = realizar_agrupamentos(df_processado)
        
        # Saída Final
        mostrar_dashboard(df_processado, resumo_final)

    except Exception as e:
        print(f"\n[ERRO NO PROCESSAMENTO]: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    executar()
    print("\n" + "_"*50)
    input("Pressione ENTER para finalizar o script...")
