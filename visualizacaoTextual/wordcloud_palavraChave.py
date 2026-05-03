from wordcloud import WordCloud
import plotly.graph_objs as go
import pandas as pd
from collections import Counter
import re

# ================= CONFIG =================
ARQUIVO_PARQUET = 'dados/cnpqTcc_palavras_chave.parquet'
STOPWORDS_ARQUIVO = 'dados/stopwords.txt'

# ================= LOAD =================
df = pd.read_parquet(ARQUIVO_PARQUET)

with open(STOPWORDS_ARQUIVO, 'r', encoding='utf-8') as f:
    STOPWORDS = set(f.read().splitlines())

# ================= FUNÇÃO =================
def extrair_dados_palavras(df_base: pd.DataFrame):
    text = ' '.join(df_base['palavra_chave'].explode().dropna().tolist())
    
    text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text_clean.split()

    words = [w for w in words if w not in STOPWORDS and len(w) > 3]

    freq = Counter(words)

    df_freq = pd.DataFrame(freq.items(), columns=['palavra', 'freq'])
    df_freq = df_freq.sort_values(by='freq', ascending=False)

    return df_freq

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

    # LIMITA 
    df_freq = df_freq.head(100)

    # EFICIENTE
    freq_dict = dict(zip(df_freq['palavra'], df_freq['freq']))

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
    title="WordCloud - Palavras-chave",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    height=600
)

# PRA NÃO FICAR GIGANTE
fig_wc_final.write_html(
    "resultados/visualizacao_textual/wordcloud_palavraChave_botoes.html",
    include_plotlyjs='cdn'
)

