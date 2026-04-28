import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import unicodedata

# ================= CONFIG =================
ARQUIVO = 'dados/sankey_pronto.parquet'

# ================= LOAD =================
df = pd.read_parquet(ARQUIVO)

df['total'] = pd.to_numeric(df['total'], errors='coerce')
df = df.fillna('Não informado')


def formatar_ano(valor):
    if pd.isna(valor):
        return 'Não informado'

    try:
        return str(int(valor))
    except (TypeError, ValueError):
        return str(valor)


# ================= NORMALIZAÇÃO =================
def normalizar(texto):
    if pd.isna(texto):
        return ""
    
    texto = str(texto).upper()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = re.sub(r'[^A-Z\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto


# ================= MAPA DE CÓDIGOS =================
mapa_codigos = {

    # ================= FORMAÇÃO =================
    # Iniciação
    "IC": "Formação - Iniciação Científica",
    "ICJ": "Formação - Iniciação Científica",
    "ITI": "Formação - Iniciação Científica",
    "IT": "Formação - Iniciação Científica",
    "ITC": "Formação - Iniciação Científica",
    "IEX": "Formação - Iniciação Científica",

    # Mestrado
    "GM": "Formação - Mestrado",
    "MPE": "Formação - Mestrado",

    # Doutorado (Brasil)
    "GD": "Formação - Doutorado",

    # ================= MOBILIDADE =================
    # Doutorado sanduíche / exterior
    "SWE": "Mobilidade - Exterior",
    "SWI": "Mobilidade - Exterior",
    "SWP": "Mobilidade - Exterior",
    "GDE": "Mobilidade - Exterior",

    # Estágios / visitante / exterior geral
    "ESN": "Mobilidade - Exterior",
    "EJR": "Mobilidade - Exterior",
    "BSP": "Mobilidade - Exterior",
    "BEP": "Mobilidade - Exterior",
    "SPE": "Mobilidade - Exterior",
    "MSP": "Mobilidade - Exterior",
    "MEP": "Mobilidade - Exterior",

    # ================= CARREIRA CIENTÍFICA =================
    # Pós-doc
    "PD": "Carreira - Pós-Doutorado",
    "PDE": "Carreira - Pós-Doutorado",
    "PDJ": "Carreira - Pós-Doutorado",
    "PDS": "Carreira - Pós-Doutorado",
    "PDI": "Carreira - Pós-Doutorado",
    "PDT": "Carreira - Pós-Doutorado",
    "PDP": "Carreira - Pós-Doutorado",

    # Produtividade / pesquisador
    "PQ": "Carreira - Produtividade",
    "DT": "Carreira - Produtividade",

    # Fixação / pesquisador visitante
    "DCR": "Carreira - Fixação de Pesquisador",
    "RD": "Carreira - Fixação de Pesquisador",
    "PV": "Carreira - Fixação de Pesquisador",
    "PVE": "Carreira - Fixação de Pesquisador",

    # ================= PESQUISA =================
    # Projetos e financiamento direto
    "APQ": "Pesquisa - Auxílio à Pesquisa",
    "ARC": "Pesquisa - Auxílio à Pesquisa",
    "AED": "Pesquisa - Auxílio à Pesquisa",
    "ADC": "Pesquisa - Auxílio à Pesquisa",
    "AI": "Pesquisa - Auxílio à Pesquisa",

    # Apoio técnico (separado porque é diferente de projeto)
    "AT": "Pesquisa - Apoio Técnico",
    "ATP": "Pesquisa - Apoio Técnico",

    # ================= TECNOLOGIA & INOVAÇÃO =================
    "DTI": "Tecnologia - Desenvolvimento",
    "DES": "Tecnologia - Desenvolvimento",
    "DEJ": "Tecnologia - Desenvolvimento",
    "DTC": "Tecnologia - Desenvolvimento",
    "SDT": "Tecnologia - Desenvolvimento",
    "INT": "Tecnologia - Desenvolvimento",
    "PIN": "Tecnologia - Desenvolvimento",

    # ================= EVENTOS / DIFUSÃO =================
    "AVG": "Difusão - Eventos Científicos",
    "EXP": "Difusão - Extensão",
    "EV": "Difusão - Visitante",
    "BEV": "Difusão - Visitante",

    # ================= FALLBACK CONTROLADO =================
    # (casos que aparecem no dataset mas são raros)
    "SET": "Outros",
    "PCI": "Outros",
    "ACT": "Outros",
    "BJT": "Outros",
    "FIX": "Outros",
    "MAT": "Outros",
    "MDT": "Outros",
}


# # ================= CLASSIFICAÇÃO =================
# def classificar_modalidade(mod):
#     if pd.isna(mod):
#         return "Não informado"

#     mod_str = str(mod).upper()

#     # extrai código antes do "-"
#     codigo = mod_str.split(" - ")[0].strip()

#     # 1. tenta pelo código
#     if codigo in mapa_codigos:
#         return mapa_codigos[codigo]

#     # 2. fallback por texto normalizado
#     mod_norm = normalizar(mod_str)

#     if "POS DOUTORADO" in mod_norm:
#         return "Pós-Doutorado"
#     elif "DOUTORADO" in mod_norm:
#         return "Doutorado"
#     elif "MESTRADO" in mod_norm:
#         return "Mestrado"
#     elif "INICIACAO" in mod_norm:
#         return "Iniciação Científica"
#     elif "PRODUTIVIDADE" in mod_norm:
#         return "Produtividade"
#     elif "DESENVOLVIMENTO" in mod_norm or "TECNOLOGICO" in mod_norm:
#         return "Desenvolvimento Tecnológico"
#     elif "APOIO" in mod_norm or "AUXILIO" in mod_norm:
#         return "Auxílio à Pesquisa"

#     return "Outros"


# ================= CLASSIFICAÇÃO =================
def classificar_modalidade(mod):
    if pd.isna(mod):
        return "Não informado"

    mod_str = str(mod).upper()

    # extrai código antes do "-"
    #codigo = mod_str.split(" - ")[0].strip()

    # 1. tenta pelo código
    #if codigo in mapa_codigos:
        #return mapa_codigos[codigo]

    # 2. fallback por texto normalizado
    mod_norm = normalizar(mod_str)

    # ===== FORMAÇÃO =====
    if "POS DOUTORADO" in mod_norm:
        return "Carreira - Pós-Doutorado"

    elif "DOUTORADO" in mod_norm:
        # cuidado: pode ser sanduíche/exterior
        if "EXTERIOR" in mod_norm or "SANDUICHE" in mod_norm:
            return "Mobilidade - Doutorado - Exterior"
        return "Formação - Doutorado"

    elif "MESTRADO" in mod_norm:
        return "Formação - Mestrado"

    elif "INICIACAO" in mod_norm:
        return "Formação - Iniciação Científica"


    # ===== CARREIRA =====
    elif "PRODUTIVIDADE" in mod_norm:
        return "Carreira - Produtividade"


    # ===== TECNOLOGIA =====
    elif "DESENVOLVIMENTO" in mod_norm or "TECNOLOGICO" in mod_norm:
        return "Tecnologia - Desenvolvimento"


    # ===== PESQUISA =====
    elif "APOIO" in mod_norm or "AUXILIO" in mod_norm:
        return "Pesquisa - Auxílio à Pesquisa"


    # ===== MOBILIDADE (fallback textual) =====
    elif "EXTERIOR" in mod_norm or "VISITANTE" in mod_norm:
        return "Mobilidade - Exterior"


    return "Outros"


# aplica classificação
df['categoria'] = df['modalidade'].apply(classificar_modalidade)
df['ano_referencia'] = pd.to_numeric(df['ano_referencia'], errors='coerce')
df['ano_referencia_label'] = df['ano_referencia'].apply(formatar_ano)
df = df[~df['ano_referencia_label'].isin(['206', '2025'])]
df = df[~df['grande_area'].isin(['Não informado', 'Não se aplica'])]

# ================= AGREGAÇÃO =================
df_grouped = (
    df.groupby(['ano_referencia_label', 'grande_area', 'categoria'])['total']
    .sum()
    .reset_index()
)

ordem_categorias = (
    df_grouped.groupby('categoria')['total']
    .sum()
    .sort_values(ascending=False)
    .index
)

# aplica ordenação como categoria ordenada
df_grouped['categoria'] = pd.Categorical(
    df_grouped['categoria'],
    categories=ordem_categorias,
    ordered=True
)

# opcional: ordenar também o dataframe
df_grouped = df_grouped.sort_values(['categoria', 'total'], ascending=[True, False])

# ================= SANKEY =================
fig = go.Figure()

df_total = (
    df.groupby(['grande_area', 'categoria'])['total']
    .sum()
    .reset_index()
)


def criar_trace_sankey(df_base):
    labels = list(pd.concat([df_base['grande_area'], df_base['categoria']]).unique())
    label_to_index = {label: i for i, label in enumerate(labels)}

    return go.Sankey(
        node=dict(label=labels),
        link=dict(
            source=df_base['grande_area'].map(label_to_index),
            target=df_base['categoria'].map(label_to_index),
            value=df_base['total'].astype(float),
        ),
        visible=False
    )


anos = (
    df.loc[df['ano_referencia'].notna(), 'ano_referencia']
    .drop_duplicates()
    .sort_values()
    .map(formatar_ano)
    .tolist()
)

if df['ano_referencia'].isna().any():
    anos.append('Não informado')

# ===== TRACE 0: TODOS OS ANOS =====
trace_total = criar_trace_sankey(df_total)
trace_total.visible = True
fig.add_trace(trace_total)

# ===== TRACES POR ANO =====
for ano in anos:
    df_temp = df_grouped[df_grouped['ano_referencia_label'] == ano]
    df_temp = df_temp.groupby(['grande_area', 'categoria'])['total'].sum().reset_index()
    fig.add_trace(criar_trace_sankey(df_temp))

# ===== DROPDOWN =====
buttons = []

# botão "todas"
visible_all = [True] + [False] * len(anos)
buttons.append(dict(
    label="Todos os anos",
    method="update",
    args=[{"visible": visible_all}]
))



# botões individuais
for i, ano in enumerate(anos):
    visible = [False] * (len(anos) + 1)
    visible[i + 1] = True  # +1 por causa do "todos"

    buttons.append(dict(
        label=ano,
        method="update",
        args=[{"visible": visible}]
    ))

fig.update_layout(
    updatemenus=[dict(
        buttons=buttons,
        direction="down",
        showactive=True
    )],
    title="Investimento por Grande Área → Categoria por ano_referencia"
)

#fig.show()
fig.write_html("resultados\sankey\sankeyplot_modalidades_botao_Ano.html")

