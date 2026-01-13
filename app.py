import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime

# =============================================================================
# 1. CONFIGURAÇÕES DE INTERFACE STREAMLIT
# =============================================================================
st.set_page_config(page_title="Relatório de Vendas", layout="wide")

def configurar_estilo():
    """Define o título e as cores da interface"""
    st.title("📊 Painel de Controle de Vendas")
    st.markdown("---")

# =============================================================================
# 2. CARREGAMENTO DE DADOS (COM TRATAMENTO DE ERRO)
# =============================================================================
def carregar_dados():
    arquivo = "dados_vendas.csv"
    
    if os.path.exists(arquivo):
        try:
            # Tenta carregar o arquivo real do GitHub
            df = pd.read_csv(arquivo, sep=None, engine='python', encoding='latin1')
            st.success(f"Dados reais carregados: {arquivo}")
            return df
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
            return None
    else:
        # Caso o arquivo ainda não tenha sido enviado ao GitHub
        st.warning(f"Aguardando arquivo '{arquivo}' no GitHub...")
        st.info("Utilizando base de demonstração temporária.")
        
        dados_demo = {
            'ID': range(101, 111),
            'DATA': [datetime.date.today()] * 10,
            'VALOR': [1500.0, 50.0, 800.0, 1200.0, 30.0, 550.0, 2000.0, 90.0, 600.0, 150.0],
            'PRODUTO': [f'Produto {i}' for i in range(1, 11)],
            'VENDEDOR': ['Equipe A'] * 10
        }
        return pd.DataFrame(dados_demo)

# =============================================================================
# 3. PROCESSAMENTO DE REGRAS DE NEGÓCIO
# =============================================================================
def processar_vendas(df):
    """Aplica a lógica de cálculo e categorização"""
    # Padroniza nomes de colunas
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    if 'VALOR' in df.columns:
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)
        
        # Criação de métricas (Original do projeto)
        df['IMPOSTO'] = df['VALOR'] * 0.15
        df['TOTAL_LIQUIDO'] = df['VALOR'] - df['IMPOSTO']
        
        # Categorização por faixa de preço
        condicoes = [
            (df['VALOR'] >= 1000),
            (df['VALOR'] >= 500) & (df['VALOR'] < 1000),
            (df['VALOR'] < 500)
        ]
        labels = ['ALTA', 'MÉDIA', 'BAIXA']
        df['PERFORMANCE'] = np.select(condicoes, labels, default='N/A')
        
    return df

# =============================================================================
# 4. EXIBIÇÃO DOS RESULTADOS NA TELA
# =============================================================================
def exibir_interface(df):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Tabela de Registros")
        st.dataframe(df, use_container_width=True)
        
    with col2:
        st.subheader("Resumo por Categoria")
        resumo = df.groupby('PERFORMANCE').agg({
            'VALOR': 'sum',
            'ID': 'count'
        }).rename(columns={'ID': 'QTD'})
        st.write(resumo)
        
    # Rodapé com timestamp
    st.markdown("---")
    st.caption(f"Sistema operacional | Atualizado em: {datetime.datetime.now()}")

# =============================================================================
# 5. EXECUÇÃO PRINCIPAL
# =============================================================================
def main():
    configurar_estilo()
    
    dados_brutos = carregar_dados()
    
    if dados_brutos is not None:
        dados_processados = processar_vendas(dados_brutos)
        exibir_interface(dados_processados)
        
        # Opção de exportação
        csv_data = dados_processados.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Relatório CSV", csv_data, "vendas_processadas.csv")

if __name__ == "__main__":
    main()

# Fim do código restaurado para Streamlit.
