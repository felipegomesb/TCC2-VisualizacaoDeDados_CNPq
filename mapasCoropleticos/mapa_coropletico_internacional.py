import re
import numpy as np
import pandas as pd
import plotly.express as px


# CONFIG
ARQUIVO = "dados/coropletico_internacional.parquet"
ARQUIVO_SAIDA_HTML = "resultados/mapas_coropleticos/mapa_coropletico_internacional.html"
ARQUIVO_SAIDA_SVG = "resultados/mapas_coropleticos/mapa_coropletico_internacional.svg"
ANIMAR_POR_ANO = True
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



# FUNÇÕES
def extrair_iso3(valor_pais_destino: str) -> str | None:
    if pd.isna(valor_pais_destino):
        return None

    texto = str(valor_pais_destino).strip().upper()

    if not texto or "NAO INFORMADA" in texto:
        return None

    # tenta pegar ISO no início
    match = re.match(r"^([A-Z]{3})", texto)
    if match:
        codigo = match.group(1)
        return ISO3_FIX.get(codigo, codigo)

    return None


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

    # remove anos irregulares
    df = df[df["ano"].between(1900, 2100)]

    # agrega
    df = df.groupby(["ano", "iso_alpha"], as_index=False)["valor_total"].sum()

    return df


def preparar_visualizacao(df: pd.DataFrame) -> pd.DataFrame:
    df["pais_destino_nome"] = df["iso_alpha"]

    # escala
    if ESCALA_MILHOES:
        df["valor_plot"] = df["valor_total"] / 1_000_000
        label = "Valor (R$ milhões)"
    else:
        df["valor_plot"] = df["valor_total"]
        label = "Valor"


    if USAR_ESCALA_LOG:
        df["valor_plot"] = np.log1p(df["valor_plot"])
        label += " (escala log)"

    df["label"] = label

    return df


def criar_figura(df: pd.DataFrame):
    fig = px.choropleth(
        df,
        locations="iso_alpha",
        locationmode="ISO-3",
        color="valor_plot",
        animation_frame="ano" if ANIMAR_POR_ANO else None,
        color_continuous_scale="YlOrRd",
        projection="natural earth",
        hover_name="pais_destino_nome",
        hover_data={
            "valor_plot": ":,.2f",
            "ano": True,
            "iso_alpha": False
        },
        title="Mapa Coroplético Internacional - Investimento por País",
        labels={"valor_plot": "Valor"},
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        transition_duration=300,
        coloraxis_colorbar_title=df["label"].iloc[0]
    )

    return fig


def main():
    df = carregar_dados(ARQUIVO)
    df = preparar_visualizacao(df)

    fig = criar_figura(df)

    #fig.show()
    #fig.write_html(ARQUIVO_SAIDA_HTML)
    fig.write_image(ARQUIVO_SAIDA_SVG)



# RUN
if __name__ == "__main__":
    main()