import streamlit as st
from datetime import datetime

from auth.auth import require_login
from styles.style import load_css
from styles.components import sidebar_nav
from database.repositories.planner_repository import get_user_meal_planner, delete_meal
from database.repositories.favorite_repository import add_favorite, is_favorite
from database.models import Favorite
from core.pdf_report import generate_meal_planner_pdf

load_css()
require_login()

user_id  = st.session_state.user_id
username = st.session_state.user_name
email    = st.session_state.user_email

sidebar_nav(username, email)

st.markdown(
    """
    <div class="hero">
        <h1>Meal Planner</h1>
        <p>Daftar menu makan yang telah Anda rencanakan</p>
    </div>
    """,
    unsafe_allow_html=True,
)

plans = get_user_meal_planner(user_id)

DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

if not plans:
    st.info("Belum ada meal plan.")
    if st.button("Cari Resep"):
        st.switch_page("pages/home.py")

else:
    total_kal   = sum(float(p.calories or 0) for p in plans)
    total_prot  = sum(float(p.protein  or 0) for p in plans)
    total_porsi = sum(float(getattr(p, "servings", 0) or 0) for p in plans)

    col_info, col_dl = st.columns([2, 1])

    with col_info:
        st.info(
            f"  {len(plans)} menu tersimpan  |  "
            f"  Total Kalori: {total_kal:.0f}  |  "
            f"  Total Protein: {total_prot:.1f} g  |  "
            f"  Total Porsi: {total_porsi:.0f}"
        )

    with col_dl:
        st.markdown("**Unduh Laporan PDF**")
        pilihan_hari = st.multiselect(
            "Pilih hari (kosong = semua):",
            DAYS,
            default=[],
            key="pdf_hari_filter",
            label_visibility="collapsed",
        )
        hari_cetak = pilihan_hari if pilihan_hari else DAYS

        if st.button("Unduh Laporan PDF", use_container_width=True, type="primary"):
            with st.spinner("Menyiapkan laporan..."):
                pdf_bytes = generate_meal_planner_pdf(
                    plans,
                    username=username,
                    days=hari_cetak,
                )
            file_name = (
                f"meal_planner_{username}_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            st.download_button(
                label="Klik di sini untuk mengunduh",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                use_container_width=True,
            )

    st.markdown("---")

    # ── Ringkasan mingguan ────────────────────────────────────────────────────
    st.subheader("Ringkasan Mingguan")

    cols = st.columns(7)
    for i, day in enumerate(DAYS):
        day_count = sum(1 for p in plans if getattr(p, "hari", "") == day)
        with cols[i]:
            st.metric(day, day_count)

    st.markdown("---")

    # ── Tab per hari ──────────────────────────────────────────────────────────
    tabs = st.tabs(DAYS)

    for tab, day in zip(tabs, DAYS):
        with tab:
            day_plans = [p for p in plans if getattr(p, "hari", "") == day]

            if not day_plans:
                st.info(f"Belum ada menu untuk hari {day}")
                continue

            total_kal_day  = sum(float(p.calories or 0) for p in day_plans)
            total_prot_day = sum(float(p.protein  or 0) for p in day_plans)

            st.success(
                f"  {len(day_plans)} menu  |  "
                f"  {total_kal_day:.0f} kalori  |  "
                f"  {total_prot_day:.1f} g protein"
            )

            st.markdown("---")

            for plan in day_plans:
                with st.container():
                    col_img, col_detail = st.columns([1, 2])

                    with col_img:
                        if (
                            getattr(plan, "image_url", None)
                            and str(plan.image_url).startswith("http")
                        ):
                            st.image(plan.image_url, use_container_width=True)

                    with col_detail:
                        st.markdown(
                            f"""
                            <div class="fav-card">
                                <div class="fav-title">{plan.recipe_name}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        kalori  = float(plan.calories or 0)
                        protein = float(plan.protein  or 0)
                        porsi   = float(getattr(plan, "servings", 0) or 0)
                        kal_per = kalori / max(porsi, 1)

                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric("Kalori per Porsi",  f"{kal_per:.0f} kkal")
                        with m2:
                            st.metric("Protein per porsi",  f"{protein:.1f} g")
                        with m3:
                            st.metric("Porsi",    f"{porsi:.0f}")

                        b1, b2, b3 = st.columns(3)

                        with b1:
                            if getattr(plan, "recipe_url", None) and plan.recipe_url:
                                st.link_button("Buka Resep", plan.recipe_url, use_container_width=True)

                        with b2:
                            already_fav = is_favorite(user_id, plan.recipe_name)
                            if not already_fav:
                                if st.button("Simpan ke Favorit", key=f"fav_{plan.id}", use_container_width=True):
                                    add_favorite(
                                        Favorite(
                                            user_id=user_id,
                                            recipe_name=plan.recipe_name,
                                            recipe_url=getattr(plan, "recipe_url", None),
                                            image_url=getattr(plan, "image_url", None),
                                            calories=kalori,
                                            protein=protein,
                                            servings=porsi,
                                            score=0,
                                        )
                                    )
                                    st.toast(f"'{plan.recipe_name}' disimpan ke Favorit!")
                                    st.rerun()
                            else:
                                st.button("Sudah di Favorit", key=f"fav_dis_{plan.id}", disabled=True, use_container_width=True)

                        with b3:
                            if st.button("Hapus dari Planner", key=f"del_{plan.id}", use_container_width=True):
                                delete_meal(plan.id)
                                st.toast("Menu dihapus dari planner.")
                                st.rerun()

                st.markdown("---")