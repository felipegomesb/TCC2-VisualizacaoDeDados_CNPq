import re
import numpy as np
import pandas as pd

# ================= CONFIG =================
ARQUIVO_ENTRADA = 'dados/cnpqBolsasCompleto.parquet'

# ================= LOAD =================
df = pd.read_parquet(ARQUIVO_ENTRADA)
print("Linhas carregadas:", len(df))

# ================= GET titulo do projeto, palavra chave & ano =================

df = df[['titulo_do_projeto', 'palavra_chave', 'ano_referencia', 'grande_area', 'area', 'subarea']]
df['titulo_do_projeto'] = df['titulo_do_projeto'].dropna()
df['palavra_chave'] = df['palavra_chave'].dropna()
df['ano_referencia'] = df['ano_referencia'].dropna()
df['grande_area'] = df['grande_area'].dropna()
df['area'] = df['area'].dropna()
df['subarea'] = df['subarea'].dropna()


# ================= SEPARAR AS PALAVRAS CHAVE =================
def separar_palavras_chave(palavra_chave):
    if pd.isna(palavra_chave):
        return []
    return re.split(r'[;,]', palavra_chave)

# Aplicar a função para criar uma nova coluna com as palavras-chave separadas
df['palavras_chave_novo'] = df['palavra_chave'].apply(separar_palavras_chave)
#deletar velho
df = df.drop(columns=['palavra_chave'])
#renomear
df = df.rename(columns={'palavras_chave_novo': 'palavra_chave'})

# ###### SALVAR EM PARQUET
df.to_parquet('dados/cnpqTcc_palavras_chave.parquet', index=False)
