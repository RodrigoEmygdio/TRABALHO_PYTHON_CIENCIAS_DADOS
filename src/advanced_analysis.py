from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import statsmodels.formula.api as smf
from scipy import stats


EXPECTED_COLUMNS = ["country", "year", "pop", "continent", "lifeExp", "gdpPercap"]
EXPECTED_CONTINENTS = {"Africa", "Americas", "Asia", "Europe", "Oceania"}
WORLD_BANK_INDICATORS = {
    "SI.POV.GINI": "gini_index",
    "SP.DYN.IMRT.IN": "infant_mortality_per_1000",
}


def load_gapminder(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df.dropna().drop_duplicates().copy()


def add_iso_codes(df: pd.DataFrame) -> pd.DataFrame:
    iso_lookup = (
        px.data.gapminder()[["country", "year", "iso_alpha", "iso_num"]]
        .drop_duplicates()
    )
    return df.merge(iso_lookup, on=["country", "year"], how="left")


def validate_gapminder_schema(df: pd.DataFrame) -> pd.DataFrame:
    checks = [
        ("colunas esperadas", list(df.columns) == EXPECTED_COLUMNS),
        ("sem valores ausentes", df.isna().sum().sum() == 0),
        ("sem duplicatas", df.duplicated().sum() == 0),
        ("populacao positiva", (df["pop"] > 0).all()),
        ("expectativa de vida positiva", (df["lifeExp"] > 0).all()),
        ("PIB per capita positivo", (df["gdpPercap"] > 0).all()),
        ("continentes validos", set(df["continent"].unique()).issubset(EXPECTED_CONTINENTS)),
        ("anos em intervalo esperado", df["year"].between(1952, 2007).all()),
    ]
    return pd.DataFrame(checks, columns=["verificacao", "aprovado"])


def add_log_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["log_gdpPercap"] = np.log(out["gdpPercap"])
    out["log_pop"] = np.log(out["pop"])
    return out


def correlation_table(df: pd.DataFrame) -> pd.DataFrame:
    data = add_log_features(df)
    pairs = [
        ("lifeExp", "gdpPercap"),
        ("lifeExp", "log_gdpPercap"),
        ("lifeExp", "pop"),
        ("lifeExp", "log_pop"),
        ("gdpPercap", "pop"),
        ("gdpPercap", "log_pop"),
    ]
    rows = []
    for x, y in pairs:
        pearson = stats.pearsonr(data[x], data[y])
        spearman = stats.spearmanr(data[x], data[y])
        rows.append(
            {
                "variavel_1": x,
                "variavel_2": y,
                "pearson_r": pearson.statistic,
                "pearson_p": pearson.pvalue,
                "spearman_r": spearman.statistic,
                "spearman_p": spearman.pvalue,
            }
        )
    return pd.DataFrame(rows).round(4)


def regression_summary(df: pd.DataFrame) -> pd.DataFrame:
    data = add_log_features(df)
    models = {
        "todos_os_anos": smf.ols("lifeExp ~ log_gdpPercap", data=data).fit(),
        "ano_2007": smf.ols("lifeExp ~ log_gdpPercap", data=data[data["year"] == 2007]).fit(),
    }
    rows = []
    for name, model in models.items():
        ci_low, ci_high = model.conf_int().loc["log_gdpPercap"]
        rows.append(
            {
                "modelo": name,
                "coef_log_gdpPercap": model.params["log_gdpPercap"],
                "ic95_min": ci_low,
                "ic95_max": ci_high,
                "r2": model.rsquared,
                "n": int(model.nobs),
            }
        )
    return pd.DataFrame(rows).round(4)


def quantile_regression_summary(
    df: pd.DataFrame,
    quantiles: tuple[float, ...] = (0.25, 0.50, 0.75),
) -> pd.DataFrame:
    data = add_log_features(df)
    model = smf.quantreg("lifeExp ~ log_gdpPercap", data=data)
    labels = {
        0.25: "países/observações abaixo da mediana",
        0.50: "mediana",
        0.75: "países/observações acima da mediana",
    }
    rows = []
    for quantile in quantiles:
        result = model.fit(q=quantile, max_iter=5000)
        ci_low, ci_high = result.conf_int().loc["log_gdpPercap"]
        rows.append(
            {
                "quantil": quantile,
                "leitura": labels.get(quantile, "quantil customizado"),
                "coef_log_gdpPercap": result.params["log_gdpPercap"],
                "ic95_min": ci_low,
                "ic95_max": ci_high,
                "pseudo_r2": result.prsquared,
                "n": int(result.nobs),
            }
        )
    return pd.DataFrame(rows).round(4)


def make_interactive_2007(df: pd.DataFrame):
    data = df[df["year"] == df["year"].max()].copy()
    data["pop_milhoes"] = data["pop"] / 1_000_000
    fig = px.scatter(
        data,
        x="gdpPercap",
        y="lifeExp",
        color="continent",
        size="pop",
        hover_name="country",
        hover_data={
            "continent": True,
            "gdpPercap": ":,.0f",
            "lifeExp": ":.1f",
            "pop_milhoes": ":.1f",
            "pop": False,
        },
        log_x=True,
        size_max=55,
        labels={
            "gdpPercap": "PIB per capita (USD, PPP, escala log)",
            "lifeExp": "Expectativa de vida (anos)",
            "continent": "Continente",
            "pop_milhoes": "Populacao (milhoes)",
        },
        title="PIB per capita x expectativa de vida por pais (2007)",
    )
    fig.update_layout(template="plotly_white", legend_title_text="Continente")
    return fig


def make_life_expectancy_choropleth(df: pd.DataFrame, year: int = 2007):
    data = add_iso_codes(df)
    data = data[data["year"] == year].copy()
    fig = px.choropleth(
        data,
        locations="iso_alpha",
        color="lifeExp",
        hover_name="country",
        hover_data={
            "continent": True,
            "lifeExp": ":.1f",
            "gdpPercap": ":,.0f",
            "pop": ":,",
            "iso_alpha": False,
        },
        color_continuous_scale="Viridis",
        labels={"lifeExp": "Expectativa de vida"},
        title=f"Expectativa de vida por pais ({year})",
    )
    fig.update_layout(template="plotly_white")
    return fig


def fetch_world_bank_indicator(
    indicator: str,
    start_year: int = 1952,
    end_year: int = 2007,
) -> pd.DataFrame:
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
    params = {
        "format": "json",
        "per_page": 20000,
        "date": f"{start_year}:{end_year}",
    }
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()
    records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    rows = []
    for record in records:
        rows.append(
            {
                "indicator_code": indicator,
                "indicator_name": record["indicator"]["value"],
                "country": record["country"]["value"],
                "iso_alpha": record.get("countryiso3code"),
                "year": int(record["date"]),
                "value": record["value"],
            }
        )
    return pd.DataFrame(rows)


def build_world_bank_dataset(
    output_path: str | Path,
    start_year: int = 1952,
    end_year: int = 2007,
    refresh: bool = False,
) -> pd.DataFrame:
    path = Path(output_path)
    if path.exists() and not refresh:
        return pd.read_csv(path)

    frames = [
        fetch_world_bank_indicator(indicator, start_year, end_year)
        for indicator in WORLD_BANK_INDICATORS
    ]
    data = pd.concat(frames, ignore_index=True)
    data["metric"] = data["indicator_code"].map(WORLD_BANK_INDICATORS)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)
    return data


def latest_world_bank_values(
    world_bank_data: pd.DataFrame,
    max_year: int = 2007,
) -> pd.DataFrame:
    data = world_bank_data.dropna(subset=["value"]).copy()
    data = data[data["year"] <= max_year]
    data = data.sort_values(["iso_alpha", "metric", "year"])
    latest = data.groupby(["iso_alpha", "metric"], as_index=False).tail(1)
    wide_values = latest.pivot(index="iso_alpha", columns="metric", values="value")
    wide_years = latest.pivot(index="iso_alpha", columns="metric", values="year")
    wide_values.columns = [f"{col}_latest" for col in wide_values.columns]
    wide_years.columns = [f"{col}_year" for col in wide_years.columns]
    return pd.concat([wide_values, wide_years], axis=1).reset_index()


def enrich_gapminder_2007_with_world_bank(
    gapminder_df: pd.DataFrame,
    world_bank_data: pd.DataFrame,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    data_2007 = add_iso_codes(gapminder_df)
    data_2007 = data_2007[data_2007["year"] == data_2007["year"].max()].copy()
    latest = latest_world_bank_values(world_bank_data, max_year=int(data_2007["year"].max()))
    enriched = data_2007.merge(latest, on="iso_alpha", how="left")
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        enriched.to_csv(path, index=False)
    return enriched


def population_weighted_life_expectancy(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year, group in df.groupby("year"):
        rows.append(
            {
                "year": year,
                "lifeExp_media_simples": group["lifeExp"].mean(),
                "lifeExp_media_ponderada_pop": np.average(group["lifeExp"], weights=group["pop"]),
            }
        )
    return pd.DataFrame(rows).round(2)


def population_weighted_by_continent(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (continent, year), group in df.groupby(["continent", "year"]):
        rows.append(
            {
                "continent": continent,
                "year": year,
                "lifeExp_media_simples": group["lifeExp"].mean(),
                "lifeExp_media_ponderada_pop": np.average(group["lifeExp"], weights=group["pop"]),
            }
        )
    return pd.DataFrame(rows).round(2)


def make_weighted_life_expectancy_chart(df: pd.DataFrame):
    data = population_weighted_life_expectancy(df)
    long = data.melt(
        id_vars="year",
        value_vars=["lifeExp_media_simples", "lifeExp_media_ponderada_pop"],
        var_name="tipo_media",
        value_name="lifeExp",
    )
    labels = {
        "lifeExp_media_simples": "Media simples por pais",
        "lifeExp_media_ponderada_pop": "Media ponderada pela populacao",
    }
    long["tipo_media"] = long["tipo_media"].map(labels)
    fig = px.line(
        long,
        x="year",
        y="lifeExp",
        color="tipo_media",
        markers=True,
        labels={"year": "Ano", "lifeExp": "Expectativa de vida", "tipo_media": "Tipo de media"},
        title="Expectativa de vida global: media simples vs. ponderada pela populacao",
    )
    fig.update_layout(template="plotly_white")
    return fig


def selected_countries_timeseries(
    gapminder_df: pd.DataFrame,
    countries: list[str] | None = None,
) -> pd.DataFrame:
    if countries is None:
        countries = ["Brazil", "China", "India", "United States", "Japan"]
    data = gapminder_df[gapminder_df["country"].isin(countries)].copy()
    data["pop_milhoes"] = data["pop"] / 1_000_000
    return data


def make_selected_countries_chart(
    gapminder_df: pd.DataFrame,
    metric: str = "lifeExp",
    countries: list[str] | None = None,
):
    data = selected_countries_timeseries(gapminder_df, countries)
    labels = {
        "lifeExp": "Expectativa de vida",
        "gdpPercap": "PIB per capita",
        "pop_milhoes": "Populacao (milhoes)",
    }
    fig = px.line(
        data,
        x="year",
        y=metric,
        color="country",
        markers=True,
        labels={"year": "Ano", metric: labels.get(metric, metric), "country": "Pais"},
        title=f"{labels.get(metric, metric)}: Brasil, China, India, EUA e Japao",
    )
    fig.update_layout(template="plotly_white")
    if metric == "gdpPercap":
        fig.update_yaxes(type="log")
    return fig


def make_world_bank_scatter(enriched_2007: pd.DataFrame):
    data = enriched_2007.dropna(
        subset=["gini_index_latest", "infant_mortality_per_1000_latest"]
    ).copy()
    fig = px.scatter(
        data,
        x="gini_index_latest",
        y="infant_mortality_per_1000_latest",
        color="continent",
        size="pop",
        hover_name="country",
        hover_data={
            "lifeExp": ":.1f",
            "gdpPercap": ":,.0f",
            "gini_index_year": True,
            "infant_mortality_per_1000_year": True,
            "pop": False,
        },
        labels={
            "gini_index_latest": "Gini mais recente ate 2007",
            "infant_mortality_per_1000_latest": "Mortalidade infantil por 1.000 nascidos vivos",
            "continent": "Continente",
        },
        title="Desigualdade de renda x mortalidade infantil (dados Banco Mundial ate 2007)",
    )
    fig.update_layout(template="plotly_white")
    return fig


def export_plotly_html(fig, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs="cdn")
    return path


def format_p_value(value: float) -> str:
    if value == 0 or math.isclose(value, 0):
        return "< 0.0001"
    return f"{value:.4f}"
