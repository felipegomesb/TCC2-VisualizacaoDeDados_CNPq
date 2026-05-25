import json
import unicodedata
from urllib.request import urlopen

import pandas as pd
import plotly.express as px



# CONFIG
ARQUIVO = "dados/coropletico_nacional.parquet"
GEOJSON_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
ARQUIVO_SAIDA_ABSOLUTO = "resultados/mapas_coropleticos/mapa_coropletico.html"
ARQUIVO_SAIDA_PER_CAPITA = "resultados/mapas_coropleticos/mapa_coropletico_por_100mil_hab.html"



# FUNÇÕES
def normalizar(texto: str) -> str:
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')


def carregar_dados(caminho_arquivo: str) -> pd.DataFrame:
    df = pd.read_parquet(caminho_arquivo)

    # padronizar colunas
    df.columns = df.columns.str.strip().str.lower()

    # validar
    required = {"ano", "sigla_uf_destino", "valor_total"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {missing}")

    # tipos
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
    df["valor_total"] = pd.to_numeric(df["valor_total"], errors="coerce")
    df["sigla_uf_destino"] = df["sigla_uf_destino"].astype(str).str.upper().str.strip()

    # limpar
    df = df.dropna(subset=["ano", "sigla_uf_destino", "valor_total"])
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

    
    # MAPEAR sigla_UF_destino → NOME ESTADO
    sigla_UF_destino_TO_STATE = {
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

    # Populacao residente por sigla_UF_destino (Censo 2022/IBGE, aproximado para normalizacao)
    sigla_UF_destino_TO_POP = {
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

    df["estado_nome"] = df["sigla_uf_destino"].map(sigla_UF_destino_TO_STATE)
    df = df.dropna(subset=["estado_nome"])

    # normalizar nomes
    df["estado_nome"] = df["estado_nome"].apply(normalizar)

    
    # AGRUPAR 
    df = df.groupby(["ano", "estado_nome", "sigla_uf_destino"], as_index=False)["valor_total"].sum()

    
    # MELHORAR ESCALA 
    df["valor_total_milhoes"] = df["valor_total"] / 1_000_000 # POR MILHOES
    df["populacao"] = df["sigla_uf_destino"].map(sigla_UF_destino_TO_POP)
    df["valor_total_por_100mil_hab"] = (df["valor_total"] / df["populacao"]) * 100_000

    
    # MAPA
    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="estado_nome",
        featureidkey="properties.name",
        color="valor_total_milhoes",
        animation_frame="ano",
        hover_name="sigla_uf_destino",
        hover_data={"estado_nome": False, "valor_total_milhoes": ":,.2f"},
        color_continuous_scale="YlOrRd",
        title="Investimento do CNPq por Estado ao Longo dos Anos",
        labels={"valor_total_milhoes": "R$ (milhões)"},
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        transition_duration=500
    )

    fig_per_capita = px.choropleth(
        df,
        geojson=geojson,
        locations="estado_nome",
        featureidkey="properties.name",
        color="valor_total_por_100mil_hab",
        animation_frame="ano",
        hover_name="sigla_uf_destino",
        hover_data={"estado_nome": False, "valor_total_por_100mil_hab": ":,.2f", "populacao": ":,.0f"},
        color_continuous_scale="YlOrRd",
        title="Investimento do CNPq por Estado (normalizado por 100 mil habitantes)",
        labels={"valor_total_por_100mil_hab": "R$ por 100 mil hab"},
    )

    fig_per_capita.update_geos(fitbounds="locations", visible=False)
    fig_per_capita.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        transition_duration=500
    )

    
    #fig.show()
    fig.write_html(ARQUIVO_SAIDA_ABSOLUTO)
    fig_per_capita.write_html(ARQUIVO_SAIDA_PER_CAPITA)
    fig_per_capita.show()

    



# RUN
if __name__ == "__main__":
    main()