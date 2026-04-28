import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# CONFIG
ARQUIVO = "dados/coropletico_internacional.parquet"
ARQUIVO_SAIDA_HTML = "resultados/mapas_coropleticos/mapa_coropletico_internacional_grandearea.html"
ARQUIVO_SAIDA_PNG = "resultados/mapas_coropleticos/mapa_coropletico_internacional_grandearea.png"

ESCALA_MILHOES = True
USAR_ESCALA_LOG = True


# CORRECOES ISO
ISO3_FIX = {
    "RFA": "DEU",
    "HOL": "NLD",
    "SUE": "SWE",
    "ESC": "GBR",
    "ING": "GBR",
    "GAL": "GBR",
    "IRN": "GBR",
    "CRS": "KOR",
    "RSS": "RUS",
    "AFS": "ZAF",
    "RTC": "CZE",
    "ARL": "DZA",
    "MBQ": "MOZ",
    "RCA": "CAF",
    "FOR": "TWN",
    "TAI": "TWN",
    "PRG": "PRY",
    "GAN": "GHA",
    "TAN": "TZA",
    "ETP": "ETH",
    "CBV": "CPV",
    "STP": "STP",
    "PTR": "PRI",
    "EAU": "ARE",
    "EUA": "USA",
    "USA": "USA",

    # EUROPA
    "ALE": "DEU",
    "ALM": "DEU",
    "ITA": "ITA",
    "ESP": "ESP",
    "POR": "PRT",
    "FRA": "FRA",
    "BEL": "BEL",
    "SUI": "CHE",
    "AUT": "AUT",
    "POL": "POL",
    "HUN": "HUN",
    "ROM": "ROU",
    "BUL": "BGR",
    "GRE": "GRC",
    "DIN": "DNK",
    "NOR": "NOR",
    "FIN": "FIN",
    "IRL": "IRL",
    "ESCÓCIA": "GBR",

    # AMÉRICAS
    "BRA": None,
    "BR": None,
    "ARG": "ARG",
    "MEX": "MEX",
    "CAN": "CAN",
    "COL": "COL",
    "CHI": "CHL",
    "PER": "PER",
    "VEN": "VEN",
    "URU": "URY",
    "BOL": "BOL",
    "EQU": "ECU",
    "PAR": "PRY",
    "DOM": "DOM",
    "CUB": "CUB",
    "HAI": "HTI",
    "GUA": "GTM",
    "HON": "HND",
    "NIC": "NIC",
    "SAL": "SLV",
    "PAN": "PAN",

    # ÁSIA
    "CHN": "CHN",
    "CHIINA": "CHN",
    "IND": "IND",
    "JAP": "JPN",
    "COR": "KOR",
    "COREIA": "KOR",
    "CDN": "PRK", 
    "VIE": "VNM",
    "TAI": "TWN",
    "HKG": "HKG",
    "MAC": "MAC",
    "SIN": "SGP",
    "INDO": "IDN",
    "MAL": "MYS",
    "FIL": "PHL",
    "PAQ": "PAK",
    "AFG": "AFG",
    "ARA": "SAU",
    "SAU": "SAU",
    "ISR": "ISR",
    "IRA": "IRN",
    "IRQ": "IRQ",
    "TUR": "TUR",

    # ÁFRICA
    "NIG": "NGA",
    "EGI": "EGY",
    "MAR": "MAR",
    "ALG": "DZA",
    "TUN": "TUN",
    "QUEN": "KEN",
    "UGA": "UGA",
    "ANG": "AGO",
    "ZIM": "ZWE",
    "BOT": "BWA",
    "NAM": "NAM",

    # OCEANIA
    "AUS": "AUS",
    "NZL": "NZL",
    "NOVA ZELANDIA": "NZL",

    # ORGANIZAÇÕES 
    "UE": "EUU",   
    "EUR": "EUU",
    "OCDE": None,
    "ONU": None,

     # INDEFINIDOS
    "NA": None,
    "N/A": None,
    "": None,
}

def extrair_iso3(valor_pais: str) -> str | None:
    if pd.isna(valor_pais):
        return None

    texto = str(valor_pais).strip().upper()
    if not texto or "NAO INFORMADA" in texto or texto == "-":
        return None

    match = re.match(r"^([A-Z]{3})", texto)
    if not match:
        return None

    codigo = match.group(1)
    return ISO3_FIX.get(codigo, codigo)


def carregar_dados(caminho_arquivo: str) -> pd.DataFrame:
	df = pd.read_parquet(caminho_arquivo)
	df.columns = df.columns.str.strip().str.lower()

	required = {"ano", "pais", "total", "grande_area"}
	missing = required.difference(df.columns)
	if missing:
		raise ValueError(f"Colunas ausentes: {missing}")

	df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
	df["total"] = pd.to_numeric(df["total"], errors="coerce")
	df["iso_alpha"] = df["pais"].apply(extrair_iso3)

	df = df.dropna(subset=["ano", "total", "iso_alpha"])
	df["ano"] = df["ano"].astype(int)
	df = df[df["ano"].between(1900, 2100)]

	# SOMATORIA
	df = df.groupby(["iso_alpha", "grande_area"], as_index=False)["total"].sum()
	return df


def preparar_visualizacao(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    if ESCALA_MILHOES:
        df["valor_plot"] = df["total"] / 1_000_000
        label = "Valor total (R$ milhoes)"
    else:
        df["valor_plot"] = df["total"]
        label = "Valor total"

    # keep raw values for display (before log transform) so we can show currency-formatted ticks
    df["valor_plot_raw"] = df["valor_plot"].copy()

    if USAR_ESCALA_LOG:
        df["valor_plot"] = np.log1p(df["valor_plot"])
        label += " (escala log)"

    return df, label


def criar_figura(df: pd.DataFrame, label: str):
    fig = px.choropleth(
        df,
        locations="iso_alpha",
        locationmode="ISO-3",
        color="valor_plot",
        color_continuous_scale="Inferno",
        projection="natural earth",
        hover_name="iso_alpha",
        hover_data={"valor_plot": ":,.2f", "iso_alpha": False},
        title="Mapa Coropletico Internacional - Soma de Todos os Anos",
        labels={"valor_plot": "Valor"},
    )

    # ensure trace colorscale is explicitly set (prevents overrides when reusing traces)
    for tr in fig.data:
        if hasattr(tr, 'colorscale'):
            tr.colorscale = "Inferno"

    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar_title=label
    )
    return fig

def criar_mapa(df, label):
    fig = px.choropleth(
        df,
        locations="iso_alpha",
        locationmode="ISO-3",
        color="valor_plot",
        color_continuous_scale="Inferno",
        projection="natural earth",
        hover_name="iso_alpha",
        hover_data={"valor_plot": ":,.2f", "iso_alpha": False},
        title="Mapa Coropletico Internacional - Soma de Todos os Anos",
        labels={"valor_plot": "Valor"},
    )

    # ensure trace colorscale is explicitly set (prevents overrides when reusing traces)
    for tr in fig.data:
        if hasattr(tr, 'colorscale'):
            tr.colorscale = "Inferno"

    # configure colorbar to show currency formatting
    if USAR_ESCALA_LOG:
        # ticks must be placed on the transformed (log1p) scale, but display original values
        raw_min = float(df["valor_plot_raw"].min())
        raw_max = float(df["valor_plot_raw"].max())
        if raw_min == raw_max:
            tick_raw = [raw_min]
        else:
            tick_raw = list(np.linspace(raw_min, raw_max, num=5))
        tickvals = [float(np.log1p(x)) for x in tick_raw]
        if ESCALA_MILHOES:
            ticktext = [f"R$ {x:,.2f}M" for x in tick_raw]
        else:
            ticktext = [f"R$ {x:,.2f}" for x in tick_raw]

        fig.update_traces(colorbar=dict(title=label, tickvals=tickvals, ticktext=ticktext))
    else:
        # linear scale: prefix with R$ and optionally show millions suffix
        ticksuffix = "M" if ESCALA_MILHOES else ""
        fig.update_traces(colorbar=dict(title=label, tickprefix="R$ ", ticksuffix=ticksuffix, tickformat=",.2f"))

    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar_title=label
    )

    return fig


def main():
    df = carregar_dados(ARQUIVO)
    df, label = preparar_visualizacao(df)

    fig = go.Figure()

    areas = df["grande_area"].unique()

    # ===== TODOS =====
    df_total = df.groupby("iso_alpha", as_index=False)[["total", "valor_plot", "valor_plot_raw"]].sum()

    fig.add_trace(
        criar_mapa(df_total, label).data[0]
    )

    # ===== POR ÁREA =====
    for area in areas:
        df_area = df[df["grande_area"] == area]

        df_area = df_area.groupby("iso_alpha", as_index=False)[["total", "valor_plot", "valor_plot_raw"]].sum()

        mapa = criar_mapa(df_area, label)

        fig.add_trace(mapa.data[0])

    # ===== BOTÕES =====
    buttons = []

    # botão geral
    visible = [True] + [False]*len(areas)
    buttons.append(dict(
        label="Todas as áreas",
        method="update",
        args=[{"visible": visible},
              {"title.text": "Mapa Coropletico Internacional - Soma de Todos os Anos"}]
    ))

    # botões individuais
    for i, area in enumerate(areas):
        visible = [False]*(len(areas)+1)
        visible[i+1] = True

        buttons.append(dict(
            label=area,
            method="update",
            args=[{"visible": visible},
                  {"title.text": f"Mapa Coropletico Internacional - {area}"}]
            
        ))

    fig.update_layout(
        title_text="Mapa Coropletico Internacional - Soma de Todos os Anos",
        margin=dict(l=0, r=0, t=50, b=0),
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
        )]
    )

    fig.show()
    fig.write_html(ARQUIVO_SAIDA_HTML)


if __name__ == "__main__":
    main()
