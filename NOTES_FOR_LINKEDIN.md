# LinkedIn post draft

I built **StreamFlix DE**, a STARZPLAY-inspired streaming data engineering project.

The project simulates an OTT platform where watch events, search events, payment events, subscription changes, and playback-quality events are produced into Kafka-compatible Redpanda, consumed into PostgreSQL, orchestrated with Airflow, and visualized in a Streamlit dashboard.

I also added ML and analytics features:

- churn prediction
- personalized recommendations
- content performance analytics
- playback-quality monitoring
- GenAI-style executive summaries

The goal was to understand how streaming platforms can use data engineering to track content performance, user retention, subscription health, and playback issues.

Tech stack: Python, Redpanda/Kafka, PostgreSQL, Airflow, Pandas, Scikit-learn, Streamlit, Docker Compose.
