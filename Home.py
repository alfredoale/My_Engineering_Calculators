import streamlit as st


st.header("My Engineering Calculators",anchor=False ,divider="grey")

st.subheader("Loads",anchor=False)
st.page_link("pages/specifiedsnowload_obc_part9.py",label="Specified Snow Loads (OBC 9.4.2.2.)")

st.markdown("""
        <footer style="position: fixed; left: 0; bottom: 0; width: 100%; 
            background-color: #f8f9fa; color: #212529; text-align: center;
            padding: 10px 0; border-top: 1px solid #e9ecef;">
            By using this site, you agree to the <a href="https://raw.githubusercontent.com/alfredoale/My_Engineering_Calculators/main/terms_of_use.md" style="text-decoration: none; color: #007bff;">Terms and Conditions</a>. 
            This site is licensed under the <a href="https://raw.githubusercontent.com/alfredoale/My_Engineering_Calculators/main/LICENSE.txt" style="text-decoration: none; color: #007bff;">MIT License</a>. 
            Please review the <a href="https://raw.githubusercontent.com/alfredoale/My_Engineering_Calculators/main/privacy_policy.md" style="text-decoration: none; color: #007bff;">Privacy Policy</a>.
        </footer>
    """, unsafe_allow_html=True)
