from database.db import SessionLocal
from database.models import SearchHistory


def add_history(history):
    db = SessionLocal()
    try:
        db.add(history)
        db.commit()
    finally:
        db.close()


def save_history(history):
    add_history(history)


def get_history(user_id):
    db = SessionLocal()
    try:
        return (db.query(SearchHistory)
                  .filter(SearchHistory.user_id == user_id)
                  .order_by(SearchHistory.created_at.desc())
                  .all())
    finally:
        db.close()


def count_history(user_id):
    db = SessionLocal()
    try:
        return db.query(SearchHistory).filter(SearchHistory.user_id == user_id).count()
    finally:
        db.close()
