import numpy as np
import pandas as pd
import pyarrow as pa
import fastparquet as fp

# ================= CONFIG =================
ARQUIVO_ENTRADA = 'dados/cnpqTcc.parquet'

# ================= LOAD =================
df = pd.read_parquet(ARQUIVO_ENTRADA, columns=['valor_pago'])


#df.info()
print(df.head())