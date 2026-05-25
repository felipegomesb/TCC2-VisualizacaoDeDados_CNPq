import json
import unicodedata
from urllib.request import urlopen

import numpy as np
import pandas as pd
import plotly.express as px



# CONFIG
ARQUIVO = "dados/coropletico_nacional.parquet"
ARQUIVO_SAIDA_HTML = "resultados/mapas_coropleticos/mapa_coropletico_nacional_somado.html"
ARQUIVO_SAIDA_PNG = "resultados/mapas_coropleticos/mapa_coropletico_nacional_somado.png"
ARQUIVO_SAIDA_HTML_100MIL = "resultados/mapas_coropleticos/mapa_coropletico_nacional_somado_100milhab.html"
ARQUIVO_SAIDA_PNG_100MIL = "resultados/mapas_coropleticos/mapa_coropletico_nacional_somado_100milhab.png"

GEOJSON_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

ESCALA_MILHOES = True
USAR_ESCALA_LOG = True


sigla_uf_destino_TO_STATE = {
	"AC": "Acre",
	"AL": "Alagoas",
	"AP": "Amapa",
	"AM": "Amazonas",
	"BA": "Bahia",
	"CE": "Ceara",
	"DF": "Distrito Federal",
	"ES": "Espirito Santo",
	"GO": "Goias",
	"MA": "Maranhao",
	"MT": "Mato Grosso",
	"MS": "Mato Grosso do Sul",
	"MG": "Minas Gerais",
	"PA": "Para",
	"PB": "Paraiba",
	"PR": "Parana",
	"PE": "Pernambuco",
	"PI": "Piaui",
	"RJ": "Rio de Janeiro",
	"RN": "Rio Grande do Norte",
	"RS": "Rio Grande do Sul",
	"RO": "Rondonia",
	"RR": "Roraima",
	"SC": "Santa Catarina",
	"SP": "Sao Paulo",
	"SE": "Sergipe",
	"TO": "Tocantins",
}

sigla_uf_destino_TO_POP = {
	"AC": 830018,
	"AL": 3125254,
	"AP": 733759,
	"AM": 3941613,
	"BA": 14136417,
	"CE": 8794957,
	"DF": 2817068,
	"ES": 3833712,
	"GO": 7056495,
	"MA": 6775152,
	"MT": 3658813,
	"MS": 2757013,
	"MG": 20538718,
	"PA": 8116132,
	"PB": 3974687,
	"PR": 11444380,
	"PE": 9058931,
	"PI": 3269200,
	"RJ": 16054524,
	"RN": 3302406,
	"RS": 10882965,
	"RO": 1581196,
	"RR": 636707,
	"SC": 7609601,
	"SP": 44420459,
	"SE": 2209558,
	"TO": 1511460,
}


def normalizar(texto: str) -> str:
	return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")


def carregar_dados(caminho_arquivo: str) -> pd.DataFrame:
	df = pd.read_parquet(caminho_arquivo)
	df.columns = df.columns.str.strip().str.lower()

	required = {"ano", "sigla_uf_destino", "valor_total"}
	missing = required.difference(df.columns)
	if missing:
		raise ValueError(f"Colunas ausentes: {missing}")

	df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
	df["valor_total"] = pd.to_numeric(df["valor_total"], errors="coerce")
	df["sigla_uf_destino"] = df["sigla_uf_destino"].astype(str).str.upper().str.strip()

	df = df.dropna(subset=["ano", "sigla_uf_destino", "valor_total"])
	df["ano"] = df["ano"].astype(int)
	df = df[df["ano"].between(1900, 2100)]

	df = df[df["sigla_uf_destino"].isin(sigla_uf_destino_TO_STATE.keys())]
	df = df.groupby("sigla_uf_destino", as_index=False)["valor_total"].sum()
	return df


def carregar_geojson(url: str) -> dict:
	with urlopen(url) as response:
		geojson = json.load(response)

	# Normaliza nomes para casar com os nomes mapeados das sigla_uf_destinos.
	for feature in geojson["features"]:
		nome = feature["properties"]["name"]
		feature["properties"]["name"] = normalizar(nome)

	return geojson


def preparar_visualizacao(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
	df["estado_nome"] = df["sigla_uf_destino"].map(sigla_uf_destino_TO_STATE).apply(normalizar)

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


def preparar_visualizacao_100mil_hab(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
	df_per_capita = df.copy()
	df_per_capita["populacao"] = df_per_capita["sigla_uf_destino"].map(sigla_uf_destino_TO_POP)
	df_per_capita = df_per_capita.dropna(subset=["populacao"])
	df_per_capita["valor_plot"] = (df_per_capita["valor_total"] / df_per_capita["populacao"]) * 100_000
	label = "Valor por 100 mil habitantes (R$)"

	if USAR_ESCALA_LOG:
		df_per_capita["valor_plot"] = np.log1p(df_per_capita["valor_plot"])
		label += " (escala log)"

	return df_per_capita, label


def criar_figura(df: pd.DataFrame, geojson: dict, label: str):
	fig = px.choropleth(
		df,
		geojson=geojson,
		locations="estado_nome",
		featureidkey="properties.name",
		color="valor_plot",
		color_continuous_scale="YlOrRd",
		hover_name="sigla_uf_destino",
		hover_data={"estado_nome": False, "valor_plot": ":,.2f"},
		title="Mapa Coropletico Nacional - Soma de Todos os Anos",
		labels={"valor_plot": "Valor"},
	)

	fig.update_geos(fitbounds="locations", visible=False)
	fig.update_layout(
		margin=dict(l=0, r=0, t=50, b=0),
		coloraxis_colorbar_title=label,
	)
	return fig


def criar_figura_100mil_hab(df: pd.DataFrame, geojson: dict, label: str):
	fig = px.choropleth(
		df,
		geojson=geojson,
		locations="estado_nome",
		featureidkey="properties.name",
		color="valor_plot",
		color_continuous_scale="YlOrRd",
		hover_name="sigla_uf_destino",
		hover_data={"estado_nome": False, "valor_plot": ":,.2f", "populacao": ":,.0f"},
		title="Mapa Coropletico Nacional - Soma de Todos os Anos (normalizado por 100 mil hab)",
		labels={"valor_plot": "Valor"},
	)

	fig.update_geos(fitbounds="locations", visible=False)
	fig.update_layout(
		margin=dict(l=0, r=0, t=50, b=0),
		coloraxis_colorbar_title=label,
	)
	return fig


def main():
	# TOP 10 ESTADOS

	df = carregar_dados(ARQUIVO)
	geojson = carregar_geojson(GEOJSON_URL)
	df, label = preparar_visualizacao(df)
	fig = criar_figura(df, geojson, label)
	df_100mil, label_100mil = preparar_visualizacao_100mil_hab(df)
	fig_100mil = criar_figura_100mil_hab(df_100mil, geojson, label_100mil)

	top10 = df.nlargest(27, "valor_total")
	print("Top 27 estados por investimento valor_total:")
	print(top10[["sigla_uf_destino", "valor_total"]].to_string(formatters={"valor_total": "R$ {:,.2f}".format}))

	fig.show()
	#fig.write_html(ARQUIVO_SAIDA_HTML)
	#fig.write_image(ARQUIVO_SAIDA_PNG, width=1200, height=800, scale=2)
	#fig_100mil.write_html(ARQUIVO_SAIDA_HTML_100MIL)
	#fig_100mil.write_image(ARQUIVO_SAIDA_PNG_100MIL, width=1200, height=800, scale=2)
	fig_100mil.show()



if __name__ == "__main__":
	main()
