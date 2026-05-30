import pandas as pd
from sqlalchemy import text
from src.db import get_engine


def main():
    engine = get_engine()
    users = pd.read_sql("SELECT * FROM user_features", engine)
    content = pd.read_sql("SELECT * FROM content_dim", engine)
    watch = pd.read_sql("SELECT * FROM clean_watch_events", engine)
    content_perf = pd.read_sql("SELECT * FROM content_performance", engine)

    if users.empty or content.empty:
        print("Not enough data for recommendations.")
        return

    watched = watch.groupby("user_id")["content_id"].apply(set).to_dict() if not watch.empty else {}
    perf = content.merge(content_perf[["content_id", "popularity_score"]], on="content_id", how="left")
    perf["popularity_score"] = perf["popularity_score"].fillna(0)

    rows = []
    for _, user in users.iterrows():
        user_id = user["user_id"]
        country = user["country"]
        already = watched.get(user_id, set())

        user_watch = watch[watch["user_id"] == user_id]
        if not user_watch.empty:
            uw = user_watch.merge(content[["content_id", "genre"]], on="content_id", how="left")
            favorite_genre = uw.groupby("genre")["watch_minutes"].sum().sort_values(ascending=False).index[0]
            candidates = perf[(perf["genre"] == favorite_genre) & (~perf["content_id"].isin(already))].copy()
            reason = f"Because this user watches {favorite_genre} content"
        else:
            candidates = perf[~perf["content_id"].isin(already)].copy()
            reason = f"Trending content for {country} users"

        if candidates.empty:
            candidates = perf.copy()
            reason = "Popular content fallback"

        candidates = candidates.sort_values("popularity_score", ascending=False).head(3)
        for _, item in candidates.iterrows():
            rows.append({
                "user_id": user_id,
                "content_id": item["content_id"],
                "title": item["title"],
                "reason": reason,
                "score": float(item["popularity_score"]),
            })

    out = pd.DataFrame(rows)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE recommendations"))
    if not out.empty:
        out.to_sql("recommendations", engine, if_exists="append", index=False)
    print(f"Generated {len(out)} recommendation rows")


if __name__ == "__main__":
    main()
