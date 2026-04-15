import json
import unicodedata
from urllib.request import urlopen

import numpy as np
import pandas as pd
import plotly.express as px



# CONFIG
ARQUIVO = "dados/mapa_geografico.txt"
ARQUIVO_SAIDA_HTML = "resultados/mapa_coropletico_nacional_somado.html"
ARQUIVO_SAIDA_PNG = "resultados/mapa_coropletico_nacional_somado.png"

GEOJSON_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

ESCALA_MILHOES = True
USAR_ESCALA_LOG = True


UF_TO_STATE = {
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


def normalizar(texto: str) -> str:
	return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")


def carregar_dados(caminho_arquivo: str) -> pd.DataFrame:
	df = pd.read_csv(caminho_arquivo)
	df.columns = df.columns.str.strip().str.lower()

	required = {"ano", "uf", "total"}
	missing = required.difference(df.columns)
	if missing:
		raise ValueError(f"Colunas ausentes: {missing}")

	df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
	df["total"] = pd.to_numeric(df["total"], errors="coerce")
	df["uf"] = df["uf"].astype(str).str.upper().str.strip()

	df = df.dropna(subset=["ano", "uf", "total"])
	df["ano"] = df["ano"].astype(int)
	df = df[df["ano"].between(1900, 2100)]

	df = df[df["uf"].isin(UF_TO_STATE.keys())]
	df = df.groupby("uf", as_index=False)["total"].sum()
	return df


def carregar_geojson(url: str) -> dict:
	with urlopen(url) as response:
		geojson = json.load(response)

	# Normaliza nomes para casar com os nomes mapeados das UFs.
	for feature in geojson["features"]:
		nome = feature["properties"]["name"]
		feature["properties"]["name"] = normalizar(nome)

	return geojson


def preparar_visualizacao(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
	df["estado_nome"] = df["uf"].map(UF_TO_STATE).apply(normalizar)

	if ESCALA_MILHOES:
		df["valor_plot"] = df["total"] / 1_000_000
		label = "Valor total (R$ milhoes)"
	else:
		df["valor_plot"] = df["total"]
		label = "Valor total"

	if USAR_ESCALA_LOG:
		df["valor_plot"] = np.log1p(df["valor_plot"])
		label += " (escala log)"

	return df, label


def criar_figura(df: pd.DataFrame, geojson: dict, label: str):
	fig = px.choropleth(
		df,
		geojson=geojson,
		locations="estado_nome",
		featureidkey="properties.name",
		color="valor_plot",
		color_continuous_scale="YlOrRd",
		hover_name="uf",
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


def main():
	# TOP 10 ESTADOS

	df = carregar_dados(ARQUIVO)
	geojson = carregar_geojson(GEOJSON_URL)
	df, label = preparar_visualizacao(df)
	fig = criar_figura(df, geojson, label)

	top10 = df.nlargest(27, "total")
	print("Top 27 estados por investimento total:")
	print(top10[["uf", "total"]].to_string(formatters={"total": "R$ {:,.2f}".format}))

	fig.show()
	fig.write_html(ARQUIVO_SAIDA_HTML)
	fig.write_image(ARQUIVO_SAIDA_PNG, width=1200, height=800, scale=2)




if __name__ == "__main__":
	main()
