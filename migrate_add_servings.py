"""
Migration: Tambah kolom 'servings' ke tabel favorites dan meal_planner
Jalankan sekali saja dari folder root project:
    python migrate_add_servings.py
"""

import sqlite3
import os

DB_PATH = "recipe_system.db"

if not os.path.exists(DB_PATH):
    print(f"❌ File database '{DB_PATH}' tidak ditemukan.")
    print("   Pastikan script ini dijalankan dari folder root project (tempat recipe_system.db berada).")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

migrations = [
    ("favorites",    "servings", "ALTER TABLE favorites    ADD COLUMN servings REAL DEFAULT 0"),
    ("meal_planner", "servings", "ALTER TABLE meal_planner ADD COLUMN servings REAL DEFAULT 0"),
]

for table, column, sql in migrations:
    # Cek apakah kolom sudah ada
    cursor.execute(f"PRAGMA table_info({table})")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if column in existing_columns:
        print(f"⏭️  {table}.{column} sudah ada, dilewati.")
    else:
        try:
            cursor.execute(sql)
            conn.commit()
            print(f"✅ Kolom '{column}' berhasil ditambahkan ke tabel '{table}'.")
        except Exception as e:
            print(f"❌ Gagal menambahkan '{column}' ke '{table}': {e}")

conn.close()
print("\n🎉 Migration selesai! Restart aplikasi Streamlit Anda.")