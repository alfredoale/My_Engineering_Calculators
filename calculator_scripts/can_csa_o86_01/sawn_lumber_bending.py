"""
Calculates the factored bending moment resistance (M_r) of sawn lumber 
members according to CAN/CSA-O86-01, Clause 5.5.4.
"""

from core.calculator_model import Calculation

def calculate_sawn_lumber_bending(inputs: dict, precisions: dict) -> dict:
    """Calculate factored bending moment resistance (M_r) from input values."""
    f_b = float(inputs["f_b"])
    S = float(inputs["S"])
    K_Zb = float(inputs["K_Zb"])
    K_L = float(inputs["K_L"])
    K_D = float(inputs["K_D"])
    K_H = float(inputs["K_H"])
    K_Sb = float(inputs["K_Sb"])
    K_T = float(inputs["K_T"])

    phi = 0.9

    # F_b calculation [MPa]
    F_b = f_b * (K_D * K_H * K_Sb * K_T)

    # M_r calculation: Phi * F_b * S * K_Zb * K_L
    # Units: MPa * mm^3 = (N/mm^2) * mm^3 = N*mm. Divide by 1e6 to convert to kN*m.
    M_r_Nmm = phi * F_b * S * K_Zb * K_L
    M_r = M_r_Nmm / 1e6

    # Precisions
    p_fb = precisions.get("f_b", 2)
    p_S = precisions.get("S", 0)
    p_K_Zb = precisions.get("K_Zb", 2)
    p_K_L = precisions.get("K_L", 2)
    p_K_D = precisions.get("K_D", 2)
    p_K_H = precisions.get("K_H", 2)
    p_K_Sb = precisions.get("K_Sb", 2)
    p_K_T = precisions.get("K_T", 2)
    p_F_b = precisions.get("F_b", 2)
    p_M_r = precisions.get("M_r", 2)

    return {
        "main_result_latex": (
            rf"$$M_r = {M_r:.{p_M_r}f}\text{{ kN}}\cdot\text{{m}}$$"
        ),
        "results": {
            "F_b": F_b,
            "M_r": M_r,
        },
        "steps": [
            {
                "step": 1,
                "description": "Calculate factored strength in bending ($F_b$)",
                "formula_general": r"$$F_b = f_b \times (K_D \times K_H \times K_{Sb} \times K_T)$$",
                "formula_substituted": (
                    rf"$$F_b = {f_b:.{p_fb}f} \times ({K_D:.{p_K_D}f} \times "
                    rf"{K_H:.{p_K_H}f} \times {K_Sb:.{p_K_Sb}f} \times {K_T:.{p_K_T}f}) "
                    rf"= {F_b:.{p_F_b}f}\text{{ MPa}}$$"
                ),
                "symbol": "F_b",
                "latex": "F_b",
                "result": F_b,
                "precision": p_F_b,
                "units": "MPa",
            },
            {
                "step": 2,
                "description": "Calculate factored bending moment resistance ($M_r$)",
                "formula_general": r"$$M_r = \Phi \times F_b \times S \times K_{Zb} \times K_L$$",
                "formula_substituted": (
                    rf"$$M_r = 0.9 \times {F_b:.{p_F_b}f} \times {S:.{p_S}f} \times "
                    rf"{K_Zb:.{p_K_Zb}f} \times {K_L:.{p_K_L}f} = "
                    rf"{M_r_Nmm:.{p_M_r}f}\text{{ N}}\cdot\text{{mm}} = "
                    rf"{M_r:.{p_M_r}f}\text{{ kN}}\cdot\text{{m}}$$"
                ),
                "symbol": "M_r",
                "latex": "M_r",
                "result": M_r,
                "precision": p_M_r,
                "units": "kN·m",
            },
        ],
    }


sawn_lumber_bending_variables = [
    {
        "symbol": "M_r",
        "latex": "M_r",
        "name": "Factored bending moment resistance",
        "units": "kN·m",
        "is_input": False,
    },
    {
        "symbol": "F_b",
        "latex": "F_b",
        "name": "Factored strength in bending",
        "units": "MPa",
        "is_input": False,
    },
    {
        "symbol": "f_b",
        "latex": "f_b",
        "name": "Specified strength in bending",
        "units": "MPa",
        "is_input": True,
        "min": 0.0,
        "step": 0.1,
        "help": "Specified strength in bending per CAN/CSA-O86-01 Tables 5.3.1A to 5.3.1D, 5.3.2, and 5.3.3.",
    },
    {
        "symbol": "S",
        "latex": "S",
        "name": "Section modulus",
        "units": "mm³",
        "is_input": True,
        "min": 0.0,
        "step": 100.0,
        "help": "Elastic section modulus of the sawn member.",
    },
    {
        "symbol": "K_Zb",
        "latex": "K_{Zb}",
        "name": "Size factor in bending",
        "units": "",
        "is_input": True,
        "min": 0.0,
        "step": 0.01,
        "help": "Size factor in bending according to Clause 5.4.5.",
    },
    {
        "symbol": "K_L",
        "latex": "K_L",
        "name": "Lateral stability factor",
        "units": "",
        "is_input": True,
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
        "help": "Lateral stability factor according to Clause 5.5.4.2.",
    },
    {
        "symbol": "K_D",
        "latex": "K_D",
        "name": "Load duration factor",
        "units": "",
        "is_input": True,
        "min": 0.0,
        "step": 0.05,
        "help": "Load duration factor according to Clause 4.3.2 and Table 4.3.2.2.",
    },
    {
        "symbol": "K_H",
        "latex": "K_H",
        "name": "System factor",
        "units": "",
        "is_input": True,
        "min": 0.0,
        "step": 0.05,
        "help": "System factor according to Clause 4.3.5.",
    },
    {
        "symbol": "K_Sb",
        "latex": "K_{Sb}",
        "name": "Service condition factor for bending",
        "units": "",
        "is_input": True,
        "min": 0.0,
        "step": 0.05,
        "help": "Service condition factor for bending.",
    },
    {
        "symbol": "K_T",
        "latex": "K_T",
        "name": "Treatment factor",
        "units": "",
        "is_input": True,
        "min": 0.0,
        "step": 0.05,
        "help": "Treatment factor according to Clause 4.3.4.1.",
    },
]


sawn_lumber_bending_notes = (
    "**Calculation Notes:**\n"
    "- Standard reference: CAN/CSA-O86-01 (Engineering Design in Wood), Clause 5.5.4.\n"
    "- Member resistance factor for sawn lumber bending $\\Phi = 0.9$.\n"
    "- Input section modulus $S$ in $\\text{mm}^3$. Result $M_r$ is converted from $\\text{N}\\cdot\\text{mm}$ to $\\text{kN}\\cdot\\text{m}$ ($1\\text{ kN}\\cdot\\text{m} = 10^6\\text{ N}\\cdot\\text{mm}$)."
)


sawn_lumber_bending_calculator = Calculation(
    calc_id="sawn_lumber_bending",
    title="CAN/CSA-O86-01 Sawn Lumber Bending Resistance",
    subtitle="Calculates factored bending moment resistance ($M_r$) according to Clause 5.5.4",
    variables=sawn_lumber_bending_variables,
    calculate_fn=calculate_sawn_lumber_bending,
    code_custom_notes=sawn_lumber_bending_notes,
)