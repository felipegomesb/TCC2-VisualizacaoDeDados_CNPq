import numpy as np
import pandas as pd
import pyarrow as pa
import fastparquet as fp
import os
import matplotlib.pyplot as plt
import seaborn as sns

# ================= CONFIG =================
ARQUIVO_ENTRADA = 'dados/cnpqTcc.parquet'

# ================= LOAD =================
df = pd.read_parquet(ARQUIVO_ENTRADA)


print(f'O conjunto de dados possui {df.shape[0]} linhas e {df.shape[1]} colunas.')

missing_values = df.isnull().sum()
missing_percentage = (df.isnull().sum() / len(df)) * 100

missing_info = pd.DataFrame({
    'Valores Ausentes': missing_values,
    'Porcentagem (%)': missing_percentage
})

missing_info = missing_info[missing_info['Valores Ausentes'] > 0].sort_values(by='Porcentagem (%)', ascending=False)

print('\nValores ausentes por coluna (e suas porcentagens):')
print(missing_info.to_string())

q = df['valor_pago'].quantile(1 - 0.01)

# Filtrar dados
filtered_prices = df[df['valor_pago'] <= q]['valor_pago']

plt.figure(figsize=(10, 6))
sns.histplot(filtered_prices.dropna(), bins=30, kde=True)

plt.title('Distribuição de Preços (sem outliers)')
plt.xlabel('Preço')
plt.ylabel('Contagem')

plt.tight_layout()
plt.show()
