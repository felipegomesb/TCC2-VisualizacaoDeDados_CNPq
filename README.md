# TCC — Visualização de Dados do CNPq

Visualizações interativas desenvolvidas como parte do Trabalho de Conclusão de Curso, com foco em dados abertos de bolsas e auxílios concedidos pelo CNPq. Todos os gráficos abaixo são interativos e podem ser acessados diretamente pelo navegador.

## Resultados

### 📊 Hierárquicos

Distribuição dos recursos por grande área e área do conhecimento.

| Visualização | Descrição |
|---|---|
| [Treemap — Áreas do Conhecimento](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/hierarquicos/treemap_areasDoConhecimento.html) | Proporção de recursos entre grandes áreas e áreas do conhecimento em formato de retângulos aninhados |
| [Sunburst — Áreas do Conhecimento](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/hierarquicos/sunburst_areasDoConhecimento.html) | Mesma hierarquia do treemap, representada em anéis radiais |

### 🗺️ Mapas Coropléticos

Distribuição geográfica dos valores concedidos, nos recortes nacional e internacional.

| Visualização | Descrição |
|---|---|
| [Mapa nacional animado](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/mapas_coropleticos/mapa_coropletico.html) | Evolução anual dos valores concedidos por estado |
| [Mapa internacional animado](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/mapas_coropleticos/mapa_coropletico_internacional.html) | Evolução anual dos valores concedidos por país |
| [Mapa nacional — somatória](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/mapas_coropleticos/mapa_coropletico_nacional_somado.html) | Total acumulado de valores concedidos por estado, em todo o período |
| [Mapa internacional — somatória](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/mapas_coropleticos/mapa_coropletico_internacional_somado.html) | Total acumulado de valores concedidos por país, em todo o período |
| [Mapa nacional animado — normalizado por 100 mil habitantes](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/mapas_coropleticos/mapa_coropletico_por_100mil_hab.html) | Evolução anual dos valores por estado, normalizada pela população |
| [Mapa nacional — somatória normalizada por 100 mil habitantes](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/mapas_coropleticos/mapa_coropletico_nacional_somado_100milhab.html) | Total acumulado por estado, normalizado pela população |
| [Mapa internacional por grande área](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/mapas_coropleticos/mapa_coropletico_internacional_grandearea.html) | Distribuição dos valores concedidos por país, segmentada por grande área do conhecimento |
| [Mapa nacional — grande área dominante](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/mapas_coropleticos/mapa_coropletico_nacional_grandearea_dominante.html) | Estado colorido conforme a grande área do conhecimento com maior volume de recursos |

### 🔀 Fluxo (Sankey)

Fluxo dos recursos entre modalidades, categorias e anos.

| Visualização | Descrição |
|---|---|
| [Sankey — modalidades (com filtro por categoria)](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/sankey/sankeyplot_button_modalidades.html) | Fluxo de valores entre modalidades de bolsa/auxílio, filtrável por categoria |
| [Sankey — categoria (com filtro por modalidade)](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/sankey/sankeyplot_button_categoria.html) | Fluxo de valores entre categorias, filtrável por modalidade |
| [Sankey — modalidades por ano](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/sankey/sankeyplot_modalidades_botao_Ano.html) | Fluxo de valores entre modalidades, filtrável por ano |

### 🌊 Streamgraph

Evolução temporal dos valores concedidos por grande área do conhecimento.

| Visualização | Descrição |
|---|---|
| [Streamgraph — grande área (interativo)](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/streamgraph/streamgraph_grande_area_interativo.html) | Mesma visualização, com filtros e interações habilitadas |

### ☁️ Nuvens de Palavras

Termos mais frequentes nos títulos e palavras-chave dos projetos financiados.

| Visualização | Descrição |
|---|---|
| [Wordcloud — palavras-chave (com botões de filtro)](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/visualizacao_textual/wordcloud_palavraChave_botoes.html) | Termos mais frequentes nas palavras-chave dos projetos |
| [Wordcloud — títulos (com botões de filtro)](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/visualizacao_textual/wordcloud_titulo_botoes.html) | Termos mais frequentes nos títulos dos projetos |
| [Wordcloud — unificado (com botões de filtro)](https://felipegomesb.github.io/TCC2-VisualizacaoDeDados_CNPq/resultados/visualizacao_textual/wordcloud_unificado_botoes.html) | Combinação de títulos e palavras-chave |
