import json
from pathlib import Path
from typing import Any

from core.calculator_model import Calculation


DATA_ROOT = Path(__file__).resolve().parents[1] / "data"

def discover_table_paths() -> list[Path]:
    """Return JSON data files in a stable, repository-relative order."""
    return sorted(DATA_ROOT.rglob("*.json"))


def _relative_path(path: Path) -> str:
    """Return a data-file path relative to the configured data root."""
    return path.relative_to(DATA_ROOT).as_posix()


def _load_table_payload(relative_path: str) -> dict[str, Any]:
    """Load and validate the canonical wrapped table structure."""
    path = DATA_ROOT / relative_path
    if path.parent != DATA_ROOT and DATA_ROOT not in path.parents:
        raise ValueError("Selected table is outside the data directory.")

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError("The selected JSON file must contain a table object.")

    metadata = payload.get("metadata")
    rows = payload.get("data")
    if not isinstance(metadata, dict) or not isinstance(metadata.get("title"), str):
        raise ValueError("The table must contain metadata.title.")
    if "subtitle" in metadata and metadata["subtitle"] is not None and not isinstance(metadata["subtitle"], str):
        raise ValueError("metadata.subtitle must be a string when provided.")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("The table data must be a list of objects.")

    return payload


def _format_table_notes(notes: Any) -> str:
    """Convert table notes into Markdown accepted by the table renderer."""
    if isinstance(notes, dict):
        return "\n".join(f"- **{key}:** {value}" for key, value in notes.items())
    if isinstance(notes, str):
        return notes
    if notes is None:
        return ""
    raise ValueError("table_notes must be a string or object when provided.")


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
    """Load canonical table rows and flatten nested row dictionaries."""
    payload = _load_table_payload(relative_path)
    return [_flatten_record(row) for row in payload["data"]]


TABLE_PATHS = discover_table_paths()


def create_data_table_calculator(relative_path: str) -> Calculation:
    """Create a calculator that loads one repository-relative JSON table."""
    metadata = _load_table_payload(relative_path)["metadata"]
    table_title = f"(Table) {metadata['title']}"
    table_subtitle = metadata.get("subtitle", "")

    def calculate_table(inputs: dict, precisions: dict) -> dict:
        payload = _load_table_payload(relative_path)
        return {
            "dataframe_records": [_flatten_record(row) for row in payload["data"]],
            "table_title": table_title,
            "table_notes": _format_table_notes(payload.get("table_notes")),
        }

    return Calculation(
        calc_id=f"data_table_{relative_path.replace('/', '_').replace('.', '_')}",
        title=table_title,
        subtitle=table_subtitle,
        variables=[],
        calculate_fn=calculate_table,
        is_table=True,
    )


data_table_calculators = {
    calculator.title: calculator
    for calculator in (create_data_table_calculator(_relative_path(path)) for path in TABLE_PATHS)
}