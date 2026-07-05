from database.db import SessionLocal
from database.models import MealPlanner


def add_meal_plan(plan):
    db = SessionLocal()
    try:
        db.add(plan)
        db.commit()
    finally:
        db.close()


def save_meal(plan):
    add_meal_plan(plan)


def get_user_meal_planner(user_id):
    db = SessionLocal()
    try:
        return (db.query(MealPlanner)
                  .filter(MealPlanner.user_id == user_id)
                  .order_by(MealPlanner.created_at.desc())
                  .all())
    finally:
        db.close()


def meal_exists_in_day(user_id: int, recipe_name: str, hari: str):
    db = SessionLocal()
    try:
        meal = (
            db.query(MealPlanner)
            .filter(
                MealPlanner.user_id == user_id,
                MealPlanner.recipe_name == recipe_name,
                MealPlanner.hari == hari,
            )
            .first()
        )
        return meal is not None
    finally:
        db.close()


def delete_meal(plan_id):
    db = SessionLocal()
    try:
        plan = db.query(MealPlanner).filter(MealPlanner.id == plan_id).first()
        if plan:
            db.delete(plan)
            db.commit()
    finally:
        db.close()
