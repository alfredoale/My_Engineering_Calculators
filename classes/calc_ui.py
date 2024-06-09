import streamlit as st


class Variables:
    def __init__(self, symbol=None, symbol_subscript=None, name=None, unit=None, input_widget=None, list=None, value=None):
        self.symbol = symbol
        self.symbol_subscript = symbol_subscript
        self.name = name
        self.unit = unit
        self.input_widget = input_widget
        self.list = list
        self.value = value

    def formatted_str(self):
        if self.name != None:
            a = "*x*".replace("x", self.name)

        if self.unit != None:
            a += " *(x)*".replace("x", self.unit)

        return a

    def formatted_value(self):
        if self.symbol_subscript != None:
            a = "**"+self.symbol+"<sub>"+self.symbol_subscript + \
                "</sub>"+" =** "+"%.2f" % self.value
        else:
            a = "**"+self.symbol+" =** "+"%.2f" % self.value

        return a

    def add_input_widget(self):
        if self.input_widget == st.selectbox:
            return st.selectbox(
                self.name, self.list, label_visibility="collapsed", index=None)
        elif self.input_widget == st.number_input:
            return st.number_input(
                self.symbol, label_visibility="collapsed", value=None, placeholder="Enter Value")

    def selectbox(self):
        return st.selectbox(
            self.name, self.list, label_visibility="collapsed", index=None)

    def number_input(self):
        return st.number_input(
            self.symbol, label_visibility="collapsed", value=None, placeholder="Enter Value")


def title_dictionary(header, subheader, caption):
    dictionary = {
        "header": header,
        "subheader": subheader,
        "caption": caption
    }

    return dictionary


class CalcStyles:
    def __init__(self, title_dictionary, inputs_list, output_list, main_output, calculations,
                 bottom_notes=None):
        self.title_dictionary = title_dictionary
        self.inputs_list = inputs_list
        self.output_list = output_list
        self.main_output = main_output
        self.calculations = calculations
        self.bottom_notes = bottom_notes

    def add_calc_style1(self):
        st.sidebar.page_link("Home.py", label="Home")
        st.sidebar.divider()
        st.markdown("**"+self.title_dictionary["header"]+"**")
        st.markdown("**"+self.title_dictionary["subheader"]+"**")
        st.caption(self.title_dictionary["caption"])

        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            with st.container(border=True):
                for x in self.inputs_list:
                    st.markdown(x.formatted_str(), unsafe_allow_html=True)
                    x.value = x.add_input_widget()

        if all(x.value is not None for x in self.inputs_list):
            self.calculations()

            with col2:
                with st.container(border=True):
                    for x in self.output_list:
                        st.markdown(x.formatted_str())
                        st.markdown(x.formatted_value(),
                                    unsafe_allow_html=True)

            with st. container(border=True):
                st.markdown(self.main_output.formatted_str())
                st.markdown(self.main_output.formatted_value())

        st.divider()

        if self.bottom_notes != None:
            st.markdown(self.bottom_notes, unsafe_allow_html=True)
