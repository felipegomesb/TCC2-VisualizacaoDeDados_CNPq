from wordcloud import WordCloud
import plotly.graph_objs as go
import pandas as pd
from collections import Counter
import re
import unicodedata

# ================= CONFIG =================
ARQUIVO_PARQUET = 'dados/cnpqTcc_palavras_chave.parquet'
STOPWORDS_ARQUIVO = 'dados/stopwords.txt'

# ================= LOAD =================
df = pd.read_parquet(ARQUIVO_PARQUET)

with open(STOPWORDS_ARQUIVO, 'r', encoding='utf-8') as f:
    STOPWORDS = set(f.read().splitlines())

# ================= SINÔNIMOS =================
SINONIMOS = {
    **{
        termo: 'tecnologia'
        for termo in [
            'tecnologia', 'tecnologias',
            'tecnologica', 'tecnologicas',
            'tecnologico', 'tecnologicos',
            'tech', 'informatica', 'ti'
        ]
    },

    **{
        termo: 'IC'
        for termo in [
            'ic', 'pibic', 'pibiti',
            'pivic', 'iniciacao',
            'cientifica'
        ]
    },

    **{
        termo: 'saude'
        for termo in [
            'saude', 'saúde',
            'clinico', 'clínico',
            'tratamento', 'paciente',
            'doenca', 'doença'
        ]
    },

    **{
        termo: 'meio_ambiente'
        for termo in [
            'ambiental',
            'meio ambiente',
            'sustentabilidade',
            'sustentavel',
            'ecologia'
        ]
    }
}

# ================= STOPWORDS EXTRA =================
STOPWORDS_EXTRA = {

    # acadêmicas
    'projeto', 'projetos',
    'pesquisa', 'pesquisas',
    'pesquisador', 'pesquisadores',
    'estudo', 'analise',
    'avaliacao', 'proposta',
    'objetivo', 'objetivos',
    'metodologia', 'resultado',
    'resultados', 'metodo',
    'metodos',

    # sistemas/modelos
    'sistema', 'sistemas',
    'modelo', 'modelos',
    'simulacao', 'simulacoes',
    'processamento',
    'desenvolvimento',
    'desenv',
    'aplicacao',
    'aplicacoes',
    'ambiente',
    'base',
    'ferramenta',
    'ferramentas',
    'uso',
    'utilizacao',
    'utilizar',
    'usar',

    # institucional
    'cnpq',
    'programa',
    'programas',
    'edital',
    'editais',
    'instituicao',
    'instituicoes',
    'universidade',
    'universidades',
    'departamento',
    'centro',
    'curso',
    'instituto',
    'federal',
    'nacional',

    # tempo/contexto
    'ano',
    'anos',
    'mes',
    'meses',
    'periodo',
    'inicio',
    'fim',
    'duracao',

    # financiamento
    'bolsa',
    'bolsas',
    'bolsista',
    'bolsistas',
    'apoio',
    'auxilio',
    'financiamento',
    'fomento',
    'recursos',
    'valor',
    'valores',

    # estrutura textual
    'atividade',
    'atividades',
    'relatorio',
    'informacao',
    'informacoes',

    # ensino
    'ensino',
    'formacao',
    'graduacao',

    # geográfico
    'brasil',
    'estado',

    # anos
    '2022',
    '2023',
    '2024',

    # conectivos
    'e', 'de', 'em',
    'para', 'com',
    'do', 'dos',
    'da', 'das',
    'um', 'uma',
    'uns', 'umas',
    'o', 'os',
    'a', 'as'
}

# junta stopwords do txt + extras
STOPWORDS = STOPWORDS.union(STOPWORDS_EXTRA)

# ================= NORMALIZAÇÃO =================
def normalizar_token(w: str) -> str:

    w = w.lower().strip()

    w = ''.join(
        c for c in unicodedata.normalize("NFD", w)
        if unicodedata.category(c) != "Mn"
    )

    return SINONIMOS.get(w, w)

# ================= EXTRAÇÃO =================
def extrair_dados_palavras(df_base: pd.DataFrame):

    if 'palavra_chave' not in df_base.columns:
        return pd.DataFrame(columns=['palavra', 'freq'])

    lista_palavras = (
        df_base['palavra_chave']
        .explode()
        .dropna()
        .astype(str)
        .tolist()
    )

    if not lista_palavras:
        return pd.DataFrame(columns=['palavra', 'freq'])

    text = ' '.join(lista_palavras)

    # limpa caracteres especiais
    text_clean = re.sub(r'[^\w\s]', ' ', text.lower())

    words = text_clean.split()

    # normaliza
    words = [normalizar_token(w) for w in words]

    # remove stopwords
    words = [
        w for w in words
        if w not in STOPWORDS
        and len(w) > 2
    ]

    if not words:
        return pd.DataFrame(columns=['palavra', 'freq'])

    freq = Counter(words)

    df_freq = pd.DataFrame(
        freq.items(),
        columns=['palavra', 'freq']
    )

    df_freq = df_freq.sort_values(
        by='freq',
        ascending=False
    )

    return df_freq

# ================= ÁREAS =================
grandes_areas = sorted(
    df['grande_area'].dropna().unique()
)

grandes_areas = ['TODAS'] + grandes_areas

# ================= FIGURA =================
fig_wc_final = go.Figure()

areas_validas = []

# ================= LOOP =================
for grande_area in grandes_areas:

    print(f'\nProcessando: {grande_area}')

    if grande_area == 'TODAS':
        df_area = df
    else:
        df_area = df[df['grande_area'] == grande_area]

    print(f'Linhas: {len(df_area)}')

    df_freq = extrair_dados_palavras(df_area)

    if df_freq.empty:
        print(f'[WARNING] Sem palavras válidas para {grande_area}')
        continue

    df_freq = df_freq.head(100)

    freq_dict = dict(
        zip(df_freq['palavra'], df_freq['freq'])
    )

    if not freq_dict:
        print(f'[WARNING] freq_dict vazio -> {grande_area}')
        continue

    print(df_freq.head())

    try:

        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            stopwords=STOPWORDS
        ).generate_from_frequencies(freq_dict)

        trace = go.Image(
            z=wordcloud.to_array(),
            visible=(len(areas_validas) == 0)
        )

        fig_wc_final.add_trace(trace)

        areas_validas.append(grande_area)

        print(f'[OK] {grande_area}')

    except Exception as e:
        print(f'[ERRO] {grande_area}')
        print(e)

# ================= BOTÕES =================
buttons = []

for i, grande_area in enumerate(areas_validas):

    visible = [False] * len(areas_validas)
    visible[i] = True

    buttons.append(
        dict(
            label=grande_area,
            method="update",
            args=[
                {"visible": visible},
                {"title": f"WordCloud - {grande_area}"}
            ]
        )
    )

# ================= LAYOUT =================
fig_wc_final.update_layout(

    updatemenus=[
        dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=0.01,
            y=1.15
        )
    ],

    title="WordCloud - Palavras-chave",

    xaxis=dict(visible=False),
    yaxis=dict(visible=False),

    height=600
)

# ================= SAVE =================
fig_wc_final.write_html(
    "resultados/visualizacao_textual/wordcloud_palavraChave_botoes.html",
    include_plotlyjs='cdn'
)

fig_wc_final.write_image(
    "resultados/visualizacao_textual/wordcloud_palavraChave_botoes.svg",
    width=1200,
    height=800,
    scale=2
)

print('\nHTML salvo com sucesso!')