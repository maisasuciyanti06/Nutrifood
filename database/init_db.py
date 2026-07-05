from database.db import engine
from database.models import Base


def create_database():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database berhasil dibuat/diperbarui!")
        print("📁 Lokasi: recipe_system.db")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    create_database()
