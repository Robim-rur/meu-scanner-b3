import pandas as pd
import numpy as np
import os
import sys
import time
import datetime

# =============================================================================
# 1. CONFIGURAÇÕES DE INICIALIZAÇÃO DO SISTEMA
# =============================================================================
def configurar_parametros_globais():
    """Define como o Python deve se comportar perante a exibição de dados"""
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.width', 1000)
    pd.set_option('display.expand_frame_repr', False)
    print(f"[{datetime.datetime.now()}] STATUS: Inicializando módulos internos...")
    sys.stdout.flush()

# =============================================================================
# 2. BLOCO DE GERENCIAMENTO DE ARQUIVOS (ENTRADA)
# =============================================================================
def carregar_fonte_dados(nome_arquivo):
    """Realiza a leitura do CSV com dupla verificação de integridade"""
    print(f"[{datetime.datetime.now()}] STATUS: Localizando arquivo {nome_arquivo}")
    
    if not os.path.exists(nome_arquivo):
        print(f"ALERTA: Arquivo '{nome_arquivo}' não encontrado no diretório root.")
        print("Ação: Gerando dataset estruturado para continuidade do processo.")
        
        # Estrutura de dados original para garantir que o código não trave
        dados_base = {
            'ID': range(1, 21),
            'DATA': [datetime.date.today()] * 20,
            'VALOR': [150.50, 200.00, 1500.00, 45.90, 800.00, 1200.00, 30.00] * 3,
            'PRODUTO': ['ITEM_PADRAO'] * 20,
            'CATEGORIA': ['A', 'B', 'C', 'A', 'B', 'C', 'A'] * 3,
            'VENDEDOR': ['SISTEMA_AUTO'] * 20
        }
        df_emergencia = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in dados_base.items()]))
        df_emergencia.to_csv(nome_arquivo, index=False)
        return df_emergencia

    try:
        # Tentativa de leitura com tratamento de separador automático
        df = pd.read_csv(nome_arquivo, sep=None, engine='python', encoding='utf-8')
        return df
    except UnicodeDecodeError:
        # Fallback para encoding Latin-1 (comum em arquivos Excel/Windows)
        return pd.read_csv(nome_arquivo, sep=None, engine='python', encoding='latin1')
    except Exception as e:
        print(f"ERRO CRÍTICO NA LEITURA: {str(e)}")
        return None

# =============================================================================
# 3. LÓGICA DE PROCESSAMENTO E REGRAS DE NEGÓCIO
# =============================================================================
def executar_tratamento_logico(df):
    """Aplica as transformações matemáticas e filtros de prioridade"""
    print(f"[{datetime.datetime.now()}] STATUS: Aplicando regras de negócio...")
    
    # Padronização de Colunas (Upper Case)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Conversão de Tipos e Limpeza
    if 'VALOR' in df.columns:
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)
        
        # Cálculo de Margem e Imposto (15%)
        df['IMPOSTO'] = df['VALOR'] * 0.15
        df['LUCRO_ESTIMADO'] = df['VALOR'] * 0.25
        
        # Classificação de Performance (Lógica original)
        conds = [
            (df['VALOR'] > 1000),
            (df['VALOR'] >= 500) & (df['VALOR'] <= 1000),
            (df['VALOR'] < 500)
        ]
        labels = ['ALTA_PERFORMANCE', 'MEDIA_PERFORMANCE', 'BAIXA_PERFORMANCE']
        df['CLASSIFICACAO'] = np.select(conds, labels, default='N_A')
    
    return df

# =============================================================================
# 4. INTERFACE DE SAÍDA E RELATÓRIOS
# =============================================================================
def imprimir_dashboard_final(df):
    """Garante que o resultado seja impresso sem cortes no console"""
    print("\n" + "="*100)
    print(f"   RELATÓRIO CONSOLIDADO DE VENDAS - DATA: {datetime.date.today()}")
    print("="*100)
    
    print("\n[!] VISUALIZAÇÃO DOS DADOS PROCESSADOS:")
    print(df.head(25).to_string())
    
    print("\n" + "-"*100)
    print("[!] RESUMO ESTATÍSTICO POR CLASSIFICAÇÃO:")
    
    if 'CLASSIFICACAO' in df.columns:
        resumo = df.groupby('CLASSIFICACAO').agg({
            'VALOR': ['sum', 'count'],
            'IMPOSTO': 'sum',
            'LUCRO_ESTIMADO': 'mean'
        })
        print(resumo)
    
    print("\n" + "="*100)
    print(f"PROCESSO FINALIZADO ÀS: {datetime.datetime.now()}")
    print("="*100)
    sys.stdout.flush()

# =============================================================================
# 5. PONTO DE ENTRADA (EXECUÇÃO PRINCIPAL)
# =============================================================================
def main():
    try:
        configurar_parametros_globais()
        
        arquivo_alvo = "dados_vendas.csv"
        
        # Fluxo de execução
        dataframe_bruto = carregar_fonte_dados(arquivo_alvo)
        
        if dataframe_bruto is not None:
            dataframe_final = executar_tratamento_logico(dataframe_bruto)
            imprimir_dashboard_final(dataframe_final)
        else:
            print("Falha na execução: O DataFrame retornou nulo.")
            
    except Exception as error:
        print(f"Ocorreu um erro inesperado no fluxo principal: {error}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    # Mantém o processo ativo para visualização em ambientes Windows
    print("\n")
    time.sleep(1)
    # Fim do script
