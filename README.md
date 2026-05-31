# StreamFlix Project Documentation

## 1. Purpose

StreamFlix is a portfolio-grade OTT streaming analytics project designed to demonstrate a complete data engineering, orchestration, and AI workflow.

The project covers:

```text
Event ingestion
Data storage
Workflow orchestration with Apache Airflow
ETL processing
Analytics marts
Machine learning
Recommendation systems
GenAI
Dashboarding
```

The system simulates how a streaming business could use data to understand user behavior, content performance, playback quality, churn risk, and personalized recommendations.

---

## 2. System Architecture

```text
Producer → Redpanda/Kafka → Consumer → PostgreSQL → Airflow Pipelines → Analytics/ML/GenAI → Streamlit Dashboard
```

### Producer

The producer creates synthetic streaming events such as watch events, search events, payments, subscription changes, and playback-quality events.

### Redpanda

Redpanda is used as a Kafka-compatible event streaming layer.

### Consumer

The consumer reads events from Redpanda and writes them into the `raw_events` PostgreSQL table.

### PostgreSQL

PostgreSQL stores raw data, cleaned data, analytics marts, model outputs, recommendation outputs, and GenAI outputs.

### Apache Airflow

Apache Airflow orchestrates the end-to-end data workflows.

Responsibilities include:

```text
Scheduling ETL jobs
Managing ML and recommendation workflows
Running GenAI enrichment tasks
Monitoring pipeline execution
Handling task dependencies and retries
Providing DAG-level observability
```

Example Airflow DAGs:

```text
event_pipeline_dag
analytics_pipeline_dag
churn_training_dag
recommendation_pipeline_dag
genai_pipeline_dag
```

### Pipeline

The pipeline transforms raw events into structured analytical tables and runs downstream intelligence jobs.

### Dashboard

The Streamlit dashboard provides an interface for viewing all analytics, ML, recommendation, GenAI, Airflow pipeline status, and operational health outputs.

---

## 3. Data Pipeline

### Raw Layer

Main table:

```text
raw_events
```

Contains the raw event stream from the consumer.

### Clean Layer

Tables:

```text
clean_watch_events
clean_business_events
```

These tables separate watch/playback behavior from business events such as payments and subscriptions.

### Analytics Layer

Tables:

```text
daily_metrics
country_metrics
content_performance
device_quality_metrics
```

These tables power the executive overview, content analytics, country analytics, and playback-quality dashboards.

### Airflow Orchestration Flow

Typical orchestration sequence:

```text
Ingestion DAG
    ↓
Cleaning DAG
    ↓
Analytics DAG
    ↓
ML & Recommendation DAG
    ↓
GenAI DAG
    ↓
Dashboard Refresh
```

Airflow manages dependencies between each stage to ensure reliable execution and recoverability.

---

## 4. Machine Learning Layer

### Churn Prediction

The churn model predicts the likelihood of a user cancelling or becoming inactive.

Input table:

```text
user_features
```

Output tables:

```text
churn_predictions
churn_model_metrics
churn_feature_importance
```

### Features

Example features:

```text
subscription_age_days
total_watch_minutes
watch_events
avg_completion_rate
days_since_last_watch
buffering_count
payment_failed_count
num_genres_watched
engagement_score
friction_score
```

### Models

The pipeline can compare multiple models such as:

```text
Logistic Regression
Random Forest
Extra Trees
Gradient Boosting
```

The best model is selected using a weighted evaluation approach prioritizing AUC, recall, F1, and precision.

### Outputs

The churn layer produces:

```text
churn_probability
risk_level
risk_reason
recommended_action
```

This turns model predictions into operational retention actions.

### Airflow ML Automation

Airflow automates ML workflows including:

```text
Feature generation
Model training
Model evaluation
Prediction refresh
Metrics tracking
Scheduled retraining
```

---

## 5. Recommendation System

The recommendation engine is hybrid.

It combines:

```text
Content-based filtering
User-based collaborative filtering
Item-based collaborative filtering
Model-based matrix factorization
Country-trending signals
Global popularity fallback
```

### Output Table

```text
recommendations
```

Important columns:

```text
user_id
content_id
title
recommendation_type
reason
score
confidence
model_cf_score
user_cf_score
item_cf_score
content_score
country_score
popularity_score
```

### Recommendation Metrics

```text
recommendation_model_metrics
```

This table tracks:

```text
total_users
total_content
users_with_history
total_recommendations
catalog_coverage
avg_hybrid_score
model_based_enabled
user_cf_enabled
item_cf_enabled
content_based_enabled
```

### Airflow Recommendation Scheduling

Airflow schedules recommendation refresh jobs daily or hourly depending on workload requirements.

Tasks include:

```text
User similarity computation
Content embedding refresh
Hybrid score generation
Recommendation publishing
Metrics validation
```

---

## 6. GenAI Layer

The GenAI layer uses Gemini API with local fallback support.

### Gemini Client

File:

```text
src/genai_client.py
```

Responsibilities:

```text
Read Gemini API settings from environment
Call Gemini model
Return fallback output if API is disabled or fails
```

### Executive Summary

File:

```text
src/genai_summary.py
```

Output table:

```text
executive_summaries
```

Purpose:

```text
Convert warehouse metrics into a leadership-ready intelligence brief.
```

### Retention Campaigns

File:

```text
src/genai_retention_campaigns.py
```

Output table:

```text
genai_retention_campaigns
```

Purpose:

```text
Generate short retention campaign messages for high-risk and medium-risk users.
```

### Content Metadata Enrichment

File:

```text
src/genai_content_enrichment.py
```

Output table:

```text
genai_content_enrichment
```

Purpose:

```text
Generate content summaries, mood tags, search keywords, audience segments, and recommendation blurbs.
```

### Airflow GenAI Automation

Airflow orchestrates GenAI tasks including:

```text
Executive summary generation
Retention campaign generation
Content enrichment refresh
Failure retries
Scheduled execution
Dependency management
```

### AI Analytics Copilot

The Streamlit dashboard includes a natural-language analytics copilot that maps common questions to safe read-only SQL templates.

Example:

```text
Question:
Which users are at highest churn risk?

SQL:
SELECT user_id, churn_probability, risk_level, risk_reason, recommended_action, country
FROM churn_predictions
ORDER BY churn_probability DESC
LIMIT 10;
```

---

## 7. Dashboard Documentation

### Executive Overview

Purpose:

```text
Summarize platform-level health.
```

Metrics:

```text
Active users
Watch hours
Completion rate
Revenue
Payment failures
```

### Content Performance

Purpose:

```text
Analyze content-market fit and engagement.
```

Metrics:

```text
Top titles
Watch time
Completion rate
Genre performance
Viewer touchpoints
```

### Churn Intelligence

Purpose:

```text
Identify users at risk and explain why.
```

Outputs:

```text
Risk distribution
Highest-risk users
Model comparison
Feature importance
Retention action queue
```

### Recommendation Engine

Purpose:

```text
Explain personalized recommendations.
```

Outputs:

```text
Top recommendations
Recommendation type
Hybrid score
Per-signal score breakdown
Catalog coverage
```

### GenAI Studio

Purpose:

```text
Show GenAI-powered business intelligence.
```

Sections:

```text
Executive brief
Retention campaigns
Content enrichment
Analytics copilot
```

### Playback Quality

Purpose:

```text
Monitor experience issues.
```

Metrics:

```text
Buffering events
Quality score
Worst device
Device-level quality table
```

### Pipeline Health

Purpose:

```text
Show data engineering and orchestration pipeline health.
```

Metrics:

```text
Raw events
Clean watch events
Clean business events
Event type distribution
Latest raw events
Airflow DAG status
Task success/failure counts
Pipeline runtime metrics
```

---

## 8. How to Run

### Start Docker

```bash
docker compose up -d
```

### Install dependencies

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Run producer

```powershell
.\venv\Scripts\python.exe producer\produce_events.py
```

### Run consumer

```powershell
.\venv\Scripts\python.exe consumer\consume_events.py
```

### Run Airflow

```powershell
docker compose up airflow-webserver airflow-scheduler -d
```

### Initialize Airflow

```powershell
docker compose run airflow-init
```

### Run pipeline

```powershell
$env:PYTHONPATH = "C:\Users\HP\Desktop\streamflix"
.\venv\Scripts\python.exe -m src.run_pipeline
```

### Run GenAI modules

```powershell
$env:PYTHONPATH = "C:\Users\HP\Desktop\streamflix"
.\venv\Scripts\python.exe -m src.genai_summary
.\venv\Scripts\python.exe -m src.genai_retention_campaigns
.\venv\Scripts\python.exe -m src.genai_content_enrichment
```

### Access Airflow UI

```text
http://localhost:8080
```

### Run dashboard

```powershell
.\venv\Scripts\streamlit.exe run app\streamlit_app.py
```

---

## 9. Notes on Synthetic Data

This project uses synthetic data. Therefore:

```text
Model scores are used to validate the workflow.
Recommendation outputs demonstrate system design.
GenAI outputs demonstrate integration and product use cases.
Airflow orchestration demonstrates production-style workflow management.
The project should not be interpreted as trained on real customer behavior.
```

---

## 10. Portfolio Value

This project demonstrates the ability to build a complete data product:

```text
Backend event streaming
Workflow orchestration with Apache Airflow
Data warehouse design
Data pipeline development
ML workflow implementation
Recommendation engine design
GenAI integration
Dashboard design
Business-facing analytics storytelling
Production-style pipeline monitoring
```
