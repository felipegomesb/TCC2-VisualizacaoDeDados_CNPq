import json
import unicodedata
from urllib.request import urlopen

import pandas as pd
import plotly.express as px



# CONFIG
ARQUIVO = "dados/mapa_geografico.txt"
GEOJSON_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"



# FUNÇÕES
def normalizar(texto: str) -> str:
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')


def carregar_dados(caminho_arquivo: str) -> pd.DataFrame:
    df = pd.read_csv(caminho_arquivo)

    # padronizar colunas
    df.columns = df.columns.str.strip().str.lower()

    # validar
    required = {"ano", "uf", "total"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {missing}")

    # tipos
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
    df["total"] = pd.to_numeric(df["total"], errors="coerce")
    df["uf"] = df["uf"].astype(str).str.upper().str.strip()

    # limpar
    df = df.dropna(subset=["ano", "uf", "total"])
    df["ano"] = df["ano"].astype(int)

    return df


def carregar_geojson(url: str) -> dict:
    with urlopen(url) as response:
        geojson = json.load(response)

    # normalizar nomes dos estados do geojson
    for feature in geojson["features"]:
        nome = feature["properties"]["name"]
        feature["properties"]["name"] = normalizar(nome)

    return geojson


def main():
    df = carregar_dados(ARQUIVO)
    geojson = carregar_geojson(GEOJSON_URL)

    
    # MAPEAR UF → NOME ESTADO
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

    df["estado_nome"] = df["uf"].map(UF_TO_STATE)
    df = df.dropna(subset=["estado_nome"])

    # normalizar nomes
    df["estado_nome"] = df["estado_nome"].apply(normalizar)

    
    # AGRUPAR 
    df = df.groupby(["ano", "estado_nome", "uf"], as_index=False)["total"].sum()

    
    # MELHORAR ESCALA 
    df["total_milhoes"] = df["total"] / 1_000_000 # POR MILHOES

    
    # MAPA
    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="estado_nome",
        featureidkey="properties.name",
        color="total_milhoes",
        animation_frame="ano",
        hover_name="uf",
        hover_data={"estado_nome": False, "total_milhoes": ":,.2f"},
        color_continuous_scale="YlOrRd",
        title="Investimento do CNPq por Estado ao Longo dos Anos",
        labels={"total_milhoes": "R$ (milhões)"},
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        transition_duration=500
    )

    fig.show()
    fig.write_html("resultados/mapa_coropletico.html")


    



# RUN
if __name__ == "__main__":
    main()