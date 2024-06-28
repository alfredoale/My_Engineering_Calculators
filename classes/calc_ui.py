import streamlit as st


class Variables:
    def __init__(self, symbol=None, symbol_subscript=None, name=None, unit=None, input_widget=None, list=None, value=None, print=True):
        self.symbol = symbol
        self.symbol_subscript = symbol_subscript
        self.name = name
        self.unit = unit
        self.input_widget = input_widget
        self.list = list
        self.value = value
        self.print = print

    def formatted_str(self):
        if self.name != None:
            a = "*x*".replace("x", self.name)

        return a

    def formatted_value(self):
        a = ""
        if self.symbol != None:
            a += "**" + self.symbol
        if self.symbol_subscript != None:
            a += "<sub>" + self.symbol_subscript + "</sub>"
        if isinstance(self.value, (int, float)):
            a += " =** "+"%.2f" % self.value
        else:
            a += self.value
        if self.unit != None:
            a += " " + self.unit

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
                 bottom_notes=None, bottom_notes_nomarkdown=None):
        self.title_dictionary = title_dictionary
        self.inputs_list = inputs_list
        self.output_list = output_list
        self.main_output = main_output
        self.calculations = calculations
        self.bottom_notes = bottom_notes
        self.bottom_notes_nomarkdown = bottom_notes_nomarkdown


    def add_calc_style1(self):
        with st.sidebar:
            st.header("Navigation")
            st.page_link("Home.py", label="Home")
            st.divider()
            st.header("Inputs")
            for x in self.inputs_list:
                if x.unit != None:
                    unit = ", *" + x.unit +"*"
                else:
                    unit = ""
                st.markdown(x.formatted_str() + unit, unsafe_allow_html=True)
                x.value = x.add_input_widget()
            st.divider()

        st.markdown("**"+self.title_dictionary["header"]+"**")
        st.markdown("**"+self.title_dictionary["subheader"]+"**")
        st.caption(self.title_dictionary["caption"])

        if all(x.value is not None for x in self.inputs_list):
            for x in self.inputs_list:
                if x.print == True :
                    col1, col2 = st.columns([0.7, 0.3])
                    with col1:
                        st.markdown(x.formatted_str())
                    with col2:
                        st.markdown(x.formatted_value(), unsafe_allow_html=True)

            self.calculations()

            for x in self.output_list:
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    st.markdown(x.formatted_str())
                with col2:
                    st.markdown(x.formatted_value(), unsafe_allow_html=True)
            st.divider()
            for x in self.main_output:
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    st.markdown("**" + x.formatted_str() + "**")
                with col2:
                    st.markdown(x.formatted_value(), unsafe_allow_html=True)


        add_user_image()
        st.divider()


        if self.bottom_notes_nomarkdown != None:
            self.bottom_notes_nomarkdown


        if self.bottom_notes != None:
            st.markdown(self.bottom_notes, unsafe_allow_html=True)



def pagebreak():
    with st.sidebar:
        pb = st.toggle("Add pagebreak")
    if pb:
        st.markdown("""
                <p style="page-break-after: always;">&nbsp;</p>
            """
            , unsafe_allow_html=True
        )

def add_user_image():
    with st.sidebar:
        img = st.toggle("Insert image")
        if img:
            uploaded_file = st.file_uploader("Choose images to insert",
                type=[".png", ".jpg"], accept_multiple_files=True,label_visibility="collapsed")
    if img:
        if uploaded_file is not None:
                st.divider()
                st.image(uploaded_file)