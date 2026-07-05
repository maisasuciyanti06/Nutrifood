import streamlit as st
import time
import base64
from pathlib import Path

from auth.auth import (
    register_user,
    is_logged_in,
)
from styles.style import load_auth_css


# ==========================================================
# LOAD CSS
# ==========================================================

load_auth_css()

if is_logged_in():
    st.switch_page("pages/dashboard.py")


# ==========================================================
# LOGO (base64 inline, transparent background)
# ==========================================================

def _logo_base64() -> str:
    logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
    if logo_path.exists():
        return base64.b64encode(logo_path.read_bytes()).decode()
    return ""


_LOGO_B64 = _logo_base64()


# ==========================================================
# LAYOUT
# ==========================================================

left, center, right = st.columns([1, 2, 1])

with center:

    # ------------------------------------------------------
    # Logo + Header
    # ------------------------------------------------------

    if _LOGO_B64:
        st.markdown(
            f"""
            <div class="auth-logo-wrap">
                <img src="data:image/png;base64,{_LOGO_B64}" alt="Nutri Food" />
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="text-align:center;margin-bottom:25px;">
            <div class="auth-title">Buat Akun Baru</div>
            <div class="auth-subtitle">
                Daftar untuk mulai menggunakan sistem rekomendasi resep
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ======================================================
    # REGISTER FORM
    # ======================================================

    with st.form("register_form"):

        nama = st.text_input(
            "Nama Lengkap",
            placeholder="Masukkan nama lengkap",
            key="reg_name",
        )

        email = st.text_input(
            "Email",
            placeholder="Masukkan email",
            key="reg_email",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Minimal 6 karakter",
            key="reg_pass",
        )

        confirm = st.text_input(
            "Konfirmasi Password",
            type="password",
            placeholder="Masukkan kembali password",
            key="reg_confirm",
        )

        submitted = st.form_submit_button(
            "Daftar",
            use_container_width=True,
            type="primary",
        )

    # ======================================================
    # VALIDASI
    # ======================================================

    if submitted:

        if nama == "" or email == "" or password == "" or confirm == "":
            st.error("Semua field wajib diisi.")
        elif password != confirm:
            st.error("Konfirmasi password tidak sesuai.")
        elif len(password) < 6:
            st.error("Password minimal 6 karakter.")
        else:
            with st.spinner("Membuat akun..."):
                ok, msg = register_user(nama, email, password)

            if ok:
                st.success("Registrasi berhasil. Silakan login.")
                time.sleep(1.2)
                st.switch_page("pages/login.py")
            else:
                st.error(msg)

    # ======================================================
    # FOOTER
    # ======================================================

    st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="auth-footer-text">Sudah memiliki akun?</div>',
        unsafe_allow_html=True,
    )

    if st.button("Masuk Sekarang", use_container_width=True, type="secondary"):
        st.switch_page("pages/login.py")