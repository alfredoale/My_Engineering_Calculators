import json
from pathlib import Path

import pytest

from calculator_scripts.data_table import (
    DATA_ROOT,
    create_data_table_calculator,
    load_table_records,
)
from calculator_scripts.ontario_building_code_2024.version_2025_01.part_9.maximum_floor_joist_span import (
    calculate_maximum_floor_joist_span,
)
from calculator_scripts.ontario_building_code_2024.version_2025_01.part_9.specified_snow_load import (
    calculate_snow_load,
)


TABLE_PATHS = [
    "ontario_building_code_2024/version_2025_01/part_4/specified_uniformly_distributed_live_loads.json",
    "ontario_building_code_2024/version_2025_01/part_9/maximum_spans_floor_joists_general_cases.json",
    "ontario_building_code_2024/version_2025_01/sb1_climatic_and_seismic_data/climatic_design_data_snow_load.json",
]


def test_all_data_files_use_wrapped_schema():
    for path in DATA_ROOT.rglob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)
        assert isinstance(payload["metadata"]["title"], str)
        assert isinstance(payload["data"], list)
        assert all(isinstance(row, dict) for row in payload["data"])


def test_load_table_records_flattens_nested_rows():
    records = load_table_records(TABLE_PATHS[0])

    assert len(records) == 38
    assert records[0]["Minimum Specified Load.value"] == 4.8
    assert records[0]["Minimum Specified Load.unit"] == "kPa"
    assert records[0]["Minimum Specified Load.note"] is None


def test_table_calculator_uses_json_metadata_and_notes():
    calculator = create_data_table_calculator(TABLE_PATHS[0])
    result = calculator.calculate({}, {})

    assert calculator.title.startswith("(Table) Table 4.1.5.3.")
    assert calculator.subtitle == "Forming Part of Sentence 4.1.5.3.(1)"
    assert "**1:**" in result["table_notes"]
    assert len(result["dataframe_records"]) == 38


def test_joist_calculator_uses_wrapped_rows():
    result = calculate_maximum_floor_joist_span(
        {
            "designation": "Douglas Fir - Larch (includes Douglas Fir and Western Larch)",
            "grade": "No. 1 and No. 2",
            "joist_size": "38 x 235",
            "joist_spacing": 400,
            "restraint": "With Strapping and Bridging",
        },
        {},
    )

    assert result["results"]["L_max"] > 0


def test_snow_calculator_uses_wrapped_rows():
    result = calculate_snow_load({"Location": "Ailsa Craig", "w": 4.3}, {})

    assert result["results"]["Ss"] == 2.2
    assert result["results"]["Sr"] == 0.4
    assert result["results"]["S"] == pytest.approx(1.39)
