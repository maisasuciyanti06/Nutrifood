import streamlit as st
import pandas as pd
from auth.auth import require_login
from styles.style import load_css
from styles.components import dashboard_header, show_dashboard_card, sidebar_nav
from database.repositories.favorite_repository import count_favorites
from database.repositories.history_repository import count_history, get_history
from utils.date_helper import format_date_indo

load_css()
require_login()

user_id  = st.session_state.user_id
username = st.session_state.user_name
email    = st.session_state.user_email

sidebar_nav(username, email)
dashboard_header(username)

# ── Stat cards ───────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    show_dashboard_card("Total Pencarian",  count_history(user_id),   "🔍")
with c2:
    show_dashboard_card("Favorit Disimpan", count_favorites(user_id), "❤️")

st.divider()

# ── Recent history + tips ─────────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="medium")

with left:
    st.markdown('<div class="section-title">📋 Riwayat Pencarian Terbaru</div>', unsafe_allow_html=True)
    histories = get_history(user_id)
    if not histories:
        st.info("Belum ada riwayat. Mulai cari resep!")
        if st.button("🔍 Cari Resep Sekarang", use_container_width=True):
            st.switch_page("pages/home.py")
    else:
        data = [
            {
                "Tanggal":  format_date_indo(h.created_at),
                "Bahan":    h.bahan,
                "Diet":     h.kategori_diet,
                "Halal":    h.halal,
            }
            for h in histories[:5]
        ]
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

with right:
    st.markdown('<div class="section-title">💡 Tips Penggunaan</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="tips-card">
            🥕 &nbsp;Masukkan bahan yang ada di dapur<br>
            🥗 &nbsp;Filter preferensi sesuai kebutuhan<br>
            ❤️ &nbsp;Simpan resep ke Favorit<br>
            📅 &nbsp;Tambahkan ke Meal Planner
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ── Quick action buttons ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">🚀 Aksi Cepat</div>', unsafe_allow_html=True)
q1, q2, q3 = st.columns(3)
with q1:
    if st.button("🔍 Cari Resep", use_container_width=True):
        st.switch_page("pages/home.py")
with q2:
    if st.button("❤️ Lihat Favorit", use_container_width=True):
        st.switch_page("pages/favorit.py")
with q3:
    if st.button("📅 Meal Planner", use_container_width=True):
        st.switch_page("pages/meal_planner.py")