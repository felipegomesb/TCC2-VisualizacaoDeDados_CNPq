import re
import numpy as np
import pandas as pd

# ================= CONFIG =================
ARQUIVO_ENTRADA = 'dados/cnpqBolsasCompleto.parquet'
ARQUIVO_AGREGADO = 'dados/streamgraph_pronto.parquet'

# ================= FUNÇÃO DE LIMPEZA =================
def parse_valor(valor):
    if pd.isna(valor):
        return np.nan

    valor = str(valor).strip()

    # remove símbolos
    valor = valor.replace('R$', '').replace('$', '').strip()

    # caso brasileiro (vírgula decimal)
    if ',' in valor:
        valor = valor.replace('.', '').replace(',', '.')
        try:
            return float(valor)
        except:
            return np.nan

    # caso múltiplos pontos (milhar)
    if valor.count('.') > 1:
        valor = valor.replace('.', '')
        try:
            return float(valor)
        except:
            return np.nan

    # caso padrão (decimal simples)
    try:
        return float(valor)
    except:
        return np.nan
    

# ================= LOAD =================
df = pd.read_parquet(ARQUIVO_ENTRADA)
print("Linhas carregadas:", len(df))

# ================= LIMPEZA =================

df['valor_numeric'] = df['valor_pago'].apply(parse_valor)

df['grande_area'] = (
    df['grande_area']
    .str.strip()
    .str.title()
)

df['area'] = (
    df['area']
    .str.strip()
    .str.title()
)

df['subarea'] = (
    df['subarea']
    .str.strip()
    .str.title()
)

df['valor_numeric'] = df['valor_pago'].apply(parse_valor)
# ================= VALIDAÇÃO =================
total_original = len(df)
total_validos = df['valor_numeric'].notna().sum()
total_invalidos = df['valor_numeric'].isna().sum()

# ==================== AGREGAÇÃO ==================== I NEED "ano","grande_area","total"
df_agg = (
    df.groupby(['ano_referencia', 'grande_area'], as_index=False)['valor_numeric']
    .sum()
    .rename(columns={'valor_numeric': 'total'})
)

print("\n===== VALIDAÇÃO =====")
print(f"Total linhas: {total_original}")
print(f"Valores válidos: {total_validos}")
print(f"Valores inválidos: {total_invalidos}")
print("\nAmostra do DataFrame agregado:")
print(df_agg[df_agg['ano_referencia'] == 2024].head())

# ==================== EXPORTAÇÃO ====================
df_agg.to_parquet(ARQUIVO_AGREGADO, index=False)
print(f"\nDataFrame agregado exportado para: {ARQUIVO_AGREGADO}")

