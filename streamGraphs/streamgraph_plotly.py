import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# CONFIG

ARQUIVO = "dados/streamgraph_pronto.parquet"
ano_referencia_INICIO = 2003
ano_referencia_FIM = 2024
TOP_N = 8
USAR_WOBBLY = True

# Paleta Okabe-Ito 
OKABE_ITO = [
    "#E69F00",  # laranja
    "#56B4E9",  # azul-céu
    "#009E73",  # verde
    "#F0E442",  # amarelo
    "#0072B2",  # azul
    "#D55E00",  # vermelhão
    "#CC79A7",  # rosa
    "#000000",  # preto
]


def hex_para_rgba(hex_color, alpha=0.6):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


# LEITURA

df = pd.read_parquet(ARQUIVO)
df = df.rename(columns={"grande_area": "Grande_Area"})

df["ano_referencia"] = pd.to_numeric(df["ano_referencia"], errors="coerce")
df["total"] = pd.to_numeric(df["total"], errors="coerce")
df = df.dropna(subset=["ano_referencia", "Grande_Area", "total"])
df["ano_referencia"] = df["ano_referencia"].astype(int)
df = df[df["ano_referencia"].between(ano_referencia_INICIO, ano_referencia_FIM)]


# AGRUPAR (resolve duplicatas)

df_grouped = df.groupby(["ano_referencia", "Grande_Area"], as_index=False)["total"].sum()


# FILTRAR TOP ÁREAS

top = df_grouped.groupby("Grande_Area")["total"].sum().nlargest(TOP_N).index
df_grouped = df_grouped[df_grouped["Grande_Area"].isin(top)]


# PLOT INTERATIVO

if not USAR_WOBBLY:
    fig = px.area(
        df_grouped,
        x="ano_referencia",
        y="total",
        color="Grande_Area",
        color_discrete_sequence=OKABE_ITO,
        title="Investimento por Grande Área (Interativo)"
    )
else:
    # Build a centered baseline (streamgraph style) for a wobbly look.
    pivot = (
        df_grouped
        .pivot(index="ano_referencia", columns="Grande_Area", values="total")
        .fillna(0)
        .sort_index()
    )
    print(2020 in pivot.index)

    x = pivot.index.to_numpy()
    y = pivot.to_numpy().T
    areas = pivot.columns.tolist()

    cor_por_area = {area: OKABE_ITO[i % len(OKABE_ITO)] for i, area in enumerate(areas)}

    baseline = -0.5 * y.sum(axis=0)

    fig = go.Figure()
    cumulative = baseline.copy()

    for i, area in enumerate(areas):
        lower = cumulative
        upper = cumulative + y[i]
        cor = cor_por_area[area]

        fig.add_trace(
            go.Scatter(
                x=x,
                y=upper,
                mode="lines",
                line=dict(width=0.5, color=cor),
                name=area,
                legendgroup=area,
                hovertemplate="ano_referencia=%{x}<br>Valor=%{customdata:,.2f}<extra>" + area + "</extra>",
                customdata=y[i]
            )
        )

        fig.add_trace(
            go.Scatter(
                x=x,
                y=lower,
                mode="lines",
                line=dict(width=0.5, color=cor),
                fill="tonexty",
                fillcolor=hex_para_rgba(cor, alpha=0.6),
                showlegend=False,
                hoverinfo="skip",
                legendgroup=area
            )
        )

        cumulative = upper

    fig.update_layout(
        title=dict(
            text="Investimento por Grande Área (Interativo - Wobbly)",
            font=dict(size=28)  
        ),
        legend=dict(
            font=dict(size=16),      
            title=dict(font=dict(size=18)),
            itemwidth=40,
            tracegroupgap=5  
        ),
        xaxis_title="ano_referencia",
        yaxis_title="Valor Pago",
        hovermode="x unified"
    )

    fig.update_xaxes(
        tickmode='linear',
        dtick=1
    )

fig.show()
fig.write_html("resultados/streamgraph/streamgraph_grande_area_interativo.html")
fig.write_image("resultados/streamgraph/streamgraph_grande_area_interativo.svg", width=1200, height=800, scale=2)