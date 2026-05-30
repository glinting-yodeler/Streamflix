import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.db import get_engine


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StreamFlix DE | OTT Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# GLOBAL STYLES
# ============================================================

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 15% 10%, rgba(255, 77, 77, 0.14), transparent 28%),
                radial-gradient(circle at 85% 20%, rgba(115, 80, 255, 0.16), transparent 30%),
                radial-gradient(circle at 50% 90%, rgba(0, 229, 255, 0.08), transparent 28%),
                linear-gradient(135deg, #07070b 0%, #101018 45%, #07070b 100%);
            color: #f4f4f5;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b0b12 0%, #11111c 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        section[data-testid="stSidebar"] * {
            color: #f4f4f5;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.055);
            border: 1px solid rgba(255, 255, 255, 0.10);
            padding: 18px 18px 16px 18px;
            border-radius: 20px;
            box-shadow: 0 12px 34px rgba(0,0,0,0.22);
            backdrop-filter: blur(18px);
        }

        div[data-testid="stMetric"] label {
            color: rgba(244,244,245,0.72) !important;
            font-size: 0.85rem !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-size: 1.9rem !important;
            font-weight: 800 !important;
        }

        .hero-card {
            padding: 30px;
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.035)),
                linear-gradient(135deg, rgba(255,65,65,0.16), rgba(90,70,255,0.10));
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 20px 70px rgba(0,0,0,0.32);
            margin-bottom: 24px;
        }

        .hero-title {
            font-size: 2.45rem;
            line-height: 1.05;
            font-weight: 850;
            letter-spacing: -1.4px;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            color: rgba(244,244,245,0.74);
            font-size: 1.02rem;
            max-width: 980px;
            line-height: 1.7;
        }

        .pill-row {
            margin-top: 18px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .pill {
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.12);
            color: rgba(255,255,255,0.86);
            font-size: 0.84rem;
            font-weight: 600;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 800;
            margin: 22px 0 10px 0;
            letter-spacing: -0.3px;
        }

        .section-caption {
            color: rgba(244,244,245,0.64);
            font-size: 0.92rem;
            margin-bottom: 14px;
        }

        .glass-card {
            background: rgba(255,255,255,0.055);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 22px;
            padding: 20px;
            box-shadow: 0 14px 45px rgba(0,0,0,0.22);
            backdrop-filter: blur(18px);
            margin-bottom: 18px;
        }

        .insight-card {
            background: linear-gradient(135deg, rgba(255,77,77,0.13), rgba(115,80,255,0.10));
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 22px;
            padding: 22px;
            box-shadow: 0 14px 45px rgba(0,0,0,0.25);
            margin-bottom: 18px;
        }

        .success-chip {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(34,197,94,0.13);
            color: #86efac;
            border: 1px solid rgba(34,197,94,0.25);
            font-weight: 700;
            font-size: 0.78rem;
        }

        .warn-chip {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(245,158,11,0.13);
            color: #fcd34d;
            border: 1px solid rgba(245,158,11,0.25);
            font-weight: 700;
            font-size: 0.78rem;
        }

        .danger-chip {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(239,68,68,0.13);
            color: #fca5a5;
            border: 1px solid rgba(239,68,68,0.25);
            font-weight: 700;
            font-size: 0.78rem;
        }

        .small-muted {
            color: rgba(244,244,245,0.60);
            font-size: 0.88rem;
        }

        .footer-note {
            color: rgba(244,244,245,0.55);
            font-size: 0.82rem;
            margin-top: 24px;
        }

        .stDataFrame {
            border-radius: 18px;
            overflow: hidden;
        }

        div[data-testid="stAlert"] {
            border-radius: 18px;
        }

        button[kind="secondary"] {
            border-radius: 999px !important;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(ttl=30)
def load_table(table):
    engine = get_engine()
    try:
        return pd.read_sql(f"SELECT * FROM {table}", engine)
    except Exception:
        return pd.DataFrame()


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


def risk_color_label(risk):
    risk = str(risk).lower()
    if risk == "high":
        return "🔴 High"
    if risk == "medium":
        return "🟠 Medium"
    return "🟢 Low"


def empty_state(title, message):
    st.markdown(
        f"""
        <div class="glass-card">
            <h3 style="margin:0 0 8px 0;">{title}</h3>
            <p class="small-muted" style="margin:0;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def plotly_theme(fig, height=420):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f4f4f5", family="Inter"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            font=dict(color="#f4f4f5")
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.08)"
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.08)"
        )
    )
    return fig


# ============================================================
# LOAD TABLES
# ============================================================

daily = load_table("daily_metrics")
country = load_table("country_metrics")
content = load_table("content_performance")
device = load_table("device_quality_metrics")
churn = load_table("churn_predictions")
churn_metrics = load_table("churn_model_metrics")
churn_importance = load_table("churn_feature_importance")
recs = load_table("recommendations")
summaries = load_table("executive_summaries")
raw = load_table("raw_events")
clean_watch = load_table("clean_watch_events")
clean_business = load_table("clean_business_events")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🎬 StreamFlix DE")
    st.markdown(
        """
        <p class="small-muted">
        STARZPLAY-inspired streaming data engineering project.
        </p>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Content Performance",
            "Churn Intelligence",
            "Recommendation Engine",
            "Playback Quality",
            "Pipeline Health",
            "Executive Summary"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### System Stack")
    st.markdown(
        """
        <div class="pill-row">
            <span class="pill">Kafka / Redpanda</span>
            <span class="pill">PostgreSQL</span>
            <span class="pill">Airflow</span>
            <span class="pill">Scikit-learn</span>
            <span class="pill">Streamlit</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    if not raw.empty:
        st.markdown('<span class="success-chip">● Data online</span>', unsafe_allow_html=True)
        st.caption(f"{len(raw):,} raw events loaded")
    else:
        st.markdown('<span class="warn-chip">● Waiting for events</span>', unsafe_allow_html=True)
        st.caption("Run producer, consumer, then pipeline.")


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">OTT Streaming Intelligence Platform</div>
        <div class="hero-subtitle">
            A STARZPLAY-inspired data engineering project that streams watch, search, payment,
            subscription, and playback-quality events through Kafka-compatible Redpanda,
            transforms them using Airflow pipelines, and powers business analytics,
            churn intelligence, recommendations, and executive insights.
        </div>
        <div class="pill-row">
            <span class="pill">Real-time event ingestion</span>
            <span class="pill">Batch analytics pipeline</span>
            <span class="pill">Churn prediction</span>
            <span class="pill">Recommendation system</span>
            <span class="pill">Executive insight layer</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":
    if daily.empty:
        empty_state(
            "No metrics yet",
            "Run the producer and consumer for a few minutes, then run the Airflow pipeline or src.run_pipeline."
        )
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
        c3.metric("Avg Completion", f"{float(avg_completion):.1%}")
        c4.metric("Revenue", format_money(total_revenue))
        c5.metric("Payment Failures", format_number(payment_failures))

        st.markdown('<div class="section-title">Platform Activity Trend</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Daily engagement trend from processed watch and business events.</div>',
            unsafe_allow_html=True
        )

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=daily_sorted["metric_date"],
                y=daily_sorted["total_watch_minutes"],
                mode="lines+markers",
                name="Watch Minutes",
                line=dict(width=4),
                marker=dict(size=8)
            )
        )
        fig = plotly_theme(fig, height=420)
        fig.update_layout(title="Daily Watch Minutes")
        st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns([1.1, 0.9])

        with left:
            st.markdown('<div class="section-title">Country Performance</div>', unsafe_allow_html=True)
            if not country.empty and "country" in country.columns:
                country_sorted = country.sort_values("total_watch_minutes", ascending=False)
                fig = px.bar(
                    country_sorted,
                    x="country",
                    y="total_watch_minutes",
                    text_auto=True,
                    title="Watch Time by Country"
                )
                fig = plotly_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
            else:
                empty_state("Country metrics unavailable", "The country_metrics table is empty.")

        with right:
            st.markdown('<div class="section-title">Business Interpretation</div>', unsafe_allow_html=True)
            best_country = "N/A"
            if not country.empty and "country" in country.columns:
                best_country = country.sort_values("total_watch_minutes", ascending=False).iloc[0]["country"]

            st.markdown(
                f"""
                <div class="insight-card">
                    <h3 style="margin-top:0;">Executive Readout</h3>
                    <p>
                        The platform currently shows <b>{format_number(active_users)}</b> active users and
                        <b>{float(total_watch_minutes) / 60:,.1f}</b> total watch hours in the latest metrics window.
                    </p>
                    <p>
                        The strongest country by watch-time contribution is <b>{best_country}</b>.
                        Average completion is <b>{float(avg_completion):.1%}</b>, which is a useful indicator of content engagement.
                    </p>
                    <p class="small-muted">
                        Product lens: a streaming business would use these signals to understand regional demand,
                        retention quality, content performance, and potential growth opportunities.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# CONTENT PERFORMANCE
# ============================================================

elif page == "Content Performance":
    if content.empty:
        empty_state("No content metrics yet", "Run the analytics pipeline to build the content_performance table.")
    else:
        st.markdown('<div class="section-title">Content Command Center</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Analyze what users watch, complete, and return to across genres and languages.</div>',
            unsafe_allow_html=True
        )

        top_content = content.sort_values("popularity_score", ascending=False).head(1).iloc[0]
        total_titles = len(content)
        avg_completion = content["avg_completion_rate"].mean() if "avg_completion_rate" in content.columns else 0
        total_watch = content["total_watch_minutes"].sum() if "total_watch_minutes" in content.columns else 0
        unique_viewers = content["unique_viewers"].sum() if "unique_viewers" in content.columns else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Catalog Titles", format_number(total_titles))
        c2.metric("Total Watch Hours", f"{float(total_watch) / 60:,.1f}")
        c3.metric("Avg Completion", f"{float(avg_completion):.1%}")
        c4.metric("Viewer Touchpoints", format_number(unique_viewers))

        left, right = st.columns([1.25, 0.75])

        with left:
            chart_data = content.sort_values("total_watch_minutes", ascending=False).head(12)
            fig = px.bar(
                chart_data,
                x="title",
                y="total_watch_minutes",
                color="genre" if "genre" in chart_data.columns else None,
                title="Top Content by Watch Time"
            )
            fig.update_xaxes(tickangle=-35)
            fig = plotly_theme(fig, height=460)
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.markdown(
                f"""
                <div class="insight-card">
                    <h3 style="margin-top:0;">Top Performing Title</h3>
                    <h2 style="margin-bottom:6px;">{top_content.get("title", "N/A")}</h2>
                    <p class="small-muted">Genre: {top_content.get("genre", "N/A")} · Language: {top_content.get("language", "N/A")}</p>
                    <p>
                        Popularity score: <b>{top_content.get("popularity_score", 0):,.2f}</b><br>
                        Watch minutes: <b>{top_content.get("total_watch_minutes", 0):,.0f}</b><br>
                        Completion rate: <b>{top_content.get("avg_completion_rate", 0):.1%}</b>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown('<div class="section-title">Engagement Quality Map</div>', unsafe_allow_html=True)

        fig2 = px.scatter(
            content,
            x="avg_completion_rate",
            y="total_watch_minutes",
            size="unique_viewers" if "unique_viewers" in content.columns else None,
            color="language" if "language" in content.columns else None,
            hover_name="title" if "title" in content.columns else None,
            title="Completion Rate vs Watch Time"
        )
        fig2 = plotly_theme(fig2, height=470)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-title">Content Table</div>', unsafe_allow_html=True)
        show_cols = [
            col for col in [
                "title", "genre", "language", "total_watch_minutes",
                "unique_viewers", "avg_completion_rate", "popularity_score"
            ]
            if col in content.columns
        ]
        st.dataframe(
            content.sort_values("popularity_score", ascending=False)[show_cols].head(30),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# CHURN INTELLIGENCE
# ============================================================

elif page == "Churn Intelligence":
    if churn.empty:
        empty_state("No churn predictions yet", "Run the ML pipeline to generate churn_predictions.")
    else:
        st.markdown('<div class="section-title">Churn Intelligence Center</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Industry-style churn pipeline with model comparison, risk explanations, feature importance, and retention actions.</div>',
            unsafe_allow_html=True
        )

        high_risk = len(churn[churn["risk_level"].str.lower() == "high"]) if "risk_level" in churn.columns else 0
        medium_risk = len(churn[churn["risk_level"].str.lower() == "medium"]) if "risk_level" in churn.columns else 0
        low_risk = len(churn[churn["risk_level"].str.lower() == "low"]) if "risk_level" in churn.columns else 0
        avg_churn_prob = churn["churn_probability"].mean() if "churn_probability" in churn.columns else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("High-Risk Users", format_number(high_risk))
        c2.metric("Medium-Risk Users", format_number(medium_risk))
        c3.metric("Low-Risk Users", format_number(low_risk))
        c4.metric("Avg Churn Risk", f"{float(avg_churn_prob):.1%}")

        if not churn_metrics.empty:
            selected = churn_metrics[churn_metrics["selected_model"] == True]
            if selected.empty:
                selected = churn_metrics.sort_values("auc", ascending=False).head(1)

            best = selected.iloc[0]

            st.markdown('<div class="section-title">Selected Model Performance</div>', unsafe_allow_html=True)

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Best Model", str(best.get("model_name", "N/A")).replace("_", " ").title())
            m2.metric("Accuracy", f"{float(best.get('accuracy', 0)):.1%}")
            m3.metric("Precision", f"{float(best.get('precision_score', 0)):.1%}")
            m4.metric("Recall", f"{float(best.get('recall', 0)):.1%}")
            m5.metric("AUC", f"{float(best.get('auc', 0)):.3f}")

            left, right = st.columns([1.15, 0.85])

            with left:
                st.markdown('<div class="section-title">Candidate Model Comparison</div>', unsafe_allow_html=True)
                metric_cols = [
                    "model_name", "accuracy", "precision_score",
                    "recall", "f1", "auc", "selected_model"
                ]
                existing_cols = [c for c in metric_cols if c in churn_metrics.columns]

                model_table = churn_metrics[existing_cols].copy()
                for col in ["accuracy", "precision_score", "recall", "f1"]:
                    if col in model_table.columns:
                        model_table[col] = model_table[col].map(lambda x: f"{float(x):.1%}")
                if "auc" in model_table.columns:
                    model_table["auc"] = model_table["auc"].map(lambda x: f"{float(x):.3f}")

                st.dataframe(
                    model_table,
                    use_container_width=True,
                    hide_index=True
                )

            with right:
                st.markdown('<div class="section-title">Confusion Matrix</div>', unsafe_allow_html=True)

                tn = int(best.get("true_negatives", 0))
                fp = int(best.get("false_positives", 0))
                fn = int(best.get("false_negatives", 0))
                tp = int(best.get("true_positives", 0))

                cm_df = pd.DataFrame(
                    [[tn, fp], [fn, tp]],
                    index=["Actual: Not Churn", "Actual: Churn"],
                    columns=["Pred: Not Churn", "Pred: Churn"]
                )

                fig_cm = px.imshow(
                    cm_df,
                    text_auto=True,
                    aspect="auto",
                    title="Confusion Matrix"
                )
                fig_cm = plotly_theme(fig_cm, height=330)
                st.plotly_chart(fig_cm, use_container_width=True)

        left, right = st.columns([0.9, 1.1])

        with left:
            if "risk_level" in churn.columns:
                risk_counts = churn["risk_level"].value_counts().reset_index()
                risk_counts.columns = ["risk_level", "users"]

                fig = px.pie(
                    risk_counts,
                    names="risk_level",
                    values="users",
                    hole=0.58,
                    title="Risk Distribution"
                )
                fig = plotly_theme(fig, height=420)
                st.plotly_chart(fig, use_container_width=True)

        with right:
            top_risk = churn.sort_values("churn_probability", ascending=False).head(12)

            fig = px.bar(
                top_risk,
                x="user_id",
                y="churn_probability",
                color="risk_level" if "risk_level" in top_risk.columns else None,
                title="Highest-Risk Users"
            )
            fig.update_yaxes(tickformat=".0%")
            fig = plotly_theme(fig, height=420)
            st.plotly_chart(fig, use_container_width=True)

        if not churn_importance.empty:
            st.markdown('<div class="section-title">Feature Importance</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-caption">Shows which behavioral, payment, subscription, and playback-quality signals influence churn prediction.</div>',
                unsafe_allow_html=True
            )

            imp = churn_importance.sort_values("importance", ascending=False).head(15)
            fig = px.bar(
                imp.sort_values("importance"),
                x="importance",
                y="feature_name",
                orientation="h",
                title="Top Churn Drivers"
            )
            fig = plotly_theme(fig, height=500)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Retention Action Queue</div>', unsafe_allow_html=True)

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

        st.dataframe(
            top_users[existing_cols],
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            """
            <div class="insight-card">
                <h3 style="margin-top:0;">Interview Explanation</h3>
                <p>
                    This churn system does not only output a probability. It compares multiple models,
                    selects the strongest one, stores model metrics, explains the main risk reasons,
                    and converts predictions into retention actions.
                </p>
                <p class="small-muted">
                    In a real OTT business, this could power lifecycle campaigns, payment recovery flows,
                    personalized content recommendations, and playback-quality interventions.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

elif page == "Recommendation Engine":
    if recs.empty:
        empty_state("No recommendations yet", "Run the recommendation pipeline to populate the recommendations table.")
    else:
        st.markdown('<div class="section-title">Personalized Recommendation Engine</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">User-level recommendations generated from viewing behavior, country trends, and content affinity.</div>',
            unsafe_allow_html=True
        )

        total_recs = len(recs)
        total_users = recs["user_id"].nunique() if "user_id" in recs.columns else 0
        avg_score = recs["score"].mean() if "score" in recs.columns else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Recommended Items", format_number(total_recs))
        c2.metric("Users Covered", format_number(total_users))
        c3.metric("Avg Recommendation Score", f"{float(avg_score):.2f}")

        users = sorted(recs["user_id"].unique()) if "user_id" in recs.columns else []
        selected_user = st.selectbox("Select a user to inspect recommendations", users)

        user_recs = recs[recs["user_id"] == selected_user].sort_values("score", ascending=False)

        left, right = st.columns([1.15, 0.85])

        with left:
            st.markdown('<div class="section-title">Top Recommendations</div>', unsafe_allow_html=True)
            cols = [col for col in ["title", "reason", "score"] if col in user_recs.columns]
            st.dataframe(user_recs[cols], use_container_width=True, hide_index=True)

        with right:
            if not user_recs.empty:
                best = user_recs.iloc[0]
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <h3 style="margin-top:0;">Best Next Watch</h3>
                        <h2>{best.get("title", "N/A")}</h2>
                        <p>{best.get("reason", "Recommended based on user behavior.")}</p>
                        <p class="small-muted">
                            Recommendation score: <b>{best.get("score", 0):.2f}</b>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        if "title" in recs.columns:
            popular_recs = recs["title"].value_counts().head(10).reset_index()
            popular_recs.columns = ["title", "recommendation_count"]
            fig = px.bar(
                popular_recs,
                x="title",
                y="recommendation_count",
                title="Most Frequently Recommended Titles"
            )
            fig.update_xaxes(tickangle=-35)
            fig = plotly_theme(fig, height=440)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """
            <div class="glass-card">
                <h3 style="margin-top:0;">Product Thinking</h3>
                <p class="small-muted">
                    For an OTT platform, recommendations are not only a machine learning feature.
                    They are a retention mechanism. Better recommendations increase watch time,
                    improve content discovery, and reduce subscription cancellation risk.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PLAYBACK QUALITY
# ============================================================

elif page == "Playback Quality":
    if device.empty:
        empty_state("No playback metrics yet", "Run the pipeline to create device_quality_metrics.")
    else:
        st.markdown('<div class="section-title">Playback Quality Observatory</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Monitor buffering and quality issues that can damage user experience and retention.</div>',
            unsafe_allow_html=True
        )

        total_buffering = device["total_buffering_events"].sum() if "total_buffering_events" in device.columns else 0
        avg_quality = device["avg_quality_score"].mean() if "avg_quality_score" in device.columns else 0
        worst_device = "N/A"
        if "total_buffering_events" in device.columns and "device" in device.columns:
            worst_device = device.sort_values("total_buffering_events", ascending=False).iloc[0]["device"]

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Buffering Events", format_number(total_buffering))
        c2.metric("Avg Quality Score", f"{float(avg_quality):.2f}")
        c3.metric("Most Problematic Device", worst_device)

        left, right = st.columns(2)

        with left:
            fig = px.bar(
                device.sort_values("total_buffering_events", ascending=False),
                x="device",
                y="total_buffering_events",
                title="Buffering Events by Device"
            )
            fig = plotly_theme(fig, height=430)
            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig2 = px.bar(
                device.sort_values("avg_quality_score", ascending=True),
                x="device",
                y="avg_quality_score",
                title="Average Quality Score by Device"
            )
            fig2 = plotly_theme(fig2, height=430)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-title">Device Quality Table</div>', unsafe_allow_html=True)
        st.dataframe(
            device.sort_values("total_buffering_events", ascending=False),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            f"""
            <div class="insight-card">
                <h3 style="margin-top:0;">Retention Risk Connection</h3>
                <p>
                    Playback quality directly affects streaming retention. If <b>{worst_device}</b>
                    consistently shows higher buffering, users on that device may show lower completion
                    rates and higher churn risk.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PIPELINE HEALTH
# ============================================================

elif page == "Pipeline Health":
    st.markdown('<div class="section-title">Data Pipeline Health</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Track raw ingestion, cleaned event volume, and event type distribution.</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Raw Events", format_number(len(raw)))
    c2.metric("Clean Watch Events", format_number(len(clean_watch)))
    c3.metric("Clean Business Events", format_number(len(clean_business)))
    c4.metric("Pipeline Tables", "9+")

    if raw.empty:
        empty_state(
            "No raw events found",
            "Start the Kafka producer and consumer to load raw events into PostgreSQL."
        )
    else:
        left, right = st.columns([1, 1])

        with left:
            if "event_type" in raw.columns:
                counts = raw["event_type"].value_counts().reset_index()
                counts.columns = ["event_type", "count"]
                fig = px.bar(counts, x="event_type", y="count", title="Raw Event Type Distribution")
                fig.update_xaxes(tickangle=-35)
                fig = plotly_theme(fig, height=430)
                st.plotly_chart(fig, use_container_width=True)

        with right:
            st.markdown(
                """
                <div class="glass-card">
                    <h3 style="margin-top:0;">Pipeline Flow</h3>
                    <p><b>1.</b> Python producer creates OTT events</p>
                    <p><b>2.</b> Kafka-compatible Redpanda streams events</p>
                    <p><b>3.</b> Consumer writes raw events to PostgreSQL</p>
                    <p><b>4.</b> Airflow/Python pipeline cleans and transforms events</p>
                    <p><b>5.</b> ML and recommendation jobs generate intelligence tables</p>
                    <p><b>6.</b> Streamlit dashboard visualizes insights</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown('<div class="section-title">Latest Raw Events</div>', unsafe_allow_html=True)
        if "inserted_at" in raw.columns:
            st.dataframe(
                raw.sort_values("inserted_at", ascending=False).head(80),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.dataframe(raw.head(80), use_container_width=True, hide_index=True)


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

elif page == "Executive Summary":
    st.markdown('<div class="section-title">AI-Style Executive Summary</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">A GenAI-style business narrative generated from warehouse metrics.</div>',
        unsafe_allow_html=True
    )

    if summaries.empty:
        empty_state("No executive summary yet", "Run the executive summary pipeline.")
    else:
        latest = summaries.sort_values("generated_at").iloc[-1]

        c1, c2 = st.columns([0.72, 0.28])

        with c1:
            st.markdown(
                f"""
                <div class="insight-card">
                    <h2 style="margin-top:0;">Summary for {latest.get("summary_date", "Latest Date")}</h2>
                    <div style="white-space: pre-wrap; line-height: 1.75; color: rgba(255,255,255,0.88);">
                    {latest.get("summary_text", "")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                """
                <div class="glass-card">
                    <h3 style="margin-top:0;">Why this matters</h3>
                    <p class="small-muted">
                    Executives do not always want to inspect dashboards manually.
                    This layer converts metrics into readable business insights:
                    what changed, why it matters, and what action should be taken.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        if not daily.empty:
            daily_sorted = daily.sort_values("metric_date")
            fig = px.line(
                daily_sorted,
                x="metric_date",
                y="total_watch_minutes",
                markers=True,
                title="Metric Context Used by Summary"
            )
            fig = plotly_theme(fig, height=390)
            st.plotly_chart(fig, use_container_width=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer-note">
        StreamFlix DE · STARZPLAY-inspired project · Kafka-compatible event streaming · Airflow orchestration · ML intelligence · OTT analytics dashboard
    </div>
    """,
    unsafe_allow_html=True
)