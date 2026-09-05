import uuid
import streamlit as st
from calculator_scripts import CALCULATORS


def get_instance_label(instance: dict) -> str:
    """Return a trimmed instance label, or an empty string when absent."""
    label = instance.get("label", "")
    return label.strip() if isinstance(label, str) else ""


def format_instance_display(calc_title: str, label: str) -> str:
    """Format a calculator title with its optional instance label."""
    return f"{calc_title} ({label})" if label else calc_title


def gather_available_variables(active_instances: list, calc_data_store: dict) -> list:
    """
    Collects all current inputs and calculated outputs from all active calculator instances
    formatted as selectable options for linked dropdowns.
    Evaluates in two passes to resolve cross-linked variables reliably.
    """
    available_vars = []

    # First Pass: Collect base inputs and initial outputs
    for instance in active_instances:
        inst_id = instance["instance_id"]
        calc_key = instance["calc_key"]
        label = get_instance_label(instance)
        calc = CALCULATORS[calc_key]

        inst_data = calc_data_store.get(inst_id, {"inputs": {}, "linked": {}, "link_select": {}, "precisions": {}})
        inputs = inst_data.get("inputs", {})
        linked = inst_data.get("linked", {})
        precisions = inst_data.get("precisions", {})

        for var in calc.variables:
            if var.get("is_input", False):
                sym = var["symbol"]

                # Exclude variables that are currently linked to another variable
                if linked.get(sym, False):
                    continue

                val = inputs.get(sym, var.get("default", 0.0))
                p = precisions.get(sym, 2)
                val_formatted = f"{val:.{p}f}" if isinstance(val, (int, float)) and not isinstance(val, bool) else str(val)
                unit_str = var.get("units", "")

                display_str = f"{sym} = {val_formatted} {unit_str} ({format_instance_display(calc.title, label)})".strip()

                available_vars.append({
                    "id": f"{inst_id}_{sym}",
                    "instance_id": inst_id,
                    "calc_title": calc.title,
                    "label": label,
                    "symbol": sym,
                    "value": val,
                    "unit": unit_str,
                    "display": display_str
                })

    # Second Pass: Resolve linked variables and calculate outputs
    for instance in active_instances:
        inst_id = instance["instance_id"]
        calc_key = instance["calc_key"]
        label = get_instance_label(instance)
        calc = CALCULATORS[calc_key]

        inst_data = calc_data_store.get(inst_id, {"inputs": {}, "linked": {}, "link_select": {}, "precisions": {}})
        inputs = dict(inst_data.get("inputs", {}))
        precisions = inst_data.get("precisions", {})

        for var in calc.variables:
            if var.get("is_input", False):
                sym = var["symbol"]
                if inst_data.get("linked", {}).get(sym, False):
                    linked_id = inst_data.get("link_select", {}).get(sym)
                    linked_var = next((v for v in available_vars if v["id"] == linked_id), None)
                    if linked_var and linked_var["value"] is not None:
                        inputs[sym] = linked_var["value"]

        try:
            res = calc.calculate(inputs=inputs, precisions=precisions)
            for step in res.get("steps", []):
                if "symbol" not in step or "result" not in step:
                    continue

                val = step.get("result")
                p = step.get("precision", 2)
                val_formatted = f"{val:.{p}f}" if isinstance(val, (int, float)) else str(val)
                unit_str = step.get("units", "")

                display_str = f"{step['symbol']} = {val_formatted} {unit_str} ({format_instance_display(calc.title, label)})".strip()

                available_vars.append({
                    "id": f"{inst_id}_{step['symbol']}",
                    "instance_id": inst_id,
                    "calc_title": calc.title,
                    "label": label,
                    "symbol": step["symbol"],
                    "value": val,
                    "unit": unit_str,
                    "display": display_str
                })
        except Exception:
            pass

    return available_vars


def main():
    st.set_page_config(page_title="My Engineering Calculators", layout="wide")

    # Persistent storage across reruns and tab switches
    if "active_instances" not in st.session_state:
        st.session_state["active_instances"] = []

    if "calc_data" not in st.session_state:
        st.session_state["calc_data"] = {}

    if "footer_accepted" not in st.session_state:
        st.session_state["footer_accepted"] = False

    calc_data_store = st.session_state["calc_data"]

    st.sidebar.header("Calculator Settings")

    st.sidebar.subheader("Add a Calculator / Table")
    
    selected_calc_key = st.sidebar.selectbox(
        "Select Calculator / Table",
        options=list(CALCULATORS.keys()),
        index=None,
        placeholder="Select Calculator or Table...",
        help="Select an engineering calculator or data table to add.",
        key="calc_type_selector"
    )

    calc_label_input = st.sidebar.text_input(
        "Label / Identifier",
        value="",
        placeholder=f"Instance {len(st.session_state['active_instances']) + 1}",
        help="Enter a custom name/label to distinguish this calculation instance.",
        key="calc_label_input"
    )

    # Centered Add Calculator Button
    col_l, col_c, col_r = st.sidebar.columns([1, 2, 1])
    with col_c:
        if st.button("Add Calculator / Table", use_container_width=True):
            if not selected_calc_key:
                st.sidebar.warning("Please select a calculator or table first.")
            else:
                new_id = f"{selected_calc_key.replace(' ', '_').lower()}_{uuid.uuid4().hex[:6]}"
                new_label = calc_label_input.strip()
                
                st.session_state["active_instances"].append({
                    "instance_id": new_id,
                    "calc_key": selected_calc_key,
                    "label": new_label
                })
                
                calc = CALCULATORS[selected_calc_key]
                calc.initialize_session_state(new_id, calc_data_store)
                
                st.session_state["selected_instance_id"] = new_id
                st.rerun()

    active_instances = st.session_state["active_instances"]

    if active_instances:
        with st.sidebar.expander("Active Calculator / Table List", expanded=False):
            to_remove = []
            for idx, inst in enumerate(active_instances):
                c_text, c_btn = st.columns([2, 1])
                with c_text:
                    label = get_instance_label(inst)
                    display_name = f"**{label}** " if label else ""
                    st.caption(f"{display_name}({inst['calc_key']})")
                with c_btn:
                    if st.button("Remove", key=f"remove_{inst['instance_id']}", use_container_width=True):
                        to_remove.append(idx)
            if to_remove:
                for idx in reversed(to_remove):
                    removed_inst = st.session_state["active_instances"].pop(idx)
                    st.session_state["calc_data"].pop(removed_inst["instance_id"], None)
                st.rerun()

    if not active_instances:
        st.title("My Engineering Calculators")
        st.info("Please select a calculator or table and click **Add Calculator / Table** in the sidebar to begin.")
        return

    # Ensure all active instances have session states initialized
    for inst in active_instances:
        calc = CALCULATORS[inst["calc_key"]]
        calc.initialize_session_state(inst["instance_id"], calc_data_store)

    active_inst_ids = [inst["instance_id"] for inst in active_instances]
    if "selected_instance_id" not in st.session_state or st.session_state["selected_instance_id"] not in active_inst_ids:
        st.session_state["selected_instance_id"] = active_inst_ids[0]

    current_idx = active_inst_ids.index(st.session_state["selected_instance_id"])

    calc_options_map = {
        inst["instance_id"]: format_instance_display(
            CALCULATORS[inst["calc_key"]].title,
            get_instance_label(inst)
        )
        for inst in active_instances
    }

    st.sidebar.divider()
    st.sidebar.subheader("Active Calculator / Table")
    
    selected_inst_id = st.sidebar.selectbox(
        "Select Active Calculator / Table",
        options=active_inst_ids,
        index=current_idx,
        format_func=lambda x: calc_options_map[x],
        key="selected_instance_id",
        help="Select which active calculator or table to view and edit."
    )

    selected_inst = next((inst for inst in active_instances if inst["instance_id"] == selected_inst_id), active_instances[0])
    selected_calc = CALCULATORS[selected_inst["calc_key"]]

    # Edit label/identifier for the active calculator
    updated_label = st.sidebar.text_input(
        "Edit Label",
        value=get_instance_label(selected_inst),
        key=f"edit_label_{selected_inst_id}",
        help="Modify the label for this active calculator instance."
    )
    normalized_updated_label = updated_label.strip()
    if normalized_updated_label != get_instance_label(selected_inst):
        selected_inst["label"] = normalized_updated_label
        st.rerun()

    selected_label = get_instance_label(selected_inst)
    st.sidebar.markdown(f"**{format_instance_display(selected_calc.title, selected_label)}**")

    if selected_calc.is_table:
        resolved_selected_inputs = {}
        show_steps = False
        selected_precisions = {}
        calc_image = None
        note_val = ""
    else:
        available_vars = gather_available_variables(active_instances, calc_data_store)

        st.sidebar.subheader("1. Variable Inputs")
        resolved_selected_inputs = selected_calc.render_sidebar_inputs(
            instance_id=selected_inst_id,
            instance_label=selected_label,
            available_vars=available_vars,
            calc_data_store=calc_data_store
        )

        st.sidebar.subheader("2. Visibility")
        show_steps = st.sidebar.checkbox("Show calculation steps", value=True, key="show_steps_global")

        st.sidebar.subheader("3. Precision")
        with st.sidebar.expander("Precision Settings", expanded=False):
            selected_precisions = selected_calc.render_sidebar_precisions(selected_inst_id, calc_data_store)

        st.sidebar.subheader("4. Reference Image")
        calc_image = st.sidebar.file_uploader(
            "Upload image",
            type=["png", "jpg", "jpeg"],
            key=f"img_{selected_inst_id}"
        )

        st.sidebar.subheader("5. Notes")
        note_val = st.sidebar.text_area(
            "Notes",
            value=calc_data_store[selected_inst_id].get("notes", ""),
            key=f"textarea_{selected_inst_id}"
        )
        calc_data_store[selected_inst_id]["notes"] = note_val

    config = {
        "instance_id": selected_inst_id,
        "instance_label": selected_label,
        "inputs": resolved_selected_inputs,
        "show_steps": show_steps,
        "precisions": selected_precisions,
        "uploaded_image": calc_image,
        "custom_notes": note_val
    }
    selected_calc.render_main_canvas(config)


if __name__ == "__main__":
    main()

if not st.session_state.get("footer_accepted", False):
    st.markdown("""
        <style>
        .st-key-consent-footer {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 999;
            padding: 10px 5%;
            background-color: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container(key="consent-footer"):
        footer_text, footer_action = st.columns([6, 1], vertical_alignment="center")
        with footer_text:
            st.markdown("""
                By using this site, you agree to the <a href="http://127.0.0.1:8503/"
                style="text-decoration: none; color: #007bff;">Terms and Conditions</a>.
                This site is licensed under the <a href="http://127.0.0.1:8503/"
                style="text-decoration: none; color: #007bff;">MIT License</a>.
                Please review the <a href="http://127.0.0.1:8503/"
                style="text-decoration: none; color: #007bff;">Privacy Policy</a>.
            """, unsafe_allow_html=True)
        with footer_action:
            if st.button("Accept", key="accept_footer", type="primary", use_container_width=True):
                st.session_state["footer_accepted"] = True
                st.rerun()