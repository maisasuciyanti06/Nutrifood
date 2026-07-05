"""
Jalankan file ini SEKALI SAJA untuk membuat database PostgreSQL
sebelum menjalankan init_db.py.

Script ini connect ke database default 'postgres', bukan ke
'recipe_system' (karena database itu belum ada), lalu membuat
database baru jika belum ada.
"""
import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "maisa123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "recipe_system")


def create_database_if_not_exists():
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"✅ Database '{DB_NAME}' berhasil dibuat.")
    else:
        print(f"ℹ️  Database '{DB_NAME}' sudah ada, tidak perlu dibuat ulang.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    create_database_if_not_exists()
