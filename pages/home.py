import streamlit as st

from auth.auth import require_login
from styles.style import load_css
from styles.components import show_hero, show_recipe_card, show_recipe_link, show_ingredients_expander, sidebar_nav

from core.recommender import load_model, get_recommendations

from database.models import Favorite, SearchHistory, MealPlanner
from database.repositories.favorite_repository import add_favorite, is_favorite
from database.repositories.history_repository import add_history
from database.repositories.planner_repository import (
    add_meal_plan,
    meal_exists_in_day,
)

# ── Init ─────────────────────────────────────────────────────────────────────
load_css()
require_login()

user_id = st.session_state.user_id
username = st.session_state.user_name
email = st.session_state.user_email

sidebar_nav(username, email)
show_hero()

# ── Load model (cached) ───────────────────────────────────────────────────────
with st.spinner("Memuat model rekomendasi..."):
    df, tfidf = load_model()

# ── Search form ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🥕 Cari Resep</div>', unsafe_allow_html=True)

with st.form("search_form"):
    bahan_user = st.text_input(
        "Bahan yang tersedia (pisahkan dengan koma)",
        placeholder="contoh: ayam, bawang putih, kentang",
    )

    st.markdown("**⚙️ Filter Opsional**")
    col1, col2 = st.columns(2)
    with col1:
        kategori_diet = st.selectbox(
            "Kategori Diet",
            ["Semua", "Rendah Kalori", "Tinggi Protein"],
        )
    with col2:
        pilih_halal = st.selectbox(
            "Filter Halal",
            ["Ya", "Tidak"],
        )

    col3, col4 = st.columns(2)
    with col3:
        alergi_user = st.multiselect(
            "Alergi",
            ["susu", "telur", "kacang", "seafood", "gluten", "kedelai", "wijen"],
        )
    with col4:
        cuisine_filter = st.selectbox(
            "Cuisine (Jenis Masakan)",
            ["Semua", "American", "Asian", "Italian"],
        )

    jumlah_porsi = st.selectbox(
        "Jumlah Porsi",
        ["Tampilkan Semua", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    )

    submitted = st.form_submit_button("🔍 Cari Rekomendasi", use_container_width=True)

# ── Process search ────────────────────────────────────────────────────────────
if submitted:
    if not bahan_user.strip():
        st.warning("⚠️ Masukkan bahan terlebih dahulu!")
    else:
        with st.spinner("Mencari resep terbaik..."):
            add_history(SearchHistory(
                user_id=user_id,
                bahan=bahan_user,
                kategori_diet=kategori_diet,
                halal=pilih_halal,
                alergi=", ".join(alergi_user) if alergi_user else "-",
                cuisine=cuisine_filter,
            ))

            hasil, _ = get_recommendations(
                df=df,
                tfidf=tfidf,
                bahan_user=bahan_user,
                kategori_diet=kategori_diet,
                jumlah_porsi=jumlah_porsi,
                pilih_halal=pilih_halal,
                alergi_user=alergi_user,
                cuisine_filter=cuisine_filter,
            )

        st.session_state.hasil = hasil
        st.session_state.k_diet = kategori_diet
        st.session_state.k_halal = pilih_halal

# ── Render results ────────────────────────────────────────────────────────────
if "hasil" in st.session_state:
    hasil = st.session_state.hasil
    kategori_diet = st.session_state.get("k_diet", "Semua")
    pilih_halal = st.session_state.get("k_halal", "Ya")

    if hasil.empty:
        st.warning("Tidak ada resep yang cocok dengan kriteria Anda. Coba kurangi filter atau tambah bahan.")
    else:
        # Eliminasi resep dengan kalori=0 atau protein=0
        hasil = hasil[
            (hasil["calories_per_serving"] > 0) &
            (hasil["protein_per_serving"] > 0)
        ]

        if hasil.empty:
            st.warning("Tidak ada resep yang cocok dengan kriteria Anda. Coba kurangi filter atau tambah bahan.")
        else:
            st.success(f"✅ Ditemukan {len(hasil)} rekomendasi resep")

            for rank, (idx, row) in enumerate(hasil.iterrows(), start=1):
                with st.container():
                    st.markdown("---")

                    col_img, col_info = st.columns([1, 2])

                    with col_img:
                        image_url = row.get("image_url", "")
                        if image_url and isinstance(image_url, str) and image_url.startswith("http"):
                            st.image(image_url, use_container_width=True)

                    with col_info:
                        show_recipe_card(row, rank, kategori_diet, pilih_halal)

                    ingredients = row.get("ingredients", "")
                    show_ingredients_expander(ingredients)

                    col_link, col_fav, col_plan = st.columns(3)

                    with col_link:
                        show_recipe_link(row.get("url"))

                    with col_fav:

                        if st.button(
                            "Simpan ke Favorit",
                            key=f"fav_{idx}",
                            use_container_width=True,
                        ):

                            if is_favorite(user_id, row["recipe_name"]):

                                st.warning(
                                    f"'{row['recipe_name']}' sudah ada di menu favorit Anda."
                                )

                            else:

                                add_favorite(
                                    Favorite(
                                        user_id=user_id,
                                        recipe_name=row["recipe_name"],
                                        recipe_url=row.get("url"),
                                        image_url=row.get("image_url"),
                                        calories=row.get("calories_per_serving", 0),
                                        protein=row.get("protein_per_serving", 0),
                                        servings=row.get("servings", 0),
                                        score=row.get("cosine_score", 0),
                                    )
                                )

                                st.success(
                                    f"'{row['recipe_name']}' berhasil disimpan ke Favorit!"
                                )

                                st.rerun()

                    with col_plan:
                        hari = st.selectbox(
                            "Hari",
                            ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
                            key=f"hari_{idx}",
                        )

                        if st.button("Tambah ke Meal Planner", key=f"plan_{idx}", use_container_width=True):

                            if meal_exists_in_day(
                                user_id=user_id,
                                recipe_name=row["recipe_name"],
                                hari=hari,
                            ):
                                st.warning(
                                    f"Menu '{row['recipe_name']}' sudah ada pada hari {hari}."
                                )

                            else:
                                add_meal_plan(
                                    MealPlanner(
                                        user_id=user_id,
                                        hari=hari,
                                        recipe_name=row["recipe_name"],
                                        recipe_url=row.get("url"),
                                        image_url=row.get("image_url"),
                                        calories=row.get("calories_per_serving", 0),
                                        protein=row.get("protein_per_serving", 0),
                                        servings=row.get("servings", 0),
                                    )
                                )

                                st.success(
                                    f"Menu berhasil ditambahkan ke hari {hari}!"
                                )