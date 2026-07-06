import re
import numpy as np
import pandas as pd

# ================= CONFIG =================
ARQUIVO_ENTRADA = 'dados/cnpqBolsasCompleto.parquet'
ARQUIVO_AGREGADO = 'dados/coropletico_nacional.parquet'

# ================= FUNÇÃO DE LIMPEZA =================
def parse_valor(valor):

    if pd.isna(valor):
        return np.nan

    valor = str(valor).strip()

    valor = (
        valor
        .replace('R$', '')
        .replace('$', '')
        .strip()
    )

    # formato brasileiro
    # 1.234,56 -> 1234.56
    if ',' in valor:

        valor = valor.replace('.', '')
        valor = valor.replace(',', '.')

        try:
            return float(valor)
        except:
            return np.nan

    # casos estranhos com múltiplos pontos
    if valor.count('.') > 1:

        valor = valor.replace('.', '')

        try:
            return float(valor)
        except:
            return np.nan

    try:
        return float(valor)
    except:
        return np.nan


# ================= LOAD =================
df = pd.read_parquet(ARQUIVO_ENTRADA)

print("Linhas carregadas:", len(df))

# ================= LIMPEZA VALOR =================
df['valor_total'] = df['valor_pago'].apply(parse_valor)

# remove inválidos
df = df[df['valor_total'].notna()]

# ================= ANO =================
df['ano'] = (
    pd.to_numeric(
        df['ano_referencia'],
        errors='coerce'
    )
    .astype('Int64')
)

# remove anos inválidos
df = df[df['ano'].notna()]

# ================= UF =================
df['sigla_uf_destino'] = (
    df['sigla_uf_destino']
    .fillna('NI')
    .astype(str)
    .str.strip()
    .str.upper()
)

# ================= UFs VÁLIDAS =================
ufs_validas = {
    'AC','AL','AP','AM','BA','CE','DF','ES',
    'GO','MA','MT','MS','MG','PA','PB','PR',
    'PE','PI','RJ','RN','RS','RO','RR','SC',
    'SP','SE','TO'
}

df = df[
    df['sigla_uf_destino'].isin(ufs_validas)
]

# ================= AGREGAÇÃO =================
df_grouped = (
    df.groupby(
        ['ano', 'sigla_uf_destino'],
        as_index=False
    )['valor_total']
    .sum()
)

# ================= ORDENAÇÃO =================
df_grouped = df_grouped.sort_values(
    ['ano', 'sigla_uf_destino']
)

# ================= VALIDAÇÃO =================
print("\n===== CHECK =====")

total_original = df['valor_total'].sum()
total_agregado = df_grouped['valor_total'].sum()

print("Total original :", total_original)
print("Total agregado :", total_agregado)

if abs(total_original - total_agregado) < 1:
    print("Tudo consistente!")
else:
    print("Diferença encontrada!")

# ================= AMOSTRA =================
print("\n===== HEAD =====")
print(df_grouped.head())

# ================= OUTPUT =================
df_grouped.to_parquet(
    ARQUIVO_AGREGADO,
    index=False
)

print(f"\nArquivo salvo em: {ARQUIVO_AGREGADO}")