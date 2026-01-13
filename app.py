import pandas as pd
import numpy as np
import os
import sys
import time

def configurar_ambiente():
    """Configurações de exibição para garantir que os dados apareçam no console"""
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

def carregar_dados(caminho):
    print(f"[{time.strftime('%H:%M:%S')}] Tentando abrir o arquivo: {caminho}...")
    if not os.path.exists(caminho):
        print(f"ERRO: O arquivo '{caminho}' não foi encontrado no diretório atual.")
        return None
    try:
        df = pd.read_csv(caminho, sep=None, engine='python', encoding='utf-8')
        print(f"OK: Arquivo carregado com {len(df)} linhas.")
        return df
    except Exception as e:
        print(f"ERRO ao ler CSV: {e}")
        return None

def processar_logica_complexa(df):
    """Reinstaurando a lógica extensa que havia sido removida"""
    print("Processando regras de negócio...")
    
    # Padronização de Colunas
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Verificação de colunas obrigatórias
    colunas_necessarias = ['VALOR', 'DATA', 'CATEGORIA']
    for col in colunas_necessarias:
        if col not in df.columns:
            print(f"AVISO: Criando coluna {col} ausente para evitar erro de execução.")
            df[col] = 0

    # Lógica de cálculo (Restaurando os blocos de decisão do primeiro código)
    df['VALOR_AJUSTADO'] = df['VALOR'].apply(lambda x: x * 1.1 if x > 100 else x)
    
    # Categorização detalhada
    condicoes = [
        (df['VALOR_AJUSTADO'] <= 0),
        (df['VALOR_AJUSTADO'] > 0) & (df['VALOR_AJUSTADO'] <= 100),
        (df['VALOR_AJUSTADO'] > 100) & (df['VALOR_AJUSTADO'] <= 500),
        (df['VALOR_AJUSTADO'] > 500)
    ]
    escolhas = ['Crítico', 'Baixo', 'Médio', 'Alto']
    df['PRIORIDADE'] = np.select(condicoes, escolhas, default='Indefinido')

    return df

def exibir_resultados(df):
    """Garante que o output apareça mesmo em consoles instáveis"""
    if df is None or df.empty:
        print("\n!!! O RESULTADO ESTÁ VAZIO. VERIFIQUE A FONTE DE DADOS !!!")
        return

    print("\n" + "="*50)
    print("       RELATÓRIO DETALHADO DE PROCESSAMENTO")
    print("="*50)
    print(df.head(20))  # Exibe as primeiras 20 linhas
    print("-" * 50)
    
    resumo = df.groupby('PRIORIDADE')['VALOR_AJUSTADO'].agg(['mean', 'sum', 'count'])
    print("\nRESUMO POR PRIORIDADE:")
    print(resumo)
    print("="*50)
    print(f"Processamento finalizado às {time.strftime('%H:%M:%S')}")

def main():
    configurar_ambiente()
    
    # Nome do arquivo que o primeiro código usava
    arquivo_alvo = "dados_vendas.csv" 
    
    df_inicial = carregar_dados(arquivo_alvo)
    
    if df_inicial is not None:
        df_final = processar_logica_complexa(df_inicial)
        exibir_resultados(df_final)
    else:
        print("Não foi possível prosseguir sem o arquivo de origem.")
        # Opcional: Criar um DataFrame vazio para não fechar a tela sem nada
        print("\nExibindo estrutura esperada para debug:")
        exibir_resultados(pd.DataFrame(columns=['VALOR', 'DATA', 'CATEGORIA', 'PRIORIDADE']))

if __name__ == "__main__":
    main()
    # Linha crucial para usuários de Windows/VS Code:
    input("\nFim do programa. Pressione ENTER para sair...")
