# Windows run guide

1. Install Docker Desktop.
2. Install Python 3.11.
3. Open Docker Desktop and keep it running.
4. Open PowerShell in the project folder.

```powershell
copy .env.example .env
docker compose up -d
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Open terminal 1:

```powershell
venv\Scripts\activate
python producer/produce_events.py
```

Open terminal 2:

```powershell
venv\Scripts\activate
python consumer/consume_events.py
```

After 2-5 minutes, open terminal 3:

```powershell
venv\Scripts\activate
python src/run_pipeline.py
streamlit run app/streamlit_app.py
```

Airflow is available at:

```text
http://localhost:8080
admin / admin
```
