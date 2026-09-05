import json
from pathlib import Path
from typing import Any

from core.calculator_model import Calculation


DATA_ROOT = Path(__file__).resolve().parents[1] / "data"

TABLE_METADATA = {
    "ontario_building_code_2024/version_2025_01/part_9/maximum_spans_floor_joists_general_cases.json": {
        "title": "OBC Part 9 - Maximum Floor Joist Spans (General Cases)",
        "notes": "Source data for OBC Table 9.23.4.2.-A maximum floor joist spans.",
    },
    "ontario_building_code_2024/version_2025_01/sb1_climatic_and_seismic_data/climatic_design_data_snow_load.json": {
        "title": "OBC SB-1 - Climatic Design Data: Snow and Rain Loads",
        "notes": "Source data for climatic design snow and rain loads in OBC Supplementary Standard SB-1.",
    },
}


def discover_table_paths() -> list[Path]:
    """Return JSON data files in a stable, repository-relative order."""
    return sorted(DATA_ROOT.rglob("*.json"))


def _relative_path(path: Path) -> str:
    """Return a data-file path relative to the configured data root."""
    return path.relative_to(DATA_ROOT).as_posix()


def _display_title(relative_path: str) -> str:
    """Return the configured title or a readable title derived from the filename."""
    metadata = TABLE_METADATA.get(relative_path)
    if metadata:
        return metadata["title"]

    filename = Path(relative_path).stem.replace("_", " ").replace("-", " ")
    return " ".join(word.capitalize() for word in filename.split())


def _table_notes(relative_path: str) -> str:
    """Return configured source notes or a generic note for an unlisted table."""
    metadata = TABLE_METADATA.get(relative_path)
    return metadata["notes"] if metadata else "Data loaded from the selected JSON file."


def _flatten_record(value: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten nested dictionaries into dot-separated table column names."""
    flattened = {}
    for key, nested_value in value.items():
        column = f"{prefix}.{key}" if prefix else key
        if isinstance(nested_value, dict):
            flattened.update(_flatten_record(nested_value, column))
        else:
            flattened[column] = nested_value
    return flattened


def load_table_records(relative_path: str) -> list[dict[str, Any]]:
    """Load a repository-relative JSON object or array and flatten its records."""
    path = DATA_ROOT / relative_path
    if path.parent != DATA_ROOT and DATA_ROOT not in path.parents:
        raise ValueError("Selected table is outside the data directory.")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValueError("The selected JSON file must contain an object or an array of objects.")

    return [_flatten_record(row) for row in data]


TABLE_PATHS = discover_table_paths()


def create_data_table_calculator(relative_path: str) -> Calculation:
    """Create a calculator that loads one repository-relative JSON table."""
    table_title = f"(Table) {_display_title(relative_path)}"

    def calculate_table(inputs: dict, precisions: dict) -> dict:
        return {
            "dataframe_records": load_table_records(relative_path),
            "table_title": table_title,
            "table_notes": _table_notes(relative_path),
        }

    return Calculation(
        calc_id=f"data_table_{relative_path.replace('/', '_').replace('.', '_')}",
        title=table_title,
        subtitle="",
        variables=[],
        calculate_fn=calculate_table,
        is_table=True,
    )


data_table_calculators = {
    calculator.title: calculator
    for calculator in (create_data_table_calculator(_relative_path(path)) for path in TABLE_PATHS)
}