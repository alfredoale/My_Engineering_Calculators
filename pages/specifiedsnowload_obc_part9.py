import classes.calc_ui as calc
st = calc.st
import data.obc_data as cdd
from formulas.ontario_building_code import specifiedsnowload_obc_part9, basicsnowloadrooffactor_obc_part9, calculation_notes
import streamlit.components.v1 as components # Import required for the google maps iframe


# Text to appear at the top of the section
title_dictionary = calc.title_dictionary("SPECIFIED LOADS (OBC 9.4.2.)", 
    "Specified Snow Loads (OBC 9.4.2.2.)","" 
    #"MMAH Supplementary Standard SB-1, Table 2, Climatic Design Data, Snow Load, 1/50"
)

# Define the lists to be used with selectbox
locations = [x[0] for x in cdd.snow_rain_load_by_location]


# Define variables, using the class Variables
# For inputs
location = calc.Variables(name="Location", input_widget=st.selectbox, list=locations)
w = calc.Variables(symbol="w", name="Entire Width Of Roof", unit="m", input_widget=st.number_input)


# For calculations
Cb = calc.Variables(symbol="C", symbol_subscript="b", name="Basic Snow Load Roof Factor")
Ss = calc.Variables(symbol="S", symbol_subscript="s", name="1-in-50 Year Ground Snow Load", unit="kPa")
Sr = calc.Variables(symbol="S", symbol_subscript="r", name="1-in-50 Year Associated Rain Load", unit="kPa")
S = calc.Variables(symbol="S", name="Specified Snow Load", unit="kPa")


# Add variables to the respective list below
inputs_list = [location, w]
output_list = [Cb, Ss, Sr]
main_output = S


# Define the calculations to be performed inside the function calculations
def calculations ():
    Cb.value = basicsnowloadrooffactor_obc_part9(w.value)
    Ss.value = cdd.snow_rain_load_by_location[locations.index(location.value)][1]
    Sr.value = cdd.snow_rain_load_by_location[locations.index(location.value)][2]
    S.value = specifiedsnowload_obc_part9(Cb.value, Ss.value, Sr.value)

calc.CalcStyles(title_dictionary, inputs_list, output_list, main_output, calculations,
    calculation_notes["specifiedsnowload_obc_part9"]).add_calc_style1()
