from pathlib import Path
import json
import unicodedata
from urllib.request import urlopen

import pandas as pd
import plotly.express as px


# CONFIG
ARQUIVO = "dados/cnpqTcc_limpo.csv"
ARQUIVO_SAIDA_HTML = "resultados/mapas_coropleticos/mapa_coropletico_nacional_grandearea_dominante.html"
#ARQUIVO_SAIDA_PNG = "resultados/mapas_coropleticos/mapa_coropletico_nacional_grandearea_dominante.png"
#ARQUIVO_SAIDA_CSV = "resultados/mapas_coropleticos/mapa_coropletico_nacional_grandearea_dominante.csv"
GEOJSON_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
UF_COL = "sigla_uf_destino"


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

    if UF_COL not in df.columns:
        raise ValueError(f"Coluna ausente: {UF_COL}")
    if "grande_area" not in df.columns:
        raise ValueError("Coluna ausente: grande_area")

    if "total" not in df.columns:
        if "valor_pago" in df.columns:
            df = df.rename(columns={"valor_pago": "total"})
        else:
            raise ValueError("Coluna ausente: total ou valor_pago")

    df["uf"] = df[UF_COL].astype(str).str.upper().str.strip()
    df["grande_area"] = df["grande_area"].astype(str).str.strip()
    df["total"] = pd.to_numeric(df["total"], errors="coerce")

    df = df.dropna(subset=["uf", "grande_area", "total"])
    df = df[df["uf"].isin(UF_TO_STATE.keys())]

    df = df.groupby(["uf", "grande_area"], as_index=False)["total"].sum()
    df = df.loc[df.groupby("uf")["total"].idxmax()].reset_index(drop=True)
    return df


def carregar_geojson(url: str) -> dict:
    with urlopen(url) as response:
        geojson = json.load(response)

    for feature in geojson["features"]:
        feature["properties"]["name"] = normalizar(feature["properties"]["name"])

    return geojson


def preparar_visualizacao(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["estado_nome"] = df["uf"].map(UF_TO_STATE).apply(normalizar)
    return df


def criar_figura(df: pd.DataFrame, geojson: dict):
    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="estado_nome",
        featureidkey="properties.name",
        color="grande_area",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hover_name="uf",
        hover_data={"estado_nome": False, "grande_area": True, "total": ":,.2f"},
        title="Mapa Coropletico Nacional - Grande area mais investida por estado",
        labels={"grande_area": "Grande area", "total": "Investimento"},
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        legend_title_text="Grande area",
    )
    return fig


def main():
    df = carregar_dados(ARQUIVO)
    geojson = carregar_geojson(GEOJSON_URL)
    df = preparar_visualizacao(df)
    fig = criar_figura(df, geojson)

    Path(ARQUIVO_SAIDA_HTML).parent.mkdir(parents=True, exist_ok=True)
    #df.to_csv(ARQUIVO_SAIDA_CSV, index=False)

    print("Grande area dominante por estado:")
    print(df[["uf", "grande_area", "total"]].sort_values("total", ascending=False).to_string(index=False, formatters={"total": "R$ {:,.2f}".format}))

    fig.show()
    fig.write_html(ARQUIVO_SAIDA_HTML)
    #fig.write_image(ARQUIVO_SAIDA_PNG, width=1200, height=800, scale=2)


if __name__ == "__main__":
    main()
