import json
from pathlib import Path

from core.calculator_model import Calculation

DATA_FILE = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "ontario_building_code_2024"
    / "version_2025_01"
    / "sb1_climatic_and_seismic_data"
    / "climatic_design_data_snow_load.json"
)

with DATA_FILE.open("r", encoding="utf-8") as f:
    snow_rain_load_by_location = json.load(f)

# Extract location options list and build lookup dictionary
LOCATION_OPTIONS = [item["location"] for item in snow_rain_load_by_location]
LOCATION_MAP = {
    item["location"]: {"Ss": float(item["Ss"]), "Sr": float(item["Sr"])}
    for item in snow_rain_load_by_location
}


def calculate_snow_load(inputs: dict, precisions: dict) -> dict:
    """Executes OBC Part 9 Snow Load calculation using location database lookup."""
    location = str(inputs["Location"])
    w = float(inputs["w"])

    loc_data = LOCATION_MAP.get(location, {"Ss": 0.0, "Sr": 0.0})
    ss = loc_data["Ss"]
    sr = loc_data["Sr"]

    p_w = precisions.get("w", 2)
    p_ss = precisions.get("Ss", 2)
    p_sr = precisions.get("Sr", 2)
    p_cb = precisions.get("Cb", 2)
    p_s = precisions.get("S", 2)

    cb = 0.45 if w <= 4.3 else 0.55
    cb_cond = rf"\le 4.3\text{{ m}}" if w <= 4.3 else rf"> 4.3\text{{ m}}"

    calculated_s = (cb * ss) + sr
    minimum_s = 1.0
    final_s = max(calculated_s, minimum_s)

    steps = [
        {
            "step": 1,
            "description": f"Look up ground snow load (S_s) and rain load (S_r) for {location}",
            "formula_general": r"$$S_s, S_r = \text{Lookup}(\text{Location})$$",
            "formula_substituted": rf"$$\text{{Location}} = \text{{{location}}} \implies S_s = {ss:.{p_ss}f}\text{{ kPa}}, \quad S_r = {sr:.{p_sr}f}\text{{ kPa}}$$",
            "symbol": rf"S_s = {ss:.{p_ss}f}\text{{ kPa}}, \quad S_r",
            "result": sr,
            "precision": p_sr,
            "units": "kPa"
        },
        {
            "step": 2,
            "description": "Determine the basic roof snow-load factor",
            "formula_general": r"$$C_b = \begin{cases} 0.45 & \text{if } w \le 4.3\text{ m} \\ 0.55 & \text{if } w > 4.3\text{ m} \end{cases}$$",
            "formula_substituted": rf"$$C_b = {cb:.{p_cb}f} \quad \text{{(since }} w = {w:.{p_w}f}\text{{ m }} {cb_cond}\text{{)}}$$",
            "symbol": "C_b",
            "result": cb,
            "precision": p_cb,
            "units": ""
        },
        {
            "step": 3,
            "description": "Calculate specified roof snow load",
            "formula_general": r"$$S = C_b \times S_s + S_r$$",
            "formula_substituted": rf"$$S = {cb:.{p_cb}f} \times {ss:.{p_ss}f} + {sr:.{p_sr}f} = {calculated_s:.{p_s}f} \text{{ kPa}}$$",
            "symbol": "S",
            "result": calculated_s,
            "precision": p_s,
            "units": "kPa"
        },
        {
            "step": 4,
            "description": "Apply the minimum specified snow load",
            "formula_general": r"$$S = \max(C_b \times S_s + S_r, 1.0 \text{ kPa})$$",
            "formula_substituted": rf"$$S = \max({calculated_s:.{p_s}f} \text{{ kPa}}, 1.00 \text{{ kPa}}) = {final_s:.{p_s}f} \text{{ kPa}}$$",
            "symbol": "S",
            "result": final_s,
            "precision": p_s,
            "units": "kPa"
        }
    ]

    return {
        "main_result_latex": rf"$$S = {final_s:.{p_s}f}\text{{ kPa}}$$",
        "results": {"S": final_s, "Cb": cb, "Ss": ss, "Sr": sr},
        "steps": steps
    }


snow_load_variables = [
    {"symbol": "S", "latex": "S", "name": "Specified snow load", "units": "kPa", "is_input": False},
    {"symbol": "Cb", "latex": "C_b", "name": "Basic roof snow-load factor", "units": "", "is_input": False},
    {"symbol": "Ss", "latex": "S_s", "name": "Ground snow load", "units": "kPa", "is_input": False},
    {"symbol": "Sr", "latex": "S_r", "name": "Rain load", "units": "kPa", "is_input": False},
    {
        "symbol": "Location",
        "latex": r"\text{Location}",
        "name": "Municipality Location",
        "units": "",
        "is_input": True,
        "widget": "selectbox",
        "options": LOCATION_OPTIONS,
        "default": LOCATION_OPTIONS[0],
        "help": "Select the location to automatically look up Ss and Sr."
    },
    {
        "symbol": "w",
        "latex": "w",
        "name": "Roof width",
        "units": "m",
        "is_input": True,
        "min": 0.1,
        "step": 0.1,
        "help": "Roof width."
    }
]

snow_load_map_url = "https://www.google.com/maps/d/viewer?mid=1rOmkZ8IGp56MVXm2q9rcsw5Rxq8ErC0&femb=1&ll=48.278889463158336%2C-84.54679069999999&z=5"
snow_load_notes = (
    "**General Calculation Notes:**\n"
    "- Specified snow load calculations conform to **OBC Part 9 (Section 9.23.11.7)**.\n"
    "- Ground snow load ($S_s$) and rain load ($S_r$) are automatically populated based on the selected municipality.\n"
    "- The minimum specified roof snow load ($S$) is set at $1.0\\text{ kPa}$ as per OBC requirements."
)

snow_load_calculator = Calculation(
    calc_id="snow_load",
    title="OBC Part 9 — Snow Load",
    subtitle="Calculate the specified roof snow load based on the Ontario Building Code (Part 9).",
    variables=snow_load_variables,
    calculate_fn=calculate_snow_load,
    code_custom_notes=snow_load_notes,
    reference_link=("🗺️ Open Ontario Snow Load Map", snow_load_map_url)
)
