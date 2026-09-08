# My Engineering Calculators

This repository contains engineering calculators and reference tables built with Streamlit. The calculators are intended to assist with day-to-day projects. Verify every result independently and use professional judgment before relying on it.

## Run the app

Create or activate a virtual environment, install the dependencies, and start Streamlit from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run home.py
```

Run the tests with:

```bash
python -m pytest -q
```

## Add a calculator or table

Copy the relevant file from the [templates](templates) directory. The templates are examples and are not loaded by the app until they are copied to an application directory.

### Formula calculator

Use [templates/calculator_template.py](templates/calculator_template.py) when the result is calculated from input values.

1. Copy the file into a suitable package under `calculator_scripts/`.
2. Rename `example_*` symbols, implement the calculation, and update the variable metadata.
3. Return a dictionary containing `main_result_latex`. Include numeric values in `results` for tests or callers, and add ordered `steps` for the rendered calculation details.
4. Import the calculator in `calculator_scripts/__init__.py` and add it to `CALCULATORS`. Python calculators require this explicit registration.
5. Add focused tests for the calculation and any edge cases.

### Lookup calculator

Use [templates/lookup_calculator_template.py](templates/lookup_calculator_template.py) when a calculator selects a row from a JSON table and displays one or more values.

1. Copy the file into a package under `calculator_scripts/` and update `DATA_FILE`.
2. Match the field names and nested value/unit structure to the JSON table.
3. Build selector options from the table data so the UI cannot select values absent from the source.
4. Match every required selector in `calculate_example_lookup` and raise `ValueError` when no row exists.
5. Register the resulting `Calculation` in `calculator_scripts/__init__.py` and add tests for representative matches and missing combinations.

### Data table

Use [templates/data_table_template.json](templates/data_table_template.json) for a read-only reference table. Copy it below `data/`, then replace its placeholder metadata and rows. Every JSON file below `data/` is discovered automatically and appears as a table in the app; no Python registration is needed.

The canonical table structure is:

```json
{
	"metadata": {
		"title": "Table title",
		"subtitle": "Optional subtitle",
		"column_titles": {
			"field": "Displayed column title",
			"nested.value": "Displayed nested column title"
		}
	},
	"data": [
		{"field": "value", "nested": {"value": 1, "unit": "kN"}}
	],
	"table_notes": "Optional Markdown notes"
}
```

`metadata.title` and `data` are required. `subtitle`, `column_titles`, and `table_notes` are optional. Table rows must be objects. Nested objects are flattened into dot-separated columns, so `nested.value` and `nested.unit` become separate displayed columns. `table_notes` may be a Markdown string or an object of labels and values.

## Calculator contracts

Each calculator is a `Calculation` object constructed with a unique `calc_id`, a title and subtitle, variable metadata, and a `calculate_fn(inputs, precisions)` function.

Each variable normally contains:

```python
{
		"symbol": "L",
		"latex": "L",
		"name": "Beam span length",
		"units": "m",
		"is_input": True,
}
```

Input variables may also specify `widget`, `options`, `min`, `max`, `step`, and `help`. Supported selection widgets include `selectbox`, `radio`, `select_slider`, `pills`, and `multiselect`; numeric inputs use `number_input` or `slider`; boolean inputs use `checkbox` or `toggle`.

For formula or lookup calculators, the result should include:

- `main_result_latex`: the primary result rendered in LaTeX.
- `results`: optional numeric or structured results useful for tests and callers.
- `steps`: optional ordered dictionaries with `step`, `description`, formulas, and result fields.

A step containing both `symbol` and `result` is exposed as a linkable value for another active calculator. Result steps can also include `latex`, `precision`, and `units`. Use `code_custom_notes` for assumptions and limitations, and `reference_link=("Label", "URL")` for an external source.

## Tables, filtering, and linking

Data tables support text search, per-column value filters, and resettable filter state. Formula and lookup calculators can expose numeric input and result variables to other active calculator instances when their units match exactly. Keep units consistent if a value should be linkable.

Variable metadata may contain `default` values, but the current session-state initializer does not apply them automatically. Set initial values in the implementation only when that behavior is required and tested.

## Project layout

- `home.py`: Streamlit application entry point.
- `core/calculator_model.py`: calculator model, widget rendering, result rendering, and linking.
- `calculator_scripts/`: registered Python calculators and table discovery code.
- `data/`: automatically discovered JSON data tables.
- `templates/`: copyable authoring templates; files here are not loaded directly.
- `tests/`: automated tests for table schemas and calculator behavior.

## Legal

- [License](LICENSE.txt)
- [Terms of Use](terms_of_use.md)
- [Privacy Policy](privacy_policy.md)

For questions or suggestions, open an issue.