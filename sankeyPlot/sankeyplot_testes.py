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

def formatar_ano(valor):
    if pd.isna(valor):
        return 'Não informado'
    try:
        return str(int(valor))
    except:
        return str(valor)


def agrupar_ano(ano):
     if pd.isna(ano):
         return 'Não informado'

     ano = int(ano)

     if 2004 <= ano <= 2010:
         return '2004-2010'
     elif 2011 <= ano <= 2017:
         return '2011-2017'
     elif 2018 <= ano <= 2024:
         return '2018-2024'
     else:
         return 'Fora do recorte'



    


df['ano_label'] = df['ano_referencia'].apply(agrupar_ano)
df = df[df['ano_label'] != 'Não informado']
df = df[df['ano_label'] != 'Fora do recorte']
df = df[~df['grande_area'].isin(['Não informado', 'Não se aplica'])]


# ================= AGREGAÇÃO =================
df_grouped = (
    df.groupby(['grande_area', 'categoria', 'ano_label'])['total']
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
    visible=True  
))

labels = list(pd.concat([
    df_grouped['grande_area'],
    df_grouped['categoria'],
    df_grouped['ano_label']
]).unique())

label_to_index = {label: i for i, label in enumerate(labels)}

# Grande Área → Categoria
source_1 = df_grouped['grande_area'].map(label_to_index)
target_1 = df_grouped['categoria'].map(label_to_index)
value_1  = df_grouped['total']

# Categoria → Ano
source_2 = df_grouped['categoria'].map(label_to_index)
target_2 = df_grouped['ano_label'].map(label_to_index)
value_2  = df_grouped['total']

source = pd.concat([source_1, source_2])
target = pd.concat([target_1, target_2])
value  = pd.concat([value_1, value_2])


#BOTAO -> FILTRAR POR GRANDE AREA

# build traces: global + one per grande_area
fig = go.Figure()

# global trace (all grande_areas)
fig.add_trace(go.Sankey(
    node=dict(label=labels),
    link=dict(source=source, target=target, value=value),
    visible=True,
))

grandes_areas = df_grouped['grande_area'].drop_duplicates().tolist()

for ga in grandes_areas:
    df_sub = df_grouped[df_grouped['grande_area'] == ga]
    # build nodes for this subset
    labels_sub = list(pd.concat([df_sub['grande_area'], df_sub['categoria'], df_sub['ano_label']]).unique())
    idx = {lab: i for i, lab in enumerate(labels_sub)}

    # links: grande_area -> categoria and categoria -> ano
    s1 = df_sub['grande_area'].map(idx)
    t1 = df_sub['categoria'].map(idx)
    v1 = df_sub['total']

    s2 = df_sub['categoria'].map(idx)
    t2 = df_sub['ano_label'].map(idx)
    v2 = df_sub['total']

    s = pd.concat([s1, s2])
    t = pd.concat([t1, t2])
    v = pd.concat([v1, v2])

    fig.add_trace(go.Sankey(node=dict(label=labels_sub), link=dict(source=s, target=t, value=v), visible=False))

# dropdown buttons: All + one per grande_area
buttons = []
visible_all = [True] + [False] * len(grandes_areas)
buttons.append(dict(label='Todas as grandes áreas', method='update', args=[{'visible': visible_all}, {'title': 'Grande Área → Categoria → Ano'}]))

for i, ga in enumerate(grandes_areas):
    vis = [False] * (1 + len(grandes_areas))
    vis[i + 1] = True
    buttons.append(dict(label=ga, method='update', args=[{'visible': vis}, {'title': f'Grande Área: {ga} → Categoria → Ano'}]))

fig.update_layout(title='Grande Área → Categoria → Ano', updatemenus=[dict(buttons=buttons, direction='down', showactive=True, x=0.0, y=1.1)])

#fig.show()
fig.write_html('resultados/sankey/sankeyplot_button_modalidades.html')

