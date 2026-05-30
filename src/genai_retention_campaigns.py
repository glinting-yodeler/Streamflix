import pandas as pd
from sqlalchemy import text

from src.db import get_engine
from src.genai_client import generate_with_gemini


def safe_read_sql(query, engine):
    try:
        return pd.read_sql(query, engine)
    except Exception:
        return pd.DataFrame()


def local_campaign(row):
    user_id = row.get("user_id", "user")
    risk_level = row.get("risk_level", "High")
    risk_reason = row.get("risk_reason", "low engagement")
    title = row.get("title", "a recommended title")

    if risk_level == "High":
        return (
            f"We noticed you have not been watching as much recently. "
            f"{title} is a strong recommendation for you based on your profile. "
            f"Come back today and continue watching content selected for your interests."
        )

    return (
        f"Based on your recent activity, you may enjoy {title}. "
        f"Explore more titles selected around your viewing preferences."
    )


def main():
    engine = get_engine()

    df = safe_read_sql(
        """
        SELECT
            c.user_id,
            c.churn_probability,
            c.risk_level,
            c.risk_reason,
            c.recommended_action,
            c.country,
            c.subscription_plan,
            r.title,
            r.reason AS recommendation_reason,
            r.score
        FROM churn_predictions c
        LEFT JOIN recommendations r
            ON c.user_id = r.user_id
           AND r.rec_rank = 1
        WHERE c.risk_level IN ('High', 'Medium')
        ORDER BY c.churn_probability DESC
        LIMIT 30
        """,
        engine
    )

    if df.empty:
        print("No high/medium risk users found for campaign generation.")
        return

    rows = []

    for _, row in df.iterrows():
        fallback = local_campaign(row)

        prompt = f"""
You are a CRM and lifecycle marketing assistant for an OTT streaming platform.

Create a short personalized retention campaign message.

Rules:
- Keep it friendly and professional.
- Maximum 45 words.
- Do not mention internal churn probability.
- Use the recommended title naturally.
- Avoid sounding creepy or overly personalized.
- The message should make the user want to return and watch.

User context:
- User ID: {row.get("user_id")}
- Country: {row.get("country")}
- Subscription plan: {row.get("subscription_plan")}
- Risk level: {row.get("risk_level")}
- Risk reason: {row.get("risk_reason")}
- Recommended title: {row.get("title")}
- Recommendation reason: {row.get("recommendation_reason")}
"""

        message = generate_with_gemini(prompt, fallback)

        rows.append({
            "user_id": row.get("user_id"),
            "risk_level": row.get("risk_level"),
            "churn_probability": row.get("churn_probability"),
            "risk_reason": row.get("risk_reason"),
            "recommended_title": row.get("title"),
            "campaign_message": message,
            "campaign_channel": "Push Notification / WhatsApp",
            "country": row.get("country"),
        })

    out = pd.DataFrame(rows)

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS genai_retention_campaigns (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                risk_level TEXT,
                churn_probability DOUBLE PRECISION,
                risk_reason TEXT,
                recommended_title TEXT,
                campaign_message TEXT,
                campaign_channel TEXT,
                country TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        conn.execute(text("TRUNCATE TABLE genai_retention_campaigns"))

    out.to_sql("genai_retention_campaigns", engine, if_exists="append", index=False)

    print(f"Generated {len(out)} Gemini-powered retention campaigns.")


if __name__ == "__main__":
    main()