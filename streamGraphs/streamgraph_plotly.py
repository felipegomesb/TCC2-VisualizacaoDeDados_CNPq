import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import kaleido


# CONFIG

ARQUIVO = "dados/streamgraph_pronto.parquet"
ano_referencia_INICIO = 2003
ano_referencia_FIM = 2024
TOP_N = 8
USAR_WOBBLY = True


# LEITURA

df = pd.read_parquet(ARQUIVO)
df = df.rename(columns={"grande_area": "Grande_Area"})

df["ano_referencia"] = pd.to_numeric(df["ano_referencia"], errors="coerce")
df["total"] = pd.to_numeric(df["total"], errors="coerce")
#print(df[df["ano_referencia"] == 2020].head())
df = df.dropna(subset=["ano_referencia", "Grande_Area", "total"])
df["ano_referencia"] = df["ano_referencia"].astype(int)
df = df[df["ano_referencia"].between(ano_referencia_INICIO, ano_referencia_FIM)]
#print(df[df["ano_referencia"] == 2020].head())


# AGRUPAR (resolve duplicatas)

df_grouped = df.groupby(["ano_referencia", "Grande_Area"], as_index=False)["total"].sum()

#print(df_grouped[df_grouped["ano_referencia"] == 2020].head())
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
                hovertemplate="ano_referencia=%{x}<br>Valor=%{customdata:,.2f}<extra>" + area + "</extra>",
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

#usando kaleido para salvar imagem estática
#fig = go.Figure(fig)
#fig.write_image("resultados/streamgraph/streamgraph_grande_area_interativo.png", engine="kaleido", scale=2)