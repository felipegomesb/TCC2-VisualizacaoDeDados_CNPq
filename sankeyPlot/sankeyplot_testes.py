import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import unicodedata

# ================= CONFIG =================
ARQUIVO = 'dados/sankeyplot.txt'
TOP_N = 6  # quantidade de categorias visíveis

# ================= LOAD =================
df = pd.read_csv(ARQUIVO)
df['total'] = pd.to_numeric(df['total'], errors='coerce')
df = df.fillna('Não informado')


# ================= NORMALIZAÇÃO =================
def normalizar(texto):
    if pd.isna(texto):
        return ""
    
    texto = str(texto).upper()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = re.sub(r'[^A-Z\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto


# ================= MAPA =================
mapa_codigos = {
    "IC": "Iniciação Científica", "ICJ": "Iniciação Científica",
    "ITI": "Iniciação Científica", "IT": "Iniciação Científica",

    "GM": "Mestrado",
    "GD": "Doutorado", "GDE": "Doutorado",

    "PD": "Pós-Doutorado", "PDE": "Pós-Doutorado",
    "PDJ": "Pós-Doutorado", "PDS": "Pós-Doutorado",

    "PQ": "Produtividade",

    "APQ": "Auxílio à Pesquisa",

    "DTI": "Desenvolvimento Tecnológico",
    "DCR": "Desenvolvimento Tecnológico"
}


def classificar_modalidade(mod):
    if pd.isna(mod):
        return "Não informado"

    mod_str = str(mod).upper()
    codigo = mod_str.split(" - ")[0].strip()

    if codigo in mapa_codigos:
        return mapa_codigos[codigo]

    mod_norm = normalizar(mod_str)

    if "POS DOUTORADO" in mod_norm:
        return "Pós-Doutorado"
    elif "DOUTORADO" in mod_norm:
        return "Doutorado"
    elif "MESTRADO" in mod_norm:
        return "Mestrado"
    elif "INICIACAO" in mod_norm:
        return "Iniciação Científica"

    return "Outros"


df['categoria'] = df['modalidade'].apply(classificar_modalidade)


# ================= AGREGAÇÃO =================
df_grouped = (
    df.groupby(['grande_area', 'categoria'])['total']
    .sum()
    .reset_index()
)

# ================= REDUZ POLUIÇÃO =================
totais = df_grouped.groupby('categoria')['total'].sum()

top_categorias = totais.sort_values(ascending=False).head(TOP_N).index

df_grouped['categoria'] = df_grouped['categoria'].apply(
    lambda x: x if x in top_categorias else 'Outros'
)

# reagrupa após colapsar
df_grouped = (
    df_grouped.groupby(['grande_area', 'categoria'])['total']
    .sum()
    .reset_index()
)


# ================= CORES =================
cores = {
    "Iniciação Científica": "#1f77b4",
    "Mestrado": "#ff7f0e",
    "Doutorado": "#2ca02c",
    "Pós-Doutorado": "#d62728",
    "Produtividade": "#9467bd",
    "Auxílio à Pesquisa": "#8c564b",
    "Desenvolvimento Tecnológico": "#e377c2",
    "Outros": "#7f7f7f"
}


# ================= SANKEY =================
labels = list(pd.concat([df_grouped['grande_area'], df_grouped['categoria']]).unique())
label_to_index = {label: i for i, label in enumerate(labels)}

source = df_grouped['grande_area'].map(label_to_index)
target = df_grouped['categoria'].map(label_to_index)
value = df_grouped['total'].astype(float) / 100


# cor dos links baseada na categoria
link_colors = df_grouped['categoria'].map(cores)

fig = go.Figure(go.Sankey(
    node=dict(
        label=labels,
        pad=20,
        thickness=20
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color=link_colors,
        hovertemplate='R$ %{value:,.2f} milhões<extra></extra>'
    )
))

fig.update_layout(
    title="Fluxo de Investimentos por Área → Modalidade (Top Categorias)",
    font_size=12
)

fig.show()