# StreamFlix DE

**StreamFlix DE** is a STARZPLAY-inspired data engineering portfolio project for an OTT/video-streaming platform.

It simulates watch events, searches, payments, subscription changes, and playback-quality events. The project streams events through **Kafka-compatible Redpanda**, stores raw data in **PostgreSQL**, orchestrates ETL/ML jobs with **Airflow**, and visualizes insights in a **Streamlit dashboard**.

## What this project shows

- Kafka-style event-driven ingestion
- Raw event storage in PostgreSQL
- Airflow orchestration for ETL, analytics, ML, recommendations, and summaries
- Data cleaning and dimensional-style analytics marts
- Churn prediction using scikit-learn
- Recommendation generation using content and country trends
- GenAI-style executive summary generation with a free template fallback
- Streamlit dashboard for OTT business insights

## Architecture

```text
Synthetic OTT Event Producer
        ↓
Redpanda / Kafka topic: streamflix_events
        ↓
Python Kafka Consumer
        ↓
PostgreSQL raw_events
        ↓
Airflow DAG: streamflix_daily_pipeline
        ↓
clean_events → build_marts → train_churn → recommend → genai_summary
        ↓
PostgreSQL analytics tables
        ↓
Streamlit Dashboard
```

## Project structure

```text
streamflix-de/
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
├── producer/
│   └── produce_events.py
├── consumer/
│   └── consume_events.py
├── sql/
│   └── create_tables.sql
├── src/
│   ├── db.py
│   ├── seed_dimensions.py
│   ├── clean_events.py
│   ├── build_marts.py
│   ├── train_churn.py
│   ├── recommend.py
│   ├── genai_summary.py
│   └── run_pipeline.py
├── airflow/
│   └── dags/
│       └── streamflix_pipeline.py
├── app/
│   └── streamlit_app.py
├── models/
├── data/
│   └── processed/
└── screenshots/
```

---

# What you need to install

## Required

1. **Docker Desktop**
   - Required for Redpanda/Kafka, PostgreSQL, and Airflow.
   - Keep Docker Desktop running before using `docker compose`.

2. **Python 3.10 or 3.11**
   - Python 3.11 is recommended.

3. **Git**
   - Optional, but useful if you upload this to GitHub.

4. **VS Code**
   - Optional, but recommended.

## Not required

You do **not** need paid subscriptions for the core project.

The project uses a free template-based executive summary by default. You can later plug in OpenAI/Gemini/Ollama if you want, but it is not required.

---

# Quick start

## 1. Unzip the project

Unzip this folder anywhere, for example:

```text
Desktop/streamflix-de
```

Open a terminal in the project folder.

## 2. Copy environment file

### Windows PowerShell

```powershell
copy .env.example .env
```

### Mac/Linux

```bash
cp .env.example .env
```

## 3. Start Docker services

```bash
docker compose up -d
```

This starts:

- Redpanda/Kafka on `localhost:9092`
- PostgreSQL on `localhost:5432`
- Airflow UI on `localhost:8080`

Wait 1-2 minutes for Airflow to fully start.

## 4. Create a Python virtual environment

### Windows PowerShell

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Start producing OTT events

Open terminal 1:

```bash
python producer/produce_events.py
```

You should see events being sent to Kafka.

## 6. Start consuming events into PostgreSQL

Open terminal 2:

```bash
python consumer/consume_events.py
```

Let producer and consumer run for 2-5 minutes. You should see inserted events.

## 7. Run the pipeline

You have two options.

### Option A: Run manually from terminal

This is easiest for demos:

```bash
python src/run_pipeline.py
```

### Option B: Run with Airflow

Open:

```text
http://localhost:8080
```

Login:

```text
username: admin
password: admin
```

Find and trigger:

```text
streamflix_daily_pipeline
```

## 8. Run the dashboard

Open terminal 3:

```bash
streamlit run app/streamlit_app.py
```

The dashboard opens at:

```text
http://localhost:8501
```

---

# Dashboard pages

The Streamlit dashboard includes:

1. **Overview**
   - total users
   - active users
   - total watch hours
   - revenue
   - payment failures
   - buffering events

2. **Content Analytics**
   - top content by watch minutes
   - completion rate
   - genre and language performance

3. **Churn + Recommendations**
   - churn probability
   - high-risk users
   - suggested retention actions
   - recommended content

4. **Playback Quality**
   - buffering by device
   - playback quality by country/device

5. **Executive Summary**
   - automated business summary generated from analytics metrics

---

# Common commands

## Stop all services

```bash
docker compose down
```

## Stop and delete database volumes

Use this only if you want a clean reset:

```bash
docker compose down -v
```

## Rebuild/restart everything

```bash
docker compose down
docker compose up -d
```

## Run pipeline manually

```bash
python src/run_pipeline.py
```

## Run dashboard

```bash
streamlit run app/streamlit_app.py
```

---

# Demo flow for interview / LinkedIn video

1. Show the architecture diagram in README.
2. Start Docker services.
3. Run producer to show streaming events.
4. Run consumer to show data landing in PostgreSQL.
5. Trigger Airflow DAG.
6. Open Streamlit dashboard.
7. Show churn predictions and recommendations.
8. Show executive summary.

---

# STARZPLAY relevance

This project is relevant to streaming companies because it models common OTT problems:

- user watch behavior
- content performance
- subscription retention
- payment failures
- playback quality
- churn prediction
- recommendations
- executive reporting

---

# Resume bullet

> Built **StreamFlix DE**, a STARZPLAY-inspired data engineering project using Kafka-compatible Redpanda, Airflow, PostgreSQL, Python, and Streamlit; implemented event-driven ingestion for OTT watch/search/payment/playback events, scheduled ETL pipelines, engineered analytics features, trained a churn prediction model, generated recommendations, and visualized streaming business insights through an interactive dashboard.

---

# Future improvements

- Add dbt for warehouse modeling
- Add Spark for distributed batch processing
- Add MLflow for model tracking
- Add real LLM API integration for executive summaries
- Add Superset/Metabase dashboards
- Add GitHub Actions CI/CD
- Deploy dashboard to a cloud VM
