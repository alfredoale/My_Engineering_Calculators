import classes.calc_ui as calc
st = calc.st
from anastruct import SystemElements
ss = SystemElements()


# Text to appear at the top of the section
title_dictionary = calc.title_dictionary("STRUCTURAL ANALYSIS", 
    "Beam: Reactions, Shear Force, Bending Moment, and Deflection",""
)

# Define the lists to be used with selectbox
# locations = [x[0] for x in cdd.snow_rain_load_by_location]
supports = ["Hinge", "Roll", "Fix"]


# Define variables, using the class Variables
# For inputs
support_1 = calc.Variables(name="Support 1", input_widget=st.selectbox, list=supports, print=False)
support_2 = calc.Variables(name="Support 2", input_widget=st.selectbox, list=supports, print=False)
w = calc.Variables(symbol="w", name="Uniformly Distributed Load", unit="kN/m", input_widget=st.number_input)
p = calc.Variables(symbol="P", name="Point Load", unit="kN", input_widget=st.number_input)
a = calc.Variables(symbol="a", name="Point Load Distance", unit="m", input_widget=st.number_input)
l = calc.Variables(symbol="l", name="Beam Length", unit="m", input_widget=st.number_input)
E = calc.Variables(symbol="E", name="Modulus of Elasticity", unit="MPa", input_widget=st.number_input)
I = calc.Variables(symbol="I", name="Moment of Inertia", unit="mm^4", input_widget=st.number_input)
#location = calc.Variables(name="Location", input_widget=st.selectbox, list=locations)


# For calculations
R1 = calc.Variables(symbol="R", symbol_subscript="1", name="Reaction At Node 1", unit="kN")
R2 = calc.Variables(symbol="R", symbol_subscript="2", name="Reaction At Node 2", unit="kN")
Vmax = calc.Variables(symbol="V", symbol_subscript="max", name="Maximum Shear Force", unit="kN")
Mmax = calc.Variables(symbol="M", symbol_subscript="max", name="Maximum Bending Moment", unit="kN*m")
Defmax = calc.Variables(symbol="Δ", symbol_subscript="max", name="Maximum Deflection", unit="mm")


# Add variables to the respective list below
inputs_list = [support_1, support_2, l, w, p, a, E, I]
output_list = [R1, R2]
main_output = [Vmax, Mmax, Defmax]

# Define the calculations to be performed inside the function calculations
def calculations ():
    global ss 
    ss = SystemElements(figsize=(10,4))
    if a.value == 0 or a.value == l.value or (0 < a.value < l.value and p.value == 0):
        ss.add_element(location=[[0,0],[l.value,0]], EI=(E.value)*(I.value)/1e12)

        if support_1.value == "Hinge" :
            ss.add_support_hinged(node_id=1)
        elif support_1.value == "Roll" :
            ss.add_support_roll(node_id=1)
        elif support_1.value == "Fix" :
            ss.add_support_fixed(node_id=1)
        if support_2.value == "Hinge" :
            ss.add_support_hinged(node_id=2)
        elif support_2.value == "Roll" :
            ss.add_support_roll(node_id=2)
        elif support_2.value == "Fix" :
            ss.add_support_fixed(node_id=2)
        
        ss.q_load(element_id=1,q=-w.value)
        if p.value != 0:
            if a.value == 0 :
                ss.point_load(node_id=1, Fy=-p.value)
            elif a.value == l.value :
                ss.point_load(node_id=2, Fy=-p.value)
        ss.solve()
        R1.value = ss.get_node_results_system(node_id=1)['Fy']
        R2.value = ss.get_node_results_system(node_id=2)['Fy']
        Vmax.value = ss.get_element_result_range('shear')[0]
        Mmax.value = ss.get_element_result_range('moment')[0]
        Defmax.value = min(ss.show_displacement(scale=0.7, show=False, values_only=True, factor=1)[1])
        

    elif 0 < a.value < l.value:
        ss.add_element(location=[[0,0],[a.value,0]], EI=(E.value)*(I.value)/1e12)
        ss.add_element(location=[[a.value,0],[l.value,0]], EI=(E.value)*(I.value)/1e12)

        if support_1.value == "Hinge" :
            ss.add_support_hinged(node_id=1)
        elif support_1.value == "Roll" :
            ss.add_support_roll(node_id=1)
        elif support_1.value == "Fix" :
            ss.add_support_fixed(node_id=1)
        if support_2.value == "Hinge" :
            ss.add_support_hinged(node_id=3)
        elif support_2.value == "Roll" :
            ss.add_support_roll(node_id=3)
        elif support_2.value == "Fix" :
            ss.add_support_fixed(node_id=3)

        ss.q_load(element_id=1,q=-w.value)
        ss.q_load(element_id=2,q=-w.value)
        if p.value != 0:
            ss.point_load(node_id=2, Fy=-p.value)

        ss.solve()
        R1.value = ss.get_node_results_system(node_id=1)['Fy']
        R2.value = ss.get_node_results_system(node_id=3)['Fy']
        R2.symbol_subscript = "3"
        R2.name = "Reaction At Node 3"
        Vmax.value = max(ss.get_element_result_range('shear')[0], ss.get_element_result_range('shear')[1])
        Mmax.value = max(ss.get_element_result_range('moment')[0], ss.get_element_result_range('moment')[1])
        Defmax.value = min(ss.show_displacement(scale=0.7, show=False, values_only=True, factor=1)[1])


calc.CalcStyles(title_dictionary, inputs_list, output_list, main_output, calculations).add_calc_style1()

# Diagrams
if all(x.value is not None for x in inputs_list):
    st.markdown("**Loads**")
    st.write(ss.show_structure(scale=0.7, show=False))

    st.markdown("**Reactions**")
    st.write(ss.show_reaction_force(scale=0.7, show=False))

    st.markdown("**Shear Force Diagram**")
    st.write(ss.show_shear_force(scale=0.7, show=False))

    st.markdown("**Bending Moment Diagram**")
    st.write(ss.show_bending_moment(scale=0.7, show=False))

    st.markdown("**Deflection Diagram**")
    st.write(ss.show_displacement(scale=0.7, show=False))