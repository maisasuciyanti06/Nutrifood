from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, index=True)
    nama       = Column(String(100), nullable=False)
    email      = Column(String(100), unique=True, nullable=False, index=True)
    password   = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Favorite(Base):
    __tablename__ = "favorites"
    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, nullable=False, index=True)
    recipe_name = Column(Text)
    recipe_url  = Column(Text)
    image_url   = Column(Text)
    calories    = Column(Float, default=0)
    protein     = Column(Float, default=0)
    servings    = Column(Float, default=0)
    score       = Column(Float, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)


class SearchHistory(Base):
    __tablename__ = "search_history"
    id            = Column(Integer, primary_key=True)
    user_id       = Column(Integer, nullable=False, index=True)
    bahan         = Column(Text)
    kategori_diet = Column(String(100))
    halal         = Column(String(20))
    alergi        = Column(Text)
    cuisine       = Column(String(100))
    created_at    = Column(DateTime, default=datetime.utcnow)


class MealPlanner(Base):
    __tablename__ = "meal_planner"
    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, nullable=False, index=True)
    hari        = Column(String(50))
    recipe_name = Column(Text)
    recipe_url  = Column(Text)
    image_url   = Column(Text)
    calories    = Column(Float, default=0)
    protein     = Column(Float, default=0)
    servings    = Column(Float, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_meal_planner_user_hari", "user_id", "hari"),
    )


class RecipeView(Base):
    __tablename__ = "recipe_views"
    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, index=True)
    recipe_name = Column(Text)
    created_at  = Column(DateTime, default=datetime.utcnow)


class ReportLog(Base):
    __tablename__ = "report_logs"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, index=True)
    file_name  = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class Recipe(Base):
    __tablename__ = "recipes"
    id               = Column(Integer, primary_key=True)
    recipe_name      = Column(Text, index=True)
    ingredient_lines = Column(Text)        # disimpan sebagai string representasi list, tetap dipakai ast.literal_eval seperti sebelumnya
    calories         = Column(Float, default=0)
    total_nutrients  = Column(Text)        # string representasi dict, sama seperti kolom asli di CSV
    servings         = Column(Float, default=1)
    url              = Column(Text)
    image_url        = Column(Text)
    cuisine_type     = Column(String(100), index=True)