from .ontario_building_code_2024.version_2025_01.part_9.specified_snow_load import snow_load_calculator
from .ontario_building_code_2024.version_2025_01.part_9.maximum_floor_joist_span import maximum_floor_joist_span_calculator
from .data_table import data_table_calculators
from .structural_analysis.beam_reactions import beam_calculator

CALCULATORS = {
    snow_load_calculator.title: snow_load_calculator,
    maximum_floor_joist_span_calculator.title: maximum_floor_joist_span_calculator,
    **data_table_calculators,
    beam_calculator.title: beam_calculator
}