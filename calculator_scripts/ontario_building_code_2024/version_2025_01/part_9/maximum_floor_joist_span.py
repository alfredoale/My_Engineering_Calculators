import json
from pathlib import Path

from core.calculator_model import Calculation


DATA_FILE = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "ontario_building_code_2024"
    / "version_2025_01"
    / "part_9"
    / "maximum_spans_floor_joists_general_cases.json"
)

with DATA_FILE.open("r", encoding="utf-8") as file:
    floor_joist_spans = json.load(file)


def _normalise_joist_size(size: str) -> str:
    return " ".join(size.replace("×", "x").split())


for row in floor_joist_spans:
    row["joistSize"]["value"] = _normalise_joist_size(row["joistSize"]["value"])


COMMERCIAL_DESIGNATION_OPTIONS = sorted(
    {row["commercialDesignation"] for row in floor_joist_spans}
)
GRADE_OPTIONS = sorted({row["grade"] for row in floor_joist_spans})
JOIST_SIZE_OPTIONS = sorted(
    {row["joistSize"]["value"] for row in floor_joist_spans},
    key=lambda size: tuple(int(value) for value in size.split(" x ")),
)
JOIST_SPACING_OPTIONS = sorted(
    {row["joistSpacing"]["value"] for row in floor_joist_spans}
)
RESTRAINT_OPTIONS = sorted({row["lateralBracing"] for row in floor_joist_spans})


def calculate_maximum_floor_joist_span(inputs: dict, precisions: dict) -> dict:
    """Look up the maximum floor joist span in OBC Table 9.23.4.2.-A."""
    designation = str(inputs["designation"])
    grade = str(inputs["grade"])
    joist_size = _normalise_joist_size(str(inputs["joist_size"]))
    joist_spacing = int(inputs["joist_spacing"])
    restraint = str(inputs["restraint"])

    matching_row = next(
        (
            row
            for row in floor_joist_spans
            if row["commercialDesignation"] == designation
            and row["grade"] == grade
            and row["joistSize"]["value"] == joist_size
            and row["joistSpacing"]["value"] == joist_spacing
            and row["lateralBracing"] == restraint
        ),
        None,
    )
    if matching_row is None:
        raise ValueError("No span is available for the selected combination.")

    span = float(matching_row["span"]["value"])
    precision = precisions.get("L_max", 2)
    size_display = joist_size.replace("x", r"\times")

    steps = [
        {
            "step": 1,
            "description": "Select the species group, lumber grade, and joist size",
            "formula_substituted": rf"$$\text{{Designation}} = \text{{{designation}}},\quad \text{{Grade}} = \text{{{grade}}},\quad \text{{Joist Size}} = {size_display}\text{{ mm}}$$"
        },
        {
            "step": 2,
            "description": "Select the lateral support arrangement and joist spacing",
            "formula_substituted": rf"$$\text{{Restraint}} = \text{{{restraint}}},\quad \text{{Spacing}} = {joist_spacing}\text{{ mm}}$$"
        },
        {
            "step": 3,
            "description": "Look up the maximum allowable joist span in OBC Table 9.23.4.2.-A",
            "symbol": "L_max",
            "latex": r"L_{max}",
            "result": span,
            "units": "m",
            "precision": precision,
        },
    ]

    return {
        "main_result_latex": rf"$$L_{{max}} = {span:.{precision}f}\text{{ m}}$$",
        "results": {"L_max": span},
        "steps": steps,
    }


maximum_floor_joist_span_variables = [
    {
        "symbol": "L_max",
        "latex": "L_{max}",
        "name": "Maximum allowable joist clear span",
        "units": "m",
        "is_input": False,
    },
    {
        "symbol": "designation",
        "latex": r"\text{Commercial Designation}",
        "name": "Wood species / group classification",
        "units": "",
        "is_input": True,
        "widget": "selectbox",
        "options": COMMERCIAL_DESIGNATION_OPTIONS,
        "default": "Douglas Fir - Larch (includes Douglas Fir and Western Larch)",
    },
    {
        "symbol": "grade",
        "latex": r"\text{Grade}",
        "name": "Structural lumber grade classification",
        "units": "",
        "is_input": True,
        "widget": "selectbox",
        "options": GRADE_OPTIONS,
        "default": "No. 1 and No. 2",
    },
    {
        "symbol": "joist_size",
        "latex": r"\text{Joist Size}",
        "name": "Nominal cross-sectional dimensions",
        "units": "mm",
        "is_input": True,
        "widget": "selectbox",
        "options": JOIST_SIZE_OPTIONS,
        "default": "38 x 235",
    },
    {
        "symbol": "joist_spacing",
        "latex": r"\text{Joist Spacing}",
        "name": "Center-to-center distance between adjacent joists",
        "units": "mm",
        "is_input": True,
        "widget": "selectbox",
        "options": JOIST_SPACING_OPTIONS,
        "default": 400,
    },
    {
        "symbol": "restraint",
        "latex": r"\text{Restraint Condition}",
        "name": "Lateral support method",
        "units": "",
        "is_input": True,
        "widget": "selectbox",
        "options": RESTRAINT_OPTIONS,
        "default": "With Strapping and Bridging",
    },
]


maximum_floor_joist_span_notes = (
    "**Table 9.23.4.2.-A Notes:**\n"
    "- Spans apply only where floors serve residential areas as described in Table 4.1.5.3., or the uniformly distributed live load does not exceed that specified for residential areas.\n"
    "- See Sentence 9.23.9.4.(5) for alternatives to strapping."
)


maximum_floor_joist_span_calculator = Calculation(
    calc_id="maximum_floor_joist_span",
    title="OBC Part 9 — Maximum Floor Joist Span (General Cases)",
    subtitle="Calculate the maximum allowable span for floor joists based on the Ontario Building Code (Part 9) for general cases.",
    variables=maximum_floor_joist_span_variables,
    calculate_fn=calculate_maximum_floor_joist_span,
    code_custom_notes=maximum_floor_joist_span_notes,
)