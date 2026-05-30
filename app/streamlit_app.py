import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import streamlit as st
from src.db import get_engine

st.set_page_config(page_title="StreamFlix DE", layout="wide")

@st.cache_data(ttl=30)
def load_table(table):
    engine = get_engine()
    try:
        return pd.read_sql(f"SELECT * FROM {table}", engine)
    except Exception:
        return pd.DataFrame()

st.title("StreamFlix DE: OTT Streaming Analytics")
st.caption("STARZPLAY-inspired data engineering project with Kafka, Airflow, PostgreSQL, ML, recommendations, and executive summaries.")

page = st.sidebar.radio("Dashboard", ["Overview", "Content Analytics", "Churn + Recommendations", "Playback Quality", "Executive Summary", "Raw Data Health"])

if page == "Overview":
    daily = load_table("daily_metrics")
    country = load_table("country_metrics")
    if daily.empty:
        st.warning("No metrics yet. Run producer + consumer, then run the pipeline.")
    else:
        latest = daily.sort_values("metric_date").iloc[-1]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Active Users", int(latest["active_users"]))
        c2.metric("Watch Hours", f"{latest['total_watch_minutes']/60:,.1f}")
        c3.metric("Avg Completion", f"{latest['avg_completion_rate']:.1%}")
        c4.metric("Revenue", f"PKR {latest['total_revenue']:,.0f}")
        c5.metric("Payment Failures", int(latest["payment_failures"]))

        st.subheader("Daily Watch Minutes")
        fig = px.line(daily.sort_values("metric_date"), x="metric_date", y="total_watch_minutes", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        if not country.empty:
            st.subheader("Watch Time by Country")
            fig = px.bar(country.sort_values("total_watch_minutes", ascending=False), x="country", y="total_watch_minutes")
            st.plotly_chart(fig, use_container_width=True)

elif page == "Content Analytics":
    content = load_table("content_performance")
    if content.empty:
        st.warning("No content metrics yet.")
    else:
        st.subheader("Top Content")
        st.dataframe(content.sort_values("popularity_score", ascending=False).head(20), use_container_width=True)
        fig = px.bar(content.sort_values("total_watch_minutes", ascending=False).head(10), x="title", y="total_watch_minutes", color="genre")
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.scatter(content, x="avg_completion_rate", y="total_watch_minutes", size="unique_viewers", color="language", hover_name="title")
        st.plotly_chart(fig2, use_container_width=True)

elif page == "Churn + Recommendations":
    churn = load_table("churn_predictions")
    recs = load_table("recommendations")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Churn Risk")
        if churn.empty:
            st.warning("No churn predictions yet.")
        else:
            risk_counts = churn["risk_level"].value_counts().reset_index()
            risk_counts.columns = ["risk_level", "users"]
            fig = px.pie(risk_counts, names="risk_level", values="users")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(churn.sort_values("churn_probability", ascending=False).head(25), use_container_width=True)
    with c2:
        st.subheader("Recommendations")
        if recs.empty:
            st.warning("No recommendations yet.")
        else:
            selected_user = st.selectbox("Select user", sorted(recs["user_id"].unique()))
            st.dataframe(recs[recs["user_id"] == selected_user][["title", "reason", "score"]], use_container_width=True)

elif page == "Playback Quality":
    device = load_table("device_quality_metrics")
    if device.empty:
        st.warning("No playback quality metrics yet.")
    else:
        st.subheader("Device Quality")
        st.dataframe(device.sort_values("total_buffering_events", ascending=False), use_container_width=True)
        fig = px.bar(device.sort_values("total_buffering_events", ascending=False), x="device", y="total_buffering_events")
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.bar(device.sort_values("avg_quality_score"), x="device", y="avg_quality_score")
        st.plotly_chart(fig2, use_container_width=True)

elif page == "Executive Summary":
    summaries = load_table("executive_summaries")
    if summaries.empty:
        st.warning("No executive summary yet.")
    else:
        latest = summaries.sort_values("generated_at").iloc[-1]
        st.subheader(f"Summary for {latest['summary_date']}")
        st.text_area("Generated Summary", latest["summary_text"], height=320)

elif page == "Raw Data Health":
    raw = load_table("raw_events")
    clean = load_table("clean_watch_events")
    business = load_table("clean_business_events")
    c1, c2, c3 = st.columns(3)
    c1.metric("Raw Events", len(raw))
    c2.metric("Clean Watch/Playback", len(clean))
    c3.metric("Clean Business", len(business))
    if not raw.empty:
        st.subheader("Raw Event Types")
        counts = raw["event_type"].value_counts().reset_index()
        counts.columns = ["event_type", "count"]
        fig = px.bar(counts, x="event_type", y="count")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(raw.sort_values("inserted_at", ascending=False).head(50), use_container_width=True)
