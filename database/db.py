import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

# Load variabel dari file .env (hanya berefek kalau file-nya ada, dipakai
# saat run di komputer lokal; di Streamlit Cloud file .env memang sengaja
# tidak di-upload karena berisi data sensitif)
load_dotenv()


def _get_config(key: str, default: str = "") -> str:
    """
    Ambil nilai konfigurasi dengan urutan prioritas:
    1. st.secrets (dipakai saat deploy di Streamlit Cloud, diisi lewat
       menu App settings -> Secrets)
    2. Environment variable / file .env (dipakai saat run lokal)
    3. Default fallback
    """
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        # st.secrets belum di-set / tidak ada secrets.toml / tidak jalan
        # di konteks Streamlit -> lanjut coba dari environment variable
        pass

    return os.getenv(key, default)


DB_USER = _get_config("DB_USER", "postgres")
DB_PASSWORD = _get_config("DB_PASSWORD", "postgres")
DB_HOST = _get_config("DB_HOST", "localhost")
DB_PORT = _get_config("DB_PORT", "5432")
DB_NAME = _get_config("DB_NAME", "recipe_system")

# PENTING: pakai URL.create() bukan f-string manual. Kalau password
# mengandung karakter spesial seperti "@", ":", "/", dsb, menggabungkan
# string secara manual (f"...{user}:{password}@{host}...") akan salah
# parsing -- "@" di dalam password bisa ketuker dianggap pemisah host,
# menyebabkan hostname yang dituju jadi salah/rusak. URL.create()
# otomatis meng-encode karakter semacam itu dengan benar.
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

# Supabase (dan kebanyakan Postgres hosting online lain) mewajibkan koneksi
# SSL. Postgres lokal biasanya tidak dikonfigurasi untuk SSL, jadi mode ini
# hanya ditambahkan kalau host-nya BUKAN localhost/127.0.0.1.
connect_args = {}
if DB_HOST not in ("localhost", "127.0.0.1"):
    connect_args["sslmode"] = "require"

# echo=True bisa diaktifkan sementara untuk debug query SQL yang dijalankan
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # otomatis cek koneksi mati sebelum dipakai
    pool_size=5,
    max_overflow=10,
    echo=False,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)