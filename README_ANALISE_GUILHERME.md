# Analise complementar - Guilherme

Esta entrega adiciona uma versao complementar da analise Gapminder com notebook limpo para apresentacao, funcoes auxiliares em `src/` e HTML final exportado.

## Arquivos adicionados

```text
data/raw/gapminder_full.csv
data/external/world_bank_gini_infant_mortality_1952_2007.csv
data/external/gapminder_2007_world_bank_enriched.csv
notebooks/analise_gapminder.ipynb
reports/analise_gapminder.html
src/advanced_analysis.py
src/notebook_state.py
src/report_builder.py
requirements_guilherme.txt
```

## Como executar

Instale as dependencias:

```bash
pip install -r requirements_guilherme.txt
```

Abra o notebook:

```text
notebooks/analise_gapminder.ipynb
```

O notebook esta sem outputs salvos para facilitar a apresentacao. As celulas de analise carregam automaticamente o estado minimo quando executadas isoladamente.

No final, execute a ultima celula para gerar o HTML:

```text
reports/analise_gapminder.html
```

## Conteudo da analise

- limpeza e validacao do Gapminder;
- tendencias globais de expectativa de vida, PIB per capita e populacao;
- comparacao por continente;
- relacao entre PIB per capita e expectativa de vida;
- rankings e crescimento entre 1952 e 2007;
- correlacoes Pearson e Spearman;
- regressao exploratoria e regressao quantilica;
- dados externos do Banco Mundial: Gini e mortalidade infantil;
- mapa mundial e graficos interativos em HTML.
