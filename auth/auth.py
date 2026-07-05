import re
import streamlit as st
import bcrypt
from database.models import User
from database.repositories.user_repository import create_user, get_user_by_email
from database.db import SessionLocal


def register_user(nama: str, email: str, password: str):
    email = email.strip().lower()
    if not nama or not email or not password:
        return False, "Semua field harus diisi."
    if len(password) < 6:
        return False, "Password minimal 6 karakter."
    existing_user = get_user_by_email(email)
    if existing_user:
        return False, "Email sudah digunakan."
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(
        nama=nama.strip(),
        email=email,
        password=hashed.decode('utf-8')
    )
    try:
        create_user(new_user)
        return True, "Registrasi berhasil! Silakan login."
    except Exception as e:
        return False, f"Error: {str(e)}"


def login_user(email: str, password: str):
    email = email.strip().lower()
    user = get_user_by_email(email)
    if not user:
        return False, "Email tidak ditemukan."
    try:
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            create_session(user)
            return True, "Login berhasil."
        else:
            return False, "Password salah."
    except Exception as e:
        return False, f"Error: {str(e)}"


def create_session(user):
    st.session_state.logged_in  = True
    st.session_state.user_id    = user.id
    st.session_state.user_name  = user.nama
    st.session_state.user_email = user.email


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def is_logged_in():
    return st.session_state.get("logged_in", False)


def get_current_user():
    if not is_logged_in():
        return None
    return {
        "id":    st.session_state.get("user_id"),
        "nama":  st.session_state.get("user_name"),
        "email": st.session_state.get("user_email"),
    }


def require_login():
    if not is_logged_in():
        st.switch_page("pages/login.py")


def reset_password(email: str, new_password: str):
    email = email.strip().lower()
    user  = get_user_by_email(email)
    if not user:
        return False, "Email tidak ditemukan."
    if len(new_password) < 6:
        return False, "Password minimal 6 karakter."
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    db = SessionLocal()
    try:
        user.password = hashed.decode('utf-8')
        db.commit()
        return True, "Password berhasil direset. Silakan login dengan password baru."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally:
        db.close()


def change_password(user_id: int, old_password: str, new_password: str):
    from database.repositories.user_repository import get_user_by_id
    user = get_user_by_id(user_id)
    if not user:
        return False, "User tidak ditemukan."
    if not bcrypt.checkpw(old_password.encode('utf-8'), user.password.encode('utf-8')):
        return False, "Password lama salah."
    if len(new_password) < 6:
        return False, "Password baru minimal 6 karakter."
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    db = SessionLocal()
    try:
        user.password = hashed.decode('utf-8')
        db.commit()
        return True, "Password berhasil diubah."
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"
    finally:
        db.close()
