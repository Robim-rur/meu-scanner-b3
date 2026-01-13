import streamlit as st
import pandas as pd
import numpy as np
import datetime

# =============================================================================
# 1. CONFIGURAÇÕES DE INTERFACE (LINHAS 1-20)
# =============================================================================
st.set_page_config(page_title="Relatório de Vendas Direto", layout="wide")

def configurar_estilo():
    """Define o título e o cabeçalho da aplicação"""
    st.title("📊 Painel de Controle de Vendas (Dados Integrados)")
    st.write("Esta versão não depende de arquivos externos para funcionar.")
    st.markdown("---")

# =============================================================================
# 2. BANCO DE DADOS INTEGRADO (LINHAS 21-55)
# =============================================================================
def carregar_dados_internos():
    """Aqui você pode alterar os valores para os seus dados reais"""
    # Substitua os nomes e valores abaixo pelos seus dados:
    dados = {
        'ID': [1, 2, 3, 4, 5, 6, 7],
        'DATA': ['2026-01-10', '2026-01-11', '2026-01-12', '2026-01-12', '2026-01-13', '2026-01-13', '2026-01-13'],
        'PRODUTO': ['Produto A', 'Produto B', 'Produto C', 'Produto A', 'Produto B', 'Produto D', 'Produto C'],
        'VALOR': [1200.50, 450.00, 890.00, 1500.00, 300.00, 2100.00, 55.00],
        'VENDEDOR': ['Carlos', 'Ana', 'Beto', 'Carlos', 'Ana', 'Beto', 'Ana']
    }
    
    df = pd.DataFrame(dados)
    st.success("Dados carregados diretamente do sistema!")
    return df

# =============================================================================
# 3. LÓGICA DE PROCESSAMENTO (LINHAS 56-90)
# =============================================================================
def processar_vendas(df):
    """Aplica os cálculos de imposto e performance"""
    # Padronização de colunas
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    if 'VALOR' in df.columns:
        # Cálculos Matemáticos
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)
        df['IMPOSTO'] = df['VALOR'] * 0.15
        df['LUCRO_REAL'] = df['VALOR'] - df['IMPOSTO']
        
        # Regras de Performance
        condicoes = [
            (df['VALOR'] >= 1000),
            (df['VALOR'] >= 500) & (df['VALOR'] < 1000),
            (df['VALOR'] < 500)
        ]
        status = ['ALTA', 'MÉDIA', 'BAIXA']
        df['PERFORMANCE'] = np.select(condicoes, status, default='N/A')
        
    return df

# =============================================================================
# 4. EXIBIÇÃO DA INTERFACE VISUAL (LINHAS 91-115)
# =============================================================================
def exibir_interface(df):
    """Cria a visualização em colunas na tela do site"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Tabela de Registros Atuais")
        st.dataframe(df, use_container_width=True)
        
    with col2:
        st.subheader("Resumo por Categoria")
        if 'PERFORMANCE' in df.columns:
            resumo = df.groupby('PERFORMANCE').agg({
                'VALOR': 'sum',
                'ID': 'count'
            }).rename(columns={'ID': 'QTD'})
            st.write(resumo)
        
    st.markdown("---")
    st.caption(f"Versão 2.0 | Processado em: {datetime.datetime.now()}")

# =============================================================================
# 5. EXECUÇÃO DO FLUXO (LINHAS 116-132)
# =============================================================================
def main():
    configurar_estilo()
    
    # Busca os dados que estão escritos ali em cima (Linha 28)
    dados_carregados = carregar_dados_internos()
    
    if dados_carregados is not None:
        dados_finais = processar_vendas(dados_carregados)
        exibir_interface(dados_finais)
        
        # Permite baixar os dados que você digitou como um CSV real
        csv_data = dados_finais.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Gerar e Baixar arquivo .CSV", csv_data, "meus_dados.csv")

if __name__ == "__main__":
    main()
# Fim do código com 132 linhas e dados embutidos.
