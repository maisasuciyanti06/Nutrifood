import streamlit as st
import streamlit.components.v1 as components
from auth.auth import logout


def _safe_translate(text: str) -> str:
    """Translate to Indonesian; fallback to original on error."""
    try:
        from core.translator import translate_to_indonesian
        return translate_to_indonesian(text)
    except Exception:
        return text


def show_hero(title: str = "🍽️ Nutrifood", subtitle: str = "Temukan resep terbaik berdasarkan bahan yang tersedia."):
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_header(username: str):
    st.markdown(
        f"""
        <div class="hero">
            <h1>Halo, {username}</h1>
            <p>Selamat datang kembali di Nutrifood</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_dashboard_card(title: str, value, icon: str = "📊"):
    st.markdown(
        f"""
        <div class="dash-card">
            <div class="dash-icon">{icon}</div>
            <div class="dash-value">{value}</div>
            <div class="dash-label">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_recipe_card(row, rank: int, kategori_label: str, pilih_halal: str):
    """Tampilkan card resep - PAKAI STREAMLIT NATIVE, BUKAN HTML"""
    
    recipe_name = row.get("recipe_name", "Nama Resep")
    match_count = int(row.get("match_count", 0))
    score = round(float(row.get("cosine_score", 0)), 3)
    calories = round(float(row.get("calories_per_serving", 0)), 1)
    protein = round(float(row.get("protein_per_serving", 0)), 1)
    servings = int(row.get("servings", 0))
    
    # Judul dengan rank
    st.markdown(f"### #{rank} - {recipe_name}")
    
    # Badges dalam satu baris - lebih rapi
    badges = []
    if pilih_halal == "Ya":
        badges.append("Halal")
    if kategori_label not in ("Semua", ""):
        badges.append(f"{kategori_label}")
    badges.append(f"Skor: {score}")
    badges.append(f"{match_count} bahan cocok")
    
    # Gabungkan badges
    badges_html = ' '.join([f'<span style="background: #f5f0f2; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; color: #2d1b21;">{b}</span>' for b in badges])
    st.markdown(f"<div style='display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px;'>{badges_html}</div>", unsafe_allow_html=True)
    
    # Nutrition metrics
    col_n1, col_n2, col_n3 = st.columns(3)
    with col_n1:
        st.metric(
            "Kalori per porsi",
            f"{float(row.get('calories_per_serving', 0)):.0f} kkal"
        )
    with col_n2:
        st.metric(
            "Protein per porsi",
            f"{float(row.get('protein_per_serving', 0)):.0f} g"
        )
    with col_n3:
        st.metric("Porsi", f"{servings}")
        


def show_recipe_link(url):
    """Tampilkan tombol link resep"""
    if url and isinstance(url, str) and url.startswith("http"):
        st.link_button("Buka Resep Lengkap", url, use_container_width=True)


def show_ingredients_expander(ingredients):
    """Tampilkan bahan-bahan di dalam expander - HANYA SEKALI"""
    if ingredients:
        with st.expander("🍴 Lihat Semua Bahan (Bahasa Indonesia)"):
            items = []
            if isinstance(ingredients, list):
                items = ingredients
            else:
                # Bersihkan string dari karakter aneh
                ingredients_str = str(ingredients)
                # Hapus tanda kurung siku dan kutip
                ingredients_str = ingredients_str.strip("[]")
                # Split berdasarkan koma
                raw_items = ingredients_str.split(",")
                for item in raw_items:
                    clean_item = item.strip().strip("'\"")
                    if clean_item:
                        items.append(clean_item)
            
            for item in items:
                if item:
                    translated = _safe_translate(item)
                    st.write(f"• {translated}")


def _render_mobile_hamburger():
    """
    Render tombol hamburger custom + overlay untuk toggle sidebar di mobile.

    Catatan penting: st.markdown() men-sanitize HTML dan MEMBUANG atribut
    seperti onclick="...", jadi pendekatan itu tidak akan pernah jalan.
    Sebagai gantinya, elemen tombol/overlay dirender polos lewat
    st.markdown (tanpa onclick), lalu event listener-nya dipasang lewat
    <script> nyata yang dieksekusi via st.components.v1.html (jalan di
    iframe, sehingga script benar-benar dieksekusi browser), yang
    menjangkau elemen di halaman utama lewat window.parent.document.
    Semua murni client-side — tidak ada rerun Streamlit yang terlibat.
    """
    st.markdown(
        """
        <button id="nf-hamburger-btn">
            <span class="nf-icon-open">☰</span>
            <span class="nf-icon-close">✕</span>
        </button>
        <div id="nf-overlay"></div>
        """,
        unsafe_allow_html=True,
    )

    components.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;
            const btn = doc.getElementById('nf-hamburger-btn');
            const overlay = doc.getElementById('nf-overlay');

            if (btn && !btn.dataset.nfBound) {
                btn.dataset.nfBound = "1";
                btn.addEventListener('click', function () {
                    doc.body.classList.toggle('nf-sidebar-open');
                });
            }
            if (overlay && !overlay.dataset.nfBound) {
                overlay.dataset.nfBound = "1";
                overlay.addEventListener('click', function () {
                    doc.body.classList.remove('nf-sidebar-open');
                });
            }
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def sidebar_nav(username: str, email: str = ""):
    # Tombol hamburger + overlay dirender di area konten utama (bukan di
    # dalam sidebar), supaya tetap bisa diklik walau sidebar sedang
    # tersembunyi di mobile.
    _render_mobile_hamburger()

    with st.sidebar:
        # Profile card compact
        st.markdown(f"""
        <div style="text-align: center; padding: 14px 10px 10px 10px; margin-bottom: 6px;">
            <div style="width: 52px; height: 52px; background: linear-gradient(135deg, #e91e63, #c2185b); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; font-size: 1.5rem; color: white;">
                👩‍🍳
            </div>
            <div style="font-family: 'Inter', sans-serif; font-size: 0.9rem; font-weight: 700; color: #2d1b21;">
                {username}
            </div>
            <div style="font-size: 0.65rem; color: #ad7a8a; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                {email}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 0 0 6px 0; border-color: #f0c4d0;'>", unsafe_allow_html=True)

        menu_items = [
            ("📊 Dashboard",    "pages/dashboard.py"),
            ("🔍 Cari Resep",   "pages/home.py"),
            ("📅 Meal Planner", "pages/meal_planner.py"),
            ("❤️ Favorit",      "pages/favorit.py"),
            ("📜 Riwayat",      "pages/riwayat.py"),
        ]

        for label, path in menu_items:
            st.page_link(path, label=label, use_container_width=True)

        st.markdown("---")

        if st.button("Keluar", use_container_width=True):
            logout()
            st.rerun()