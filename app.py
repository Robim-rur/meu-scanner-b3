import pandas as pd
import numpy as np
import os
import sys
import datetime

def configurar_display():
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.width', 1000)

def listar_arquivos_locais():
    """Auxilia a encontrar o nome correto do arquivo se ele falhar"""
    print("\n[DIAGNÓSTICO] Arquivos encontrados na pasta atual:")
    arquivos = os.listdir('.')
    for arq in arquivos:
        print(f"  - {arq}")
    print("-" * 30)

def carregar_dados_seguro(nome_arquivo):
    """Tenta carregar o arquivo e informa o erro exato se falhar"""
    if not os.path.exists(nome_arquivo):
        print(f"\n[!] ERRO: O arquivo '{nome_arquivo}' NÃO foi encontrado.")
        listar_arquivos_locais()
        return None
    
    try:
        # Tenta ler tratando possíveis problemas de separador e acentuação
        df = pd.read_csv(nome_arquivo, sep=None, engine='python', encoding='utf-8')
        return df
    except UnicodeDecodeError:
        return pd.read_csv(nome_arquivo, sep=None, engine='python', encoding='latin1')
    except Exception as e:
        print(f"[!] Erro ao ler o conteúdo do arquivo: {e}")
        return None

def processar_dados(df):
    """Lógica restaurada do código original"""
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Garantindo que a coluna VALOR existe para os cálculos
    if 'VALOR' in df.columns:
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)
        df['STATUS'] = np.where(df['VALOR'] > 0, 'ATIVO', 'INATIVO')
        df['IMPOSTO'] = df['VALOR'] * 0.15
    
    df['DATA_PROCESSAMENTO'] = datetime.datetime.now().strftime("%H:%M:%S")
    return df

def principal():
    configurar_display()
    
    # IMPORTANTE: Verifique se o nome do seu arquivo é exatamente este:
    arquivo_alvo = "dados_vendas.csv" 
    
    print(f"--- Iniciando Processamento ({datetime.datetime.now().strftime('%H:%M:%S')}) ---")
    
    df_bruto = carregar_dados_seguro(arquivo_alvo)
    
    if df_bruto is not None:
        df_final = processar_dados(df_bruto)
        
        print("\n=== RESULTADOS ENCONTRADOS ===")
        print(df_final.head(20))
        
        print("\n=== RESUMO FINANCEIRO ===")
        if 'VALOR' in df_final.columns:
            print(df_final.groupby('STATUS')['VALOR'].sum())
    else:
        print("\n[Interrompido] O sistema não encontrou dados para processar.")

if __name__ == "__main__":
    principal()
    print("\n" + "="*40)
    input("Script finalizado. Pressione ENTER para sair...")
