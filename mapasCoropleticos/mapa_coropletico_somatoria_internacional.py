import re

import numpy as np
import pandas as pd
import plotly.express as px



# CONFIG
ARQUIVO = "dados/coropletico_internacional.parquet"
ARQUIVO_SAIDA_HTML = "resultados/mapas_coropleticos/mapa_coropletico_internacional_somado.html"
ARQUIVO_SAIDA_SVG = "resultados/mapas_coropleticos/mapa_coropletico_internacional_somado.svg"

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

def extrair_iso3(valor_pais_destino: str) -> str | None:
	if pd.isna(valor_pais_destino):
		return None

	texto = str(valor_pais_destino).strip().upper()
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

	required = {"ano", "pais_destino", "valor_total"}
	missing = required.difference(df.columns)
	if missing:
		raise ValueError(f"Colunas ausentes: {missing}")

	df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
	df["valor_total"] = pd.to_numeric(df["valor_total"], errors="coerce")
	df["iso_alpha"] = df["pais_destino"].apply(extrair_iso3)

	df = df.dropna(subset=["ano", "valor_total", "iso_alpha"])
	df["ano"] = df["ano"].astype(int)
	df = df[df["ano"].between(1900, 2100)]

	# SOMATORIA
	df = df.groupby("iso_alpha", as_index=False)["valor_total"].sum()
	return df


def preparar_visualizacao(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
	if ESCALA_MILHOES:
		df["valor_plot"] = df["valor_total"] / 1_000_000
		label = "Valor valor_total (R$ milhoes)"
	else:
		df["valor_plot"] = df["valor_total"]
		label = "Valor valor_total"

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
		color_continuous_scale="YlOrRd",
		projection="natural earth",
		hover_name="iso_alpha",
		hover_data={"valor_plot": ":,.2f", "iso_alpha": False},
		title="Mapa Coropletico Internacional - Soma de Todos os Anos",
		labels={"valor_plot": "Valor"},
	)

	fig.update_layout(
		margin=dict(l=0, r=0, t=50, b=0),
		coloraxis_colorbar_title=label
	)
	return fig


def main():
    df = carregar_dados(ARQUIVO)
    df, label = preparar_visualizacao(df)
    fig = criar_figura(df, label)

    #fig.show()
    #fig.write_html(ARQUIVO_SAIDA_HTML)

    # top 10 países
    top10 = df.nlargest(10, "valor_total")
    print("Top 10 países por investimento valor_total:")
    print(top10[["iso_alpha", "valor_total"]].to_string(formatters={"valor_total": "R$ {:,.2f}".format}))

    try:
        fig.write_image(ARQUIVO_SAIDA_SVG, width=1400, height=800, scale=2)
    except Exception:
        pass


if __name__ == "__main__":
	main()
