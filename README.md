# Trabalho Final - Python para Ciencia de Dados

Projeto desenvolvido em grupo para a pos-graduacao em IA e Machine Learning da PUC.

O objetivo deste repositorio e centralizar os dados, notebooks, scripts e documentacao usados no trabalho final. Cada integrante pode criar seu proprio notebook e escolher a ferramenta que preferir para executar o projeto localmente.

## Estrutura do projeto

```text
.
├── datasets/      # Bases de dados utilizadas no projeto
├── notebook/     # Notebooks individuais ou exploratorios
├── docs/          # Documentos, enunciado e materiais de apoio
├── src/           # Scripts e funcoes auxiliares
├── pyproject.toml # Metadados e dependencias usadas para criar o ambiente local
└── uv.lock        # Lockfile para quem optar por usar uv
```

## Requisitos

Recomendado:

- Python 3.12 ou superior
- Git
- Alguma ferramenta para executar notebooks, como JupyterLab, VS Code, PyCharm ou outra de sua preferencia

Dependencias principais usadas no projeto:

- `pandas`
- `matplotlib`
- `seaborn`
- `jupyterlab`

As dependências oficiais do projeto estão declaradas no arquivo `pyproject.toml`. Cada integrante deve criar localmente o seu próprio ambiente Python utilizando as dependências declaradas no `pyproject.toml`.

A pasta `.venv/` não é versionada porque ambientes virtuais possuem arquivos específicos do sistema operacional.

## Como obter o projeto

Como este é um trabalho em grupo, o fluxo recomendado de cada integrante é criar um fork do repositorio principal. Assim, cada pessoa trabalha na propria cópia e depois envia a suas alterações por Pull Request.

Passos recomendados:

1. Acesse o repositorio principal:

```text
https://github.com/RodrigoEmygdio/TRABALHO_PYTHON_CIENCIAS_DADOS
```

2. Clique em `Fork` no GitHub para criar uma cópia do repositorio na sua conta.
3. Clone o seu fork localmente:

```bash
git clone https://github.com/SEU_USUARIO/TRABALHO_PYTHON_CIENCIAS_DADOS.git
cd TRABALHO_PYTHON_CIENCIAS_DADOS
```

4. Configure o repositorio principal do trabalho como `upstream`:

```bash
git remote add upstream https://github.com/RodrigoEmygdio/TRABALHO_PYTHON_CIENCIAS_DADOS.git
```

Nesse fluxo:

- `origin` aponta para o fork do integrante, criado na conta GitHub dele;
- `upstream` aponta para o repositorio principal do trabalho, usado como fonte oficial para buscar atualizações.

## Formas de iniciar localmente

Você não precisa usar uma ferramenta especifica. Escolha uma das opções abaixo conforme o seu ambiente.

### Opcao 1: Usando uv

Se você já usa `uv`, ele cria ou atualiza o ambiente local `.venv/` a partir do `pyproject.toml`:

```bash
uv sync
```

Depois, abra o JupyterLab:

```bash
uv run jupyter lab
```

### Opcao 2: Usando venv e pip

Crie um ambiente virtual local:

```bash
python -m venv .venv
```

Ative o ambiente:

```bash
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install .
```

Inicie o JupyterLab:

```bash
jupyter lab
```

### Opcao 3: Usando Conda ou Mamba

Crie um ambiente com a versão recomendada do Python:

```bash
conda create -n trabalho-final python=3.12
```

Ative o ambiente:

```bash
conda activate trabalho-final
```

Instale as dependências declaradas no `pyproject.toml`:

```bash
pip install .
```

Inicie o JupyterLab:

```bash
jupyter lab
```

Se preferir `mamba`, os comandos sao equivalentes:

```bash
mamba create -n trabalho-final python=3.12
mamba activate trabalho-final
pip install .
jupyter lab
```

### Opção 4: Usando VS Code, PyCharm ou outra IDE

Também e possível abrir a pasta do projeto diretamente em uma IDE.

Fluxo sugerido:

1. Abrir a pasta do projeto.
2. Criar ou selecionar um ambiente Python.
3. Instalar as dependências a partir do `pyproject.toml`.
4. Abrir um notebook dentro da pasta `notebook/`.
5. selecionar o kernel Python do ambiente criado.

### Opção 5: Usando Google Colab

Para usar no Google Colab:

1. Faca, upload do notebook desejado.
2. Faca, upload dos arquivos da pasta `datasets/` usados no notebook.
3. Ajuste os caminhos dos arquivos, se necessário.

Exemplo de leitura local no projeto:

```python
import pandas as pd

df = pd.read_csv("../datasets/gap_minder_merged.csv")
```

No Colab, o caminho pode precisar ser alterado conforme onde o arquivo foi carregado.

## Como cada integrante deve trabalhar

Cada integrante deve criar o seu próprio notebook dentro da pasta `notebook/`.

Boas praticas:

- Manter os dados originais dentro de `datasets/`.
- Evitar alterar notebooks de outros integrantes sem combinar antes.
- Usar nomes claros para arquivos, gráficos e variáveis.
- Documentar as principais decisões dentro do próprio notebook.
- Antes de enviar alterações, executar o notebook para verificar se ele roda do início ao fim.

## Caminhos dos arquivos de dados

Como os notebooks ficam em `notebook/` e os dados ficam em `datasets/`, o caminho relativo mais comum sera:

```python
pd.read_csv("../datasets/nome_do_arquivo.csv")
```

Exemplo:

```python
import pandas as pd

df = pd.read_csv("../datasets/drinking_water.csv")
df.head()
```

Se você executar scripts a partir da raiz do projeto, o caminho pode ser:

```python
pd.read_csv("datasets/drinking_water.csv")
```

## Bases de dados disponíveis

Arquivos atualmente disponíveis em `datasets/`:

- `drinking_water.csv`
- `gapminder_full.csv`
- `gap_minder_merged.csv`
- `gdp.csv`
- `health_expenditure.csv`
- `literacy_rate.csv`
- `mortality_rate.csv`

## Fluxo recomendado para contribuição

Antes de começar uma nova alteração, atualize a sua cópia local com o repositorio principal:

```bash
git checkout main
git fetch upstream
git pull upstream main
```

Crie uma branch para o seu trabalho:

```bash
git checkout -b notebook-nome-integrante
```

Depois de criar ou alterar o seu notebook, confira os arquivos modificados:

```bash
git status
```

Adicione apenas os arquivos relacionados ao seu trabalho:

```bash
git add notebook/seu_notebook.ipynb
```

Crie um commit:

```bash
git commit -m "Adiciona analise de <tema>"
```

Envie sua branch para o seu fork:

```bash
git push origin notebook-nome-integrante
```

No GitHub, abra um Pull Request do seu fork para o repositorio principal.

Esse fluxo ajuda a:

- manter o repositorio principal mais organizado;
- reduzir conflitos entre notebooks de integrantes diferentes;
- revisar as contribuições antes de integrar;
- preservar o histórico de autoria de cada integrante.

Evite commitar arquivos grandes gerados localmente, ambientes virtuais, arquivos temporários ou configurações pessoais da IDE.

## Observações

- A pasta `.venv/` não deve ser enviada para o repositorio.
- Cada integrante deve gerar a sua propria `.venv/` localmente a partir do `pyproject.toml`.
- Isso evita problemas de compatibilidade entre Windows, Linux, macOS e diferentes instalacoes Python.
- Arquivos de configuração pessoal da IDE podem variar entre os integrantes.
- O arquivo `uv.lock` existe para quem optar por usar `uv`, mas o projeto também pode ser executado com `pip`, `venv`, `conda`, `mamba`, IDEs ou Colab.
