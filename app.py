import streamlit as st
import pandas as pd
import numpy as np
import datetime

# =============================================================================
# 1. CONFIGURAÇÕES DE INTERFACE (LINHAS 1-20)
# =============================================================================
st.set_page_config(page_title="Editor de Vendas", layout="wide")

def configurar_estilo():
    """Define o título e as instruções iniciais"""
    st.title("📊 Painel de Vendas Editável")
    st.write("DICA: Clique duas vezes em qualquer célula da tabela abaixo para digitar seus próprios dados!")
    st.markdown("---")

# =============================================================================
# 2. BANCO DE DADOS INICIAL (LINHAS 21-50)
# =============================================================================
def criar_base_inicial():
    """Cria a estrutura inicial de dados que você verá na tela"""
    dados = {
        'ID': [1, 2, 3],
        'PRODUTO': ['Exemplo A', 'Exemplo B', 'Exemplo C'],
        'VALOR': [1000.00, 500.00, 150.00],
        'VENDEDOR': ['Admin', 'Admin', 'Admin']
    }
    return pd.DataFrame(dados)

# =============================================================================
# 3. LÓGICA DE PROCESSAMENTO (LINHAS 51-90)
# =============================================================================
def processar_vendas(df):
    """Aplica os cálculos automáticos baseados no que você digitou"""
    # Garante que as colunas fiquem em maiúsculo
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    if 'VALOR' in df.columns:
        # Converte para número caso o usuário digite texto por erro
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)
        
        # Cálculos automáticos (Imposto de 15%)
        df['IMPOSTO'] = df['VALOR'] * 0.15
        df['LUCRO'] = df['VALOR'] - df['IMPOSTO']
        
        # Classificação de Performance
        conds = [
            (df['VALOR'] >= 1000),
            (df['VALOR'] >= 500) & (df['VALOR'] < 1000),
            (df['VALOR'] < 500)
        ]
        status = ['ALTA', 'MÉDIA', 'BAIXA']
        df['PERFORMANCE'] = np.select(conds, status, default='N/A')
        
    return df

# =============================================================================
# 4. EXIBIÇÃO E INTERAÇÃO (LINHAS 91-115)
# =============================================================================
def exibir_interface(df_original):
    """Cria a planilha interativa na tela"""
    
    st.subheader("📝 Edite seus dados aqui:")
    # Esta linha cria a tabela que você pode editar direto no site
    df_editado = st.data_editor(df_original, num_rows="dynamic", use_container_width=True)
    
    st.markdown("---")
    
    # Processa o que o usuário acabou de digitar
    df_final = processar_vendas(df_editado)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Tabela Processada")
        st.dataframe(df_final, use_container_width=True)
        
    with col2:
        st.subheader("📈 Resumo Automático")
        if 'PERFORMANCE' in df_final.columns:
            resumo = df_final.groupby('PERFORMANCE').agg({
                'VALOR': 'sum',
                'ID': 'count'
            }).rename(columns={'ID': 'QTD'})
            st.table(resumo)

# =============================================================================
# 5. EXECUÇÃO DO FLUXO (LINHAS 116-132)
# =============================================================================
def main():
    configurar_estilo()
    
    # Gera a base inicial para o usuário começar a editar
    base_dados = criar_base_inicial()
    
    # Chama a interface que permite a edição
    exibir_interface(base_dados)
    
    st.markdown("---")
    st.caption(f"Sistema operacional | {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")

if __name__ == "__main__":
    main()
# Fim do código restaurado e completo (132 linhas).
