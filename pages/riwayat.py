import streamlit as st
import pandas as pd
from auth.auth import require_login
from styles.style import load_css
from styles.components import sidebar_nav
from database.repositories.history_repository import get_history
from utils.date_helper import format_date_indo

load_css()
require_login()

user_id  = st.session_state.user_id
username = st.session_state.user_name
email    = st.session_state.user_email

sidebar_nav(username, email)

st.markdown(
    """
    <div class="hero">
        <h1>📜 Riwayat Pencarian</h1>
        <p>Semua pencarian resep yang pernah Anda lakukan</p>
    </div>
    """,
    unsafe_allow_html=True,
)

histories = get_history(user_id)

if not histories:
    st.info("Belum ada riwayat pencarian. Mulai cari resep!")
    if st.button("🔍 Cari Resep", use_container_width=True):
        st.switch_page("pages/home.py")
else:
    st.markdown(f"**{len(histories)} pencarian tercatat**")

    data = [
        {
            "Tanggal":  format_date_indo(h.created_at),
            "Bahan":    h.bahan,
            "Diet":     h.kategori_diet,
            "Halal":    h.halal,
            "Alergi":   h.alergi  or "-",
            "Cuisine":  h.cuisine or "-",
        }
        for h in histories
    ]
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)