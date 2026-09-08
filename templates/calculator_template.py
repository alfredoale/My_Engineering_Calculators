"""Template for a formula-based Streamlit engineering calculator.

Copy this file into an appropriate package under calculator_scripts/, rename the
public symbols, implement the calculation, and register the Calculation in
calculator_scripts/__init__.py.
"""

from core.calculator_model import Calculation


CALCULATOR_ID = "example_calculator"


def calculate_example(inputs: dict, precisions: dict) -> dict:
    """Calculate the result from validated input values."""
    input_a = float(inputs["input_a"])
    input_b = float(inputs["input_b"])

    result_precision = precisions.get("result", 2)
    result = input_a * input_b

    return {
        # Required for formula-based calculators. Streamlit renders this as LaTeX.
        "main_result_latex": (
            rf"$$R = {result:.{result_precision}f}\text{{ kN}}$$"
        ),
        # Useful for automated tests and callers that need numeric outputs.
        "results": {"result": result},
        # Steps are rendered in order. A step with symbol/result becomes linkable.
        "steps": [
            {
                "step": 1,
                "description": "Multiply the two input values",
                "formula_general": r"$$R = A \times B$$",
                "formula_substituted": (
                    rf"$$R = {input_a:.{precisions.get('input_a', 2)}f}"
                    rf" \times {input_b:.{precisions.get('input_b', 2)}f}"
                    rf" = {result:.{result_precision}f}\text{{ kN}}$$"
                ),
                "symbol": "R",
                "latex": "R",
                "result": result,
                "precision": result_precision,
                "units": "kN",
            }
        ],
    }


example_variables = [
    {
        "symbol": "result",
        "latex": "R",
        "name": "Calculated result",
        "units": "kN",
        "is_input": False,
    },
    {
        "symbol": "input_a",
        "latex": "A",
        "name": "First input",
        "units": "kN",
        "is_input": True,
        "min": 0.0,
        "step": 0.1,
        "help": "Describe what this input represents.",
    },
    {
        "symbol": "input_b",
        "latex": "B",
        "name": "Second input",
        "units": "m",
        "is_input": True,
        "min": 0.0,
        "step": 0.1,
        "help": "Describe what this input represents.",
    },
]


example_notes = (
    "**Calculation Notes:**\n"
    "- Replace this text with assumptions, limitations, and code references.\n"
    "- Add a `reference_link=(\"Reference\", \"https://example.com\")` "
    "argument when an external reference is useful."
)


example_calculator = Calculation(
    calc_id=CALCULATOR_ID,
    title="Example Calculator",
    subtitle="Replace this subtitle with a concise description of the calculation.",
    variables=example_variables,
    calculate_fn=calculate_example,
    code_custom_notes=example_notes,
)


# Register the calculator in calculator_scripts/__init__.py:
#
# from .your_package.your_module import example_calculator
#
# CALCULATORS = {
#     ...,
#     example_calculator.title: example_calculator,
# }
