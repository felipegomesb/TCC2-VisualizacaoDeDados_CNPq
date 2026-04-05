
""""
import plotly.express as px
df = px.data.tips()
fig = px.treemap(df, path=[px.Constant("all"), 'sex', 'day', 'time'],
                 values='total_bill', color='day')
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
fig.show()
"""

import plotly.express as px
import pandas as pd

#config
ARQUIVO = 'dados/treemap_novo.txt'

#leitura do arquivo
df = pd.read_csv(ARQUIVO)
df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
df = df.fillna('Não informado')
#criando o gráfico "grande_area","area","subarea","valor"
fig = px.treemap(df, path=[px.Constant("Areas do conhecimento"), 'grande_area', 'area', 'subarea'], values='valor', color='grande_area')

fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
fig.update_traces(
    hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<extra></extra>'
)

fig.write_html("resultados/treemap_areasDoConhecimento.html")
fig.show()