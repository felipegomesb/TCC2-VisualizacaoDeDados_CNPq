from wordcloud import WordCloud
import plotly.graph_objs as go
import pandas as pd
from wordcloud import WordCloud

#load
ARQUIVO_PARQUET = 'dados/cnpqTcc_palavras_chave.parquet'
df = pd.read_parquet(ARQUIVO_PARQUET)

STOPWORDS = 'dados/stopwords.txt'

with open(STOPWORDS, 'r', encoding='utf-8') as f:
    STOPWORDS = set(f.read().splitlines())

# wordcloud simples

text = ' '.join(df['palavra_chave'].explode().dropna().tolist())
wordcloud = WordCloud(width=1920, height=1080, background_color='white', stopwords=STOPWORDS).generate(text)
# Criar o gráfico de barras usando Plotly
fig = go.Figure(go.Image(z=wordcloud.to_array()))
fig.update_layout(title='Word Cloud - Palavras-chave', xaxis=dict(visible=False), yaxis=dict(visible=False))
fig.show()