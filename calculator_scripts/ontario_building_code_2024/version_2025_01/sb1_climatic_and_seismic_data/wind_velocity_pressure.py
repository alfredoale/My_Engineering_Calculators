"""
Calculates the wind velocity pressure (q) according to MMAH Supplementary Standard SB-1.
"""

from core.calculator_model import Calculation


def calculate_wind_velocity_pressure(inputs: dict, precisions: dict) -> dict:
    """Calculate wind velocity pressure (q) in kPa from wind speed (V) in m/s."""
    V = float(inputs["V"])

    # Formula: q = 0.00064645 * V^2
    q = 0.00064645 * (V**2)

    # Precisions
    p_V = precisions.get("V", 2)
    p_q = precisions.get("q", 4)

    return {
        "main_result_latex": rf"$$q = {q:.{p_q}f}\text{{ kPa}}$$",
        "results": {
            "q": q,
        },
        "steps": [
            {
                "step": 1,
                "description": "Calculate wind velocity pressure ($q$)",
                "formula_general": r"$$q = 0.00064645 \times V^2$$",
                "formula_substituted": (
                    rf"$$q = 0.00064645 \times ({V:.{p_V}f})^2 "
                    rf"= {q:.{p_q}f}\text{{ kPa}}$$"
                ),
                "symbol": "q",
                "latex": "q",
                "result": q,
                "precision": p_q,
                "units": "kPa",
            },
        ],
    }


wind_velocity_pressure_variables = [
    {
        "symbol": "q",
        "latex": "q",
        "name": "Wind velocity pressure",
        "units": "kPa",
        "is_input": False,
    },
    {
        "symbol": "V",
        "latex": "V",
        "name": "Wind speed",
        "units": "m/s",
        "is_input": True,
        "min": 0.0,
        "step": 0.1,
        "help": "Wind speed in meters per second (m/s).",
    },
]


wind_velocity_pressure_notes = (
    "**Calculation Notes:**\n"
    "- Standard reference: MMAH Supplementary Standard SB-1[span_0](start_span)[span_0](end_span).\n"
    "- To convert wind speed from $\\text{km/h}$ to $\\text{m/s}$, divide the value in $\\text{km/h}$ by $3.6$.\n"
    "  $$\\text{Speed (m/s)} = \\frac{\\text{Speed (km/h)}}{3.6}$$"
)


wind_velocity_pressure_calculator = Calculation(
    calc_id="mmah_sb1_wind_velocity_pressure",
    title="MMAH SB-1 Wind Velocity Pressure",
    subtitle="Calculates wind velocity pressure ($q$) from wind speed ($V$)",
    variables=wind_velocity_pressure_variables,
    calculate_fn=calculate_wind_velocity_pressure,
    code_custom_notes=wind_velocity_pressure_notes,
)
