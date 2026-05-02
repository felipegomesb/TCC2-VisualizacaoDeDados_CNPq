from wordcloud import WordCloud
import plotly.graph_objs as go
import pandas as pd
from collections import Counter
import plotly.express as px
import re

# load
ARQUIVO_PARQUET = 'dados/cnpqTcc_palavras_chave.parquet'
df = pd.read_parquet(ARQUIVO_PARQUET)

STOPWORDS = 'dados/stopwords_pesado.txt'

with open(STOPWORDS, 'r', encoding='utf-8') as f:
    STOPWORDS = set(f.read().splitlines())

# ================= TEXTO =================
text = ' '.join(df['titulo_do_projeto'].explode().dropna().tolist())

# ================= CONTADOR  =================
# limpa pontuação
text_clean = re.sub(r'[^\w\s]', ' ', text.lower())

# separa palavras
words = text_clean.split()

# remove stopwords + palavras curtas
words = [w for w in words if w not in STOPWORDS and len(w) > 3]

# conta
freq = Counter(words)

# dataframe
df_freq = pd.DataFrame(freq.items(), columns=['palavra', 'freq'])
df_freq = df_freq.sort_values(by='freq', ascending=False)

# printa top 50
print("\nTOP 50 PALAVRAS:\n")
print(df_freq.head(50))

# salva pra analisar melhor
df_freq.to_csv('dados/debug_palavras.csv', index=False)

# gráfico de barras (top 30)
top = df_freq.head(30)
fig_bar = px.bar(top, x='freq', y='palavra', orientation='h', title='Top 30 Palavras')
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
fig_bar.show()

# ================= WORDCLOUD =================
wordcloud = WordCloud(
    width=1920,
    height=1080,
    background_color='white',
    stopwords=STOPWORDS
).generate(text)

fig = go.Figure(go.Image(z=wordcloud.to_array()))
fig.update_layout(
    title='Word Cloud - Títulos',
    xaxis=dict(visible=False),
    yaxis=dict(visible=False)
)

fig.show()