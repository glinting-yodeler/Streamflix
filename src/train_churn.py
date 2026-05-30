from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy import text
from src.db import get_engine

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_DIR.mkdir(exist_ok=True)

ACTIONS = {
    "High": "Offer discount and recommend high-completion content",
    "Medium": "Send personalized content recommendations",
    "Low": "No immediate retention action needed",
}


def risk_level(prob):
    if prob >= 0.65:
        return "High"
    if prob >= 0.35:
        return "Medium"
    return "Low"


def main():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM user_features", engine)
    if df.empty or df["churn_label"].nunique() < 2:
        print("Not enough labeled user feature data to train churn model.")
        return

    features = [
        "country", "subscription_plan", "subscription_age_days", "total_watch_minutes",
        "watch_events", "avg_completion_rate", "days_since_last_watch",
        "buffering_count", "payment_failed_count", "num_genres_watched"
    ]
    X = df[features]
    y = df["churn_label"].astype(int)

    numeric = [c for c in features if c not in ["country", "subscription_plan"]]
    categorical = ["country", "subscription_plan"]
    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ])
    model = Pipeline([
        ("preprocess", pre),
        ("classifier", RandomForestClassifier(n_estimators=120, random_state=42, class_weight="balanced")),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, preds, average="binary", zero_division=0)
    try:
        auc = roc_auc_score(y_test, probs)
    except Exception:
        auc = 0
    metrics = {
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "auc": auc,
    }
    joblib.dump({"model": model, "features": features, "metrics": metrics}, MODEL_DIR / "churn_model.pkl")

    all_probs = model.predict_proba(X)[:, 1]
    out = pd.DataFrame({
        "user_id": df["user_id"],
        "churn_probability": all_probs,
    })
    out["risk_level"] = out["churn_probability"].apply(risk_level)
    out["recommended_action"] = out["risk_level"].map(ACTIONS)

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE churn_predictions"))
    out.to_sql("churn_predictions", engine, if_exists="append", index=False)
    print("Trained churn model and saved churn_predictions")
    print(metrics)


if __name__ == "__main__":
    main()
