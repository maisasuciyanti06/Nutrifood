import streamlit as st

from auth.auth import require_login
from styles.style import load_css
from styles.components import sidebar_nav
from database.repositories.favorite_repository import get_user_favorites, delete_favorite
from database.models import MealPlanner
from database.repositories.planner_repository import (
    add_meal_plan,
    meal_exists_in_day,
)


# Fungsi pembantu untuk konversi float dengan aman
def safe_float(value, default=0.0):
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

load_css()
require_login()

user_id  = st.session_state.user_id
username = st.session_state.user_name
email    = st.session_state.user_email

sidebar_nav(username, email)

st.markdown(
    """
    <div class="hero">
        <h1>❤️ Resep Favorit</h1>
        <p>Koleksi resep pilihan yang telah Anda simpan</p>
    </div>
    """,
    unsafe_allow_html=True,
)

favorites = get_user_favorites(user_id)

if not favorites:
    st.info("Belum ada resep favorit. Mulai cari dan simpan resep!")
    if st.button("🔍 Cari Resep", use_container_width=True):
        st.switch_page("pages/home.py")

else:
    st.success(f"❤️ {len(favorites)} resep tersimpan")
    st.markdown("---")

    for fav in favorites:
        with st.container():
            col_img, col_detail = st.columns([1, 2])

            with col_img:
                if fav.image_url and str(fav.image_url).startswith("http"):
                    st.image(fav.image_url, use_container_width=True)

            with col_detail:
                st.markdown(
                    f"""
                    <div class="fav-card">
                        <div class="fav-title" style="font-size: 1.5rem; font-weight: bold; margin-bottom: 10px;">
                            {fav.recipe_name}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Metrics — 4 kolom termasuk porsi
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    calories = safe_float(getattr(fav, 'calories', 0))
                    st.metric("Kalori per porsi", f"{calories:.0f} kkal")

                with m2:
                    protein = safe_float(getattr(fav, 'protein', 0))
                    st.metric("Protein per porsi", f"{protein:.0f} g")

                with m3:
                    servings = safe_float(getattr(fav, "servings", 0))
                    st.metric("Porsi", f"{servings:.0f}")

                with m4:
                    score = safe_float(getattr(fav, "score", 0))
                    st.metric("Skor", f"{score:.3f}")
                
                st.write("") # Spacer

                # Menu dropdown diletakkan full-width di atas deretan tombol agar rapi
                hari = st.selectbox(
                    "Pilih Hari untuk Meal Planner:",
                    ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
                    key=f"hari_{fav.id}"
                )

                # Buttons — 3 kolom aksi
                b1, b2, b3 = st.columns(3)

                with b1:
                    if getattr(fav, "recipe_url", None):
                        st.link_button("Buka Resep", fav.recipe_url, use_container_width=True)
                    else:
                        st.button("No Link", disabled=True, use_container_width=True)

                with b2:
                    if st.button("Tambah Planner", key=f"plan_{fav.id}", use_container_width=True):

                        if meal_exists_in_day(
                            user_id=user_id,
                            recipe_name=fav.recipe_name,
                            hari=hari,
                        ):
                            st.warning(
                                f"Menu '{fav.recipe_name}' sudah ada pada hari {hari}."
                            )

                        else:
                            add_meal_plan(
                                MealPlanner(
                                    user_id=user_id,
                                    hari=hari,
                                    recipe_name=fav.recipe_name,
                                    recipe_url=getattr(fav, "recipe_url", None),
                                    image_url=getattr(fav, "image_url", None),
                                    calories=safe_float(getattr(fav, "calories", 0)),
                                    protein=safe_float(getattr(fav, "protein", 0)),
                                    servings=safe_float(getattr(fav, "servings", 0)),
                                )
                            )

                            st.toast(f"✅ Ditambahkan ke hari {hari}!")

                with b3:
                    if st.button("Hapus", key=f"del_{fav.id}", use_container_width=True):
                        delete_favorite(fav.id)
                        st.toast("Favorit berhasil dihapus!")
                        st.rerun()

        st.markdown("---")