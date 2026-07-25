from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from advanced_analysis import (
    build_world_bank_dataset,
    correlation_table,
    enrich_gapminder_2007_with_world_bank,
    format_p_value,
    latest_world_bank_values,
    load_gapminder,
    population_weighted_by_continent,
    population_weighted_life_expectancy,
    regression_summary,
    selected_countries_timeseries,
    validate_gapminder_schema,
)


def sample_gapminder() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Brazil", 1952, 56602560, "Americas", 50.9, 2108.9],
            ["Brazil", 2007, 190010647, "Americas", 72.4, 9065.8],
            ["China", 1952, 556263527, "Asia", 44.0, 400.4],
            ["China", 2007, 1318683096, "Asia", 73.0, 4959.1],
            ["Germany", 1952, 69145952, "Europe", 67.5, 7144.1],
            ["Germany", 2007, 82400996, "Europe", 79.4, 32170.4],
        ],
        columns=["country", "year", "pop", "continent", "lifeExp", "gdpPercap"],
    )


def sample_world_bank() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["SI.POV.GINI", "Gini index", "Brazil", "BRA", 2001, 59.0, "gini_index"],
            ["SI.POV.GINI", "Gini index", "Brazil", "BRA", 2007, 53.3, "gini_index"],
            ["SP.DYN.IMRT.IN", "Infant mortality", "Brazil", "BRA", 2006, 18.1, "infant_mortality_per_1000"],
            ["SI.POV.GINI", "Gini index", "China", "CHN", 2005, 42.5, "gini_index"],
            ["SP.DYN.IMRT.IN", "Infant mortality", "China", "CHN", 2007, 15.4, "infant_mortality_per_1000"],
            ["SI.POV.GINI", "Gini index", "Germany", "DEU", 2007, None, "gini_index"],
            ["SP.DYN.IMRT.IN", "Infant mortality", "Germany", "DEU", 2007, 3.7, "infant_mortality_per_1000"],
            ["SI.POV.GINI", "Gini index", "Brazil", "BRA", 2010, 51.9, "gini_index"],
        ],
        columns=["indicator_code", "indicator_name", "country", "iso_alpha", "year", "value", "metric"],
    )


def test_load_gapminder_removes_missing_rows_and_duplicates(tmp_path: Path):
    path = tmp_path / "gapminder.csv"
    data = pd.concat(
        [
            sample_gapminder(),
            sample_gapminder().iloc[[0]],
            pd.DataFrame(
                [["Invalid", 2007, 1, "Asia", np.nan, 1000]],
                columns=["country", "year", "pop", "continent", "lifeExp", "gdpPercap"],
            ),
        ],
        ignore_index=True,
    )
    data.to_csv(path, index=False)

    loaded = load_gapminder(path)

    assert len(loaded) == len(sample_gapminder())
    assert loaded.isna().sum().sum() == 0
    assert loaded.duplicated().sum() == 0


def test_validate_gapminder_schema_accepts_expected_dataset():
    checks = validate_gapminder_schema(sample_gapminder())

    assert checks["aprovado"].all()


def test_population_weighted_life_expectancy_uses_population_as_weight():
    result = population_weighted_life_expectancy(sample_gapminder())
    year_2007 = result[result["year"] == 2007].iloc[0]
    raw_2007 = sample_gapminder()[sample_gapminder()["year"] == 2007]
    expected = np.average(raw_2007["lifeExp"], weights=raw_2007["pop"])

    assert year_2007["lifeExp_media_simples"] == pytest.approx(raw_2007["lifeExp"].mean(), abs=0.01)
    assert year_2007["lifeExp_media_ponderada_pop"] == pytest.approx(expected, abs=0.01)


def test_population_weighted_by_continent_keeps_continent_and_year_grain():
    result = population_weighted_by_continent(sample_gapminder())

    assert set(result.columns) == {
        "continent",
        "year",
        "lifeExp_media_simples",
        "lifeExp_media_ponderada_pop",
    }
    assert len(result) == 6


def test_latest_world_bank_values_pivots_latest_available_year_until_cutoff():
    result = latest_world_bank_values(sample_world_bank(), max_year=2007)
    brazil = result[result["iso_alpha"] == "BRA"].iloc[0]

    assert brazil["gini_index_latest"] == pytest.approx(53.3)
    assert brazil["gini_index_year"] == 2007
    assert brazil["infant_mortality_per_1000_latest"] == pytest.approx(18.1)
    assert brazil["infant_mortality_per_1000_year"] == 2006


def test_enrich_gapminder_2007_with_world_bank_adds_external_indicators():
    enriched = enrich_gapminder_2007_with_world_bank(sample_gapminder(), sample_world_bank())

    assert set(enriched["country"]) == {"Brazil", "China", "Germany"}
    assert {"gini_index_latest", "infant_mortality_per_1000_latest"}.issubset(enriched.columns)
    assert enriched.loc[enriched["country"] == "Brazil", "gini_index_latest"].iloc[0] == pytest.approx(53.3)


def test_selected_countries_timeseries_filters_default_countries():
    result = selected_countries_timeseries(sample_gapminder())

    assert set(result["country"]) == {"Brazil", "China"}
    assert "pop_milhoes" in result.columns


def test_build_world_bank_dataset_uses_cached_file_without_requesting_network(tmp_path: Path, monkeypatch):
    path = tmp_path / "world_bank.csv"
    sample_world_bank().to_csv(path, index=False)

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("network should not be called when refresh=False and cache exists")

    monkeypatch.setattr("advanced_analysis.fetch_world_bank_indicator", fail_if_called)
    result = build_world_bank_dataset(path, refresh=False)

    assert len(result) == len(sample_world_bank())


def test_correlation_and_regression_return_expected_contracts_on_real_data():
    data = pd.read_csv("data/raw/gapminder_full.csv").dropna().drop_duplicates()

    correlations = correlation_table(data)
    regression = regression_summary(data)

    assert {"pearson_r", "pearson_p", "spearman_r", "spearman_p"}.issubset(correlations.columns)
    assert set(regression["modelo"]) == {"todos_os_anos", "ano_2007"}
    assert regression["r2"].between(0, 1).all()
    assert (regression["n"] > 0).all()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.0, "< 0.0001"),
        (0.012345, "0.0123"),
    ],
)
def test_format_p_value(value: float, expected: str):
    assert format_p_value(value) == expected
