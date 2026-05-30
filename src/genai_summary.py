from datetime import datetime
import pandas as pd
from sqlalchemy import text

from src.db import get_engine
from src.genai_client import generate_with_gemini


def safe_read_sql(query, engine):
    try:
        return pd.read_sql(query, engine)
    except Exception:
        return pd.DataFrame()


def value_or_default(df, col, default=0):
    if df.empty or col not in df.columns:
        return default
    try:
        return df.iloc[0][col]
    except Exception:
        return default


def build_local_fallback(context):
    return f"""
Daily OTT Intelligence Brief

Executive Summary:
The platform generated {context['watch_hours']:.1f} watch hours from {context['active_users']} active users. Revenue reached PKR {context['revenue']:,.0f}, while the average content completion rate was {context['avg_completion']:.1%}.

Content Performance:
The strongest title was {context['top_title']}, while {context['top_genre']} appears to be one of the strongest content categories. This suggests that content discovery and genre-level engagement are important drivers of watch time.

Churn & Retention Risk:
The system identified {context['high_risk_users']} high-risk users and {context['medium_risk_users']} medium-risk users. The main churn signals include inactivity, low watch time, payment failures, and playback friction.

Recommendation Intelligence:
The hybrid recommendation system generated {context['total_recommendations']} recommendations across {context['recommended_users']} users. This supports personalization through collaborative filtering, content similarity, country trends, and global popularity.

Playback Quality:
The most problematic device is {context['worst_device']}, with {context['buffering_events']} buffering events. Playback quality should be monitored because buffering can reduce completion rates and increase churn risk.

Recommended Actions:
1. Promote high-completion titles to medium-risk users.
2. Trigger payment recovery campaigns for failed-payment users.
3. Investigate playback quality on problematic devices.
4. Use country-specific recommendations for regional personalization.
5. Send win-back campaigns to inactive high-risk users.
""".strip()


def main():
    engine = get_engine()

    daily = safe_read_sql(
        """
        SELECT *
        FROM daily_metrics
        ORDER BY metric_date DESC
        LIMIT 1
        """,
        engine
    )

    content = safe_read_sql(
        """
        SELECT *
        FROM content_performance
        ORDER BY popularity_score DESC
        LIMIT 5
        """,
        engine
    )

    country = safe_read_sql(
        """
        SELECT *
        FROM country_metrics
        ORDER BY total_watch_minutes DESC
        LIMIT 5
        """,
        engine
    )

    churn = safe_read_sql(
        """
        SELECT risk_level, COUNT(*) AS users
        FROM churn_predictions
        GROUP BY risk_level
        """,
        engine
    )

    churn_reasons = safe_read_sql(
        """
        SELECT risk_reason, COUNT(*) AS users
        FROM churn_predictions
        WHERE risk_level = 'High'
        GROUP BY risk_reason
        ORDER BY users DESC
        LIMIT 5
        """,
        engine
    )

    device = safe_read_sql(
        """
        SELECT *
        FROM device_quality_metrics
        ORDER BY total_buffering_events DESC
        LIMIT 5
        """,
        engine
    )

    rec_metrics = safe_read_sql(
        """
        SELECT *
        FROM recommendation_model_metrics
        ORDER BY generated_at DESC
        LIMIT 1
        """,
        engine
    )

    rec_types = safe_read_sql(
        """
        SELECT recommendation_type, COUNT(*) AS recommendations
        FROM recommendations
        GROUP BY recommendation_type
        ORDER BY recommendations DESC
        LIMIT 5
        """,
        engine
    )

    active_users = int(value_or_default(daily, "active_users", 0))
    total_watch_minutes = float(value_or_default(daily, "total_watch_minutes", 0))
    watch_hours = total_watch_minutes / 60
    avg_completion = float(value_or_default(daily, "avg_completion_rate", 0))
    revenue = float(value_or_default(daily, "total_revenue", 0))
    payment_failures = int(value_or_default(daily, "payment_failures", 0))

    top_title = "N/A"
    top_genre = "N/A"
    if not content.empty:
        top_title = str(content.iloc[0].get("title", "N/A"))
        top_genre = str(content.iloc[0].get("genre", "N/A"))

    top_country = "N/A"
    if not country.empty:
        top_country = str(country.iloc[0].get("country", "N/A"))

    worst_device = "N/A"
    buffering_events = 0
    if not device.empty:
        worst_device = str(device.iloc[0].get("device", "N/A"))
        buffering_events = int(device.iloc[0].get("total_buffering_events", 0))

    high_risk_users = 0
    medium_risk_users = 0
    if not churn.empty:
        for _, row in churn.iterrows():
            risk = str(row.get("risk_level", "")).lower()
            if risk == "high":
                high_risk_users = int(row.get("users", 0))
            elif risk == "medium":
                medium_risk_users = int(row.get("users", 0))

    total_recommendations = int(value_or_default(rec_metrics, "total_recommendations", 0))
    recommended_users = int(value_or_default(rec_metrics, "total_users", 0))
    catalog_coverage = float(value_or_default(rec_metrics, "catalog_coverage", 0))

    context = {
        "active_users": active_users,
        "watch_hours": watch_hours,
        "avg_completion": avg_completion,
        "revenue": revenue,
        "payment_failures": payment_failures,
        "top_title": top_title,
        "top_genre": top_genre,
        "top_country": top_country,
        "worst_device": worst_device,
        "buffering_events": buffering_events,
        "high_risk_users": high_risk_users,
        "medium_risk_users": medium_risk_users,
        "total_recommendations": total_recommendations,
        "recommended_users": recommended_users,
        "catalog_coverage": catalog_coverage,
    }

    fallback = build_local_fallback(context)

    prompt = f"""
You are a senior GenAI analytics assistant for an OTT streaming platform similar to STARZPLAY.

Generate a polished executive intelligence brief from the metrics below.

Rules:
- Keep it professional and business-focused.
- Do not invent numbers.
- Mention that this is based on synthetic project data if needed.
- Include clear sections:
  1. Executive Summary
  2. Content Performance
  3. Churn & Retention Risk
  4. Recommendation Intelligence
  5. Playback Quality
  6. Revenue & Payments
  7. Recommended Actions
- Make the language sound like something a data team would send to leadership.

Core metrics:
- Active users: {active_users}
- Watch hours: {watch_hours:.1f}
- Average completion rate: {avg_completion:.1%}
- Revenue: PKR {revenue:,.0f}
- Payment failures: {payment_failures}
- Top content title: {top_title}
- Top genre: {top_genre}
- Top country by watch time: {top_country}
- High-risk churn users: {high_risk_users}
- Medium-risk churn users: {medium_risk_users}
- Most problematic playback device: {worst_device}
- Buffering events on worst device: {buffering_events}
- Total recommendations generated: {total_recommendations}
- Users covered by recommendation system: {recommended_users}
- Recommendation catalog coverage: {catalog_coverage:.1%}

Top content table:
{content.to_string(index=False) if not content.empty else "No content data available."}

Top countries:
{country.to_string(index=False) if not country.empty else "No country data available."}

High-risk churn reasons:
{churn_reasons.to_string(index=False) if not churn_reasons.empty else "No churn reason data available."}

Recommendation method distribution:
{rec_types.to_string(index=False) if not rec_types.empty else "No recommendation method data available."}
"""

    summary_text = generate_with_gemini(prompt, fallback)

    summary_date = datetime.now().date()

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS executive_summaries (
                id SERIAL PRIMARY KEY,
                summary_date DATE,
                summary_text TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        conn.execute(text("TRUNCATE TABLE executive_summaries"))

    out = pd.DataFrame([{
        "summary_date": summary_date,
        "summary_text": summary_text,
    }])

    out.to_sql("executive_summaries", engine, if_exists="append", index=False)

    print("Generated Gemini-powered executive summary.")
    print(summary_text)


if __name__ == "__main__":
    main()