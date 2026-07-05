import ast
import re

import pandas as pd
import streamlit as st

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from core.translator import translate_to_english
from database.db import engine
from config import (
    BATAS_KALORI_RENDAH, BATAS_PROTEIN_TINGGI, BATAS_PROTEIN_DENSITY,
    USE_PROTEIN_DENSITY, NON_HALAL_KEYWORDS, MAIN_PROTEINS,
    ALERGEN_MAPPING, DESSERT_KEYWORDS, SAVORY_KEYWORDS, COOKING_STOPWORDS,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_parse(val):
    try:
        return ast.literal_eval(val) if isinstance(val, str) else val
    except Exception:
        return []


def get_protein(row):
    try:
        nutrients = ast.literal_eval(row) if isinstance(row, str) else {}
        return nutrients.get("PROCNT", {}).get("quantity", 0)
    except Exception:
        return 0


def is_exact_match(term: str, ingredient_string: str) -> bool:
    pattern = r"\b" + re.escape(term.lower()) + r"\b"
    return bool(re.search(pattern, ingredient_string.lower(), re.IGNORECASE))


_PROTEIN_DERIVATIVES = [
    "broth", "stock", "bouillon", "fat", "cube", "extract",
    "flavor", "powder", "kaldu", "minyak", "sauce",
]


def is_real_meat(meat_term: str, text: str) -> bool:
    for m in re.finditer(r"\b" + re.escape(meat_term) + r"\b", text, re.IGNORECASE):
        snippet = text[max(0, m.start() - 20): min(len(text), m.end() + 25)].lower()
        if any(d in snippet for d in _PROTEIN_DERIVATIVES):
            return False
    return True


def clean_text_for_tfidf(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s,]", "", text)
    return " ".join(w for w in text.split() if w not in COOKING_STOPWORDS)


# ── Load model (cached for performance) ──────────────────────────────────────

@st.cache_resource(show_spinner="⏳ Memuat dataset resep dari database, harap tunggu...")
def load_model():
    # Sebelumnya: pd.read_csv("recipes9k.csv", ...)
    # Sekarang: ambil langsung dari tabel 'recipes' di PostgreSQL.
    # CSV tidak lagi disimpan di folder project / repo GitHub.
    query = """
        SELECT recipe_name, ingredient_lines, calories,
               total_nutrients, servings, url, image_url, cuisine_type
        FROM recipes
    """
    df = pd.read_sql(query, con=engine)

    if df.empty:
        st.error(
            "❌ Tabel 'recipes' kosong. Jalankan `python import_recipes_csv.py` "
            "terlebih dahulu untuk mengisi data resep ke database."
        )
        st.stop()

    df["calories"] = pd.to_numeric(df["calories"], errors="coerce").fillna(0)
    df["protein"]  = df["total_nutrients"].apply(get_protein) if "total_nutrients" in df.columns else 0
    df["servings"] = pd.to_numeric(df.get("servings", 1), errors="coerce").fillna(1)
    df = df[df["servings"] > 0].copy()

    df["calories_per_serving"] = df["calories"] / df["servings"]
    df["protein_per_serving"]  = df["protein"]  / df["servings"]
    df["protein_density"]      = df["protein"]  / df["calories"].replace(0, 1)

    df["ingredients"]          = df["ingredient_lines"].apply(safe_parse)
    df["raw_ingredients_text"] = df["ingredients"].apply(
        lambda x: " ".join(x) if isinstance(x, list) else ""
    )
    df["cleaned_ingredients"]  = df["raw_ingredients_text"].apply(clean_text_for_tfidf)

    df = df[df["cleaned_ingredients"].str.strip() != ""].reset_index(drop=True)

    tfidf = TfidfVectorizer(stop_words="english", max_features=8_000)
    tfidf.fit(df["cleaned_ingredients"])

    return df, tfidf


# ── Main recommendation function ──────────────────────────────────────────────

def get_recommendations(
    df, tfidf, bahan_user, kategori_diet,
    jumlah_porsi, pilih_halal, alergi_user, cuisine_filter,
):
    input_terms_indo = [t.strip() for t in bahan_user.split(",") if t.strip()]
    total_bahan_asli = max(len(input_terms_indo), 1)

    try:
        bahan_en = translate_to_english(bahan_user).replace(" and ", ", ")
    except Exception:
        bahan_en = bahan_user.lower()

    input_terms  = [t.strip().lower() for t in bahan_en.split(",") if t.strip()]
    cleaned_user = clean_text_for_tfidf(bahan_en)

    df_result    = df.copy()
    dessert_mode = any(k in cleaned_user for k in DESSERT_KEYWORDS)

    # ── Diet filter ───────────────────────────────────────────────────────────
    if kategori_diet == "Low Calories":
        df_result = df_result[df_result["calories_per_serving"] <= BATAS_KALORI_RENDAH]
    elif kategori_diet == "High Protein":
        df_result = df_result[
            (df_result["protein_per_serving"] >= BATAS_PROTEIN_TINGGI) &
            (df_result["calories_per_serving"] <= BATAS_KALORI_RENDAH)
        ]
        if USE_PROTEIN_DENSITY:
            df_result = df_result[df_result["protein_density"] >= BATAS_PROTEIN_DENSITY]

    if not dessert_mode:
        df_result = df_result[df_result["protein_per_serving"] >= 12]

    # ── Allergy filter ────────────────────────────────────────────────────────
    if alergi_user:
        alergi_list = [str(a).strip().lower() for a in alergi_user if str(a).strip()]
        forbidden   = []
        for a in alergi_list:
            try:
                a_en = translate_to_english(a).lower()
                forbidden.append(a_en)
            except Exception:
                pass
            if a in ALERGEN_MAPPING:
                forbidden.extend(ALERGEN_MAPPING[a])

        for kw in set(forbidden):
            if not kw:
                continue
            df_result = df_result[
                ~df_result["raw_ingredients_text"]
                .astype(str)
                .str.lower()
                .str.contains(rf"\b{re.escape(kw)}\b", regex=True, na=False)
            ]

    # ── Halal filter ──────────────────────────────────────────────────────────
    if pilih_halal.lower() in ("ya", "yes", "true"):
        for kw in NON_HALAL_KEYWORDS:
            df_result = df_result[
                ~df_result["raw_ingredients_text"].apply(lambda x: is_exact_match(kw, str(x)))
            ]

    # ── Cuisine filter ────────────────────────────────────────────────────────
    if cuisine_filter != "Semua" and "cuisine_type" in df_result.columns:
        df_result = df_result[
            df_result["cuisine_type"].str.contains(cuisine_filter, case=False, na=False)
        ]

    if df_result.empty:
        return df_result.head(10), total_bahan_asli

    # ── Match count ───────────────────────────────────────────────────────────
    user_proteins    = [p for p in MAIN_PROTEINS if any(is_exact_match(p, t) for t in input_terms)]
    allowed_proteins = set(user_proteins)

    df_result = df_result.copy()
    df_result["match_count"] = df_result["raw_ingredients_text"].apply(
        lambda x: sum(1 for t in input_terms if is_exact_match(t, str(x)))
    )

    min_match = 2 if dessert_mode else max(2, int(total_bahan_asli * 0.25))
    df_result = df_result[df_result["match_count"] >= min_match]

    if df_result.empty:
        return df_result.head(10), total_bahan_asli

    # ── Serving filter ────────────────────────────────────────────────────────
    if jumlah_porsi != "Tampilkan Semua":
        try:
            porsi_int = int(jumlah_porsi)
            df_result = df_result[df_result["servings"].round().astype(int) == porsi_int]
        except Exception:
            pass

    if df_result.empty:
        return df_result.head(10), total_bahan_asli

    # ── TF-IDF cosine score ───────────────────────────────────────────────────
    cand_vec = tfidf.transform(df_result["cleaned_ingredients"])
    user_vec = tfidf.transform([cleaned_user])
    df_result["cosine_score"] = cosine_similarity(cand_vec, user_vec).flatten()

    def adjust_score(row):
        ing      = str(row["raw_ingredients_text"]).lower()
        sim      = float(row["cosine_score"])
        ratio    = row["match_count"] / total_bahan_asli
        penalty  = 1.0
        extra    = 0.0

        detected       = [p for p in MAIN_PROTEINS if is_real_meat(p, ing)]
        has_user_prot  = any(p in detected for p in allowed_proteins)
        has_other_prot = any(p not in allowed_proteins for p in detected)

        if has_user_prot:
            extra += 0.28
        if not has_user_prot and has_other_prot:
            penalty = 0.55
        if row["match_count"] >= 4:
            extra += 0.05
        if dessert_mode and any(sk in ing for sk in SAVORY_KEYWORDS):
            penalty *= 0.3

        final = (0.72 * sim + 0.28 * ratio + extra) * penalty
        if row["match_count"] <= 1:
            final *= 0.7
        return final

    df_result["cosine_score"] = df_result.apply(adjust_score, axis=1)

    # ── Protein consistency filter ────────────────────────────────────────────
    if allowed_proteins:
        def keep(row):
            ing      = str(row["raw_ingredients_text"]).lower()
            detected = [p for p in MAIN_PROTEINS if is_real_meat(p, ing)]
            return any(p in allowed_proteins for p in detected) or len(detected) == 0

        df_result = df_result[df_result.apply(keep, axis=1)]

    df_result = df_result[df_result["cosine_score"] >= 0.03]

    if df_result.empty:
        return df_result.head(10), total_bahan_asli

    # ── Minimum nutrition filter ───────────────────────────────────────────────
    df_result = df_result[
        (df_result["calories_per_serving"] >= 50) &
        (df_result["protein_per_serving"]  >= 3)
    ]

    if df_result.empty:
        return df_result.head(10), total_bahan_asli

    # ── Deduplication ─────────────────────────────────────────────────────────
    if "recipe_name" in df_result.columns:
        df_result["recipe_name_clean"] = df_result["recipe_name"].astype(str).str.lower().str.strip()
        df_result = df_result.drop_duplicates(subset=["recipe_name_clean"])
    if "url" in df_result.columns:
        df_result = df_result.drop_duplicates(subset=["url"])

    df_result["similarity_percent"] = (df_result["cosine_score"] * 100).round(2)

    return (
        df_result.sort_values("cosine_score", ascending=False).head(10),
        total_bahan_asli,
    )