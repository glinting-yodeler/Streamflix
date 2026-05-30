import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import text

from src.db import get_engine


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StreamFlix DE | OTT Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM CSS
# ============================================================

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

        :root {
            --background: #0A0A0A;
            --foreground: #FAFAFA;
            --muted: #1A1A1A;
            --muted-foreground: #737373;
            --accent: #FF3D00;
            --accent-foreground: #0A0A0A;
            --border: #262626;
            --input: #1A1A1A;
            --card: #0F0F0F;
            --card-foreground: #FAFAFA;
            --ring: #FF3D00;
        }

        html, body, [class*="css"] {
            font-family: "Inter", system-ui, sans-serif;
            letter-spacing: -0.01em;
        }

        .stApp {
            background-color: var(--background);
            color: var(--foreground);
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            opacity: 0.035;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 250 250' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
        }

        .main .block-container {
            padding-top: 2rem;
            padding-left: 3.5rem;
            padding-right: 3.5rem;
            max-width: 1440px;
        }

        section[data-testid="stSidebar"] {
            background: var(--background);
            border-right: 1px solid var(--border);
        }

        section[data-testid="stSidebar"] * {
            color: var(--foreground);
        }

        section[data-testid="stSidebar"] [role="radiogroup"] label {
            border-bottom: 1px solid var(--border);
            padding: 0.9rem 0;
            transition: 150ms ease;
        }

        section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
            color: var(--accent) !important;
        }

        div[data-testid="stMetric"] {
            background: transparent;
            border-top: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
            padding: 1.3rem 0;
            box-shadow: none;
        }

        div[data-testid="stMetric"] label {
            color: var(--muted-foreground) !important;
            font-family: "JetBrains Mono", monospace !important;
            font-size: 0.72rem !important;
            text-transform: uppercase;
            letter-spacing: 0.14em;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--foreground) !important;
            font-family: "Inter Tight", sans-serif !important;
            font-size: 2.65rem !important;
            font-weight: 900 !important;
            letter-spacing: -0.06em;
            line-height: 1;
        }

        .hero {
            border-top: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
            padding: 4.2rem 0 3.4rem 0;
            margin-bottom: 3.25rem;
            position: relative;
        }

        .eyebrow {
            font-family: "JetBrains Mono", monospace;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.75rem;
            font-weight: 700;
            margin-bottom: 1.1rem;
        }

        .hero-title {
            font-family: "Inter Tight", sans-serif;
            font-size: clamp(4rem, 10vw, 9.5rem);
            line-height: 0.9;
            font-weight: 900;
            letter-spacing: -0.065em;
            max-width: 1150px;
            margin: 0;
        }

        .hero-title .accent {
            color: var(--accent);
        }

        .hero-subtitle {
            max-width: 760px;
            margin-top: 1.6rem;
            color: var(--muted-foreground);
            font-size: 1.15rem;
            line-height: 1.75;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: 1fr 320px;
            gap: 2.5rem;
            align-items: end;
        }

        .stack-list {
            border-left: 2px solid var(--accent);
            padding-left: 1rem;
            font-family: "JetBrains Mono", monospace;
            color: var(--muted-foreground);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-size: 0.74rem;
            line-height: 2;
        }

        .section-kicker {
            color: var(--accent);
            font-family: "JetBrains Mono", monospace;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.72rem;
            font-weight: 700;
            margin-top: 2.2rem;
            margin-bottom: 0.8rem;
        }

        .section-title {
            font-family: "Inter Tight", sans-serif;
            font-size: clamp(2.4rem, 5vw, 5.25rem);
            font-weight: 900;
            letter-spacing: -0.06em;
            line-height: 0.95;
            margin-bottom: 1rem;
        }

        .section-caption {
            color: var(--muted-foreground);
            font-size: 1rem;
            line-height: 1.7;
            max-width: 760px;
            margin-bottom: 1.5rem;
        }

        .rule {
            height: 1px;
            background: var(--border);
            margin: 2.5rem 0;
        }

        .editorial-card {
            background: transparent;
            border-top: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
            padding: 1.5rem 0;
            margin-bottom: 1.5rem;
            position: relative;
        }

        .editorial-card::before {
            content: "";
            position: absolute;
            top: -1px;
            left: 0;
            width: 64px;
            height: 2px;
            background: var(--accent);
        }

        .insight-card {
            background: var(--card);
            border: 1px solid var(--border);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            position: relative;
        }

        .insight-card::before {
            content: "";
            position: absolute;
            top: -1px;
            left: -1px;
            width: 72px;
            height: 3px;
            background: var(--accent);
        }

        .insight-card h3,
        .insight-card h2,
        .genai-card h2,
        .genai-card h3 {
            font-family: "Inter Tight", sans-serif;
            letter-spacing: -0.04em;
            line-height: 1;
        }

        .genai-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-left: 4px solid var(--accent);
            padding: 1.6rem;
            margin-bottom: 1.5rem;
        }

        .pull-quote {
            font-family: "Playfair Display", Georgia, serif;
            font-size: clamp(1.8rem, 3vw, 3rem);
            line-height: 1.12;
            letter-spacing: -0.03em;
            color: var(--foreground);
            border-left: 3px solid var(--accent);
            padding-left: 1rem;
            margin: 1rem 0;
        }

        .muted {
            color: var(--muted-foreground);
        }

        .mono-label {
            font-family: "JetBrains Mono", monospace;
            color: var(--muted-foreground);
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.72rem;
            font-weight: 700;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 1.2rem;
        }

        .chip {
            border: 1px solid var(--border);
            padding: 0.55rem 0.75rem;
            font-family: "JetBrains Mono", monospace;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.68rem;
            color: var(--muted-foreground);
        }

        .chip-accent {
            color: var(--accent);
            border-color: var(--accent);
        }

        .empty-state {
            border: 1px solid var(--border);
            background: var(--card);
            padding: 2rem;
            margin: 1.4rem 0;
        }

        .empty-state h3 {
            font-family: "Inter Tight", sans-serif;
            font-size: 2rem;
            letter-spacing: -0.05em;
            margin: 0 0 0.5rem 0;
        }

        .empty-state p {
            color: var(--muted-foreground);
            margin: 0;
            line-height: 1.6;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border);
        }

        div[data-testid="stAlert"] {
            border-radius: 0 !important;
            border: 1px solid var(--border);
        }

        .stButton > button {
            border-radius: 0 !important;
            border: 1px solid var(--foreground);
            background: transparent;
            color: var(--foreground);
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-family: "JetBrains Mono", monospace;
            transition: 150ms ease;
        }

        .stButton > button:hover {
            background: var(--foreground);
            color: var(--background);
            border-color: var(--foreground);
        }

        input, textarea {
            border-radius: 0 !important;
            background: var(--input) !important;
            border: 1px solid var(--border) !important;
            color: var(--foreground) !important;
        }

        .footer-note {
            border-top: 1px solid var(--border);
            margin-top: 3rem;
            padding-top: 1.2rem;
            color: var(--muted-foreground);
            font-family: "JetBrains Mono", monospace;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.68rem;
        }

        @media (max-width: 900px) {
            .main .block-container {
                padding-left: 1.4rem;
                padding-right: 1.4rem;
            }

            .hero-grid {
                grid-template-columns: 1fr;
            }

            .hero-title {
                font-size: clamp(3.4rem, 16vw, 6rem);
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

@st.cache_data(ttl=30)
def load_table(table):
    engine = get_engine()
    try:
        return pd.read_sql(f"SELECT * FROM {table}", engine)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=30)
def run_safe_query(query):
    engine = get_engine()
    try:
        with engine.begin() as conn:
            return pd.read_sql(text(query), conn)
    except Exception as exc:
        return pd.DataFrame({"error": [str(exc)]})


def format_number(value):
    try:
        value = float(value)
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        if value >= 1_000:
            return f"{value / 1_000:.1f}K"
        return f"{value:,.0f}"
    except Exception:
        return "0"


def format_money(value):
    try:
        return f"PKR {float(value):,.0f}"
    except Exception:
        return "PKR 0"


def page_header(kicker, title, subtitle, chips=None):
    chip_html = ""
    if chips:
        chip_html = '<div class="chip-row">' + "".join(
            f'<span class="chip">{chip}</span>' for chip in chips
        ) + "</div>"

    st.markdown(
        f"""
        <div class="editorial-card">
            <div class="section-kicker">{kicker}</div>
            <div class="section-title">{title}</div>
            <div class="section-caption">{subtitle}</div>
            {chip_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(title, message):
    st.markdown(
        f"""
        <div class="empty-state">
            <h3>{title}</h3>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title, body, kicker="Insight"):
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="mono-label">{kicker}</div>
            <h3>{title}</h3>
            <p class="muted">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def genai_card(title, body, subtitle=None):
    subtitle_html = f'<p class="mono-label">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="genai-card">
            {subtitle_html}
            <h2>{title}</h2>
            <div style="white-space: pre-wrap; line-height: 1.75; color: rgba(250,250,250,0.9);">
            {body}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def plotly_theme(fig, height=420):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA", family="Inter"),
        margin=dict(l=20, r=20, t=54, b=24),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#FAFAFA")),
        title=dict(font=dict(size=18, family="Inter Tight", color="#FAFAFA")),
        xaxis=dict(
            gridcolor="rgba(250,250,250,0.06)",
            zerolinecolor="rgba(250,250,250,0.08)",
            linecolor="#262626",
            tickfont=dict(color="#737373"),
        ),
        yaxis=dict(
            gridcolor="rgba(250,250,250,0.06)",
            zerolinecolor="rgba(250,250,250,0.08)",
            linecolor="#262626",
            tickfont=dict(color="#737373"),
        ),
    )
    return fig


def classify_question_to_sql(question):
    q = question.lower().strip()

    if "highest churn" in q or "high risk" in q or "churn risk" in q:
        return """
        SELECT user_id, churn_probability, risk_level, risk_reason, recommended_action, country
        FROM churn_predictions
        ORDER BY churn_probability DESC
        LIMIT 10;
        """

    if "top content" in q or "highest watch" in q or "most watched" in q:
        return """
        SELECT title, genre, language, total_watch_minutes, unique_viewers, avg_completion_rate, popularity_score
        FROM content_performance
        ORDER BY total_watch_minutes DESC
        LIMIT 10;
        """

    if "completion" in q and "content" in q:
        return """
        SELECT title, genre, language, avg_completion_rate, total_watch_minutes, unique_viewers
        FROM content_performance
        ORDER BY avg_completion_rate DESC
        LIMIT 10;
        """

    if "country" in q or "countries" in q or "region" in q:
        return """
        SELECT country, total_watch_minutes, active_users, avg_completion_rate, total_revenue
        FROM country_metrics
        ORDER BY total_watch_minutes DESC
        LIMIT 10;
        """

    if "device" in q or "buffer" in q or "playback" in q or "quality" in q:
        return """
        SELECT device, total_buffering_events, avg_quality_score, affected_users
        FROM device_quality_metrics
        ORDER BY total_buffering_events DESC
        LIMIT 10;
        """

    if "recommend" in q or "recommendation" in q:
        return """
        SELECT user_id, rec_rank, title, recommendation_type, score, confidence, reason
        FROM recommendations
        ORDER BY user_id, rec_rank
        LIMIT 20;
        """

    if "revenue" in q or "payment" in q or "failures" in q:
        return """
        SELECT metric_date, active_users, total_watch_minutes, total_revenue, payment_failures
        FROM daily_metrics
        ORDER BY metric_date DESC
        LIMIT 10;
        """

    if "raw" in q or "events" in q or "event type" in q:
        return """
        SELECT event_type, COUNT(*) AS event_count
        FROM raw_events
        GROUP BY event_type
        ORDER BY event_count DESC;
        """

    return """
    SELECT metric_date, active_users, total_watch_minutes, avg_completion_rate, total_revenue, payment_failures
    FROM daily_metrics
    ORDER BY metric_date DESC
    LIMIT 10;
    """


# ============================================================
# LOAD DATA
# ============================================================

daily = load_table("daily_metrics")
country = load_table("country_metrics")
content = load_table("content_performance")
device = load_table("device_quality_metrics")

churn = load_table("churn_predictions")
churn_metrics = load_table("churn_model_metrics")
churn_importance = load_table("churn_feature_importance")

recs = load_table("recommendations")
recommendation_metrics = load_table("recommendation_model_metrics")

summaries = load_table("executive_summaries")
retention_campaigns = load_table("genai_retention_campaigns")
content_enrichment = load_table("genai_content_enrichment")

raw = load_table("raw_events")
clean_watch = load_table("clean_watch_events")
clean_business = load_table("clean_business_events")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## STREAMFLIX")
    st.markdown(
        """
        <div class="mono-label">Data Engineering × ML × GenAI</div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Content Performance",
            "Churn Intelligence",
            "Recommendation Engine",
            "GenAI Studio",
            "Playback Quality",
            "Pipeline Health",
            "Executive Summary",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### STACK")
    st.markdown(
        """
        <div class="chip-row">
            <span class="chip chip-accent">Kafka</span>
            <span class="chip">Postgres</span>
            <span class="chip">Airflow</span>
            <span class="chip">Sklearn</span>
            <span class="chip">Gemini</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    if not raw.empty:
        st.markdown('<div class="mono-label" style="color:#FF3D00;">● Data Online</div>', unsafe_allow_html=True)
        st.caption(f"{len(raw):,} raw events loaded")
    else:
        st.markdown('<div class="mono-label">● Waiting For Events</div>', unsafe_allow_html=True)
        st.caption("Run producer, consumer, then pipeline.")


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <section class="hero">
        <div class="hero-grid">
            <div>
                <div class="eyebrow">OTT intelligence system / STARZPLAY-inspired</div>
                <h1 class="hero-title">STREAMING<br><span class="accent">DATA</span><br>COMMAND.</h1>
                <p class="hero-subtitle">
                    A bold analytics interface for a Kafka-powered OTT platform:
                    ingestion, warehouse modeling, churn intelligence, hybrid recommendations,
                    Gemini-powered GenAI insights, and pipeline observability.
                </p>
            </div>
            <div class="stack-list">
                Redpanda event stream<br>
                PostgreSQL warehouse<br>
                Airflow orchestration<br>
                Churn prediction<br>
                Hybrid recommender<br>
                Gemini GenAI studio
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":
    page_header(
        "01 / Executive Overview",
        "THE PLATFORM AT A GLANCE.",
        "A leadership-level view of activity, revenue, engagement, and regional demand.",
        ["Watch time", "Revenue", "Completion", "Regional demand"],
    )

    if daily.empty:
        empty_state("No metrics yet", "Run producer + consumer, then run src.run_pipeline.")
    else:
        daily_sorted = daily.sort_values("metric_date")
        latest = daily_sorted.iloc[-1]

        active_users = latest.get("active_users", 0)
        total_watch_minutes = latest.get("total_watch_minutes", 0)
        avg_completion = latest.get("avg_completion_rate", 0)
        total_revenue = latest.get("total_revenue", 0)
        payment_failures = latest.get("payment_failures", 0)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Active Users", format_number(active_users))
        c2.metric("Watch Hours", f"{float(total_watch_minutes) / 60:,.1f}")
        c3.metric("Completion", f"{float(avg_completion):.1%}")
        c4.metric("Revenue", format_money(total_revenue))
        c5.metric("Failures", format_number(payment_failures))

        st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=daily_sorted["metric_date"],
                y=daily_sorted["total_watch_minutes"],
                mode="lines+markers",
                name="Watch Minutes",
                line=dict(width=3, color="#FF3D00"),
                marker=dict(size=7, color="#FAFAFA"),
            )
        )
        fig = plotly_theme(fig, height=430)
        fig.update_layout(title="Daily Watch Minutes")
        st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns([1.15, 0.85])

        with left:
            if not country.empty and "country" in country.columns:
                country_sorted = country.sort_values("total_watch_minutes", ascending=False)
                fig = px.bar(
                    country_sorted,
                    x="country",
                    y="total_watch_minutes",
                    text_auto=True,
                    title="Watch Time By Country",
                )
                fig.update_traces(marker_color="#FF3D00")
                fig = plotly_theme(fig)
                st.plotly_chart(fig, use_container_width=True)

        with right:
            best_country = "N/A"
            if not country.empty and "country" in country.columns:
                best_country = country.sort_values("total_watch_minutes", ascending=False).iloc[0]["country"]

            insight_card(
                "Regional demand is visible.",
                f"The strongest watch-time market is {best_country}. The platform currently shows {format_number(active_users)} active users and {float(total_watch_minutes) / 60:,.1f} watch hours. Completion rate sits at {float(avg_completion):.1%}, which acts as a content-market fit signal.",
                "Executive readout",
            )


# ============================================================
# CONTENT PERFORMANCE
# ============================================================

elif page == "Content Performance":
    page_header(
        "02 / Content Performance",
        "CONTENT IS THE PRODUCT.",
        "Understand what users actually complete, revisit, and spend time watching.",
        ["Catalog", "Completion", "Genre demand", "Viewer touchpoints"],
    )

    if content.empty:
        empty_state("No content metrics yet", "Run the analytics pipeline to build content_performance.")
    else:
        top_content = content.sort_values("popularity_score", ascending=False).head(1).iloc[0]
        total_titles = len(content)
        avg_completion = content["avg_completion_rate"].mean() if "avg_completion_rate" in content.columns else 0
        total_watch = content["total_watch_minutes"].sum() if "total_watch_minutes" in content.columns else 0
        unique_viewers = content["unique_viewers"].sum() if "unique_viewers" in content.columns else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Catalog Titles", format_number(total_titles))
        c2.metric("Watch Hours", f"{float(total_watch) / 60:,.1f}")
        c3.metric("Avg Completion", f"{float(avg_completion):.1%}")
        c4.metric("Touchpoints", format_number(unique_viewers))

        left, right = st.columns([1.25, 0.75])

        with left:
            chart_data = content.sort_values("total_watch_minutes", ascending=False).head(12)
            fig = px.bar(
                chart_data,
                x="title",
                y="total_watch_minutes",
                color="genre" if "genre" in chart_data.columns else None,
                title="Top Content By Watch Time",
            )
            fig.update_xaxes(tickangle=-35)
            fig = plotly_theme(fig, height=460)
            st.plotly_chart(fig, use_container_width=True)

        with right:
            insight_card(
                str(top_content.get("title", "N/A")),
                f"Genre: {top_content.get('genre', 'N/A')} · Language: {top_content.get('language', 'N/A')} · Popularity score: {top_content.get('popularity_score', 0):,.2f}. This is the leading title by the current scoring model.",
                "Top performing title",
            )

        fig2 = px.scatter(
            content,
            x="avg_completion_rate",
            y="total_watch_minutes",
            size="unique_viewers" if "unique_viewers" in content.columns else None,
            color="language" if "language" in content.columns else None,
            hover_name="title" if "title" in content.columns else None,
            title="Completion Rate vs Watch Time",
        )
        fig2 = plotly_theme(fig2, height=470)
        st.plotly_chart(fig2, use_container_width=True)

        show_cols = [
            col
            for col in [
                "title",
                "genre",
                "language",
                "total_watch_minutes",
                "unique_viewers",
                "avg_completion_rate",
                "popularity_score",
            ]
            if col in content.columns
        ]
        st.dataframe(
            content.sort_values("popularity_score", ascending=False)[show_cols].head(30),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# CHURN INTELLIGENCE
# ============================================================

elif page == "Churn Intelligence":
    page_header(
        "03 / Churn Intelligence",
        "RETENTION BEFORE CANCELLATION.",
        "A machine-learning layer that turns behavioral signals into churn risk, reasons, and actions.",
        ["Model comparison", "Risk scoring", "Feature importance", "Retention actions"],
    )

    if churn.empty:
        empty_state("No churn predictions yet", "Run the ML pipeline to generate churn_predictions.")
    else:
        high_risk = len(churn[churn["risk_level"].str.lower() == "high"]) if "risk_level" in churn.columns else 0
        medium_risk = len(churn[churn["risk_level"].str.lower() == "medium"]) if "risk_level" in churn.columns else 0
        low_risk = len(churn[churn["risk_level"].str.lower() == "low"]) if "risk_level" in churn.columns else 0
        avg_churn_prob = churn["churn_probability"].mean() if "churn_probability" in churn.columns else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("High Risk", format_number(high_risk))
        c2.metric("Medium Risk", format_number(medium_risk))
        c3.metric("Low Risk", format_number(low_risk))
        c4.metric("Avg Risk", f"{float(avg_churn_prob):.1%}")

        if not churn_metrics.empty:
            selected = churn_metrics[churn_metrics["selected_model"] == True]
            if selected.empty:
                selected = churn_metrics.sort_values("auc", ascending=False).head(1)

            best = selected.iloc[0]

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Best Model", str(best.get("model_name", "N/A")).replace("_", " ").title())
            m2.metric("Accuracy", f"{float(best.get('accuracy', 0)):.1%}")
            m3.metric("Precision", f"{float(best.get('precision_score', 0)):.1%}")
            m4.metric("Recall", f"{float(best.get('recall', 0)):.1%}")
            m5.metric("AUC", f"{float(best.get('auc', 0)):.3f}")

            left, right = st.columns([1.15, 0.85])

            with left:
                metric_cols = ["model_name", "accuracy", "precision_score", "recall", "f1", "auc", "selected_model"]
                existing_cols = [c for c in metric_cols if c in churn_metrics.columns]
                model_table = churn_metrics[existing_cols].copy()

                for col in ["accuracy", "precision_score", "recall", "f1"]:
                    if col in model_table.columns:
                        model_table[col] = model_table[col].map(lambda x: f"{float(x):.1%}")
                if "auc" in model_table.columns:
                    model_table["auc"] = model_table["auc"].map(lambda x: f"{float(x):.3f}")

                st.markdown('<div class="section-kicker">Candidate models</div>', unsafe_allow_html=True)
                st.dataframe(model_table, use_container_width=True, hide_index=True)

            with right:
                tn = int(best.get("true_negatives", 0))
                fp = int(best.get("false_positives", 0))
                fn = int(best.get("false_negatives", 0))
                tp = int(best.get("true_positives", 0))

                cm_df = pd.DataFrame(
                    [[tn, fp], [fn, tp]],
                    index=["Actual: Not Churn", "Actual: Churn"],
                    columns=["Pred: Not Churn", "Pred: Churn"],
                )

                fig_cm = px.imshow(cm_df, text_auto=True, aspect="auto", title="Confusion Matrix")
                fig_cm = plotly_theme(fig_cm, height=330)
                st.plotly_chart(fig_cm, use_container_width=True)

        left, right = st.columns([0.9, 1.1])

        with left:
            if "risk_level" in churn.columns:
                risk_counts = churn["risk_level"].value_counts().reset_index()
                risk_counts.columns = ["risk_level", "users"]
                fig = px.pie(risk_counts, names="risk_level", values="users", hole=0.58, title="Risk Distribution")
                fig = plotly_theme(fig, height=420)
                st.plotly_chart(fig, use_container_width=True)

        with right:
            top_risk = churn.sort_values("churn_probability", ascending=False).head(12)
            fig = px.bar(
                top_risk,
                x="user_id",
                y="churn_probability",
                color="risk_level" if "risk_level" in top_risk.columns else None,
                title="Highest-Risk Users",
            )
            fig.update_yaxes(tickformat=".0%")
            fig = plotly_theme(fig, height=420)
            st.plotly_chart(fig, use_container_width=True)

        if not churn_importance.empty:
            imp = churn_importance.sort_values("importance", ascending=False).head(15)
            fig = px.bar(
                imp.sort_values("importance"),
                x="importance",
                y="feature_name",
                orientation="h",
                title="Top Churn Drivers",
            )
            fig.update_traces(marker_color="#FF3D00")
            fig = plotly_theme(fig, height=500)
            st.plotly_chart(fig, use_container_width=True)

        top_users = churn.sort_values("churn_probability", ascending=False).head(40).copy()
        if "churn_probability" in top_users.columns:
            top_users["churn_probability"] = top_users["churn_probability"].map(lambda x: f"{float(x):.1%}")

        preferred_cols = [
            "user_id",
            "churn_probability",
            "risk_level",
            "risk_reason",
            "recommended_action",
            "country",
            "subscription_plan",
            "days_since_last_watch",
            "total_watch_minutes",
            "avg_completion_rate",
            "buffering_count",
            "payment_failed_count",
            "engagement_score",
            "friction_score",
        ]
        existing_cols = [c for c in preferred_cols if c in top_users.columns]
        st.markdown('<div class="section-kicker">Retention action queue</div>', unsafe_allow_html=True)
        st.dataframe(top_users[existing_cols], use_container_width=True, hide_index=True)


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

elif page == "Recommendation Engine":
    page_header(
        "04 / Recommendation Engine",
        "PERSONALIZATION IS RETENTION.",
        "Hybrid recommendation intelligence using collaborative filtering, content similarity, country trends, and popularity.",
        ["User CF", "Item CF", "SVD", "TF-IDF", "Country trending"],
    )

    if recs.empty:
        empty_state("No recommendations yet", "Run the recommendation pipeline to populate the recommendations table.")
    else:
        total_recs = len(recs)
        total_users = recs["user_id"].nunique() if "user_id" in recs.columns else 0
        avg_score = recs["score"].mean() if "score" in recs.columns else 0
        catalog_coverage = 0

        if not recommendation_metrics.empty and "catalog_coverage" in recommendation_metrics.columns:
            catalog_coverage = recommendation_metrics.sort_values("generated_at").iloc[-1].get("catalog_coverage", 0)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Recommended", format_number(total_recs))
        c2.metric("Users Covered", format_number(total_users))
        c3.metric("Hybrid Score", f"{float(avg_score):.3f}")
        c4.metric("Catalog", f"{float(catalog_coverage):.1%}")

        if not recommendation_metrics.empty:
            latest_metrics = recommendation_metrics.sort_values("generated_at").iloc[-1]
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Model CF", "Enabled" if latest_metrics.get("model_based_enabled", False) else "Off")
            s2.metric("User CF", "Enabled" if latest_metrics.get("user_cf_enabled", False) else "Off")
            s3.metric("Item CF", "Enabled" if latest_metrics.get("item_cf_enabled", False) else "Off")
            s4.metric("Content", "Enabled" if latest_metrics.get("content_based_enabled", False) else "Off")

        users = sorted(recs["user_id"].unique()) if "user_id" in recs.columns else []
        selected_user = st.selectbox("Select user", users)

        user_recs = recs[recs["user_id"] == selected_user].sort_values("score", ascending=False)

        left, right = st.columns([1.05, 0.95])

        with left:
            show_cols = ["rec_rank", "title", "recommendation_type", "reason", "score", "confidence", "content_genre", "content_language"]
            existing_cols = [col for col in show_cols if col in user_recs.columns]
            display_recs = user_recs[existing_cols].copy()

            for col in ["score", "confidence"]:
                if col in display_recs.columns:
                    display_recs[col] = display_recs[col].map(lambda x: f"{float(x):.3f}")

            st.markdown('<div class="section-kicker">Top personalized recommendations</div>', unsafe_allow_html=True)
            st.dataframe(display_recs, use_container_width=True, hide_index=True)

        with right:
            if not user_recs.empty:
                best = user_recs.iloc[0]
                insight_card(
                    str(best.get("title", "N/A")),
                    f"Method: {best.get('recommendation_type', 'Hybrid recommendation')}. Score: {float(best.get('score', 0)):.3f}. Confidence: {float(best.get('confidence', 0)):.1%}. {best.get('reason', '')}",
                    "Best next watch",
                )

                if "user_profile" in best:
                    st.markdown(
                        f"""
                        <div class="insight-card">
                            <div class="mono-label">User profile</div>
                            <p class="muted">{best.get("user_profile", "")}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        score_cols = ["model_cf_score", "user_cf_score", "item_cf_score", "content_score", "country_score", "popularity_score"]
        available_score_cols = [col for col in score_cols if col in user_recs.columns]

        if available_score_cols and not user_recs.empty:
            breakdown_rows = []
            for _, row in user_recs.head(5).iterrows():
                title = row.get("title", "Unknown")
                for col in available_score_cols:
                    breakdown_rows.append(
                        {
                            "title": title,
                            "signal": col.replace("_", " ").replace("cf", "CF").title(),
                            "score": float(row.get(col, 0)),
                        }
                    )

            breakdown_df = pd.DataFrame(breakdown_rows)
            fig = px.bar(
                breakdown_df,
                x="title",
                y="score",
                color="signal",
                barmode="group",
                title="Hybrid Signal Breakdown",
            )
            fig.update_xaxes(tickangle=-25)
            fig = plotly_theme(fig, height=500)
            st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns([1, 1])

        with col_a:
            if "recommendation_type" in recs.columns:
                method_counts = recs["recommendation_type"].value_counts().reset_index()
                method_counts.columns = ["recommendation_type", "count"]
                fig = px.pie(method_counts, names="recommendation_type", values="count", hole=0.55, title="Dominant Method")
                fig = plotly_theme(fig, height=430)
                st.plotly_chart(fig, use_container_width=True)

        with col_b:
            if "title" in recs.columns:
                popular_recs = recs["title"].value_counts().head(10).reset_index()
                popular_recs.columns = ["title", "recommendation_count"]
                fig = px.bar(popular_recs, x="recommendation_count", y="title", orientation="h", title="Most Recommended Titles")
                fig.update_traces(marker_color="#FF3D00")
                fig = plotly_theme(fig, height=430)
                st.plotly_chart(fig, use_container_width=True)


# ============================================================
# GENAI STUDIO
# ============================================================

elif page == "GenAI Studio":
    page_header(
        "05 / GenAI Studio",
        "WAREHOUSE DATA, MADE VERBAL.",
        "Gemini converts structured metrics into executive briefs, retention campaigns, metadata enrichment, and safe analytics answers.",
        ["Gemini API", "Executive brief", "Campaigns", "Metadata", "SQL copilot"],
    )

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Briefs", format_number(len(summaries)))
    g2.metric("Campaigns", format_number(len(retention_campaigns)))
    g3.metric("Enriched", format_number(len(content_enrichment)))
    g4.metric("Provider", "Gemini")

    genai_tab_1, genai_tab_2, genai_tab_3, genai_tab_4 = st.tabs(
        ["Executive Brief", "Retention Campaigns", "Content Enrichment", "Analytics Copilot"]
    )

    with genai_tab_1:
        if summaries.empty:
            empty_state("No executive summary found", "Run: python -m src.genai_summary")
        else:
            latest = summaries.sort_values("generated_at").iloc[-1]
            genai_card(
                "Daily OTT Intelligence Brief",
                latest.get("summary_text", ""),
                f"Generated for {latest.get('summary_date', 'latest date')}",
            )

            st.markdown(
                """
                <div class="pull-quote">
                GenAI is not replacing analytics here. It is translating warehouse metrics into leadership language.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with genai_tab_2:
        if retention_campaigns.empty:
            empty_state("No retention campaigns found", "Run: python -m src.genai_retention_campaigns")
        else:
            high_count = len(retention_campaigns[retention_campaigns["risk_level"].str.lower() == "high"]) if "risk_level" in retention_campaigns.columns else 0
            medium_count = len(retention_campaigns[retention_campaigns["risk_level"].str.lower() == "medium"]) if "risk_level" in retention_campaigns.columns else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("High Risk", format_number(high_count))
            c2.metric("Medium Risk", format_number(medium_count))
            c3.metric("Channels", "Push / WhatsApp")

            selected_campaign_user = st.selectbox(
                "Inspect generated campaign",
                sorted(retention_campaigns["user_id"].unique()) if "user_id" in retention_campaigns.columns else [],
            )

            user_campaign = retention_campaigns[retention_campaigns["user_id"] == selected_campaign_user].head(1)

            if not user_campaign.empty:
                row = user_campaign.iloc[0]
                genai_card(
                    f"Campaign for {row.get('user_id', 'N/A')}",
                    row.get("campaign_message", ""),
                    f"Risk: {row.get('risk_level', 'N/A')} / Title: {row.get('recommended_title', 'N/A')}",
                )

            show_cols = [
                "user_id",
                "risk_level",
                "churn_probability",
                "risk_reason",
                "recommended_title",
                "campaign_message",
                "campaign_channel",
                "country",
            ]
            existing_cols = [c for c in show_cols if c in retention_campaigns.columns]
            display_campaigns = retention_campaigns[existing_cols].copy()

            if "churn_probability" in display_campaigns.columns:
                display_campaigns["churn_probability"] = display_campaigns["churn_probability"].map(lambda x: f"{float(x):.1%}")

            st.dataframe(display_campaigns, use_container_width=True, hide_index=True)

    with genai_tab_3:
        if content_enrichment.empty:
            empty_state("No enriched metadata found", "Run: python -m src.genai_content_enrichment")
        else:
            e1, e2, e3 = st.columns(3)
            e1.metric("Enriched Titles", format_number(len(content_enrichment)))
            e2.metric("Metadata Fields", "6")
            e3.metric("Use Cases", "Search + Discovery")

            selected_title = st.selectbox(
                "Select enriched title",
                sorted(content_enrichment["title"].dropna().unique()) if "title" in content_enrichment.columns else [],
            )

            title_row = content_enrichment[content_enrichment["title"] == selected_title].head(1)

            if not title_row.empty:
                row = title_row.iloc[0]
                genai_card(
                    row.get("title", "N/A"),
                    f"""Short Summary:
{row.get("short_summary", "")}

Mood Tags:
{row.get("mood_tags", "")}

Theme Tags:
{row.get("theme_tags", "")}

Search Keywords:
{row.get("search_keywords", "")}

Audience Segment:
{row.get("audience_segment", "")}

Recommendation Blurb:
{row.get("recommendation_blurb", "")}
""",
                    "Gemini metadata enrichment",
                )

            show_cols = [
                "title",
                "short_summary",
                "mood_tags",
                "theme_tags",
                "search_keywords",
                "audience_segment",
                "recommendation_blurb",
            ]
            existing_cols = [c for c in show_cols if c in content_enrichment.columns]
            st.dataframe(content_enrichment[existing_cols], use_container_width=True, hide_index=True)

    with genai_tab_4:
        example_questions = [
            "Which users are at highest churn risk?",
            "Which content has the highest watch time?",
            "Which countries have the most engagement?",
            "Which devices have the worst playback quality?",
            "Show top recommendations.",
            "Show revenue and payment failures.",
            "Show raw event type distribution.",
        ]

        selected_question = st.selectbox("Try an example question", example_questions)
        custom_question = st.text_input("Or ask your own analytics question", value=selected_question)

        generated_sql = classify_question_to_sql(custom_question)

        st.markdown('<div class="section-kicker">Generated SQL</div>', unsafe_allow_html=True)
        st.code(generated_sql.strip(), language="sql")

        if st.button("Run Copilot Query"):
            result = run_safe_query(generated_sql)
            st.markdown('<div class="section-kicker">Copilot answer</div>', unsafe_allow_html=True)

            if "error" in result.columns:
                st.error(result["error"].iloc[0])
            else:
                st.dataframe(result, use_container_width=True, hide_index=True)

                if not result.empty:
                    insight_card(
                        "Safe warehouse answer.",
                        f"The copilot found {len(result)} matching records using a safe read-only SQL template. This demonstrates natural-language analytics without exposing arbitrary SQL execution.",
                        "AI analytics copilot",
                    )


# ============================================================
# PLAYBACK QUALITY
# ============================================================

elif page == "Playback Quality":
    page_header(
        "06 / Playback Quality",
        "FRICTION KILLS RETENTION.",
        "Buffering and device quality signals help explain experience-driven churn.",
        ["Buffering", "Quality score", "Device friction", "Retention risk"],
    )

    if device.empty:
        empty_state("No playback metrics yet", "Run the pipeline to create device_quality_metrics.")
    else:
        total_buffering = device["total_buffering_events"].sum() if "total_buffering_events" in device.columns else 0
        avg_quality = device["avg_quality_score"].mean() if "avg_quality_score" in device.columns else 0
        worst_device = "N/A"

        if "total_buffering_events" in device.columns and "device" in device.columns:
            worst_device = device.sort_values("total_buffering_events", ascending=False).iloc[0]["device"]

        c1, c2, c3 = st.columns(3)
        c1.metric("Buffering", format_number(total_buffering))
        c2.metric("Quality", f"{float(avg_quality):.2f}")
        c3.metric("Worst Device", worst_device)

        left, right = st.columns(2)

        with left:
            fig = px.bar(
                device.sort_values("total_buffering_events", ascending=False),
                x="device",
                y="total_buffering_events",
                title="Buffering Events By Device",
            )
            fig.update_traces(marker_color="#FF3D00")
            fig = plotly_theme(fig, height=430)
            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig2 = px.bar(
                device.sort_values("avg_quality_score", ascending=True),
                x="device",
                y="avg_quality_score",
                title="Average Quality Score By Device",
            )
            fig2 = plotly_theme(fig2, height=430)
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(device.sort_values("total_buffering_events", ascending=False), use_container_width=True, hide_index=True)

        insight_card(
            "Playback quality is a churn signal.",
            f"{worst_device} currently has the highest buffering load. In an OTT platform, device-level playback friction can lower completion rates and increase cancellation risk.",
            "Experience risk",
        )


# ============================================================
# PIPELINE HEALTH
# ============================================================

elif page == "Pipeline Health":
    page_header(
        "07 / Pipeline Health",
        "THE DATA MACHINE.",
        "A control-room view of Kafka ingestion, cleaned tables, event distribution, and the flow into ML and GenAI.",
        ["Kafka", "Raw events", "Cleaned events", "Airflow", "Warehouse"],
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Raw Events", format_number(len(raw)))
    c2.metric("Clean Watch", format_number(len(clean_watch)))
    c3.metric("Clean Business", format_number(len(clean_business)))
    c4.metric("Tables", "13+")

    if raw.empty:
        empty_state("No raw events found", "Start Kafka producer and consumer to load raw events into PostgreSQL.")
    else:
        left, right = st.columns([1, 1])

        with left:
            if "event_type" in raw.columns:
                counts = raw["event_type"].value_counts().reset_index()
                counts.columns = ["event_type", "count"]
                fig = px.bar(counts, x="event_type", y="count", title="Raw Event Type Distribution")
                fig.update_xaxes(tickangle=-35)
                fig.update_traces(marker_color="#FF3D00")
                fig = plotly_theme(fig, height=430)
                st.plotly_chart(fig, use_container_width=True)

        with right:
            st.markdown(
                """
                <div class="insight-card">
                    <div class="mono-label">Pipeline flow</div>
                    <p><b>01</b> Python producer creates OTT events</p>
                    <p><b>02</b> Redpanda streams Kafka-compatible events</p>
                    <p><b>03</b> Consumer writes raw events to PostgreSQL</p>
                    <p><b>04</b> Airflow/Python pipeline transforms data</p>
                    <p><b>05</b> ML jobs generate churn intelligence</p>
                    <p><b>06</b> Recommender generates personalized titles</p>
                    <p><b>07</b> Gemini converts metrics into business language</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if "inserted_at" in raw.columns:
            st.dataframe(raw.sort_values("inserted_at", ascending=False).head(80), use_container_width=True, hide_index=True)
        else:
            st.dataframe(raw.head(80), use_container_width=True, hide_index=True)


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

elif page == "Executive Summary":
    page_header(
        "08 / Executive Summary",
        "METRICS BECOME LANGUAGE.",
        "A Gemini-generated narrative layer that turns warehouse signals into leadership-ready interpretation.",
        ["Gemini", "Leadership brief", "Actions", "Risks"],
    )

    if summaries.empty:
        empty_state("No executive summary yet", "Run: python -m src.genai_summary")
    else:
        latest = summaries.sort_values("generated_at").iloc[-1]

        left, right = st.columns([0.72, 0.28])

        with left:
            genai_card(
                f"Summary for {latest.get('summary_date', 'latest date')}",
                latest.get("summary_text", ""),
                "Generated executive brief",
            )

        with right:
            insight_card(
                "Why this matters.",
                "Executives do not always want dashboards. This layer turns warehouse metrics into plain-English insight, risk interpretation, and action recommendations.",
                "GenAI layer",
            )

        if not daily.empty:
            daily_sorted = daily.sort_values("metric_date")
            fig = px.line(
                daily_sorted,
                x="metric_date",
                y="total_watch_minutes",
                markers=True,
                title="Metric Context Used By Summary",
            )
            fig.update_traces(line_color="#FF3D00", marker_color="#FAFAFA")
            fig = plotly_theme(fig, height=390)
            st.plotly_chart(fig, use_container_width=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer-note">
        StreamFlix DE · Kafka-compatible event streaming · Airflow orchestration · ML intelligence · Hybrid recommendation engine · Gemini GenAI Studio · OTT analytics dashboard
    </div>
    """,
    unsafe_allow_html=True,
)