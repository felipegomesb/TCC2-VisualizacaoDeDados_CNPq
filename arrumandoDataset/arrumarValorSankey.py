import re
import numpy as np
import pandas as pd

# ================= CONFIG =================
ARQUIVO_ENTRADA = 'dados/cnpqBolsasCompleto.parquet'
ARQUIVO_AGREGADO = 'dados/sankey_pronto.parquet'


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


# ================= VALIDAÇÃO =================
total_original = len(df)
total_validos = df['valor_numeric'].notna().sum()
total_invalidos = df['valor_numeric'].isna().sum()

print("\n===== VALIDAÇÃO =====")
print(f"Total linhas: {total_original}")
print(f"Valores válidos: {total_validos}")
print(f"Valores inválidos: {total_invalidos}")

if total_invalidos > 0:
    print("\nExemplos inválidos:")
    print(df[df['valor_numeric'].isna()][['valor_pago']].head())


print("\nTotal financeiro (R$):")
print(df['valor_numeric'].sum())


# ================= SUBSTITUI COLUNA =================
df['total'] = df['valor_numeric']

# ================= AGREGAÇÃO (Sankey) =================
df_grouped = (
    df.groupby(['grande_area', 'modalidade', 'linha_de_fomento', 'ano_referencia'])['total']
    .sum()
    .reset_index()
)

df_grouped.to_parquet(ARQUIVO_AGREGADO, index=False)
print(f"Arquivo agregado salvo em: {ARQUIVO_AGREGADO}")


# ================= CHECK FINAL =================
print("\n===== CHECK FINAL =====")
print("Total original (limpo):", df['total'].sum())
print("Total agregado:", df_grouped['total'].sum())

if abs(df['total'].sum() - df_grouped['total'].sum()) < 1:
    print("Tudo consistente!")
else:
    print("Tem diferença nos totais!")