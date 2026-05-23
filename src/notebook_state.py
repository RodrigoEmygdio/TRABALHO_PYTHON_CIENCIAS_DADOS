from pathlib import Path
import importlib.util

import pandas as pd
import plotly.express as px
from IPython.display import HTML, display


PROJECT_ROOT = next(
    candidate for candidate in [Path.cwd(), *Path.cwd().parents]
    if (candidate / "src" / "advanced_analysis.py").exists()
)


def load_local_module(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar {module_name} em {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


advanced_analysis = load_local_module(
    "advanced_analysis",
    PROJECT_ROOT / "src" / "advanced_analysis.py",
)
report_builder = load_local_module(
    "report_builder",
    PROJECT_ROOT / "src" / "report_builder.py",
)

build_world_bank_dataset = advanced_analysis.build_world_bank_dataset
correlation_table = advanced_analysis.correlation_table
enrich_gapminder_2007_with_world_bank = advanced_analysis.enrich_gapminder_2007_with_world_bank
make_interactive_2007 = advanced_analysis.make_interactive_2007
make_life_expectancy_choropleth = advanced_analysis.make_life_expectancy_choropleth
make_selected_countries_chart = advanced_analysis.make_selected_countries_chart
make_weighted_life_expectancy_chart = advanced_analysis.make_weighted_life_expectancy_chart
make_world_bank_scatter = advanced_analysis.make_world_bank_scatter
population_weighted_life_expectancy = advanced_analysis.population_weighted_life_expectancy
quantile_regression_summary = advanced_analysis.quantile_regression_summary
regression_summary = advanced_analysis.regression_summary
selected_countries_timeseries = advanced_analysis.selected_countries_timeseries
validate_gapminder_schema = advanced_analysis.validate_gapminder_schema

DATA_RAW = PROJECT_ROOT / "data" / "raw" / "gapminder_full.csv"
WB_RAW = PROJECT_ROOT / "data" / "external" / "world_bank_gini_infant_mortality_1952_2007.csv"
WB_ENRICHED_2007 = PROJECT_ROOT / "data" / "external" / "gapminder_2007_world_bank_enriched.csv"

df_raw = pd.read_csv(DATA_RAW)
df_clean = df_raw.dropna().drop_duplicates().copy()


def show_plot(fig):
    display(HTML(fig.to_html(full_html=False, include_plotlyjs="cdn")))


def build_final_html(open_browser=True):
    print("Gerando HTML final da apresentação...")
    caminho = report_builder.build_all_reports(open_browser=open_browser)
    display(HTML(f"""
    <p><strong>HTML final gerado com sucesso.</strong></p>
    <p><a href="{caminho.as_uri()}" target="_blank">Abrir apresentação em HTML</a></p>
    <p><code>{caminho}</code></p>
    """))
    return caminho
