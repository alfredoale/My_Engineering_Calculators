from typing import Any, Callable, List, Optional, Tuple
import streamlit as st

from core.table_filters import (
    column_values,
    filter_table_records,
    sort_filter_options,
    table_columns,
)


def format_unit_latex(unit_str: str) -> str:
    """
    Formats engineering unit strings cleanly into LaTeX math mode syntax.
    Replaces unicode dots or broken cdotp sequences with proper LaTeX \cdot spacing.
    """
    if not unit_str:
        return ""
    cleaned = unit_str.replace("·", r"}\cdot\text{").replace(r"\cdotp", r"}\cdot\text{")
    return rf" \text{{ {cleaned}}}"


class Calculation:
    """
    Generic calculation model and UI runner for engineering calculations.
    Encapsulates variable definitions, execution logic, persistence, and rendering.
    """

    def __init__(
        self,
        calc_id: str,
        title: str,
        subtitle: str,
        variables: List[dict],
        calculate_fn: Callable[[dict, dict], dict],
        code_custom_notes: str = "",
        reference_link: Optional[Tuple[str, str]] = None,
        is_table: bool = False
    ):
        self.calc_id = calc_id
        self.title = title
        self.subtitle = subtitle
        self.variables = variables
        self.calculate_fn = calculate_fn
        self.code_custom_notes = code_custom_notes
        self.reference_link = reference_link  # Tuple format: ("Button Label", "URL")
        self.is_table = is_table

    def calculate(self, inputs: dict, precisions: dict) -> dict:
        """Executes the core engineering logic using supplied inputs and precisions."""
        return self.calculate_fn(inputs, precisions)

    def initialize_session_state(self, instance_id: str, calc_data_store: dict):
        """
        Initializes default values in persistent state store for a specific calculator instance.
        """
        if instance_id not in calc_data_store:
            calc_data_store[instance_id] = {
                "inputs": {},
                "linked": {},
                "link_select": {},
                "precisions": {},
                "notes": ""
            }

        inst_data = calc_data_store[instance_id]

        for var in self.variables:
            symbol = var["symbol"]
            widget_type = var.get("widget", var.get("type", "number_input")).lower()
            opts = var.get("options", [])

            if var.get("is_input", False):
                if symbol not in inst_data["inputs"]:
                    if widget_type == "slider":
                        min_v = float(var.get("min", 0.0))
                        default_v = float(var.get("default", min_v))
                        inst_data["inputs"][symbol] = default_v
                    elif widget_type in ("selectbox", "radio", "select_slider", "pills", "spills"):
                        default_v = var.get("default", opts[0] if opts else None)
                        inst_data["inputs"][symbol] = default_v
                    elif widget_type == "multiselect":
                        default_v = var.get("default", [])
                        inst_data["inputs"][symbol] = default_v
                    elif widget_type in ("checkbox", "toggle"):
                        default_v = bool(var.get("default", False))
                        inst_data["inputs"][symbol] = default_v
                    else:
                        min_v = float(var["min"]) if "min" in var and var["min"] is not None else None
                        try:
                            default_v = float(var.get("default", 0.0))
                        except (ValueError, TypeError):
                            default_v = min_v if min_v is not None else 0.0
                        if min_v is not None and default_v < min_v:
                            default_v = min_v
                        inst_data["inputs"][symbol] = default_v

            if symbol not in inst_data["precisions"]:
                inst_data["precisions"][symbol] = 2

            if symbol not in inst_data["linked"]:
                inst_data["linked"][symbol] = False

    def render_sidebar_inputs(
        self, 
        instance_id: str, 
        instance_label: str, 
        available_vars: list, 
        calc_data_store: dict
    ) -> dict:
        """
        Renders input controls for this calculator instance inside the sidebar.
        Renders the main input control first, followed below by the variable linking controls.
        """
        inst_data = calc_data_store[instance_id]
        resolved_inputs = {}

        for var in self.variables:
            if not var.get("is_input", False):
                continue

            symbol = var["symbol"]
            widget_type = var.get("widget", var.get("type", "number_input")).lower()
            opts = var.get("options", [])
            var_units = var.get("units", "").strip()

            base_help = var.get("help", var["name"])
            help_text = f"{base_help} In {var_units}." if var_units else base_help

            # Label always displays units beside symbol if present
            widget_label = f"{symbol} [{var_units}] ({var['name']})" if var_units else f"{symbol} ({var['name']})"

            # Linking is strictly supported for numeric inputs (number_input and slider)
            supports_linking = widget_type in ("number_input", "slider")

            toggle_key = f"toggle_link_{instance_id}_{symbol}"
            select_key = f"select_link_{instance_id}_{symbol}"
            input_key = f"input_{instance_id}_{symbol}"

            matching_candidates = []
            is_linked = False
            linked_value = None

            if supports_linking:
                # Filter matching candidate variables from other active instances
                matching_candidates = [
                    v for v in available_vars 
                    if v["instance_id"] != instance_id  # Exclude self
                    and v["unit"].strip() == var_units   # Match units strictly
                ]
                has_candidates = len(matching_candidates) > 0

                # Pre-evaluate toggle link status from session state
                if toggle_key in st.session_state:
                    is_linked = bool(st.session_state[toggle_key]) and has_candidates
                else:
                    is_linked = bool(inst_data["linked"].get(symbol, False)) and has_candidates

                inst_data["linked"][symbol] = is_linked

                # Determine selected linked variable value
                candidate_options = [v["id"] for v in matching_candidates]
                current_link_id = st.session_state.get(select_key, inst_data["link_select"].get(symbol))

                if is_linked and current_link_id:
                    selected_var = next((v for v in matching_candidates if v["id"] == current_link_id), None)
                    if selected_var is not None:
                        linked_value = selected_var["value"]
            else:
                inst_data["linked"][symbol] = False

            # Determine default bounds and values
            if widget_type in ("number_input", "slider"):
                min_v = float(var["min"]) if "min" in var and var["min"] is not None else None
                max_v = float(var["max"]) if "max" in var and var["max"] is not None else None
                step_v = float(var["step"]) if "step" in var and var["step"] is not None else None

                try:
                    fallback_def = float(var.get("default", 0.0))
                except (ValueError, TypeError):
                    fallback_def = min_v if min_v is not None else 0.0

                if min_v is not None and fallback_def < min_v:
                    fallback_def = min_v

                current_input_val = inst_data["inputs"].get(symbol, fallback_def)
                if is_linked and linked_value is not None:
                    current_input_val = linked_value
            else:
                min_v, max_v, step_v = None, None, None
                fallback_def = var.get(
                    "default",
                    opts[0] if opts else (False if widget_type in ("checkbox", "toggle") else [] if widget_type == "multiselect" else None)
                )
                current_input_val = inst_data["inputs"].get(symbol, fallback_def)

            if widget_type == "slider":
                slider_min = float(var.get("min", 0.0))
                slider_max = float(var.get("max", 100.0))
                slider_step = float(var.get("step", 1.0))
                try:
                    slider_val = float(current_input_val) if current_input_val is not None else slider_min
                except (ValueError, TypeError):
                    slider_val = slider_min
                if slider_val < slider_min:
                    slider_val = slider_min
                if slider_val > slider_max:
                    slider_val = slider_max

                val = st.sidebar.slider(
                    label=widget_label,
                    min_value=slider_min,
                    max_value=slider_max,
                    value=slider_val,
                    step=slider_step,
                    help=help_text,
                    key=input_key,
                    disabled=is_linked
                )
            elif widget_type == "selectbox":
                default_idx = opts.index(current_input_val) if current_input_val in opts else 0
                val = st.sidebar.selectbox(
                    label=widget_label,
                    options=opts,
                    index=default_idx,
                    help=help_text,
                    key=input_key,
                    disabled=is_linked
                )
            elif widget_type == "multiselect":
                default_sel = current_input_val if isinstance(current_input_val, list) else []
                val = st.sidebar.multiselect(
                    label=widget_label,
                    options=opts,
                    default=default_sel,
                    help=help_text,
                    key=input_key,
                    disabled=is_linked
                )
            elif widget_type in ("checkbox", "toggle"):
                val = st.sidebar.checkbox(
                    label=widget_label,
                    value=bool(current_input_val),
                    help=help_text,
                    key=input_key,
                    disabled=is_linked
                )
            else:
                # Default to number_input
                try:
                    num_val = float(current_input_val) if current_input_val is not None else (min_v if min_v is not None else 0.0)
                except (ValueError, TypeError):
                    num_val = min_v if min_v is not None else 0.0

                if min_v is not None and num_val < min_v:
                    num_val = min_v
                if max_v is not None and num_val > max_v:
                    num_val = max_v
                
                val = st.sidebar.number_input(
                    label=widget_label,
                    min_value=min_v,
                    max_value=max_v,
                    value=num_val,
                    step=step_v,
                    help=help_text,
                    key=input_key,
                    disabled=is_linked
                )

            if supports_linking:
                col_t, col_s = st.sidebar.columns([1, 2])
                has_candidates = len(matching_candidates) > 0

                with col_t:
                    toggle_val = st.toggle(
                        "Link",
                        value=is_linked,
                        disabled=not has_candidates,
                        key=toggle_key,
                        help="Link this input to a calculated or input variable from another active calculator." if has_candidates else "No available variables with matching units to link."
                    )
                    is_linked = toggle_val and has_candidates
                    inst_data["linked"][symbol] = is_linked

                with col_s:
                    candidate_options = [v["id"] for v in matching_candidates]
                    candidate_map = {v["id"]: v["display"] for v in matching_candidates}

                    current_link_id = inst_data["link_select"].get(symbol)
                    default_idx = candidate_options.index(current_link_id) if current_link_id in candidate_options else 0

                    selected_link_id = st.selectbox(
                        "Linked Variable",
                        options=candidate_options,
                        index=default_idx if candidate_options else None,
                        format_func=lambda x: candidate_map.get(x, x),
                        disabled=not is_linked,
                        key=select_key,
                        label_visibility="collapsed"
                    )
                    inst_data["link_select"][symbol] = selected_link_id

                    if is_linked and selected_link_id:
                        selected_var = next((v for v in matching_candidates if v["id"] == selected_link_id), None)
                        if selected_var is not None:
                            linked_value = selected_var["value"]

            # Store resolved value
            if is_linked and linked_value is not None:
                resolved_inputs[symbol] = linked_value
            else:
                resolved_inputs[symbol] = val
                inst_data["inputs"][symbol] = val

        return resolved_inputs

    def render_sidebar_precisions(self, instance_id: str, calc_data_store: dict) -> dict:
        """Renders decimal precision sliders for each variable in this calculator instance."""
        inst_data = calc_data_store[instance_id]
        precisions = {}

        for var in self.variables:
            sym = var["symbol"]
            prec_key = f"prec_{instance_id}_{sym}"
            default_p = inst_data["precisions"].get(sym, 2)

            p_val = st.number_input(
                label=f"{sym} ({var['name']})",
                min_value=0,
                max_value=6,
                value=default_p,
                step=1,
                key=prec_key
            )
            inst_data["precisions"][sym] = p_val
            precisions[sym] = p_val

        return precisions

    def render_main_canvas(self, config: dict):
        """Executes calculation logic and renders clean LaTeX step-by-step outputs on the main canvas."""
        st.title(self.title)
        st.markdown(self.subtitle)
        instance_label = config.get("instance_label", "")
        if isinstance(instance_label, str):
            instance_label = instance_label.strip()
        else:
            instance_label = ""

        if instance_label:
            st.caption(instance_label)

        if config["uploaded_image"] is not None:
            image_caption = f"{self.title} ({instance_label}) Reference Image" if instance_label else f"{self.title} Reference Image"
            st.image(config["uploaded_image"], caption=image_caption, use_container_width=True)

        inputs = config["inputs"]
        precisions = config["precisions"]

        missing_inputs = [
            var["symbol"] for var in self.variables
            if var.get("is_input", False) and inputs.get(var["symbol"]) is None
        ]

        if missing_inputs:
            st.info("Please complete all required input variables in the sidebar to perform the calculation.")
            return

        try:
            result = self.calculate(inputs=inputs, precisions=precisions)

            if "dataframe_records" in result:
                records = result["dataframe_records"]
                instance_id = config.get("instance_id", self.calc_id)
                filter_key = f"table_filters_{instance_id}"
                filter_state_key = f"{filter_key}_state"
                filter_state = st.session_state.setdefault(
                    filter_state_key,
                    {"search": "", "columns": {}},
                )
                column_filters: dict[str, Any] = {}
                filter_widget_keys = [f"{filter_key}_search"]

                def persist_filter_value(widget_key: str, column: str | None):
                    state = st.session_state[filter_state_key]
                    value = st.session_state[widget_key]
                    if column is None:
                        state["search"] = value
                    else:
                        state["columns"][column] = value

                def reset_table_filters():
                    state = st.session_state[filter_state_key]
                    state["search"] = ""
                    state["columns"] = {}
                    for widget_key in filter_widget_keys:
                        st.session_state[widget_key] = [] if widget_key != f"{filter_key}_search" else ""

                with st.expander("Filter", expanded=False):
                    search_key = f"{filter_key}_search"
                    if search_key not in st.session_state:
                        st.session_state[search_key] = filter_state["search"]
                    search = st.text_input(
                        "Search table values",
                        label_visibility="collapsed",
                        key=search_key,
                        placeholder="Search table values",
                        on_change=persist_filter_value,
                        args=(search_key, None),
                    )
                    for column in table_columns(records):
                        values = column_values(records, column)
                        options = sort_filter_options(values)
                        widget_key = f"{filter_key}_{column}"
                        if widget_key not in st.session_state:
                            st.session_state[widget_key] = filter_state["columns"].get(column, [])
                        selected_values = st.multiselect(
                            column,
                            options=options,
                            format_func=str,
                            key=widget_key,
                            on_change=persist_filter_value,
                            args=(widget_key, column),
                        )
                        filter_widget_keys.append(widget_key)
                        if selected_values:
                            column_filters[column] = set(selected_values)

                st.button(
                    "Reset table filters",
                    key=f"{filter_key}_reset",
                    on_click=reset_table_filters,
                )

                filtered_records = filter_table_records(records, search, column_filters)
                st.caption(f"Showing {len(filtered_records)} of {len(records)} rows")
                st.dataframe(
                    filtered_records,
                    hide_index=True,
                    use_container_width=True,
                )
                st.divider()
                st.subheader("Notes")

                if self.reference_link:
                    btn_label, btn_url = self.reference_link
                    st.link_button(btn_label, btn_url)

                if self.code_custom_notes.strip():
                    st.markdown(self.code_custom_notes)

                if result.get("table_notes"):
                    st.markdown(result["table_notes"])

                if config["custom_notes"].strip():
                    st.markdown(f"**Project Specific Notes:**  \n{config['custom_notes']}")
                return

            st.subheader("Given")
            for var in self.variables:
                if var.get("is_input", False):
                    val = inputs[var["symbol"]]
                    p = precisions.get(var["symbol"], 2)
                    unit_str = format_unit_latex(var.get("units", ""))

                    if isinstance(val, (int, float)) and not isinstance(val, bool):
                        st.markdown(rf"$${var['latex']} = {val:.{p}f}{unit_str}$$")
                    else:
                        st.markdown(rf"$${var['latex']} = \text{{{val}}}{unit_str}$$")

            st.subheader("We get")
            st.markdown(result["main_result_latex"])
            st.divider()

            if config["show_steps"]:
                st.subheader("Calculation Steps")
                for step in result.get("steps", []):
                    st.markdown(f"**Step {step['step']}: {step['description']}**")
                    if step.get("formula_general"):
                        st.markdown(step["formula_general"])
                    if step.get("formula_substituted"):
                        st.markdown(step["formula_substituted"])

                    if "symbol" in step and "result" in step:
                        p_res = step.get("precision", 2)
                        unit_str = format_unit_latex(step.get("units", ""))
                        symbol_latex = step.get("latex", step["symbol"])
                        st.markdown(rf"$${symbol_latex} = {step['result']:.{p_res}f}{unit_str}$$")
                    st.divider()

            st.subheader("Variables Reference")
            for var in self.variables:
                var_u = var.get("units", "")
                if var_u:
                    cleaned_u = var_u.replace("·", r"}\cdot\text{").replace(r"\cdotp", r"}\cdot\text{")
                    unit_display = rf" \text{{ ({cleaned_u})}}"
                else:
                    unit_display = ""
                st.markdown(rf"$${var['latex']} = \text{{{var['name']}}}{unit_display}$$")

            st.divider()
            st.subheader("Notes")

            if self.reference_link:
                btn_label, btn_url = self.reference_link
                st.link_button(btn_label, btn_url)

            if self.code_custom_notes.strip():
                st.markdown(self.code_custom_notes)

            if config["custom_notes"].strip():
                st.markdown(f"**Project Specific Notes:**  \n{config['custom_notes']}")

        except Exception as e:
            st.error(f"Calculation Error: {e}")