import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (Isso impede a tela branca logo no início)
st.set_page_config(page_title="Sistema de Gestão de Vendas", layout="wide")

def main():
    st.title("📊 Relatório de Gestão de Vendas")
    st.sidebar.info(f"Última atualização: {datetime.datetime.now().strftime('%H:%M:%S')}")

    # Nome do arquivo que o sistema procura
    arquivo_alvo = "dados_vendas.csv"

    # 2. VERIFICAÇÃO E CARREGAMENTO
    if not os.path.exists(arquivo_alvo):
        st.warning(f"O arquivo '{arquivo_alvo}' não foi encontrado no seu GitHub.")
        st.info("Gerando dados de demonstração para que o sistema funcione...")
        
        # Criando dados fictícios para o sistema não ficar em branco
        df = pd.DataFrame({
            'ID': range(1, 11),
            'DATA': [datetime.date.today()] * 10,
            'VALOR': [150.0, 250.0, 1200.0, 45.0, 900.0, 50.0, 2000.0, 300.0, 85.0, 500.0],
            'CATEGORIA': ['A', 'B', 'C', 'A', 'B', 'A', 'C', 'B', 'A', 'B']
        })
    else:
        try:
            df = pd.read_csv(arquivo_alvo, sep=None, engine='python', encoding='latin1')
            st.success("Arquivo 'dados_vendas.csv' carregado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return

    # 3. PROCESSAMENTO (Lógica das 132 linhas)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    if 'VALOR' in df.columns:
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)
        df['IMPOSTO'] = df['VALOR'] * 0.15
        
        # Categorização
        condicoes = [df['VALOR'] > 1000, df['VALOR'] >= 500, df['VALOR'] < 500]
        escolhas = ['ALTA', 'MÉDIA', 'BAIXA']
        df['PERFORMANCE'] = np.select(condicoes, escolhas, default='N/A')

    # 4. EXIBIÇÃO VISUAL (Garante que o usuário veja algo)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tabela de Dados")
        st.dataframe(df.head(20), use_container_width=True)

    with col2:
        st.subheader("Resumo Financeiro")
        if 'PERFORMANCE' in df.columns:
            resumo = df.groupby('PERFORMANCE')['VALOR'].agg(['sum', 'count']).reset_index()
            st.table(resumo)

    # Botão para baixar o que foi processado
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Baixar Dados Processados", csv, "resultado_vendas.csv", "text/csv")

if __name__ == "__main__":
    main()
    
