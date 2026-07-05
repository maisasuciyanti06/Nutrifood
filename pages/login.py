import streamlit as st
import time
import base64
from pathlib import Path

from auth.auth import (
    login_user,
    is_logged_in,
    reset_password,
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
# SESSION
# ==========================================================

if "show_forgot" not in st.session_state:
    st.session_state.show_forgot = False


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
            <div class="auth-title">Masuk ke Akun Anda</div>
            <div class="auth-subtitle">
                Temukan rekomendasi resep dan kelola meal planner Anda
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ======================================================
    # LOGIN
    # ======================================================

    if not st.session_state.show_forgot:

        with st.form("login_form", clear_on_submit=False):

            email = st.text_input(
                "Email",
                placeholder="Masukkan email",
                key="login_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Masukkan password",
                key="login_password",
            )

            remember = st.checkbox("Ingat saya", value=False)

            # Teks lupa password kecil di atas tombol Masuk
            st.markdown(
                """
                """,
                unsafe_allow_html=True,
            )

            login = st.form_submit_button(
                "Masuk",
                use_container_width=True,
                type="primary",
            )

        # Teks klik lupa password di luar form (harus di luar agar bisa trigger rerun)
        st.markdown(
            """
            <div style="text-align:center; margin-top:8px; margin-bottom:4px;">
                <span style="font-size:12.5px; color:#6B7280;">
                    Lupa password?
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Reset Password",
            key="forgot_btn",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.show_forgot = True
            st.rerun()

        if login:
            if email == "" or password == "":
                st.error("Email dan password wajib diisi.")
            else:
                with st.spinner("Memverifikasi akun..."):
                    success, message = login_user(email, password)

                if success:
                    st.success("Login berhasil.")
                    time.sleep(0.8)
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error(message)

        st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="auth-footer-text">Belum memiliki akun?</div>',
            unsafe_allow_html=True,
        )

        if st.button("Daftar Sekarang", use_container_width=True, key="goto_register"):
            st.switch_page("pages/register.py")

    # ======================================================
    # RESET PASSWORD
    # ======================================================

    else:

        st.markdown(
            """
            <div style="text-align:center;margin-bottom:20px;">
                <div class="auth-title" style="font-size:22px;">Reset Password</div>
                <div class="auth-subtitle">Buat password baru untuk akun Anda</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("reset_form"):

            reset_email = st.text_input("Email", placeholder="Masukkan email")

            new_password = st.text_input(
                "Password Baru",
                type="password",
                placeholder="Minimal 6 karakter",
            )

            confirm_password = st.text_input(
                "Konfirmasi Password",
                type="password",
                placeholder="Ulangi password",
            )

            submit_reset = st.form_submit_button(
                "Reset Password",
                use_container_width=True,
                type="primary",
            )

        if submit_reset:

            if reset_email == "" or new_password == "" or confirm_password == "":
                st.error("Semua field wajib diisi.")
            elif new_password != confirm_password:
                st.error("Konfirmasi password tidak sesuai.")
            elif len(new_password) < 6:
                st.error("Password minimal 6 karakter.")
            else:
                with st.spinner("Memperbarui password..."):
                    ok, msg = reset_password(reset_email, new_password)

                if ok:
                    st.success("Password berhasil diperbarui.")
                    time.sleep(1)
                    st.session_state.show_forgot = False
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)

        if st.button("Kembali ke Login", use_container_width=True, type="secondary"):
            st.session_state.show_forgot = False
            st.rerun()