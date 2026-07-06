import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# CONFIG

ARQUIVO = "dados/streamgraph_pronto.parquet"
ano_referencia_INICIO = 2003
ano_referencia_FIM = 2024
TOP_N = 8
USAR_WIGGLE = True  
CORES_DALTONICOS = [
    "#0072B2",  # azul
    "#E69F00",  # laranja
    "#009E73",  # verde
    "#D55E00",  # vermelho queimado
    "#56B4E9",  # azul claro
    "#F0E442",  # amarelo
    "#CC79A7",  # rosa
    "#000000",  # preto
]


# LEITURA

df = pd.read_parquet(ARQUIVO)

df = df.rename(columns={"grande_area": "Grande_Area"})

# colunas
required_cols = {"ano_referencia", "Grande_Area", "total"}
missing = required_cols.difference(df.columns)
if missing:
    raise ValueError(f"Colunas ausentes: {missing}")


# CONVERSÃO E LIMPEZA

df["ano"] = pd.to_numeric(df["ano_referencia"], errors="coerce")
df["total"] = pd.to_numeric(df["total"], errors="coerce")

df = df.dropna(subset=["ano_referencia", "Grande_Area", "total"])
df["ano_referencia"] = df["ano_referencia"].astype(int)

# INTERVALO DE ano_referenciaS

df = df[df["ano_referencia"].between(ano_referencia_INICIO, ano_referencia_FIM)]


# PIVOT (usei por conta de uma linha duplicada)

pivot = df.pivot_table(
    index="ano_referencia",
    columns="Grande_Area",
    values="total",
    aggfunc="sum"
).fillna(0)

# garantir ano_referencias contínuos
pivot = pivot.reindex(range(ano_referencia_INICIO, ano_referencia_FIM + 1), fill_value=0)

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
cores = CORES_DALTONICOS[:len(pivot.columns)]

if USAR_WIGGLE:
    ax.stackplot(x, y, labels=pivot.columns, baseline='wiggle', colors=cores)
else:
    ax.stackplot(x, y, labels=pivot.columns, colors=cores)

# EIXO X INTEIRO
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

# legenda e labels
ax.legend(loc='upper left', fontsize=8)
ax.set_title("Streamgraph - Investimento por Grande Área")
ax.set_xlabel("ano_referencia")
ax.set_ylabel("Valor Pago")

plt.tight_layout()
plt.show()

# salva imagem 

fig.savefig("resultados/streamgraph/streamgraph_grande_area.svg", dpi=300)