import streamlit as st
from calculation import get_available_variables
from formulas import CALCULATORS


def main():
    st.set_page_config(page_title="My Engineering Calculators", layout="centered")

    st.sidebar.header("Calculator Settings")

    # 1. Calculator selection widget in sidebar (Default: No selection)
    selected_titles = st.sidebar.multiselect(
        "Select Calculators",
        options=list(CALCULATORS.keys()),
        default=[],
        help="Select one or more engineering calculators to activate."
    )

    if not selected_titles:
        st.title("My Engineering Calculators")
        st.info("Please select the calculators and fill in all the required input variables in the sidebar to perform the calculations.")
        return

    active_calculators = [CALCULATORS[title] for title in selected_titles]

    # Initialize state for all selected calculators
    for calc in active_calculators:
        calc.initialize_session_state()

    # Pre-read precisions first for linking format preview
    calc_precisions = {}
    for calc in active_calculators:
        calc_precisions[calc.calc_id] = {
            var["symbol"]: st.session_state.get(f"prec_{calc.calc_id}_{var['symbol']}", 2)
            for var in calc.variables
        }

    # Sidebar Section 1: Variable Inputs grouped by calculator
    st.sidebar.subheader("1. Variable Inputs")
    calc_inputs = {}
    calc_linked_info = {}
    is_multi_calc = len(active_calculators) > 1

    for calc in active_calculators:
        st.sidebar.markdown(f"**{calc.title}**")
        # Gather available variables from other active calculators
        available_vars = get_available_variables(
            active_calculators=active_calculators,
            current_calc_id=calc.calc_id,
            precisions=calc_precisions
        )
        inputs, linked_info = calc.render_sidebar_inputs(available_vars, is_multi_calc=is_multi_calc)
        calc_inputs[calc.calc_id] = inputs
        calc_linked_info[calc.calc_id] = linked_info
        st.sidebar.divider()

    # Sidebar Section 2: Visibility Toggle
    st.sidebar.subheader("2. Visibility")
    show_steps = st.sidebar.checkbox("Show calculation steps", value=True)

    # Sidebar Section 3: Decimal Precision Settings
    st.sidebar.subheader("3. Precision")
    with st.sidebar.expander("Decimal Precision Settings", expanded=False):
        for calc in active_calculators:
            st.markdown(f"**{calc.title}**")
            calc_precisions[calc.calc_id] = calc.render_sidebar_precisions()

    # Sidebar Section 4: Images
    st.sidebar.subheader("4. Reference Image")
    calc_images = {}
    for calc in active_calculators:
        calc_images[calc.calc_id] = st.sidebar.file_uploader(
            f"Image for {calc.title}",
            type=["png", "jpg", "jpeg"],
            key=f"img_{calc.calc_id}"
        )

    # Sidebar Section 5: Notes
    st.sidebar.subheader("5. Notes")
    calc_notes = {}
    for calc in active_calculators:
        notes_key = f"notes_{calc.calc_id}"
        note_val = st.sidebar.text_area(
            f"Notes for {calc.title}",
            value=st.session_state.get(notes_key, ""),
            key=f"textarea_{calc.calc_id}"
        )
        st.session_state[notes_key] = note_val
        calc_notes[calc.calc_id] = note_val

    # Main page tabbed layout for selected calculators
    tabs = st.tabs([calc.title for calc in active_calculators])

    for tab, calc in zip(tabs, active_calculators):
        with tab:
            config = {
                "inputs": calc_inputs[calc.calc_id],
                "linked_info": calc_linked_info[calc.calc_id],
                "show_steps": show_steps,
                "precisions": calc_precisions[calc.calc_id],
                "uploaded_image": calc_images[calc.calc_id],
                "custom_notes": calc_notes[calc.calc_id]
            }
            calc.render_main_canvas(config)


if __name__ == "__main__":
    main()

st.markdown("""
        <footer style="position: fixed; left: 0; bottom: 0; width: 100%; 
            background-color: #f8f9fa; color: #212529; text-align: center;
            padding: 10px 0; border-top: 1px solid #e9ecef;">
            By using this site, you agree to the <a href="" style="text-decoration: none; color: #007bff;">Terms and Conditions</a>. 
            This site is licensed under the <a href="" style="text-decoration: none; color: #007bff;">MIT License</a>. 
            Please review the <a href="" style="text-decoration: none; color: #007bff;">Privacy Policy</a>.
        </footer>
    """, unsafe_allow_html=True)