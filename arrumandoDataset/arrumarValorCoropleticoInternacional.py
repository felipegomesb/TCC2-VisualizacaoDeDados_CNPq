import re
import numpy as np
import pandas as pd

# ================= CONFIG =================
ARQUIVO_ENTRADA = 'dados/cnpqTcc.parquet'
ARQUIVO_AGREGADO = 'dados/coropletico_internacional.parquet'


# ================= FUNÇÃO DE LIMPEZA =================
def parse_valor(valor):
    if pd.isna(valor):
        return np.nan

    valor = str(valor).strip()
    valor = valor.replace('R$', '').replace('$', '').strip()

    if ',' in valor:
        valor = valor.replace('.', '').replace(',', '.')
        try:
            return float(valor)
        except:
            return np.nan

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


# ================= LIMPEZA =================
df['total'] = df['valor_pago'].apply(parse_valor)

# remove inválidos (opcional, mas recomendado)
df = df[df['total'].notna()]


# ================= TRATAMENTO DE COLUNAS =================

# ANO
df['ano'] = pd.to_numeric(df['ano_referencia'], errors='coerce')

# PAÍS (ajusta conforme o nome da sua coluna real)
if 'pais' not in df.columns:
    if 'pais_destino' in df.columns:
        df['pais'] = df['pais_destino']
    elif 'regiao_destino' in df.columns:
        df['pais'] = df['regiao_destino']
    else:
        df['pais'] = 'Não informado'

df['pais'] = df['pais'].fillna('Não informado').astype(str)

# GRANDE ÁREA
df['grande_area'] = df['grande_area'].fillna('Não informado')


# ================= AGREGAÇÃO =================
df_grouped = (
    df.groupby(['ano', 'pais', 'grande_area'])['total']
    .sum()
    .reset_index()
)


# ================= VALIDAÇÃO =================
print("\n===== CHECK =====")
print("Total original:", df['total'].sum())
print("Total agregado:", df_grouped['total'].sum())

if abs(df['total'].sum() - df_grouped['total'].sum()) < 1:
    print("✅ Tudo consistente!")
else:
    print("❌ Diferença encontrada!")


# ================= OUTPUT =================
df_grouped.to_parquet(ARQUIVO_AGREGADO, index=False)
print(f"Arquivo salvo em: {ARQUIVO_AGREGADO}")