import json
from pathlib import Path

import report_builder


def test_copy_notebook_without_removed_cells(tmp_path: Path, monkeypatch):
    notebooks_dir = tmp_path / "notebooks"
    notebooks_dir.mkdir()
    source = notebooks_dir / "analise_gapminder.ipynb"
    output = tmp_path / "export.ipynb"
    notebook = {
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": ["fica"]},
            {"cell_type": "code", "metadata": {"tags": ["remove_cell"]}, "source": ["sai"]},
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    source.write_text(json.dumps(notebook), encoding="utf-8")
    monkeypatch.setattr(report_builder, "NOTEBOOKS", notebooks_dir)

    report_builder._copy_notebook_without_removed_cells(output)
    exported = json.loads(output.read_text(encoding="utf-8"))

    assert len(exported["cells"]) == 1
    assert exported["cells"][0]["source"] == ["fica"]


def test_build_all_reports_calls_nbconvert_and_returns_final_html(tmp_path: Path, monkeypatch):
    notebooks_dir = tmp_path / "notebooks"
    reports_dir = tmp_path / "reports"
    notebooks_dir.mkdir()
    (notebooks_dir / "analise_gapminder.ipynb").write_text(
        json.dumps({"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}),
        encoding="utf-8",
    )

    calls = []

    def fake_run(command, cwd, check):
        calls.append({"command": command, "cwd": cwd, "check": check})
        reports_dir.mkdir(parents=True, exist_ok=True)
        (reports_dir / "analise_gapminder.html").write_text("<html></html>", encoding="utf-8")

    monkeypatch.setattr(report_builder, "NOTEBOOKS", notebooks_dir)
    monkeypatch.setattr(report_builder, "REPORTS", reports_dir)
    monkeypatch.setattr(report_builder.subprocess, "run", fake_run)
    monkeypatch.setattr(report_builder, "_jupyter_executable", lambda: "jupyter")

    result = report_builder.build_all_reports(open_browser=False)

    assert result == reports_dir / "analise_gapminder.html"
    assert calls[0]["cwd"] == notebooks_dir
    assert "nbconvert" in calls[0]["command"]
    assert "--execute" in calls[0]["command"]
