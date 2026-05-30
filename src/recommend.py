import json
import warnings

import numpy as np
import pandas as pd

from sqlalchemy import text
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.db import get_engine

warnings.filterwarnings("ignore")


TOP_K = 5
RANDOM_STATE = 42


# ============================================================
# DATABASE HELPERS
# ============================================================

def ensure_recommendation_tables(engine):
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id BIGSERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                content_id TEXT NOT NULL,
                title TEXT NOT NULL,
                reason TEXT NOT NULL,
                score FLOAT NOT NULL,
                generated_at TIMESTAMP DEFAULT NOW()
            );
        """))

        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS rec_rank INTEGER;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS recommendation_type TEXT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS confidence FLOAT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS user_profile TEXT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS user_country TEXT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS content_genre TEXT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS content_language TEXT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS model_cf_score FLOAT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS user_cf_score FLOAT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS item_cf_score FLOAT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS content_score FLOAT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS popularity_score FLOAT;
        """))
        conn.execute(text("""
            ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS country_score FLOAT;
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS recommendation_model_metrics (
                id BIGSERIAL PRIMARY KEY,
                total_users INTEGER,
                total_content INTEGER,
                users_with_history INTEGER,
                total_recommendations INTEGER,
                catalog_coverage FLOAT,
                avg_hybrid_score FLOAT,
                model_based_enabled BOOLEAN,
                user_cf_enabled BOOLEAN,
                item_cf_enabled BOOLEAN,
                content_based_enabled BOOLEAN,
                generated_at TIMESTAMP DEFAULT NOW()
            );
        """))


def reset_recommendation_tables(engine):
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE recommendations"))
        conn.execute(text("TRUNCATE TABLE recommendation_model_metrics"))


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def normalize_series(series):
    series = pd.to_numeric(series, errors="coerce").fillna(0)
    min_v = series.min()
    max_v = series.max()

    if max_v == min_v:
        if max_v == 0:
            return pd.Series(0.0, index=series.index)
        return pd.Series(1.0, index=series.index)

    return (series - min_v) / (max_v - min_v)


def normalize_array(arr):
    arr = np.nan_to_num(np.array(arr, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    min_v = arr.min()
    max_v = arr.max()

    if max_v == min_v:
        if max_v == 0:
            return np.zeros_like(arr, dtype=float)
        return np.ones_like(arr, dtype=float)

    return (arr - min_v) / (max_v - min_v)


def safe_text(value):
    if pd.isna(value):
        return ""
    return str(value)


def get_top_key(df, key_col, weight_col):
    if df.empty or key_col not in df.columns:
        return "Unknown"

    temp = df.copy()
    if weight_col not in temp.columns:
        temp[weight_col] = 1

    grouped = (
        temp.groupby(key_col)[weight_col]
        .sum()
        .sort_values(ascending=False)
    )

    if grouped.empty:
        return "Unknown"

    return str(grouped.index[0])


def build_interaction_score(watch, content):
    if watch.empty:
        return pd.DataFrame(columns=["user_id", "content_id", "interaction_score"])

    df = watch.copy()

    if "duration_minutes" not in df.columns:
        df = df.merge(content[["content_id", "duration_minutes"]], on="content_id", how="left")

    df["watch_minutes"] = pd.to_numeric(df.get("watch_minutes", 0), errors="coerce").fillna(0)
    df["completion_rate"] = pd.to_numeric(df.get("completion_rate", 0), errors="coerce").fillna(0)
    df["quality_score"] = pd.to_numeric(df.get("quality_score", 0), errors="coerce").fillna(0)
    df["buffering_count"] = pd.to_numeric(df.get("buffering_count", 0), errors="coerce").fillna(0)
    df["duration_minutes"] = pd.to_numeric(df.get("duration_minutes", 1), errors="coerce").fillna(1)

    df["watch_ratio"] = (df["watch_minutes"] / df["duration_minutes"]).clip(0, 1.5)
    df["quality_component"] = (df["quality_score"] / 5).clip(0, 1)
    df["buffer_penalty"] = (df["buffering_count"] * 0.035).clip(0, 0.25)

    df["event_interaction_score"] = (
        df["watch_ratio"] * 0.40
        + df["completion_rate"] * 0.42
        + df["quality_component"] * 0.13
        - df["buffer_penalty"]
    ).clip(0, 1.5)

    interactions = (
        df.groupby(["user_id", "content_id"])
        .agg(
            interaction_score=("event_interaction_score", "sum"),
            watch_events=("event_id", "count"),
            total_watch_minutes=("watch_minutes", "sum"),
            avg_completion_rate=("completion_rate", "mean"),
        )
        .reset_index()
    )

    interactions["interaction_score"] = (
        interactions["interaction_score"]
        + np.log1p(interactions["watch_events"]) * 0.15
        + np.log1p(interactions["total_watch_minutes"]) * 0.03
        + interactions["avg_completion_rate"] * 0.20
    )

    interactions["interaction_score"] = interactions["interaction_score"].clip(0, 5)

    return interactions[["user_id", "content_id", "interaction_score"]]


def build_user_profiles(users, watch, content):
    rows = []

    watch_content = watch.merge(content, on="content_id", how="left") if not watch.empty else pd.DataFrame()

    for _, user in users.iterrows():
        user_id = user["user_id"]
        user_watch = watch_content[watch_content["user_id"] == user_id] if not watch_content.empty else pd.DataFrame()

        favorite_genre = get_top_key(user_watch, "genre", "watch_minutes")
        favorite_language = get_top_key(user_watch, "language", "watch_minutes")

        watched_count = int(user_watch["content_id"].nunique()) if not user_watch.empty else 0
        total_watch_minutes = float(user_watch["watch_minutes"].sum()) if not user_watch.empty else 0.0
        avg_completion = float(user_watch["completion_rate"].mean()) if not user_watch.empty else 0.0

        rows.append({
            "user_id": user_id,
            "country": user.get("country", "Unknown"),
            "subscription_plan": user.get("subscription_plan", "Unknown"),
            "favorite_genre": favorite_genre,
            "favorite_language": favorite_language,
            "watched_count": watched_count,
            "total_watch_minutes": total_watch_minutes,
            "avg_completion_rate": avg_completion,
        })

    return pd.DataFrame(rows)


# ============================================================
# CONTENT-BASED FILTERING
# ============================================================

def build_content_vectors(content):
    content = content.copy()

    for col in ["title", "genre", "language", "description", "release_year"]:
        if col not in content.columns:
            content[col] = ""

    content["content_text"] = (
        content["title"].apply(safe_text) + " "
        + content["genre"].apply(safe_text) + " "
        + content["language"].apply(safe_text) + " "
        + content["description"].apply(safe_text) + " "
        + content["release_year"].apply(safe_text)
    )

    vectorizer = TfidfVectorizer(
        max_features=700,
        ngram_range=(1, 2),
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(content["content_text"])

    return vectorizer, tfidf_matrix


def content_based_scores_for_user(user_id, interactions, tfidf_matrix, content_ids, content_id_to_idx):
    user_interactions = interactions[interactions["user_id"] == user_id]

    if user_interactions.empty:
        return np.zeros(len(content_ids))

    vectors = []
    weights = []

    for _, row in user_interactions.iterrows():
        content_id = row["content_id"]

        if content_id not in content_id_to_idx:
            continue

        vectors.append(tfidf_matrix[content_id_to_idx[content_id]])
        weights.append(float(row["interaction_score"]))

    if len(vectors) == 0:
        return np.zeros(len(content_ids))

    weights = np.array(weights, dtype=float)
    if weights.sum() == 0:
        weights = np.ones_like(weights)

    user_profile_vector = vectors[0] * weights[0]
    for i in range(1, len(vectors)):
        user_profile_vector = user_profile_vector + vectors[i] * weights[i]

    user_profile_vector = user_profile_vector / weights.sum()

    scores = cosine_similarity(user_profile_vector, tfidf_matrix).flatten()
    return normalize_array(scores)


# ============================================================
# COLLABORATIVE FILTERING
# ============================================================

def build_user_item_matrix(users, content, interactions):
    user_ids = list(users["user_id"].astype(str))
    content_ids = list(content["content_id"].astype(str))

    matrix_df = pd.DataFrame(0.0, index=user_ids, columns=content_ids)

    for _, row in interactions.iterrows():
        user_id = str(row["user_id"])
        content_id = str(row["content_id"])

        if user_id in matrix_df.index and content_id in matrix_df.columns:
            matrix_df.loc[user_id, content_id] = float(row["interaction_score"])

    return matrix_df


def build_user_based_scores(matrix_df):
    if matrix_df.shape[0] < 2 or matrix_df.shape[1] < 2:
        return pd.DataFrame(0.0, index=matrix_df.index, columns=matrix_df.columns), False

    values = matrix_df.values

    if np.count_nonzero(values) == 0:
        return pd.DataFrame(0.0, index=matrix_df.index, columns=matrix_df.columns), False

    user_similarity = cosine_similarity(values)

    # Remove self-similarity
    np.fill_diagonal(user_similarity, 0)

    denom = np.abs(user_similarity).sum(axis=1, keepdims=True) + 1e-9
    predicted = user_similarity.dot(values) / denom

    predicted = np.nan_to_num(predicted, nan=0.0, posinf=0.0, neginf=0.0)

    return pd.DataFrame(predicted, index=matrix_df.index, columns=matrix_df.columns), True


def build_item_based_scores(matrix_df):
    if matrix_df.shape[0] < 2 or matrix_df.shape[1] < 2:
        return pd.DataFrame(0.0, index=matrix_df.index, columns=matrix_df.columns), False

    values = matrix_df.values

    if np.count_nonzero(values) == 0:
        return pd.DataFrame(0.0, index=matrix_df.index, columns=matrix_df.columns), False

    item_similarity = cosine_similarity(values.T)

    # Remove self-similarity
    np.fill_diagonal(item_similarity, 0)

    denom = np.abs(item_similarity).sum(axis=1, keepdims=True).T + 1e-9
    predicted = values.dot(item_similarity) / denom

    predicted = np.nan_to_num(predicted, nan=0.0, posinf=0.0, neginf=0.0)

    return pd.DataFrame(predicted, index=matrix_df.index, columns=matrix_df.columns), True


def build_model_based_scores(matrix_df):
    if matrix_df.shape[0] < 4 or matrix_df.shape[1] < 4:
        return pd.DataFrame(0.0, index=matrix_df.index, columns=matrix_df.columns), False

    values = matrix_df.values

    if np.count_nonzero(values) == 0:
        return pd.DataFrame(0.0, index=matrix_df.index, columns=matrix_df.columns), False

    max_components = min(matrix_df.shape[0] - 1, matrix_df.shape[1] - 1, 20)

    if max_components < 2:
        return pd.DataFrame(0.0, index=matrix_df.index, columns=matrix_df.columns), False

    svd = TruncatedSVD(
        n_components=max_components,
        random_state=RANDOM_STATE
    )

    user_factors = svd.fit_transform(values)
    item_factors = svd.components_

    reconstructed = np.dot(user_factors, item_factors)
    reconstructed = np.nan_to_num(reconstructed, nan=0.0, posinf=0.0, neginf=0.0)

    # Normalize per user so scores are comparable
    normalized = np.zeros_like(reconstructed)

    for i in range(reconstructed.shape[0]):
        normalized[i, :] = normalize_array(reconstructed[i, :])

    return pd.DataFrame(normalized, index=matrix_df.index, columns=matrix_df.columns), True


# ============================================================
# POPULARITY AND TRENDING SIGNALS
# ============================================================

def build_popularity_scores(content, content_perf):
    content = content.copy()

    if content_perf.empty or "popularity_score" not in content_perf.columns:
        content["popularity_score"] = 0.0
    else:
        content = content.merge(
            content_perf[["content_id", "popularity_score"]],
            on="content_id",
            how="left"
        )

    content["popularity_score"] = content["popularity_score"].fillna(0)
    content["popularity_norm"] = normalize_series(content["popularity_score"])

    return dict(zip(content["content_id"], content["popularity_norm"]))


def build_country_scores(watch, content_ids):
    if watch.empty or "country" not in watch.columns:
        return {}

    country_scores = {}

    grouped = (
        watch.groupby(["country", "content_id"])
        .agg(
            country_watch_minutes=("watch_minutes", "sum"),
            country_viewers=("user_id", "nunique"),
            country_completion=("completion_rate", "mean"),
        )
        .reset_index()
    )

    grouped["country_score"] = (
        grouped["country_watch_minutes"] * 0.60
        + grouped["country_viewers"] * 10
        + grouped["country_completion"] * 100
    )

    for country, temp in grouped.groupby("country"):
        temp = temp.copy()
        temp["country_score"] = normalize_series(temp["country_score"])
        country_scores[country] = dict(zip(temp["content_id"], temp["country_score"]))

    return country_scores


# ============================================================
# REASONING
# ============================================================

def choose_recommendation_type(model_score, user_score, item_score, content_score, popularity_score, country_score):
    scores = {
        "model_based_cf": model_score,
        "user_based_cf": user_score,
        "item_based_cf": item_score,
        "content_based": content_score,
        "global_popularity": popularity_score,
        "country_trending": country_score,
    }

    best_method = max(scores, key=scores.get)

    label_map = {
        "model_based_cf": "Model-based collaborative filtering",
        "user_based_cf": "User-based collaborative filtering",
        "item_based_cf": "Item-based collaborative filtering",
        "content_based": "Content-based filtering",
        "global_popularity": "Popularity fallback",
        "country_trending": "Country-trending signal",
    }

    return label_map[best_method]


def build_reason(user_profile, item, model_score, user_score, item_score, content_score, popularity_score, country_score):
    recommendation_type = choose_recommendation_type(
        model_score,
        user_score,
        item_score,
        content_score,
        popularity_score,
        country_score,
    )

    favorite_genre = user_profile.get("favorite_genre", "Unknown")
    favorite_language = user_profile.get("favorite_language", "Unknown")
    country = user_profile.get("country", "Unknown")

    genre = item.get("genre", "Unknown")
    language = item.get("language", "Unknown")

    reasons = []

    if model_score >= 0.55:
        reasons.append("matrix factorization predicts strong user-item affinity")

    if user_score >= 0.55:
        reasons.append("similar users showed interest in this title")

    if item_score >= 0.55:
        reasons.append("similar items were watched by this user")

    if content_score >= 0.55:
        reasons.append(f"content metadata matches the user's {favorite_genre}/{favorite_language} profile")

    if country_score >= 0.55:
        reasons.append(f"this title is trending among users in {country}")

    if popularity_score >= 0.60:
        reasons.append("it has strong overall platform popularity")

    if genre == favorite_genre and favorite_genre != "Unknown":
        reasons.append(f"matches user's strongest genre: {favorite_genre}")

    if language == favorite_language and favorite_language != "Unknown":
        reasons.append(f"matches user's preferred language: {favorite_language}")

    if len(reasons) == 0:
        reasons.append("balanced hybrid score from engagement, similarity, and popularity signals")

    reason_text = "; ".join(reasons[:3])

    return f"{recommendation_type}: {reason_text}"


def build_user_profile_text(user_profile):
    return (
        f"Country={user_profile.get('country', 'Unknown')}; "
        f"Plan={user_profile.get('subscription_plan', 'Unknown')}; "
        f"Favorite genre={user_profile.get('favorite_genre', 'Unknown')}; "
        f"Favorite language={user_profile.get('favorite_language', 'Unknown')}; "
        f"Watched titles={int(user_profile.get('watched_count', 0))}; "
        f"Avg completion={float(user_profile.get('avg_completion_rate', 0)):.1%}"
    )


# ============================================================
# MAIN RECOMMENDATION PIPELINE
# ============================================================

def main():
    engine = get_engine()
    ensure_recommendation_tables(engine)

    users = pd.read_sql("SELECT * FROM user_features", engine)
    content = pd.read_sql("SELECT * FROM content_dim", engine)
    watch = pd.read_sql("SELECT * FROM clean_watch_events", engine)
    content_perf = pd.read_sql("SELECT * FROM content_performance", engine)

    if users.empty or content.empty:
        print("Not enough data for recommendations.")
        return

    users["user_id"] = users["user_id"].astype(str)
    content["content_id"] = content["content_id"].astype(str)

    if not watch.empty:
        watch["user_id"] = watch["user_id"].astype(str)
        watch["content_id"] = watch["content_id"].astype(str)

    content_ids = list(content["content_id"])
    content_id_to_idx = {content_id: idx for idx, content_id in enumerate(content_ids)}

    content_lookup = content.set_index("content_id").to_dict(orient="index")

    interactions = build_interaction_score(watch, content)
    user_profiles = build_user_profiles(users, watch, content)
    user_profile_lookup = user_profiles.set_index("user_id").to_dict(orient="index")

    matrix_df = build_user_item_matrix(users, content, interactions)

    user_cf_df, user_cf_enabled = build_user_based_scores(matrix_df)
    item_cf_df, item_cf_enabled = build_item_based_scores(matrix_df)
    model_cf_df, model_cf_enabled = build_model_based_scores(matrix_df)

    vectorizer, tfidf_matrix = build_content_vectors(content)
    content_based_enabled = True

    popularity_scores = build_popularity_scores(content, content_perf)
    country_scores_lookup = build_country_scores(watch, content_ids)

    watched_lookup = (
        interactions.groupby("user_id")["content_id"].apply(set).to_dict()
        if not interactions.empty
        else {}
    )

    rows = []

    for _, user in users.iterrows():
        user_id = str(user["user_id"])
        user_profile = user_profile_lookup.get(user_id, {})
        country = user_profile.get("country", user.get("country", "Unknown"))

        watched_items = watched_lookup.get(user_id, set())
        candidate_ids = [content_id for content_id in content_ids if content_id not in watched_items]

        # If user has consumed nearly the whole catalog, allow all content as fallback.
        if len(candidate_ids) == 0:
            candidate_ids = content_ids

        user_has_history = len(watched_items) > 0

        content_scores_all = content_based_scores_for_user(
            user_id,
            interactions,
            tfidf_matrix,
            content_ids,
            content_id_to_idx,
        )

        candidate_rows = []

        for content_id in candidate_ids:
            item = content_lookup.get(content_id, {})

            model_score = 0.0
            user_score = 0.0
            item_score = 0.0

            if user_id in model_cf_df.index and content_id in model_cf_df.columns:
                model_score = float(model_cf_df.loc[user_id, content_id])

            if user_id in user_cf_df.index and content_id in user_cf_df.columns:
                user_score = float(user_cf_df.loc[user_id, content_id])

            if user_id in item_cf_df.index and content_id in item_cf_df.columns:
                item_score = float(item_cf_df.loc[user_id, content_id])

            content_score = float(content_scores_all[content_id_to_idx[content_id]]) if content_id in content_id_to_idx else 0.0
            popularity_score = float(popularity_scores.get(content_id, 0.0))
            country_score = float(country_scores_lookup.get(country, {}).get(content_id, 0.0))

            # Dynamic hybrid weights:
            # - Users with history get stronger collaborative and personalization signals.
            # - Cold-start users rely more on country trends and popularity.
            if user_has_history:
                hybrid_score = (
                    model_score * 0.28
                    + item_score * 0.22
                    + user_score * 0.16
                    + content_score * 0.20
                    + country_score * 0.08
                    + popularity_score * 0.06
                )
            else:
                hybrid_score = (
                    country_score * 0.40
                    + popularity_score * 0.35
                    + content_score * 0.25
                )

            confidence = min(1.0, max(0.0, hybrid_score))

            recommendation_type = choose_recommendation_type(
                model_score,
                user_score,
                item_score,
                content_score,
                popularity_score,
                country_score,
            )

            reason = build_reason(
                user_profile,
                item,
                model_score,
                user_score,
                item_score,
                content_score,
                popularity_score,
                country_score,
            )

            candidate_rows.append({
                "user_id": user_id,
                "content_id": content_id,
                "title": item.get("title", "Unknown Title"),
                "reason": reason,
                "score": float(hybrid_score),
                "recommendation_type": recommendation_type,
                "confidence": float(confidence),
                "user_profile": build_user_profile_text(user_profile),
                "user_country": country,
                "content_genre": item.get("genre", "Unknown"),
                "content_language": item.get("language", "Unknown"),
                "model_cf_score": float(model_score),
                "user_cf_score": float(user_score),
                "item_cf_score": float(item_score),
                "content_score": float(content_score),
                "popularity_score": float(popularity_score),
                "country_score": float(country_score),
            })

        candidate_df = pd.DataFrame(candidate_rows)

        if candidate_df.empty:
            continue

        candidate_df = candidate_df.sort_values("score", ascending=False).head(TOP_K)
        candidate_df["rec_rank"] = range(1, len(candidate_df) + 1)

        rows.extend(candidate_df.to_dict(orient="records"))

    out = pd.DataFrame(rows)

    if out.empty:
        print("No recommendations generated.")
        return

    # Make scores cleaner for dashboard display
    score_cols = [
        "score",
        "confidence",
        "model_cf_score",
        "user_cf_score",
        "item_cf_score",
        "content_score",
        "popularity_score",
        "country_score",
    ]

    for col in score_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).round(4)

    recommended_catalog = out["content_id"].nunique()
    catalog_coverage = recommended_catalog / max(1, len(content))
    users_with_history = sum(1 for user_id in users["user_id"] if user_id in watched_lookup and len(watched_lookup[user_id]) > 0)

    metrics = pd.DataFrame([{
        "total_users": int(users["user_id"].nunique()),
        "total_content": int(content["content_id"].nunique()),
        "users_with_history": int(users_with_history),
        "total_recommendations": int(len(out)),
        "catalog_coverage": float(catalog_coverage),
        "avg_hybrid_score": float(out["score"].mean()),
        "model_based_enabled": bool(model_cf_enabled),
        "user_cf_enabled": bool(user_cf_enabled),
        "item_cf_enabled": bool(item_cf_enabled),
        "content_based_enabled": bool(content_based_enabled),
    }])

    reset_recommendation_tables(engine)

    out.to_sql("recommendations", engine, if_exists="append", index=False)
    metrics.to_sql("recommendation_model_metrics", engine, if_exists="append", index=False)

    print("==============================================")
    print("Hybrid recommendation pipeline complete")
    print(f"Generated recommendations: {len(out)}")
    print(f"Users covered: {out['user_id'].nunique()}")
    print(f"Catalog coverage: {catalog_coverage:.1%}")
    print("Methods used:")
    print(f"- Model-based CF enabled: {model_cf_enabled}")
    print(f"- User-based CF enabled: {user_cf_enabled}")
    print(f"- Item-based CF enabled: {item_cf_enabled}")
    print(f"- Content-based enabled: {content_based_enabled}")
    print("Saved tables:")
    print("- recommendations")
    print("- recommendation_model_metrics")
    print("==============================================")


if __name__ == "__main__":
    main()