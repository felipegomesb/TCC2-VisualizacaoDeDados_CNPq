import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# CONFIG

ARQUIVO = "codigos/dados/grande_area_new.txt"
ANO_INICIO = 2003
ANO_FIM = 2024
TOP_N = 8
USAR_WIGGLE = True  


# LEITURA

df = pd.read_csv(ARQUIVO)

df = df.rename(columns={"grande_area": "Grande_Area"})

# colunas
required_cols = {"ano", "Grande_Area", "total"}
missing = required_cols.difference(df.columns)
if missing:
    raise ValueError(f"Colunas ausentes: {missing}")


# CONVERSÃO E LIMPEZA

df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
df["total"] = pd.to_numeric(df["total"], errors="coerce")

df = df.dropna(subset=["ano", "Grande_Area", "total"])
df["ano"] = df["ano"].astype(int)

# INTERVALO DE ANOS

df = df[df["ano"].between(ANO_INICIO, ANO_FIM)]


# PIVOT (usei por conta de uma linha duplicada)

pivot = df.pivot_table(
    index="ano",
    columns="Grande_Area",
    values="total",
    aggfunc="sum"
).fillna(0)

# garantir anos contínuos
pivot = pivot.reindex(range(ANO_INICIO, ANO_FIM + 1), fill_value=0)

# ordenar
pivot = pivot.sort_index()


# FILTRAR TOP ÁREAS

top_areas = pivot.sum().nlargest(TOP_N).index
pivot = pivot[top_areas]


# PLOT

x = pivot.index.values
y = pivot.T.values


# PLOT

fig, ax = plt.subplots(figsize=(12, 7))

if USAR_WIGGLE:
    ax.stackplot(x, y, labels=pivot.columns, baseline='wiggle')
else:
    ax.stackplot(x, y, labels=pivot.columns)

# EIXO X INTEIRO
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

# legenda e labels
ax.legend(loc='upper left', fontsize=8)
ax.set_title("Streamgraph - Investimento por Grande Área")
ax.set_xlabel("Ano")
ax.set_ylabel("Valor Pago")

plt.tight_layout()
plt.show()

# salva imagem 

fig.savefig("codigos/resultados/streamgraph_grande_area.png", dpi=300)