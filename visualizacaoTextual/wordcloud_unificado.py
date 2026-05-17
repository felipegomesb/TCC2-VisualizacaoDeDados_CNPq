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

# SINONIMOS

SINONIMOS = {
    **{termo: 'tecnologia' 
       for termo in [
           'tecnologia', 'tecnologias',
           'tecnologica', 'tecnologicas',
           'tecnologico', 'tecnologicos',
           'tech', 'informatica', 'ti'
       ]},
    **{termo: 'IC'
       for termo in [
           'ic', 'pibic', 'pibiti', 'pivic',
           'iniciacao', 'cientifica'
       ]},
    **{termo: 'saude'
       for termo in [
            'saude', 'saúde', 'clinico', 'clínico',
            'tratamento', 'paciente', 'doenca', 'doença'
       ]},
    **{termo: 'meio_ambiente' 
       for termo in [
            'ambiental', 'meio ambiente', 'sustentabilidade',
            'sustentavel', 'ecologia'
            ]}

}


# ================= STOPWORDS =================
STOPWORDS_EXTRA = {
    # === genéricas acadêmicas ===
    'projeto', 'projetos', 'pesquisa', 'pesquisas',
    'pesquisador', 'pesquisadores',
    'estudo', 'analise', 'avaliacao',
    'proposta', 'objetivo', 'objetivos',
    'metodologia', 'resultado', 'resultados',
    'metodo', 'metodos',

    # === sistemas e modelos ===
    'sistema', 'sistemas', 'modelo', 'modelos',
    'simulacao', 'simulacoes',
    'processamento', 'desenvolvimento', 'desenv',
    'aplicacao', 'aplicacoes', 'ambiente',
    'base', 'ferramenta', 'ferramentas',
    'uso', 'utilizacao', 'utilizar', 'usar',

    # === estrutura institucional ===
    'cnpq', 'programa', 'programas',
    'edital', 'editais',
    'instituicao', 'instituicoes',
    'universidade', 'universidades',
    'departamento', 'centro', 'curso',
    'instituto', 'federal', 'nacional',

    # === tempo / contexto ===
    'ano', 'anos', 'mes', 'meses',
    'periodo', 'inicio', 'fim',
    'duracao',

    # === financiamento ===
    'bolsa', 'bolsas', 'bolsista', 'bolsistas',
    'apoio', 'auxilio', 'financiamento',
    'fomento', 'recursos', 'valor', 'valores',

    # === estrutura textual ===
    'atividade', 'atividades',
    'relatorio', 
    'informacao', 'informacoes',

    # === ensino genérico ===
    'ensino', 'formacao', 'graduacao',

    # === geográfico ===
    'brasil', 'estado',

    # === números comuns ===
    '2022', '2023', '2024',
    
    # === preposições/conjunções que passam pelo regex ===
    'e', 'de', 'em', 'para', 'com', 'do', 'dos', 'da', 'das',
    'um', 'uma', 'uns', 'umas', 'o', 'os', 'a', 'as'
}

STOPWORDS = set(STOPWORDS_EXTRA)

# ================= FUNÇÃO =================
def extrair_dados_palavras(df_base: pd.DataFrame):
    textos = []
    for coluna in ['palavra_chave', 'titulo_do_projeto']:
        textos.extend(df_base[coluna].explode().dropna().astype(str).tolist())
    text = ' '.join(textos)
    
    text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text_clean.split()

 
    words = [normalizar_token(w) for w in words]
    words = [w for w in words if w not in STOPWORDS and len(w) > 4]
    freq = Counter(words)

    df_freq = pd.DataFrame(freq.items(), columns=['palavra', 'freq'])
    df_freq = df_freq.sort_values(by='freq', ascending=False)


    return df_freq

def normalizar_token(w: str) -> str:
    
    w = w.lower().strip()
    w = ''.join(
        c for c in unicodedata.normalize("NFD", w)
        if unicodedata.category(c) != "Mn"
    )
    return SINONIMOS.get(w, w)

# ================= PREPARAR ÁREAS =================
grandes_areas = sorted(df['grande_area'].dropna().unique())
grandes_areas = ['TODAS'] + grandes_areas

# ================= FIGURA =================
fig_wc_final = go.Figure()

# ================= LOOP =================
for i, grande_area in enumerate(grandes_areas):

    if grande_area == 'TODAS':
        df_area = df
    else:
        df_area = df[df['grande_area'] == grande_area]

    df_freq = extrair_dados_palavras(df_area)


  
    df_freq = df_freq.head(100)
    freq_dict = dict(zip(df_freq['palavra'], df_freq['freq']))

    df_freq.to_csv(f"resultados/visualizacao_textual/wordcloud_unificado_freq_{grande_area}.csv", index=False)
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=STOPWORDS
    ).generate_from_frequencies(freq_dict)

    trace = go.Image(
        z=wordcloud.to_array(),
        visible=(i == 0)
    )

    fig_wc_final.add_trace(trace)

# ================= BOTÕES =================
buttons = []

for i, grande_area in enumerate(grandes_areas):
    visible = [False] * len(grandes_areas)
    visible[i] = True

    buttons.append(dict(
        label=grande_area,
        method="update",
        args=[
            {"visible": visible},
            {"title": f"WordCloud - {grande_area}"}
        ]
    ))

# ================= LAYOUT =================
fig_wc_final.update_layout(
    updatemenus=[dict(
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0.01,
        y=1.15
    )],
    title="WordCloud - Unificado - Títulos e Palavras-chave",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    height=600
)

# PRA NÃO FICAR GIGANTE
fig_wc_final.write_html(
    "resultados/visualizacao_textual/wordcloud_unificado_botoes.html",
    include_plotlyjs='cdn'
)

