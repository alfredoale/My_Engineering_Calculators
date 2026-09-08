"""Template for a calculator that looks up a row in a JSON data table.

Copy this file into a package under calculator_scripts/, update DATA_FILE and
field names, then register the resulting Calculation in __init__.py.
"""

import json
from pathlib import Path

from core.calculator_model import Calculation


# This location assumes the copied file is two directories below the repository
# root, for example calculator_scripts/my_domain/my_lookup.py. Adjust as needed.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "your_domain" / "your_table.json"


with DATA_FILE.open("r", encoding="utf-8") as file:
    table_rows = json.load(file)["data"]


CATEGORY_OPTIONS = sorted({row["category"] for row in table_rows})
SIZE_OPTIONS = sorted({row["size"]["value"] for row in table_rows})


def calculate_example_lookup(inputs: dict, precisions: dict) -> dict:
    """Find the row matching every selected input."""
    category = str(inputs["category"])
    size = str(inputs["size"])

    matching_row = next(
        (
            row
            for row in table_rows
            if row["category"] == category and row["size"]["value"] == size
        ),
        None,
    )
    if matching_row is None:
        raise ValueError("No table row matches the selected inputs.")

    result = float(matching_row["result"]["value"])
    result_unit = matching_row["result"].get("unit", "")
    result_precision = precisions.get("result", 2)

    return {
        "main_result_latex": (
            rf"$$R = {result:.{result_precision}f}"
            rf"\text{{ {result_unit}}}$$"
        ),
        "results": {"result": result},
        "steps": [
            {
                "step": 1,
                "description": "Select the matching row in the reference table",
                "formula_substituted": (
                    rf"$$\text{{Category}} = \text{{{category}}}, "
                    rf"\quad \text{{Size}} = \text{{{size}}}$$"
                ),
            },
            {
                "step": 2,
                "description": "Read the result from the selected row",
                "symbol": "R",
                "latex": "R",
                "result": result,
                "precision": result_precision,
                "units": result_unit,
            },
        ],
    }


example_lookup_variables = [
    {
        "symbol": "result",
        "latex": "R",
        "name": "Lookup result",
        "units": "unit",
        "is_input": False,
    },
    {
        "symbol": "category",
        "latex": r"\text{Category}",
        "name": "Reference-table category",
        "units": "",
        "is_input": True,
        "widget": "selectbox",
        "options": CATEGORY_OPTIONS,
        "help": "Select the category used to find a table row.",
    },
    {
        "symbol": "size",
        "latex": r"\text{Size}",
        "name": "Reference-table size",
        "units": "",
        "is_input": True,
        "widget": "selectbox",
        "options": SIZE_OPTIONS,
        "help": "Select the size used to find a table row.",
    },
]


example_lookup_calculator = Calculation(
    calc_id="example_lookup_calculator",
    title="Example Lookup Calculator",
    subtitle="Replace this subtitle with the source table and lookup purpose.",
    variables=example_lookup_variables,
    calculate_fn=calculate_example_lookup,
)


# Register the calculator in calculator_scripts/__init__.py:
#
# from .your_package.your_module import example_lookup_calculator
#
# CALCULATORS = {
#     ...,
#     example_lookup_calculator.title: example_lookup_calculator,
# }
