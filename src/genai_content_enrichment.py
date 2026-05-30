import json
import pandas as pd
from sqlalchemy import text

from src.db import get_engine
from src.genai_client import generate_with_gemini


def local_metadata(row):
    title = row.get("title", "Unknown Title")
    genre = row.get("genre", "General")
    language = row.get("language", "Unknown")

    return {
        "short_summary": f"{title} is a {language} {genre} title designed for viewers interested in engaging OTT content.",
        "mood_tags": [genre.lower(), "engaging", "streaming"],
        "theme_tags": ["entertainment", "storytelling", "regional appeal"],
        "search_keywords": [title.lower(), genre.lower(), language.lower()],
        "audience_segment": f"{genre} fans and {language} content viewers",
        "recommendation_blurb": f"Recommended for viewers who enjoy {genre} content in {language}.",
    }


def parse_json_or_fallback(text, fallback):
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except Exception:
        return fallback


def main():
    engine = get_engine()

    content = pd.read_sql(
        """
        SELECT *
        FROM content_dim
        LIMIT 50
        """,
        engine
    )

    if content.empty:
        print("No content found for metadata enrichment.")
        return

    rows = []

    for _, row in content.iterrows():
        fallback_dict = local_metadata(row)
        fallback_text = json.dumps(fallback_dict)

        prompt = f"""
You are a GenAI metadata enrichment assistant for an OTT streaming platform.

Generate JSON metadata for the content item below.

Return ONLY valid JSON with these keys:
- short_summary: string
- mood_tags: list of 3 to 5 strings
- theme_tags: list of 3 to 5 strings
- search_keywords: list of 5 to 8 strings
- audience_segment: string
- recommendation_blurb: string

Content:
Title: {row.get("title")}
Genre: {row.get("genre")}
Language: {row.get("language")}
Description: {row.get("description")}
Release year: {row.get("release_year")}
"""

        generated = generate_with_gemini(prompt, fallback_text)
        parsed = parse_json_or_fallback(generated, fallback_dict)

        rows.append({
            "content_id": row.get("content_id"),
            "title": row.get("title"),
            "short_summary": parsed.get("short_summary", ""),
            "mood_tags": ", ".join(parsed.get("mood_tags", [])),
            "theme_tags": ", ".join(parsed.get("theme_tags", [])),
            "search_keywords": ", ".join(parsed.get("search_keywords", [])),
            "audience_segment": parsed.get("audience_segment", ""),
            "recommendation_blurb": parsed.get("recommendation_blurb", ""),
        })

    out = pd.DataFrame(rows)

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS genai_content_enrichment (
                id SERIAL PRIMARY KEY,
                content_id TEXT,
                title TEXT,
                short_summary TEXT,
                mood_tags TEXT,
                theme_tags TEXT,
                search_keywords TEXT,
                audience_segment TEXT,
                recommendation_blurb TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        conn.execute(text("TRUNCATE TABLE genai_content_enrichment"))

    out.to_sql("genai_content_enrichment", engine, if_exists="append", index=False)

    print(f"Generated Gemini-powered metadata enrichment for {len(out)} titles.")


if __name__ == "__main__":
    main()