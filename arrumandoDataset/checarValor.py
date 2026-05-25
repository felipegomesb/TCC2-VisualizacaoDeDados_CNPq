import numpy as np
import pandas as pd

# ================= CONFIG =================
ARQUIVO_1 = 'dados/cnpqTcc.txt'
ARQUIVO_2 = 'dados/cnpqTcc_limpo.csv'
ARQUIVO_3 = 'dados/cnpqTcc.parquet'

# ================= FUNÇÃO DE LIMPEZA =================
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
df1 = pd.read_csv(ARQUIVO_1)
df2 = pd.read_csv(ARQUIVO_2)
df3 = pd.read_parquet(ARQUIVO_3)

# ================= VALIDAÇÃO =================
print("===== VALIDAÇÃO =====")
print(f"Arquivo 1 (txt): {len(df1)} linhas")
print(f"Arquivo 2 (csv): {len(df2)} linhas")
print(f"Arquivo 3 (parquet): {len(df3)} linhas")


#DF1
df1['valor_numeric'] = df1['valor_pago'].apply(parse_valor)
total_original = len(df1)
total_validos = df1['valor_numeric'].notna().sum()
total_invalidos = df1['valor_numeric'].isna().sum()

print("\n===== VALIDAÇÃO =====")
print(f"Total linhas: {total_original}")
print(f"Valores válidos: {total_validos}")
print(f"Valores inválidos: {total_invalidos}")

if total_invalidos > 0:
    print("\nExemplos inválidos:")
    print(df1[df1['valor_numeric'].isna()][['valor_pago']].head())


print("\nTotal financeiro (R$):")
print(df1['valor_numeric'].sum())

#DF2
df2['valor_numeric'] = df2['valor_pago'].apply(parse_valor)
total_original = len(df2)
total_validos = df2['valor_numeric'].notna().sum()
total_invalidos = df2['valor_numeric'].isna().sum()
print("\n===== VALIDAÇÃO =====")
print(f"Total linhas: {total_original}")
print(f"Valores válidos: {total_validos}")
print(f"Valores inválidos: {total_invalidos}")  

if total_invalidos > 0:
    print("\nExemplos inválidos:")
    print(df2[df2['valor_numeric'].isna()][['valor_pago']].head())
print("\nTotal financeiro (R$):")
print(df2['valor_numeric'].sum())

#DF3
df3['valor_numeric'] = df3['valor_pago'].apply(parse_valor) 
total_original = len(df3)
total_validos = df3['valor_numeric'].notna().sum()
total_invalidos = df3['valor_numeric'].isna().sum()
print("\n===== VALIDAÇÃO =====")
print(f"Total linhas: {total_original}")
print(f"Valores válidos: {total_validos}")
print(f"Valores inválidos: {total_invalidos}")
if total_invalidos > 0:
    print("\nExemplos inválidos:")
    print(df3[df3['valor_numeric'].isna()][['valor_pago']].head())
print("\nTotal financeiro (R$):")
print(df3['valor_numeric'].sum())


# ================= CHECK FINAL =================
print("\n===== CHECK FINAL =====")
total_df1 = df1['valor_numeric'].sum()
total_df2 = df2['valor_numeric'].sum()
total_df3 = df3['valor_numeric'].sum()

print("Total arquivo 1 (txt):", total_df1)
print("Total arquivo 2 (csv limpo):", total_df2)
print("Total arquivo 3 (parquet):", total_df3)

consistente_12 = np.isclose(total_df1, total_df2, rtol=0, atol=1)
consistente_13 = np.isclose(total_df1, total_df3, rtol=0, atol=1)

if consistente_12 and consistente_13:
    print("✅ Tudo consistente entre txt, csv e parquet!")
else:
    print("❌ Tem diferença nos totais!")
    print("Diferença txt - csv:", total_df1 - total_df2)
    print("Diferença txt - parquet:", total_df1 - total_df3)

