from .snow_load import snow_load_calculator
from .beam_reactions import beam_calculator

CALCULATORS = {
    snow_load_calculator.title: snow_load_calculator,
    beam_calculator.title: beam_calculator
}