import streamlit as st

st.set_page_config(
    page_title="Nutrifood",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded" 
)

from styles.style import HIDE_NAV_CSS
st.markdown(HIDE_NAV_CSS, unsafe_allow_html=True)

if not st.session_state.get("logged_in", False):
    st.switch_page("pages/login.py")
else:
    st.switch_page("pages/dashboard.py")
