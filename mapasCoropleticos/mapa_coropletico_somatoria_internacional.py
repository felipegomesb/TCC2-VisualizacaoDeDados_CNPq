import re

import numpy as np
import pandas as pd
import plotly.express as px



# CONFIG
ARQUIVO = "codigos/dados/mapa_internacional.txt"
ARQUIVO_SAIDA_HTML = "codigos/resultados/mapa_coropletico_internacional_somado.html"
ARQUIVO_SAIDA_PNG = "codigos/resultados/mapa_coropletico_internacional_somado.png"

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
	df = pd.read_csv(caminho_arquivo)
	df.columns = df.columns.str.strip().str.lower()

	required = {"ano", "pais", "total"}
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
	df = df.groupby("iso_alpha", as_index=False)["total"].sum()
	return df


def preparar_visualizacao(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
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

	fig.show()
	fig.write_html(ARQUIVO_SAIDA_HTML)

	try:
		fig.write_image(ARQUIVO_SAIDA_PNG, width=1400, height=800, scale=2)
	except Exception:
		pass


if __name__ == "__main__":
	main()
