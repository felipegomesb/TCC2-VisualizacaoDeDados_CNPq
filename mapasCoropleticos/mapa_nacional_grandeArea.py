from pathlib import Path
import json
import unicodedata
from urllib.request import urlopen

import pandas as pd
import plotly.express as px


# ================= CONFIG =================
ARQUIVO = "dados/cnpqBolsasCompleto.parquet"

ARQUIVO_SAIDA_HTML = (
    "resultados/mapas_coropleticos/"
    "mapa_coropletico_nacional_grandearea_dominante.html"
)

GEOJSON_URL = (
    "https://raw.githubusercontent.com/"
    "codeforamerica/click_that_hood/master/"
    "public/data/brazil-states.geojson"
)

ARQUIVO_SAIDA_SVG = (
    "resultados/mapas_coropleticos/"
    "mapa_coropletico_nacional_grandearea_dominante.svg"
)

UF_COL = "sigla_uf_destino"


# ================= UFs =================
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


# ================= NORMALIZAÇÃO =================
def normalizar(texto: str) -> str:

    return (
        unicodedata
        .normalize("NFKD", texto)
        .encode("ASCII", "ignore")
        .decode("ASCII")
    )


# ================= PARSE VALOR =================
def parse_valor(valor):

    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    valor = (
        valor
        .replace("R$", "")
        .replace("$", "")
        .strip()
    )

    # formato brasileiro
    if "," in valor:

        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")

    # múltiplos pontos
    elif valor.count(".") > 1:

        valor = valor.replace(".", "")

    try:
        return float(valor)

    except:
        return None


# ================= LOAD =================
def carregar_dados(caminho_arquivo: str) -> pd.DataFrame:

    # parquet
    df = pd.read_parquet(caminho_arquivo)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    # validação
    colunas_necessarias = [
        UF_COL,
        "grande_area",
        "valor_pago"
    ]

    for col in colunas_necessarias:

        if col not in df.columns:
            raise ValueError(f"Coluna ausente: {col}")

    # ================= LIMPEZA =================
    df["uf"] = (
        df[UF_COL]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df["grande_area"] = (
        df["grande_area"]
        .astype(str)
        .str.strip()
    )

    df["total"] = (
        df["valor_pago"]
        .apply(parse_valor)
    )

    # remove inválidos
    df = df.dropna(
        subset=[
            "uf",
            "grande_area",
            "total"
        ]
    )

    # apenas UFs válidas
    df = df[
        df["uf"].isin(UF_TO_STATE.keys())
    ]

    # ================= AGREGAÇÃO =================
    df_grouped = (
        df.groupby(
            ["uf", "grande_area"],
            as_index=False
        )["total"]
        .sum()
    )

    # pega grande área dominante
    df_grouped = (
        df_grouped.loc[
            df_grouped.groupby("uf")["total"].idxmax()
        ]
        .reset_index(drop=True)
    )

    return df_grouped


# ================= GEOJSON =================
def carregar_geojson(url: str) -> dict:

    with urlopen(url) as response:

        geojson = json.load(response)

    for feature in geojson["features"]:

        feature["properties"]["name"] = normalizar(
            feature["properties"]["name"]
        )

    return geojson


# ================= PREP VIS =================
def preparar_visualizacao(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df["estado_nome"] = (
        df["uf"]
        .map(UF_TO_STATE)
        .apply(normalizar)
    )

    return df


# ================= FIGURA =================
def criar_figura(df: pd.DataFrame, geojson: dict):

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="estado_nome",
        featureidkey="properties.name",

        color="grande_area",

        color_discrete_sequence=px.colors.qualitative.Set3,

        hover_name="uf",

        hover_data={
            "estado_nome": False,
            "grande_area": True,
            "total": ":,.2f",
        },

        title=(
            "Mapa Coroplético Nacional - "
            "Grande Área Mais Investida por Estado"
        ),

        labels={
            "grande_area": "Grande Área",
            "total": "Investimento",
        },
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=50,
            b=0
        ),

        legend_title_text="Grande Área",
    )

    return fig


# ================= MAIN =================
def main():

    df = carregar_dados(ARQUIVO)

    geojson = carregar_geojson(GEOJSON_URL)

    df = preparar_visualizacao(df)

    fig = criar_figura(df, geojson)

    Path(
        ARQUIVO_SAIDA_HTML
    ).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\n===== GRANDE ÁREA DOMINANTE =====\n")

    print(
        df[
            ["uf", "grande_area", "total"]
        ]
        .sort_values(
            "total",
            ascending=False
        )
        .to_string(
            index=False,
            formatters={
                "total": "R$ {:,.2f}".format
            }
        )
    )

    #fig.show()
    #fig.write_html(ARQUIVO_SAIDA_HTML)
    fig.write_image(ARQUIVO_SAIDA_SVG, width=1400, height=800, scale=2)
    
    #print(
    #    f"\nHTML salvo em:\n"
    #    f"{ARQUIVO_SAIDA_HTML}"
    #)


if __name__ == "__main__":
    main()