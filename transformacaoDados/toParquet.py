import numpy as np
import pandas as pd
import pyarrow as pa
import fastparquet as fp

# ================= CONFIG =================
ARQUIVO_ENTRADA = 'dados/cnpqTcc.txt'

# FUNC

def parse_valor(valor):
    if pd.isna(valor):
        return np.nan
    
    valor = str(valor).strip()
    if not valor:
        return np.nan

    # remove símbolos
    valor = valor.replace('R$', '').replace('$', '').replace(' ', '')

    # mantém apenas dígitos e separadores numéricos
    valor = ''.join(ch for ch in valor if ch.isdigit() or ch in ',.-')
    if valor in {'', '-', '.', ',', '-.', '-,'}:
        return np.nan

    ultima_virgula = valor.rfind(',')
    ultimo_ponto = valor.rfind('.')

    # escolhe separador decimal pelo último símbolo encontrado
    if ultima_virgula != -1 and ultimo_ponto != -1:
        if ultima_virgula > ultimo_ponto:
            normalizado = valor.replace('.', '').replace(',', '.')
        else:
            normalizado = valor.replace(',', '')
    elif ultima_virgula != -1:
        partes = valor.split(',')
        if len(partes[-1]) in (1, 2):
            normalizado = valor.replace('.', '').replace(',', '.')
        else:
            normalizado = valor.replace(',', '')
    elif ultimo_ponto != -1:
        partes = valor.split('.')
        if len(partes[-1]) in (1, 2):
            normalizado = valor.replace(',', '')
        else:
            normalizado = valor.replace('.', '')
    else:
        normalizado = valor

    try:
        return float(normalizado)
    except:
        return np.nan
    
# ================= LOAD =================

df = pd.read_csv(ARQUIVO_ENTRADA)
df['valor_pago'] = df['valor_pago'].apply(parse_valor)
cols_str = [
    'data_inicio_processo',
    'data_termino_processo',
    'regiao_destino',
    'titulo_do_projeto',
    'palavra_chave',
    'uo',
    'acaoppa',
    'cpf',
    'processo'
]

for col in cols_str:
    if col in df.columns:
        df[col] = df[col].astype(str)

cols_para_excluir = [
    'data_extracao',
    'cod_modalidade',
    'id_lattes',
    'id_2020_ignorar'
    'acaoppa',
    'programappa',
    'cpf',
    'nome_chamada',
    'beneficiario',
    'processo',
    'data_inicio_processo',
    'data_termino_processo',
    'categoria_nivel',
    'uo',
    'natureza_de_despesa',

]

df = df.drop(columns=cols_para_excluir, errors='ignore')
df = df.drop(columns=['id_2020_ignorar','acaoppa'], errors='ignore')


#parquet


df.to_parquet('dados/cnpqTcc.parquet', engine='pyarrow', index=False)




