CREATE TABLE IF NOT EXISTS users_dim (
    user_id TEXT PRIMARY KEY,
    country TEXT NOT NULL,
    age_group TEXT NOT NULL,
    subscription_plan TEXT NOT NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS content_dim (
    content_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    language TEXT NOT NULL,
    duration_minutes INT NOT NULL,
    release_year INT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_events (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    user_id TEXT,
    content_id TEXT,
    country TEXT,
    device TEXT,
    event_timestamp TIMESTAMP NOT NULL,
    event_payload JSONB NOT NULL,
    inserted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clean_watch_events (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    content_id TEXT NOT NULL,
    country TEXT NOT NULL,
    device TEXT NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    watch_minutes FLOAT NOT NULL,
    completion_rate FLOAT NOT NULL,
    buffering_count INT NOT NULL,
    quality_score FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS clean_business_events (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    country TEXT NOT NULL,
    device TEXT NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    amount FLOAT DEFAULT 0,
    search_query TEXT DEFAULT '',
    status TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS daily_metrics (
    metric_date DATE PRIMARY KEY,
    active_users INT,
    total_watch_minutes FLOAT,
    avg_completion_rate FLOAT,
    total_revenue FLOAT,
    payment_failures INT,
    buffering_events INT,
    generated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS content_performance (
    content_id TEXT PRIMARY KEY,
    title TEXT,
    genre TEXT,
    language TEXT,
    total_watch_minutes FLOAT,
    unique_viewers INT,
    avg_completion_rate FLOAT,
    popularity_score FLOAT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS country_metrics (
    country TEXT PRIMARY KEY,
    active_users INT,
    total_watch_minutes FLOAT,
    avg_completion_rate FLOAT,
    total_revenue FLOAT,
    buffering_events INT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS device_quality_metrics (
    device TEXT PRIMARY KEY,
    total_events INT,
    total_buffering_events INT,
    avg_quality_score FLOAT,
    avg_completion_rate FLOAT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_features (
    user_id TEXT PRIMARY KEY,
    country TEXT,
    subscription_plan TEXT,
    subscription_age_days INT,
    total_watch_minutes FLOAT,
    watch_events INT,
    avg_completion_rate FLOAT,
    days_since_last_watch INT,
    buffering_count INT,
    payment_failed_count INT,
    num_genres_watched INT,
    churn_label INT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS churn_predictions (
    user_id TEXT PRIMARY KEY,
    churn_probability FLOAT NOT NULL,
    risk_level TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    predicted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recommendations (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    content_id TEXT NOT NULL,
    title TEXT NOT NULL,
    reason TEXT NOT NULL,
    score FLOAT NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS executive_summaries (
    id BIGSERIAL PRIMARY KEY,
    summary_date DATE NOT NULL,
    summary_text TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW()
);
