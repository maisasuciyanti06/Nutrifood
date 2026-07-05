"""
Jalankan file ini SEKALI SAJA untuk memindahkan recipes9k.csv
ke tabel 'recipes' di PostgreSQL.

Setelah ini berhasil, recipes9k.csv TIDAK PERLU lagi ikut di-push
ke GitHub / disimpan di folder project.

Cara pakai:
    python import_recipes_csv.py path/ke/recipes9k.csv

Kalau tidak diisi path-nya, defaultnya cari "recipes9k.csv" di folder ini.
"""
import sys
import pandas as pd
from database.db import engine
from database.models import Base, Recipe

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "recipes9k.csv"

NEEDED_COLS = [
    "recipe_name", "ingredient_lines", "calories",
    "total_nutrients", "servings", "url", "image_url", "cuisine_type",
]


def main():
    print(f"📄 Membaca {CSV_PATH} ...")
    df = pd.read_csv(
        CSV_PATH,
        engine="python",
        on_bad_lines="skip",
        usecols=lambda c: c in NEEDED_COLS,
    )
    print(f"✅ {len(df)} baris terbaca dari CSV.")

    # Pastikan tabel 'recipes' sudah ada
    Base.metadata.create_all(bind=engine, tables=[Recipe.__table__])

    # Kosongkan dulu isi tabel kalau sudah pernah diisi sebelumnya
    with engine.begin() as conn:
        conn.execute(Recipe.__table__.delete())

    # Bersihkan tipe data sebelum insert
    df["calories"] = pd.to_numeric(df.get("calories"), errors="coerce").fillna(0)
    df["servings"] = pd.to_numeric(df.get("servings", 1), errors="coerce").fillna(1)

    print("⏳ Mengimpor ke PostgreSQL (bisa beberapa saat)...")
    df.to_sql(
        "recipes",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,   # insert per 1000 baris supaya tidak berat sekali kirim
        method="multi",
    )

    print(f"🎉 Selesai! {len(df)} resep berhasil dimasukkan ke tabel 'recipes'.")


if __name__ == "__main__":
    main()