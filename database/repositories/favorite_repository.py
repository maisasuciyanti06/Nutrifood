from database.db import SessionLocal
from database.models import Favorite

def add_favorite(favorite):
    db = SessionLocal()
    try:
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return favorite
    finally:
        db.close()


def get_user_favorites(user_id):
    db = SessionLocal()
    try:
        return (db.query(Favorite)
                  .filter(Favorite.user_id == user_id)
                  .order_by(Favorite.created_at.desc())
                  .all())
    finally:
        db.close()


def delete_favorite(favorite_id):
    db = SessionLocal()
    try:
        fav = db.query(Favorite).filter(Favorite.id == favorite_id).first()
        if fav:
            db.delete(fav)
            db.commit()
            return True
        return False
    finally:
        db.close()


def count_favorites(user_id):
    db = SessionLocal()
    try:
        return db.query(Favorite).filter(Favorite.user_id == user_id).count()
    finally:
        db.close()


def is_favorite(user_id, recipe_name):
    db = SessionLocal()
    try:
        return db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.recipe_name == recipe_name
        ).first() is not None
    finally:
        db.close()


def get_favorite_by_recipe(user_id, recipe_name):
    db = SessionLocal()
    try:
        return db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.recipe_name == recipe_name
        ).first()
    finally:
        db.close()


def delete_all_favorites(user_id):
    db = SessionLocal()
    try:
        db.query(Favorite).filter(Favorite.user_id == user_id).delete()
        db.commit()
    finally:
        db.close()
