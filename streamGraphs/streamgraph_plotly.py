import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import kaleido


# CONFIG

ARQUIVO = "codigos/dados/grande_area_new.txt"
ANO_INICIO = 2003
ANO_FIM = 2024
TOP_N = 8
USAR_WOBBLY = True


# LEITURA

df = pd.read_csv(ARQUIVO)
df = df.rename(columns={"grande_area": "Grande_Area"})

df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
df["total"] = pd.to_numeric(df["total"], errors="coerce")

df = df.dropna(subset=["ano", "Grande_Area", "total"])
df["ano"] = df["ano"].astype(int)
df = df[df["ano"].between(ANO_INICIO, ANO_FIM)]


# AGRUPAR (resolve duplicatas)

df_grouped = df.groupby(["ano", "Grande_Area"], as_index=False)["total"].sum()


# FILTRAR TOP ÁREAS

top = df_grouped.groupby("Grande_Area")["total"].sum().nlargest(TOP_N).index
df_grouped = df_grouped[df_grouped["Grande_Area"].isin(top)]


# PLOT INTERATIVO

if not USAR_WOBBLY:
    fig = px.area(
        df_grouped,
        x="ano",
        y="total",
        color="Grande_Area",
        title="Investimento por Grande Área (Interativo)"
    )
else:
    # Build a centered baseline (streamgraph style) for a wobbly look.
    pivot = (
        df_grouped
        .pivot(index="ano", columns="Grande_Area", values="total")
        .fillna(0)
        .sort_index()
    )

    x = pivot.index.to_numpy()
    y = pivot.to_numpy().T
    areas = pivot.columns.tolist()

    baseline = -0.5 * y.sum(axis=0)

    fig = go.Figure()
    cumulative = baseline.copy()

    for i, area in enumerate(areas):
        lower = cumulative
        upper = cumulative + y[i]

        fig.add_trace(
            go.Scatter(
                x=x,
                y=upper,
                mode="lines",
                line=dict(width=0.5),
                name=area,
                legendgroup=area,
                hovertemplate="Ano=%{x}<br>Valor=%{customdata:,.2f}<extra>" + area + "</extra>",
                customdata=y[i]
            )
        )

        fig.add_trace(
            go.Scatter(
                x=x,
                y=lower,
                mode="lines",
                line=dict(width=0.5),
                fill="tonexty",
                showlegend=False,
                hoverinfo="skip",
                legendgroup=area
            )
        )

        cumulative = upper

    fig.update_layout(
        title="Investimento por Grande Área (Interativo - Wobbly)",
        xaxis_title="Ano",
        yaxis_title="Valor Pago",
        hovermode="x unified"
    )

fig.show()
fig.write_html("codigos/resultados/streamgraph_grande_area_interativo.html")

#usando kaleido para salvar imagem estática
fig = go.Figure(fig)
fig.write_image("codigos/resultados/streamgraph_grande_area_interativo.png", engine="kaleido", scale=2)