from typing import Callable, List, Optional, Tuple
import streamlit as st


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
    Encapsulates variable definitions, execution logic, rendering, and variable linking.
    """

    def __init__(
        self,
        calc_id: str,
        title: str,
        subtitle: str,
        variables: List[dict],
        calculate_fn: Callable[[dict, dict], dict],
        code_custom_notes: str = "",
        reference_link: Optional[Tuple[str, str]] = None
    ):
        self.calc_id = calc_id
        self.title = title
        self.subtitle = subtitle
        self.variables = variables
        self.calculate_fn = calculate_fn
        self.code_custom_notes = code_custom_notes
        self.reference_link = reference_link  # Tuple format: ("Button Label", "URL")

    def calculate(self, inputs: dict, precisions: dict) -> dict:
        """Executes the core engineering logic."""
        return self.calculate_fn(inputs, precisions)

    def initialize_session_state(self):
        """Initializes default values in Streamlit session state for this calculation."""
        for var in self.variables:
            if var.get("is_input", False):
                key = f"input_{self.calc_id}_{var['symbol']}"
                widget_type = var.get("widget", var.get("type", "number_input")).lower()
                opts = var.get("options", [])

                if key not in st.session_state:
                    if widget_type == "slider":
                        min_v = float(var.get("min", 0.0))
                        default_v = float(var.get("default", min_v))
                        st.session_state[key] = default_v
                    elif widget_type in ("selectbox", "radio", "select_slider", "pills", "spills"):
                        default_v = var.get("default", opts[0] if opts else None)
                        st.session_state[key] = default_v
                    elif widget_type == "multiselect":
                        default_v = var.get("default", [])
                        st.session_state[key] = default_v
                    elif widget_type in ("checkbox", "toggle"):
                        default_v = bool(var.get("default", False))
                        st.session_state[key] = default_v
                    else:
                        st.session_state[key] = var.get("default", None)

            prec_key = f"prec_{self.calc_id}_{var['symbol']}"
            if prec_key not in st.session_state:
                st.session_state[prec_key] = 2

        notes_key = f"notes_{self.calc_id}"
        if notes_key not in st.session_state:
            st.session_state[notes_key] = ""

    def render_sidebar_inputs(self, available_vars: dict, is_multi_calc: bool = False) -> Tuple[dict, dict]:
        """
        Renders input controls for this calculator inside the sidebar.
        Supports linking ALL inputs to available variables from other active calculators.
        Returns tuple of (inputs_dict, linked_info_dict).
        """
        inputs = {}
        linked_info = {}

        for var in self.variables:
            if var.get("is_input", False):
                symbol = var["symbol"]
                base_help = var.get("help", var["name"])
                help_text = f"{base_help} In {var['units']}." if var.get("units") else base_help

                # 1. Render input widget control first
                key = f"input_{self.calc_id}_{symbol}"
                widget_type = var.get("widget", var.get("type", "number_input")).lower()
                opts = var.get("options", [])

                if widget_type == "slider":
                    min_v = float(var.get("min", 0.0))
                    max_v = float(var.get("max", 100.0))
                    step_v = float(var.get("step", 1.0))
                    val = st.sidebar.slider(
                        label=f"{symbol} ({var['name']})",
                        min_value=min_v,
                        max_value=max_v,
                        step=step_v,
                        help=help_text,
                        key=key
                    )
                elif widget_type == "selectbox":
                    val = st.sidebar.selectbox(
                        label=f"{symbol} ({var['name']})",
                        options=opts,
                        help=help_text,
                        key=key
                    )
                elif widget_type == "checkbox":
                    val = st.sidebar.checkbox(
                        label=f"{symbol} ({var['name']})",
                        help=help_text,
                        key=key
                    )
                elif widget_type == "toggle":
                    val = st.sidebar.toggle(
                        label=f"{symbol} ({var['name']})",
                        help=help_text,
                        key=key
                    )
                else:
                    # Default: number_input
                    min_v = float(var["min"]) if "min" in var else None
                    max_v = float(var["max"]) if "max" in var else None
                    step_v = float(var["step"]) if "step" in var else None
                    val = st.sidebar.number_input(
                        label=f"{symbol} ({var['name']})",
                        min_value=min_v,
                        max_value=max_v,
                        step=step_v,
                        help=help_text,
                        key=key
                    )

                # 2. Render link option below the input control
                link_key = f"use_link_{self.calc_id}_{symbol}"
                select_link_key = f"select_link_{self.calc_id}_{symbol}"

                use_link = False
                if is_multi_calc or available_vars:
                    use_link = st.sidebar.checkbox(
                        "Link to another variable",
                        key=link_key
                    )

                if use_link:
                    if available_vars:
                        options_keys = list(available_vars.keys())
                        selected_key = st.sidebar.selectbox(
                            label=f"Select source variable for {symbol} ({var['name']})",
                            options=options_keys,
                            format_func=lambda k: available_vars[k]["label"],
                            key=select_link_key
                        )

                        source_var = available_vars[selected_key]
                        val_linked = source_var["value"]
                        st.sidebar.caption(
                            f"**Linked Value:** {val_linked} {var.get('units', '')}  \n"
                            f"*Source: {source_var['calc_title']} ({source_var['symbol']} - {source_var['name']})*"
                        )
                        inputs[symbol] = val_linked
                        linked_info[symbol] = source_var
                    else:
                        st.sidebar.caption("⚠️ No active source variables available to link from other calculators yet.")
                        inputs[symbol] = None
                else:
                    inputs[symbol] = val

        return inputs, linked_info

    def render_sidebar_precisions(self) -> dict:
        """Renders precision controls for this calculator."""
        precisions = {}
        for var in self.variables:
            prec_key = f"prec_{self.calc_id}_{var['symbol']}"
            p_val = st.number_input(
                label=f"{var['symbol']} ({var['name']})",
                min_value=0,
                max_value=6,
                value=st.session_state.get(prec_key, 2),
                step=1,
                key=prec_key
            )
            precisions[var["symbol"]] = p_val
        return precisions

    def render_main_canvas(self, config: dict):
        """Executes calculation and renders outputs on the main canvas inside its assigned tab."""
        st.subheader(self.title)
        st.markdown(self.subtitle)

        if config["uploaded_image"] is not None:
            st.image(config["uploaded_image"], caption=f"{self.title} - Reference Image", use_container_width=True)

        inputs = config["inputs"]
        precisions = config["precisions"]

        # Ensure all required inputs have a valid non-None value
        missing_inputs = [
            var["symbol"] for var in self.variables
            if var.get("is_input", False) and inputs[var["symbol"]] is None
        ]

        if missing_inputs:
            st.info("Please complete all required input variables in the sidebar to perform the calculation.")
            return

        try:
            # Execute calculation function
            result = self.calculate(inputs=inputs, precisions=precisions)

            # Display Given Parameters
            st.subheader("Given")
            for var in self.variables:
                if var.get("is_input", False):
                    val = inputs[var["symbol"]]
                    p = precisions.get(var["symbol"], 2)
                    unit_str = format_unit_latex(var["units"])

                    if isinstance(val, (int, float)) and not isinstance(val, bool):
                        st.markdown(rf"$${var['latex']} = {val:.{p}f}{unit_str}$$")
                    else:
                        st.markdown(rf"$${var['latex']} = \text{{{val}}}{unit_str}$$")

            # Display Main Result
            st.subheader("We get")
            st.markdown(result["main_result_latex"])
            st.divider()

            # Display Step-by-Step Calculation Steps
            if config["show_steps"]:
                st.subheader("Calculation Steps")
                for step in result["steps"]:
                    st.markdown(f"**Step {step['step']}: {step['description']}**")

                    st.caption("General Formula:")
                    st.markdown(step["formula_general"])

                    st.caption("Substituted Values:")
                    st.markdown(step["formula_substituted"])

                    p_res = step["precision"]
                    unit_str = format_unit_latex(step["units"])
                    st.markdown(rf"$${step['symbol']} = {step['result']:.{p_res}f}{unit_str}$$")
                    st.divider()

            # Variables Reference
            st.subheader("Variables Reference")
            for var in self.variables:
                if var["units"]:
                    cleaned_u = var["units"].replace("·", r"}\cdot\text{").replace(r"\cdotp", r"}\cdot\text{")
                    unit_display = rf" \text{{ ({cleaned_u})}}"
                else:
                    unit_display = ""
                st.markdown(rf"$${var['latex']} = \text{{{var['name']}}}{unit_display}$$")

            # Notes and Reference Links
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


def get_available_variables(active_calculators: List[Calculation], current_calc_id: str, precisions: dict) -> dict:
    """
    Collects inputs and calculated outputs from other active calculators from session state so they can be referenced/linked.
    Formats options as: "[Calc Title] Symbol — Name: Value Unit"
    """
    available = {}
    for calc in active_calculators:
        if calc.calc_id == current_calc_id:
            continue

        c_precs = precisions.get(calc.calc_id, {})
        c_inputs = {}

        # 1. Available Input Variables from other active calculators
        for var in calc.variables:
            if var.get("is_input", False):
                val = st.session_state.get(f"input_{calc.calc_id}_{var['symbol']}")
                c_inputs[var["symbol"]] = val
                if val is not None and isinstance(val, (int, float)) and not isinstance(val, bool):
                    p = c_precs.get(var["symbol"], 2)
                    unit_str = f" {var['units']}" if var.get("units") else ""
                    key = f"{calc.calc_id}.{var['symbol']}"
                    label = f"[{calc.title}] {var['symbol']} — {var['name']}: {val:.{p}f}{unit_str}"
                    available[key] = {
                        "label": label,
                        "value": float(val),
                        "symbol": var["symbol"],
                        "name": var["name"],
                        "units": var.get("units", ""),
                        "calc_title": calc.title
                    }

        # 2. Available Calculated Output Variables from other active calculators
        missing_inputs = [
            v["symbol"] for v in calc.variables
            if v.get("is_input", False) and c_inputs.get(v["symbol"]) is None
        ]
        if not missing_inputs:
            try:
                res = calc.calculate(inputs=c_inputs, precisions=c_precs)
                results_dict = res.get("results", {})
                for var in calc.variables:
                    if not var.get("is_input", False) and var["symbol"] in results_dict:
                        val = results_dict[var["symbol"]]
                        if val is not None and isinstance(val, (int, float)) and not isinstance(val, bool):
                            p = c_precs.get(var["symbol"], 2)
                            unit_str = f" {var['units']}" if var.get("units") else ""
                            key = f"{calc.calc_id}.{var['symbol']}"
                            label = f"[{calc.title}] {var['symbol']} — {var['name']}: {val:.{p}f}{unit_str}"
                            available[key] = {
                                "label": label,
                                "value": float(val),
                                "symbol": var["symbol"],
                                "name": var["name"],
                                "units": var.get("units", ""),
                                "calc_title": calc.title
                            }
            except Exception:
                pass

    return available