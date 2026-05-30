import numpy as np
import pandas as pd
from sqlalchemy import text
from src.db import get_engine
from src.seed_dimensions import main as seed_dimensions


def risk_label(row):
    score = 0
    if row["days_since_last_watch"] > 14:
        score += 1
    if row["avg_completion_rate"] < 0.35:
        score += 1
    if row["payment_failed_count"] > 0:
        score += 1
    if row["buffering_count"] > 6:
        score += 1
    if row["total_watch_minutes"] < 60:
        score += 1
    return 1 if score >= 2 else 0


def replace_table(engine, table, df):
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table}"))
    if not df.empty:
        df.to_sql(table, engine, if_exists="append", index=False)


def main():
    seed_dimensions()
    engine = get_engine()
    watch = pd.read_sql("SELECT * FROM clean_watch_events", engine)
    business = pd.read_sql("SELECT * FROM clean_business_events", engine)
    users = pd.read_sql("SELECT * FROM users_dim", engine)
    content = pd.read_sql("SELECT * FROM content_dim", engine)

    if watch.empty:
        print("No clean watch events found. Run clean_events first.")
        return

    watch["event_date"] = pd.to_datetime(watch["event_timestamp"]).dt.date
    today = pd.Timestamp.today().normalize()

    revenue = business[business["event_type"] == "payment_success"].copy() if not business.empty else pd.DataFrame()
    failures = business[business["event_type"] == "payment_failed"].copy() if not business.empty else pd.DataFrame()

    daily = watch.groupby("event_date").agg(
        active_users=("user_id", "nunique"),
        total_watch_minutes=("watch_minutes", "sum"),
        avg_completion_rate=("completion_rate", "mean"),
        buffering_events=("buffering_count", "sum"),
    ).reset_index().rename(columns={"event_date": "metric_date"})

    if not revenue.empty:
        revenue["metric_date"] = pd.to_datetime(revenue["event_timestamp"]).dt.date
        rev = revenue.groupby("metric_date")["amount"].sum().reset_index(name="total_revenue")
        daily = daily.merge(rev, on="metric_date", how="left")
    else:
        daily["total_revenue"] = 0

    if not failures.empty:
        failures["metric_date"] = pd.to_datetime(failures["event_timestamp"]).dt.date
        fail = failures.groupby("metric_date").size().reset_index(name="payment_failures")
        daily = daily.merge(fail, on="metric_date", how="left")
    else:
        daily["payment_failures"] = 0

    daily["total_revenue"] = daily["total_revenue"].fillna(0)
    daily["payment_failures"] = daily["payment_failures"].fillna(0).astype(int)
    replace_table(engine, "daily_metrics", daily)

    cp = watch.merge(content, on="content_id", how="left")
    content_perf = cp.groupby(["content_id", "title", "genre", "language"], dropna=False).agg(
        total_watch_minutes=("watch_minutes", "sum"),
        unique_viewers=("user_id", "nunique"),
        avg_completion_rate=("completion_rate", "mean"),
    ).reset_index()
    content_perf["popularity_score"] = (
        content_perf["total_watch_minutes"] * 0.6
        + content_perf["unique_viewers"] * 10
        + content_perf["avg_completion_rate"] * 100
    )
    replace_table(engine, "content_performance", content_perf)

    country = watch.groupby("country").agg(
        active_users=("user_id", "nunique"),
        total_watch_minutes=("watch_minutes", "sum"),
        avg_completion_rate=("completion_rate", "mean"),
        buffering_events=("buffering_count", "sum"),
    ).reset_index()
    if not revenue.empty:
        rev_country = revenue.groupby("country")["amount"].sum().reset_index(name="total_revenue")
        country = country.merge(rev_country, on="country", how="left")
    else:
        country["total_revenue"] = 0
    country["total_revenue"] = country["total_revenue"].fillna(0)
    replace_table(engine, "country_metrics", country)

    device = watch.groupby("device").agg(
        total_events=("event_id", "count"),
        total_buffering_events=("buffering_count", "sum"),
        avg_quality_score=("quality_score", "mean"),
        avg_completion_rate=("completion_rate", "mean"),
    ).reset_index()
    replace_table(engine, "device_quality_metrics", device)

    uf = watch.merge(content[["content_id", "genre"]], on="content_id", how="left")
    features = uf.groupby("user_id").agg(
        total_watch_minutes=("watch_minutes", "sum"),
        watch_events=("event_id", "count"),
        avg_completion_rate=("completion_rate", "mean"),
        last_watch=("event_timestamp", "max"),
        buffering_count=("buffering_count", "sum"),
        num_genres_watched=("genre", "nunique"),
    ).reset_index()

    features["last_watch"] = pd.to_datetime(features["last_watch"])
    features["days_since_last_watch"] = (today - features["last_watch"].dt.normalize()).dt.days.clip(lower=0)
    features = features.drop(columns=["last_watch"])

    if not failures.empty:
        fail_user = failures.groupby("user_id").size().reset_index(name="payment_failed_count")
        features = features.merge(fail_user, on="user_id", how="left")
    else:
        features["payment_failed_count"] = 0
    features["payment_failed_count"] = features["payment_failed_count"].fillna(0).astype(int)

    features = users[["user_id", "country", "subscription_plan", "signup_date"]].merge(features, on="user_id", how="left")
    features["signup_date"] = pd.to_datetime(features["signup_date"])
    features["subscription_age_days"] = (today - features["signup_date"].dt.normalize()).dt.days.clip(lower=1)
    for col in ["total_watch_minutes", "watch_events", "avg_completion_rate", "days_since_last_watch", "buffering_count", "payment_failed_count", "num_genres_watched"]:
        features[col] = features[col].fillna(0)
    features.loc[features["watch_events"] == 0, "days_since_last_watch"] = 999
    features["churn_label"] = features.apply(risk_label, axis=1)
    features = features.drop(columns=["signup_date"])
    replace_table(engine, "user_features", features)

    print("Built analytics marts: daily_metrics, content_performance, country_metrics, device_quality_metrics, user_features")


if __name__ == "__main__":
    main()
