from datetime import date
import pandas as pd
from sqlalchemy import text
from src.db import get_engine


def pct(value):
    return f"{value:.1%}"


def main():
    engine = get_engine()
    daily = pd.read_sql("SELECT * FROM daily_metrics ORDER BY metric_date", engine)
    content = pd.read_sql("SELECT * FROM content_performance ORDER BY popularity_score DESC LIMIT 5", engine)
    country = pd.read_sql("SELECT * FROM country_metrics ORDER BY total_watch_minutes DESC LIMIT 3", engine)
    device = pd.read_sql("SELECT * FROM device_quality_metrics ORDER BY total_buffering_events DESC LIMIT 3", engine)
    churn = pd.read_sql("SELECT risk_level, COUNT(*) AS users FROM churn_predictions GROUP BY risk_level", engine)

    if daily.empty:
        print("No daily metrics found for summary.")
        return

    latest = daily.iloc[-1]
    prev = daily.iloc[-2] if len(daily) > 1 else None
    watch_change = "not enough historical data for comparison"
    if prev is not None and prev["total_watch_minutes"] > 0:
        change = (latest["total_watch_minutes"] - prev["total_watch_minutes"]) / prev["total_watch_minutes"]
        direction = "increased" if change >= 0 else "decreased"
        watch_change = f"watch time {direction} by {abs(change):.1%} compared to the previous day"

    top_content = content.iloc[0]["title"] if not content.empty else "no content yet"
    top_country = country.iloc[0]["country"] if not country.empty else "no country data yet"
    worst_device = device.iloc[0]["device"] if not device.empty else "no device data yet"
    high_risk = int(churn[churn["risk_level"] == "High"]["users"].sum()) if not churn.empty else 0

    summary = f"""
Daily OTT Executive Summary - {latest['metric_date']}

Platform activity shows that {watch_change}. The platform recorded {int(latest['active_users'])} active users and {latest['total_watch_minutes']:.0f} total watch minutes. The top-performing content title is {top_content}, while {top_country} currently leads by watch-time contribution.

Playback quality needs attention on {worst_device}, which has the highest buffering count among tracked devices. Payment failures recorded for the latest period were {int(latest['payment_failures'])}, and the churn model currently identifies {high_risk} users as high risk.

Recommended action: promote high-performing content to medium-risk users, investigate buffering issues on weaker devices, and target high-risk users with personalized recommendations or subscription offers.
""".strip()

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM executive_summaries WHERE summary_date = :d"), {"d": latest["metric_date"]})
        conn.execute(text("""
            INSERT INTO executive_summaries (summary_date, summary_text)
            VALUES (:summary_date, :summary_text)
        """), {"summary_date": latest["metric_date"], "summary_text": summary})

    print(summary)


if __name__ == "__main__":
    main()
