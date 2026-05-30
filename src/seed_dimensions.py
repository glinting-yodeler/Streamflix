from datetime import date, timedelta
import random
import pandas as pd
from sqlalchemy import text
from src.db import get_engine

COUNTRIES = ["Pakistan", "Saudi Arabia", "UAE", "Egypt", "Kuwait", "Qatar", "Bahrain"]
AGE_GROUPS = ["18-24", "25-34", "35-44", "45+"]
PLANS = ["monthly", "quarterly", "annual"]
GENRES = ["Drama", "Action", "Thriller", "Comedy", "Sports", "Documentary", "Kids", "Romance"]
LANGUAGES = ["English", "Arabic", "Turkish", "Urdu", "Hindi"]

CONTENT_TITLES = [
    "Desert Shadows", "City of Secrets", "The Last Signal", "Midnight Chase",
    "Court of Kings", "Karachi Nights", "Riyadh Drift", "Hidden Goals",
    "Family Weekend", "The Quiet Storm", "Champions Live", "Laugh Lines",
    "Ancient Roads", "Pixel Detectives", "Moon Over Istanbul", "The Final Over",
    "Blue Horizon", "Dune Patrol", "The Crowned Falcon", "Signal Lost"
]


def seed_users(n=500):
    today = date.today()
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "user_id": f"u_{i:04d}",
            "country": random.choice(COUNTRIES),
            "age_group": random.choice(AGE_GROUPS),
            "subscription_plan": random.choices(PLANS, weights=[0.65, 0.2, 0.15])[0],
            "signup_date": today - timedelta(days=random.randint(5, 900)),
        })
    return pd.DataFrame(rows)


def seed_content():
    rows = []
    for i, title in enumerate(CONTENT_TITLES, start=1):
        genre = random.choice(GENRES)
        language = random.choice(LANGUAGES)
        rows.append({
            "content_id": f"c_{i:04d}",
            "title": title,
            "genre": genre,
            "language": language,
            "duration_minutes": random.randint(25, 140),
            "release_year": random.randint(2014, 2026),
            "description": f"{title} is a {genre.lower()} title in {language} with strong audience engagement and regional streaming appeal.",
        })
    return pd.DataFrame(rows)


def main():
    engine = get_engine()
    with engine.begin() as conn:
        user_count = conn.execute(text("SELECT COUNT(*) FROM users_dim")).scalar()
        content_count = conn.execute(text("SELECT COUNT(*) FROM content_dim")).scalar()

    if user_count == 0:
        seed_users().to_sql("users_dim", engine, if_exists="append", index=False)
        print("Seeded users_dim")
    else:
        print("users_dim already has data")

    if content_count == 0:
        seed_content().to_sql("content_dim", engine, if_exists="append", index=False)
        print("Seeded content_dim")
    else:
        print("content_dim already has data")


if __name__ == "__main__":
    main()
