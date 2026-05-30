import pandas as pd
from sqlalchemy import text
from src.db import get_engine


def main():
    engine = get_engine()
    raw = pd.read_sql("SELECT * FROM raw_events", engine)
    if raw.empty:
        print("No raw events found. Run producer and consumer first.")
        return

    payload = pd.json_normalize(raw["event_payload"])
    payload["event_timestamp"] = pd.to_datetime(raw["event_timestamp"])
    payload["event_id"] = raw["event_id"]
    payload["event_type"] = raw["event_type"]

    watch = payload[payload["event_type"].isin(["watch_event", "playback_quality_event"])].copy()
    if not watch.empty:
        watch_clean = pd.DataFrame({
            "event_id": watch["event_id"].astype(str),
            "user_id": watch["user_id"].fillna("unknown").astype(str),
            "content_id": watch["content_id"].fillna("unknown").astype(str),
            "country": watch["country"].fillna("Unknown").astype(str),
            "device": watch["device"].fillna("Unknown").astype(str),
            "event_timestamp": watch["event_timestamp"],
            "watch_minutes": pd.to_numeric(watch.get("watch_minutes", 0), errors="coerce").fillna(0).clip(lower=0),
            "completion_rate": pd.to_numeric(watch.get("completion_rate", 0), errors="coerce").fillna(0).clip(0, 1),
            "buffering_count": pd.to_numeric(watch.get("buffering_count", 0), errors="coerce").fillna(0).astype(int).clip(lower=0),
            "quality_score": pd.to_numeric(watch.get("quality_score", 0.8), errors="coerce").fillna(0.8).clip(0, 1),
        })
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE clean_watch_events"))
        watch_clean.drop_duplicates("event_id").to_sql("clean_watch_events", engine, if_exists="append", index=False)
        print(f"Loaded {len(watch_clean)} clean watch/playback rows")

    business = payload[~payload["event_type"].isin(["watch_event", "playback_quality_event"])].copy()
    if not business.empty:
        business_clean = pd.DataFrame({
            "event_id": business["event_id"].astype(str),
            "user_id": business["user_id"].fillna("unknown").astype(str),
            "event_type": business["event_type"].astype(str),
            "country": business["country"].fillna("Unknown").astype(str),
            "device": business["device"].fillna("Unknown").astype(str),
            "event_timestamp": business["event_timestamp"],
            "amount": pd.to_numeric(business.get("amount", 0), errors="coerce").fillna(0),
            "search_query": business.get("search_query", "").fillna("").astype(str) if "search_query" in business else "",
            "status": business.get("status", "").fillna("").astype(str) if "status" in business else "",
        })
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE clean_business_events"))
        business_clean.drop_duplicates("event_id").to_sql("clean_business_events", engine, if_exists="append", index=False)
        print(f"Loaded {len(business_clean)} clean business rows")


if __name__ == "__main__":
    main()
