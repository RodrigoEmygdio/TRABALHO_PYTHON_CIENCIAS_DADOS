from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
REPORTS = ROOT / "reports"
PRESENTATION_NOTEBOOK = "analise_gapminder.ipynb"
PRESENTATION_HTML = "analise_gapminder.html"


def _jupyter_executable() -> str:
    anaconda_jupyter = Path("/opt/anaconda3/bin/jupyter")
    if anaconda_jupyter.exists():
        return str(anaconda_jupyter)
    return shutil.which("jupyter") or "jupyter"


def _copy_notebook_without_removed_cells(output_path: Path) -> None:
    notebook_path = NOTEBOOKS / PRESENTATION_NOTEBOOK
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    notebook["cells"] = [
        cell
        for cell in notebook["cells"]
        if "remove_cell" not in cell.get("metadata", {}).get("tags", [])
    ]
    output_path.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )


def build_all_reports(open_browser: bool = False) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".nbconvert-", dir=NOTEBOOKS) as tmp_dir:
        export_notebook = Path(tmp_dir) / PRESENTATION_NOTEBOOK
        _copy_notebook_without_removed_cells(export_notebook)
        command = [
            _jupyter_executable(),
            "nbconvert",
            "--execute",
            "--to",
            "html",
            "--output-dir",
            str(REPORTS),
            "--output",
            PRESENTATION_HTML,
            str(export_notebook),
            "--ExecutePreprocessor.timeout=300",
        ]
        subprocess.run(command, cwd=NOTEBOOKS, check=True)
    final_report = REPORTS / PRESENTATION_HTML
    if open_browser:
        webbrowser.open(final_report.as_uri())
    return final_report


if __name__ == "__main__":
    print(build_all_reports(open_browser=False))
