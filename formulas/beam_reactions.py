from core.calculator_model import Calculation


def calculate_beam_reactions(inputs: dict, precisions: dict) -> dict:
    """Executes Simply Supported Beam Reactions calculation for Uniformly Distributed Load."""
    q = float(inputs["q"])
    l_len = float(inputs["L"])

    p_q = precisions.get("q", 2)
    p_l = precisions.get("L", 2)
    p_ra = precisions.get("R_A", 2)
    p_rb = precisions.get("R_B", 2)
    p_m = precisions.get("M_max", 2)

    total_load = q * l_len
    ra = total_load / 2.0
    rb = ra
    m_max = (q * (l_len ** 2)) / 8.0

    steps = [
        {
            "step": 1,
            "description": "Calculate vertical support reactions (R_A and R_B)",
            "formula_general": r"$$R_A = R_B = \frac{q \times L}{2}$$",
            "formula_substituted": rf"$$R_A = R_B = \frac{{{q:.{p_q}f} \times {l_len:.{p_l}f}}}{{2}} = {ra:.{p_ra}f} \text{{ kN}}$$",
            "symbol": "R_A = R_B",
            "result": ra,
            "precision": p_ra,
            "units": "kN"
        },
        {
            "step": 2,
            "description": "Calculate maximum bending moment at mid-span",
            "formula_general": r"$$M_{max} = \frac{q \times L^2}{8}$$",
            "formula_substituted": rf"$$M_{{max}} = \frac{{{q:.{p_q}f} \times ({l_len:.{p_l}f})^2}}{{8}} = {m_max:.{p_m}f} \text{{ kN}}\cdot\text{{m}}$$",
            "symbol": "M_{max}",
            "result": m_max,
            "precision": p_m,
            "units": "kN·m"
        }
    ]

    return {
        "main_result_latex": rf"$$R_A = R_B = {ra:.{p_ra}f}\text{{ kN}}, \quad M_{{max}} = {m_max:.{p_m}f}\text{{ kN}}\cdot\text{{m}}$$",
        "results": {"R_A": ra, "R_B": rb, "M_max": m_max},
        "steps": steps
    }


beam_variables = [
    {"symbol": "R_A", "latex": "R_A", "name": "Reaction at Support A", "units": "kN", "is_input": False},
    {"symbol": "R_B", "latex": "R_B", "name": "Reaction at Support B", "units": "kN", "is_input": False},
    {"symbol": "M_max", "latex": "M_{max}", "name": "Maximum Bending Moment", "units": "kN·m", "is_input": False},
    {"symbol": "q", "latex": "q", "name": "Uniformly distributed load", "units": "kN/m", "is_input": True, "min": 0.0, "step": 0.5, "help": "Uniformly distributed load on the beam."},
    {"symbol": "L", "latex": "L", "name": "Beam span length", "units": "m", "is_input": True, "min": 0.5, "step": 0.5, "help": "Span length of the beam."}
]

beam_notes = (
    "**Beam Analysis Notes:**\n"
    "- Standard simply supported beam model subjected to a uniform continuous load $q$.\n"
    "- Reactions are symmetric: $R_A = R_B = \\frac{qL}{2}$.\n"
    "- Maximum moment occurs at mid-span: $M_{max} = \\frac{qL^2}{8}$."
)

beam_calculator = Calculation(
    calc_id="beam_reactions",
    title="Beam Reactions (UDL)",
    subtitle="Calculate support reactions and maximum bending moment for a simply supported beam with a uniformly distributed load.",
    variables=beam_variables,
    calculate_fn=calculate_beam_reactions,
    code_custom_notes=beam_notes
)