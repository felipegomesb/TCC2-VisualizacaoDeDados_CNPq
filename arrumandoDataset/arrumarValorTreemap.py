import re
import numpy as np
import pandas as pd

# ================= CONFIG =================
ARQUIVO_ENTRADA = 'dados/cnpqBolsasCompleto.parquet'
ARQUIVO_LIMPO = 'dados/cnpqTcc_limpo.parquet'
ARQUIVO_AGREGADO = 'dados/treemap_pronto.parquet'


# ================= FUNÇÃO DE LIMPEZA =================
def parse_valor(valor):
    if pd.isna(valor):
        return np.nan

    valor = str(valor).strip()

    # remove símbolos
    valor = valor.replace('R$', '').replace('$', '').strip()

    # caso brasileiro
    if ',' in valor:
        valor = valor.replace('.', '').replace(',', '.')
        try:
            return float(valor)
        except:
            return np.nan

    # múltiplos pontos
    if valor.count('.') > 1:
        valor = valor.replace('.', '')
        try:
            return float(valor)
        except:
            return np.nan

    # padrão simples
    try:
        return float(valor)
    except:
        return np.nan


# ================= LOAD =================
df = pd.read_parquet(ARQUIVO_ENTRADA)

print("Linhas carregadas:", len(df))


# ================= LIMPEZA =================
df['valor_numeric'] = df['valor_pago'].apply(parse_valor)


# ================= VALIDAÇÃO =================
print("\n===== VALIDAÇÃO =====")
print("Valores válidos:", df['valor_numeric'].notna().sum())
print("Valores inválidos:", df['valor_numeric'].isna().sum())

if df['valor_numeric'].isna().sum() > 0:
    print("\nExemplos inválidos:")
    print(df[df['valor_numeric'].isna()][['valor_pago']].head())


print("\nTotal financeiro (R$):")
print(df['valor_numeric'].sum())


# ================= SUBSTITUI =================
df['total'] = df['valor_numeric']


# ================= SALVA LIMPO =================
#df.to_parquet(ARQUIVO_LIMPO, index=False)
#print(f"\nArquivo limpo salvo em: {ARQUIVO_LIMPO}")


# ================= AGREGAÇÃO =================
#"ano","uf","total"

df_grouped = (
    df.groupby(['grande_area', 'area', 'subarea'])['total']
    .sum()
    .reset_index()
)

df_grouped.to_parquet(ARQUIVO_AGREGADO, index=False)
print(f"Arquivo agregado salvo em: {ARQUIVO_AGREGADO}")


# ================= CHECK =================
print("\n===== CHECK FINAL =====")
print("Total original:", df['total'].sum())
print("Total agregado:", df_grouped['total'].sum())

if abs(df['total'].sum() - df_grouped['total'].sum()) < 1:
    print("✅ Tudo consistente!")
else:
    print("❌ Tem diferença nos totais!")