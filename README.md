# StreamFlix

**StreamFlix** is an end-to-end OTT streaming analytics, data engineering, machine learning, recommendation, orchestration, and GenAI platform built as a portfolio-grade project.

The project simulates how a modern subscription-based streaming company can ingest real-time user activity, process large-scale behavioral data, orchestrate workflows with Apache Airflow, generate analytics marts, train machine learning models, build recommendation systems, enrich insights using Gemini-powered GenAI, and expose business intelligence through an interactive Streamlit dashboard.

The platform demonstrates a complete production-style analytics workflow covering:

```text
Event ingestion
Streaming pipelines
Data warehousing
Workflow orchestration
ETL processing
Analytics marts
Machine learning
Recommendation systems
GenAI integration
Dashboarding
Operational monitoring
Business intelligence
```

---

# 1. Project Purpose

The purpose of StreamFlix is to demonstrate how data engineering and AI systems can work together to power a streaming platform.

The project answers business-critical questions such as:

* Which content drives the highest engagement?
* Which users are likely to churn?
* Which devices experience playback-quality issues?
* Which users should receive retention campaigns?
* Which titles should be recommended to each user?
* How can GenAI summarize warehouse metrics into executive insights?
* How can natural-language analytics queries be mapped safely to SQL?

The project is designed to showcase practical engineering and analytics capabilities across:

* Kafka-compatible event streaming
* PostgreSQL warehouse design
* Apache Airflow orchestration
* ETL and analytics engineering
* Machine learning workflows
* Recommendation systems
* GenAI integration
* Dashboard development
* Product-focused analytics storytelling

---

# 2. System Architecture

```text
Synthetic OTT Event Producer
        ↓
Kafka-Compatible Redpanda
        ↓
Python Consumer
        ↓
PostgreSQL Raw Event Tables
        ↓
Apache Airflow / Python Pipelines
        ↓
Cleaned Tables + Analytics Marts
        ↓
Machine Learning + Recommendation Jobs
        ↓
Gemini GenAI Intelligence Layer
        ↓
Streamlit Analytics Dashboard
```

---

## Architecture Components

### Producer

The producer generates synthetic OTT streaming events that simulate user behavior on a streaming platform.

Generated events include:

```text
video_play
video_pause
video_complete
search_query
payment_success
payment_failed
subscription_started
subscription_cancelled
buffering_event
```

The producer continuously streams events into Kafka-compatible Redpanda topics.

---

### Redpanda

Redpanda acts as the event streaming layer.

Responsibilities include:

```text
Real-time event transport
Kafka-compatible messaging
Topic-based event streaming
Decoupling producers and consumers
Streaming scalability simulation
```

---

### Consumer

The consumer reads events from Redpanda and writes them into PostgreSQL.

Responsibilities include:

```text
Kafka topic consumption
JSON event parsing
Database insertion
Raw event persistence
Streaming ingestion simulation
```

Primary destination table:

```text
raw_events
```

---

### PostgreSQL Warehouse

PostgreSQL stores all layers of the analytics platform.

The warehouse contains:

```text
Raw events
Cleaned events
Analytics marts
Machine learning outputs
Recommendation outputs
GenAI outputs
Operational metrics
```

Main warehouse tables include:

```text
raw_events
clean_watch_events
clean_business_events
daily_metrics
country_metrics
content_performance
device_quality_metrics
user_features
churn_predictions
recommendations
executive_summaries
```

---

### Apache Airflow

Apache Airflow orchestrates the entire workflow pipeline.

Responsibilities include:

```text
Scheduling ETL jobs
Managing ML workflows
Running recommendation pipelines
Executing GenAI enrichment tasks
Handling retries and dependencies
Monitoring DAG execution
Providing workflow observability
```

Example Airflow DAGs:

```text
event_pipeline_dag
analytics_pipeline_dag
churn_training_dag
recommendation_pipeline_dag
genai_pipeline_dag
```

Typical orchestration flow:

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

---

### Streamlit Dashboard

The Streamlit dashboard acts as the business intelligence and operational analytics layer.

The dashboard exposes:

```text
Executive analytics
Content analytics
Churn intelligence
Recommendation insights
Playback-quality monitoring
GenAI outputs
Pipeline health monitoring
```

---

# 3. Tech Stack

| Layer                  | Tools                                                   |
| ---------------------- | ------------------------------------------------------- |
| Event Streaming        | Redpanda, Kafka-compatible topics                       |
| Data Storage           | PostgreSQL                                              |
| Workflow Orchestration | Apache Airflow                                          |
| Data Processing        | Python, Pandas, SQLAlchemy                              |
| Machine Learning       | Scikit-learn                                            |
| Recommendation System  | TF-IDF, cosine similarity, SVD, collaborative filtering |
| GenAI                  | Gemini API with local fallback                          |
| Dashboard              | Streamlit, Plotly                                       |
| Infrastructure         | Docker Compose                                          |
| Version Control        | Git, GitHub                                             |

---

# 4. Data Pipeline

## Raw Layer

Primary table:

```text
raw_events
```

This table stores the raw streaming event feed consumed from Redpanda.

Example event categories:

```text
Playback events
Search events
Payment events
Subscription events
Playback-quality events
```

---

## Clean Layer

Tables:

```text
clean_watch_events
clean_business_events
```

Responsibilities:

```text
Data normalization
Schema standardization
Event separation
Timestamp cleanup
Null handling
Business-rule filtering
```

The clean layer separates playback behavior from business-related events.

---

## Analytics Layer

Analytics marts include:

```text
daily_metrics
country_metrics
content_performance
device_quality_metrics
```

These marts power:

```text
Executive dashboards
Country analytics
Content analytics
Playback-quality monitoring
Revenue analysis
Operational reporting
```

---

## Pipeline Responsibilities

The pipeline performs:

```text
Raw ingestion
Data cleaning
Analytics aggregation
Feature engineering
ML model training
Recommendation generation
GenAI enrichment
Dashboard refresh
```

---

# 5. Apache Airflow Orchestration

Apache Airflow manages workflow orchestration across all pipeline stages.

Core orchestration tasks include:

```text
seed_dimensions
clean_events
build_marts
train_churn_model
generate_recommendations
generate_genai_summary
generate_retention_campaigns
generate_content_enrichment
```

Airflow capabilities demonstrated:

* DAG scheduling
* Dependency management
* Retry handling
* Workflow observability
* Task monitoring
* Pipeline automation
* Scheduled retraining
* Operational orchestration

Airflow automates:

```text
Feature generation
Analytics refresh
Recommendation refresh
GenAI execution
Metrics tracking
Scheduled retraining
Pipeline dependency management
```

---

# 6. Machine Learning Layer

## Churn Prediction

The churn prediction system estimates the likelihood of a user cancelling or becoming inactive.

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

---

## Feature Engineering

Example engineered features:

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

These features combine behavioral, engagement, and playback-quality signals.

---

## ML Models

The pipeline compares multiple machine learning models:

```text
Logistic Regression
Random Forest
Extra Trees
Gradient Boosting
```

The best model is selected using weighted evaluation metrics prioritizing:

```text
AUC
Recall
F1 Score
Precision
```

---

## Churn Outputs

The churn layer generates:

```text
churn_probability
risk_level
risk_reason
recommended_action
```

Risk levels include:

```text
Low
Medium
High
```

The system converts ML predictions into operational retention actions.

Example actions:

```text
Offer discount
Recommend trending content
Send retention campaign
Investigate playback issues
Promote personalized recommendations
```

---

## ML Automation with Airflow

Airflow automates:

```text
Feature generation
Model training
Model evaluation
Prediction refresh
Metrics tracking
Scheduled retraining
```

---

# 7. Hybrid Recommendation Engine

The recommendation engine combines multiple recommendation strategies.

Recommendation methods include:

```text
Content-based filtering
User-based collaborative filtering
Item-based collaborative filtering
Model-based matrix factorization
Country-trending fallback
Global popularity fallback
```

---

## Recommendation Explainability

Each recommendation includes explainability metadata.

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

---

## Recommendation Tables

Primary tables:

```text
recommendations
recommendation_model_metrics
```

Metrics tracked include:

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

---

## Recommendation Scheduling

Airflow schedules recommendation refresh jobs.

Automated tasks include:

```text
User similarity computation
Content embedding refresh
Hybrid score generation
Recommendation publishing
Metrics validation
```

---

# 8. Gemini GenAI Layer

The project includes a Gemini-powered GenAI intelligence layer with local fallback support.

---

## Gemini Client

File:

```text
src/genai_client.py
```

Responsibilities:

```text
Read Gemini API settings
Call Gemini models
Handle fallback generation
Manage API failures
Provide local fallback responses
```

---

## Executive Intelligence Brief

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
Convert warehouse metrics into leadership-ready intelligence summaries.
```

The executive brief covers:

* Platform activity
* Revenue signals
* Content performance
* Churn risk
* Recommendation insights
* Playback quality
* Operational concerns
* Suggested business actions

---

## Retention Campaign Generator

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
Generate personalized retention messages for medium-risk and high-risk users.
```

The campaigns combine:

```text
Churn predictions
Recommendation outputs
Engagement signals
```

---

## Content Metadata Enrichment

File:

```text
src/genai_content_enrichment.py
```

Output table:

```text
genai_content_enrichment
```

Generated metadata includes:

```text
short_summary
mood_tags
theme_tags
search_keywords
audience_segment
recommendation_blurb
```

---

## AI Analytics Copilot

The dashboard includes a natural-language analytics copilot.

The copilot maps business questions to safe read-only SQL templates.

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

Supported analytics questions include:

* Which content has the highest watch time?
* Which countries have the most engagement?
* Which devices have the worst playback quality?
* Show top recommendations.
* Show payment failures.
* Show revenue metrics.

---

## Airflow GenAI Automation

Airflow orchestrates:

```text
Executive summary generation
Retention campaign generation
Content enrichment refresh
Failure retries
Scheduled execution
Dependency management
```

---

# 9. Dashboard Documentation

The Streamlit dashboard contains multiple analytics pages.

---

## Executive Overview

Purpose:

```text
Summarize platform-level health and engagement.
```

Metrics include:

```text
Active users
Watch hours
Completion rate
Revenue
Payment failures
Daily watch trends
Country-level performance
```

---

## Content Performance

Purpose:

```text
Analyze content engagement and catalog performance.
```

Metrics include:

```text
Top titles
Watch time
Completion rate
Genre performance
Viewer touchpoints
Catalog size
```

---

## Churn Intelligence

Purpose:

```text
Identify users at risk and explain why.
```

Outputs include:

```text
Risk distribution
Highest-risk users
Model comparison
Feature importance
Retention action queue
Confusion matrix
AUC
Precision
Recall
```

---

## Recommendation Engine

Purpose:

```text
Explain personalized recommendations and hybrid scoring.
```

Outputs include:

```text
Top recommendations
Recommendation type
Hybrid score
Per-signal score breakdown
Catalog coverage
Most recommended titles
```

---

## GenAI Studio

Purpose:

```text
Show GenAI-powered business intelligence.
```

Sections include:

```text
Executive brief
Retention campaigns
Content enrichment
Analytics copilot
```

---

## Playback Quality

Purpose:

```text
Monitor playback experience and device quality.
```

Metrics include:

```text
Buffering events
Quality score
Worst-performing devices
Device-level quality metrics
```

---

## Pipeline Health

Purpose:

```text
Monitor operational pipeline health and orchestration status.
```

Metrics include:

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

# 10. Project Structure

```text
streamflix/
│
├── app/
│   └── streamlit_app.py
│
├── airflow/
│   └── dags/
│       └── streamflix_pipeline.py
│
├── consumer/
│   └── consume_events.py
│
├── producer/
│   └── produce_events.py
│
├── src/
│   ├── db.py
│   ├── seed_dimensions.py
│   ├── clean_events.py
│   ├── build_marts.py
│   ├── train_churn.py
│   ├── recommend.py
│   ├── genai_client.py
│   ├── genai_summary.py
│   ├── genai_retention_campaigns.py
│   ├── genai_content_enrichment.py
│   └── run_pipeline.py
│
├── sql/
│   └── create_tables.sql
│
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── PROJECT_DOCUMENTATION.md
└── README.md
```

---

# 11. Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/Streamflix.git
cd Streamflix
```

---

## 2. Create Environment File

Windows:

```powershell
copy .env.example .env
```

Mac/Linux:

```bash
cp .env.example .env
```

Example `.env`:

```env
POSTGRES_USER=streamflix
POSTGRES_PASSWORD=streamflix
POSTGRES_DB=streamflix
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

KAFKA_BOOTSTRAP_SERVERS=localhost:9092

USE_GEMINI=false
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

If Gemini is disabled, the project automatically uses local fallback generation.

---

## 3. Start Docker Services

```bash
docker compose up -d
```

Services started:

```text
PostgreSQL
Redpanda
Airflow
```

---

## 4. Initialize Airflow

```powershell
docker compose run airflow-init
```

---

## 5. Access Airflow UI

```text
http://localhost:8080
```

Default credentials:

```text
username: admin
password: admin
```

---

## 6. Create Python Virtual Environment

Windows:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

# 12. Running the Project

## 1. Run Producer

```powershell
.\venv\Scripts\python.exe producer\produce_events.py
```

This generates synthetic OTT events.

---

## 2. Run Consumer

```powershell
.\venv\Scripts\python.exe consumer\consume_events.py
```

This consumes Redpanda events and writes them into PostgreSQL.

---

## 3. Run Airflow Services

```powershell
docker compose up airflow-webserver airflow-scheduler -d
```

---

## 4. Run Main Pipeline

Windows:

```powershell
$env:PYTHONPATH = "C:\Users\HP\Desktop\streamflix"
.\venv\Scripts\python.exe -m src.run_pipeline
```

Mac/Linux:

```bash
export PYTHONPATH=$(pwd)
python -m src.run_pipeline
```

This executes:

```text
Cleaning
Analytics marts
Feature engineering
Churn prediction
Recommendation generation
Core analytics
```

---

## 5. Run GenAI Modules

Windows:

```powershell
$env:PYTHONPATH = "C:\Users\HP\Desktop\streamflix"
.\venv\Scripts\python.exe -m src.genai_summary
.\venv\Scripts\python.exe -m src.genai_retention_campaigns
.\venv\Scripts\python.exe -m src.genai_content_enrichment
```

Mac/Linux:

```bash
export PYTHONPATH=$(pwd)
python -m src.genai_summary
python -m src.genai_retention_campaigns
python -m src.genai_content_enrichment
```

---

## 6. Launch Dashboard

Windows:

```powershell
.\venv\Scripts\streamlit.exe run app\streamlit_app.py
```

Mac/Linux:

```bash
streamlit run app/streamlit_app.py
```

Dashboard URL:

```text
http://localhost:8501
```

---

# 13. Recommended Demo Flow

Suggested walkthrough order:

1. Show producer → Redpanda → consumer → PostgreSQL flow.
2. Open Executive Overview dashboard.
3. Demonstrate Content Performance analytics.
4. Explain Churn Intelligence and ML scoring.
5. Demonstrate Recommendation Engine outputs.
6. Show GenAI Studio and executive summaries.
7. Demonstrate AI analytics copilot.
8. End with Pipeline Health and Airflow orchestration.

---

# 14. Notes on Synthetic Data

This project uses synthetic data.

Therefore:

```text
Model scores validate workflow design rather than real-world predictive accuracy.
Recommendation outputs demonstrate recommendation architecture.
GenAI outputs demonstrate integration and business use cases.
Airflow orchestration demonstrates production-style workflow management.
The project is not trained on real customer behavior.
```

---

# 15. What This Project Demonstrates

This project demonstrates practical capability in:

```text
Data engineering
Kafka-compatible event streaming
PostgreSQL warehouse design
Workflow orchestration with Apache Airflow
ETL and analytics engineering
Feature engineering
Machine learning pipelines
Churn prediction
Recommendation systems
Collaborative filtering
Content-based filtering
Matrix factorization
Gemini API integration
GenAI business intelligence
Dashboard development
Operational monitoring
Business-facing analytics storytelling
Production-style workflow management
```

---

# 16. Future Improvements

Planned enhancements:

```text
Add dbt transformations
Add MLflow experiment tracking
Add Great Expectations or Soda data
```
