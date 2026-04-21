import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import unicodedata

# ================= CONFIG =================
ARQUIVO = 'dados/sankey_pronto.csv'

# ================= LOAD =================
df = pd.read_csv(ARQUIVO)

df['total'] = pd.to_numeric(df['total'], errors='coerce')
df = df.fillna('Não informado')


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
    codigo = mod_str.split(" - ")[0].strip()

    # 1. tenta pelo código
    if codigo in mapa_codigos:
        return mapa_codigos[codigo]

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


# ================= AGREGAÇÃO =================
df_grouped = (
    df.groupby(['grande_area', 'categoria'])['total']
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
labels = list(pd.concat([df_grouped['grande_area'], df_grouped['categoria']]).unique())
label_to_index = {label: i for i, label in enumerate(labels)}

source = df_grouped['grande_area'].map(label_to_index)
target = df_grouped['categoria'].map(label_to_index)
value = df_grouped['total'].astype(float)


fig = go.Figure()

categorias = df_grouped['categoria'].unique()

# ===== TRACE 0: TODAS AS CATEGORIAS =====
labels_all = list(pd.concat([df_grouped['grande_area'], df_grouped['categoria']]).unique())
label_to_index_all = {label: i for i, label in enumerate(labels_all)}

source_all = df_grouped['grande_area'].map(label_to_index_all)
target_all = df_grouped['categoria'].map(label_to_index_all)
value_all = df_grouped['total'].astype(float)

fig.add_trace(go.Sankey(
    node=dict(label=labels_all),
    link=dict(source=source_all, target=target_all, value=value_all),
    visible=True  # começa mostrando tudo
))

# ===== TRACES POR CATEGORIA =====
for cat in categorias:
    df_temp = df_grouped[df_grouped['categoria'] == cat]

    labels = list(pd.concat([df_temp['grande_area'], df_temp['categoria']]).unique())
    label_to_index = {label: i for i, label in enumerate(labels)}

    source = df_temp['grande_area'].map(label_to_index)
    target = df_temp['categoria'].map(label_to_index)
    value = df_temp['total'].astype(float)

    fig.add_trace(go.Sankey(
        node=dict(label=labels),
        link=dict(source=source, target=target, value=value),
        visible=False
    ))

# ===== DROPDOWN =====
buttons = []

# botão "todas"
visible_all = [True] + [False] * len(categorias)
buttons.append(dict(
    label="Todas as categorias",
    method="update",
    args=[{"visible": visible_all}]
))

# botões individuais
for i, cat in enumerate(categorias):
    visible = [False] * (len(categorias) + 1)
    visible[i + 1] = True  # +1 por causa do "todas"

    buttons.append(dict(
        label=cat,
        method="update",
        args=[{"visible": visible}]
    ))

fig.update_layout(
    updatemenus=[dict(
        buttons=buttons,
        direction="down",
        showactive=True
    )],
    title="Investimento por Grande Área → Categoria"
)

fig.show()
#fig.write_html("resultados\sankeyplot_modalidades_detalhado.html")

