from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.calibration import CalibratedClassifierCV

from sqlalchemy import text
from src.db import get_engine

warnings.filterwarnings("ignore")

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "churn_model.pkl"

RANDOM_STATE = 42


# ============================================================
# BUSINESS ACTIONS
# ============================================================

ACTIONS = {
    "High": "Offer discount + recommend high-completion content + monitor playback issues",
    "Medium": "Send personalized recommendations + remind user about trending content",
    "Low": "No immediate retention action needed",
}


def risk_level(prob):
    if prob >= 0.70:
        return "High"
    if prob >= 0.40:
        return "Medium"
    return "Low"


def risk_reason(row):
    reasons = []

    if row.get("days_since_last_watch", 0) >= 10:
        reasons.append("inactive for many days")

    if row.get("total_watch_minutes", 0) < 120:
        reasons.append("low watch time")

    if row.get("avg_completion_rate", 0) < 0.45:
        reasons.append("low content completion")

    if row.get("payment_failed_count", 0) >= 1:
        reasons.append("payment failure detected")

    if row.get("buffering_count", 0) >= 3:
        reasons.append("high buffering experience")

    if row.get("num_genres_watched", 0) <= 1:
        reasons.append("limited genre engagement")

    if len(reasons) == 0:
        return "healthy engagement pattern"

    return ", ".join(reasons[:3])


def recommended_action(row):
    risk = row.get("risk_level", "Low")
    reason = row.get("risk_reason", "")

    if risk == "High":
        if "payment failure" in reason:
            return "Trigger payment recovery flow and offer temporary discount"
        if "buffering" in reason:
            return "Prioritize playback-quality support and recommend shorter high-completion titles"
        if "inactive" in reason:
            return "Send win-back notification with trending local content"
        return ACTIONS["High"]

    if risk == "Medium":
        if "limited genre" in reason:
            return "Recommend content from adjacent genres to broaden engagement"
        if "low content completion" in reason:
            return "Recommend shorter high-completion content"
        return ACTIONS["Medium"]

    return ACTIONS["Low"]


# ============================================================
# DATABASE HELPERS
# ============================================================

def ensure_ml_tables(engine):
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS churn_model_metrics (
                id SERIAL PRIMARY KEY,
                model_name TEXT,
                accuracy DOUBLE PRECISION,
                precision_score DOUBLE PRECISION,
                recall DOUBLE PRECISION,
                f1 DOUBLE PRECISION,
                auc DOUBLE PRECISION,
                true_negatives INTEGER,
                false_positives INTEGER,
                false_negatives INTEGER,
                true_positives INTEGER,
                selected_model BOOLEAN,
                trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS churn_feature_importance (
                id SERIAL PRIMARY KEY,
                feature_name TEXT,
                importance DOUBLE PRECISION,
                model_name TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))


def reset_ml_tables(engine):
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE churn_predictions"))
        conn.execute(text("TRUNCATE TABLE churn_model_metrics"))
        conn.execute(text("TRUNCATE TABLE churn_feature_importance"))


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def prepare_features(df):
    df = df.copy()

    numeric_defaults = {
        "subscription_age_days": 0,
        "total_watch_minutes": 0,
        "watch_events": 0,
        "avg_completion_rate": 0,
        "days_since_last_watch": 999,
        "buffering_count": 0,
        "payment_failed_count": 0,
        "num_genres_watched": 0,
    }

    categorical_defaults = {
        "country": "Unknown",
        "subscription_plan": "Unknown",
    }

    for col, default in numeric_defaults.items():
        if col not in df.columns:
            df[col] = default
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)

    for col, default in categorical_defaults.items():
        if col not in df.columns:
            df[col] = default
        df[col] = df[col].fillna(default).astype(str)

    # Extra engineered features
    df["watch_hours"] = df["total_watch_minutes"] / 60
    df["watch_events_per_day"] = df["watch_events"] / (df["subscription_age_days"] + 1)
    df["minutes_per_event"] = df["total_watch_minutes"] / (df["watch_events"] + 1)
    df["buffering_per_hour"] = df["buffering_count"] / (df["watch_hours"] + 1)
    df["payment_failure_rate"] = df["payment_failed_count"] / (df["subscription_age_days"] + 1)
    df["engagement_score"] = (
        df["watch_hours"] * 0.35
        + df["watch_events"] * 0.20
        + df["avg_completion_rate"] * 100 * 0.25
        + df["num_genres_watched"] * 0.20
    )
    df["friction_score"] = (
        df["days_since_last_watch"] * 0.35
        + df["buffering_count"] * 1.7
        + df["payment_failed_count"] * 5
    )
    df["completion_x_watch"] = df["avg_completion_rate"] * df["watch_hours"]

    features = [
        "country",
        "subscription_plan",
        "subscription_age_days",
        "total_watch_minutes",
        "watch_events",
        "avg_completion_rate",
        "days_since_last_watch",
        "buffering_count",
        "payment_failed_count",
        "num_genres_watched",
        "watch_hours",
        "watch_events_per_day",
        "minutes_per_event",
        "buffering_per_hour",
        "payment_failure_rate",
        "engagement_score",
        "friction_score",
        "completion_x_watch",
    ]

    numeric_features = [
        "subscription_age_days",
        "total_watch_minutes",
        "watch_events",
        "avg_completion_rate",
        "days_since_last_watch",
        "buffering_count",
        "payment_failed_count",
        "num_genres_watched",
        "watch_hours",
        "watch_events_per_day",
        "minutes_per_event",
        "buffering_per_hour",
        "payment_failure_rate",
        "engagement_score",
        "friction_score",
        "completion_x_watch",
    ]

    categorical_features = [
        "country",
        "subscription_plan",
    ]

    return df, features, numeric_features, categorical_features


# ============================================================
# MODEL BUILDING
# ============================================================

def build_preprocessor(numeric_features, categorical_features):
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    return ColumnTransformer([
        ("num", numeric_pipe, numeric_features),
        ("cat", categorical_pipe, categorical_features),
    ])


def candidate_models():
    return {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=250,
            max_depth=None,
            min_samples_split=4,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=250,
            max_depth=None,
            min_samples_split=4,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=180,
            learning_rate=0.045,
            max_depth=3,
            random_state=RANDOM_STATE,
        ),
    }


def evaluate_model(model, X_test, y_test):
    preds = model.predict(X_test)

    try:
        probs = model.predict_proba(X_test)[:, 1]
    except Exception:
        probs = preds

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test,
        preds,
        average="binary",
        zero_division=0,
    )

    try:
        auc = roc_auc_score(y_test, probs)
    except Exception:
        auc = 0

    tn, fp, fn, tp = confusion_matrix(y_test, preds, labels=[0, 1]).ravel()

    return {
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision_score": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "auc": float(auc),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
    }


def select_best_model(results):
    # In churn, AUC and recall matter a lot.
    # Missing churners is usually more costly than flagging some extra users.
    best_name = None
    best_score = -1

    for name, result in results.items():
        m = result["metrics"]
        score = (
            m["auc"] * 0.40
            + m["recall"] * 0.30
            + m["f1"] * 0.20
            + m["precision_score"] * 0.10
        )

        if score > best_score:
            best_score = score
            best_name = name

    return best_name


def get_feature_names(model, numeric_features, categorical_features):
    preprocessor = model.named_steps["preprocess"]

    feature_names = []

    feature_names.extend(numeric_features)

    try:
        cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
        cat_names = cat_encoder.get_feature_names_out(categorical_features)
        feature_names.extend(list(cat_names))
    except Exception:
        feature_names.extend(categorical_features)

    return feature_names


def extract_feature_importance(best_model, best_model_name, numeric_features, categorical_features):
    feature_names = get_feature_names(best_model, numeric_features, categorical_features)
    classifier = best_model.named_steps["classifier"]

    if hasattr(classifier, "feature_importances_"):
        importances = classifier.feature_importances_
    elif hasattr(classifier, "coef_"):
        importances = np.abs(classifier.coef_[0])
    else:
        importances = np.zeros(len(feature_names))

    if len(importances) != len(feature_names):
        min_len = min(len(importances), len(feature_names))
        importances = importances[:min_len]
        feature_names = feature_names[:min_len]

    out = pd.DataFrame({
        "feature_name": feature_names,
        "importance": importances,
        "model_name": best_model_name,
    })

    out = out.sort_values("importance", ascending=False)

    if out["importance"].sum() > 0:
        out["importance"] = out["importance"] / out["importance"].sum()

    return out.head(30)


# ============================================================
# MAIN TRAINING PIPELINE
# ============================================================

def main():
    engine = get_engine()
    ensure_ml_tables(engine)

    df = pd.read_sql("SELECT * FROM user_features", engine)

    if df.empty:
        print("No user_features found. Run the feature engineering pipeline first.")
        return

    if "churn_label" not in df.columns:
        print("churn_label column missing from user_features.")
        return

    if df["churn_label"].nunique() < 2:
        print("Not enough label variety to train churn model.")
        return

    df, features, numeric_features, categorical_features = prepare_features(df)

    X = df[features]
    y = df["churn_label"].astype(int)

    if len(df) < 20:
        print("Warning: very small dataset. Model will train, but metrics may not be reliable.")

    test_size = 0.25
    if len(df) < 30:
        test_size = 0.30

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    preprocessor = build_preprocessor(numeric_features, categorical_features)

    results = {}

    for name, clf in candidate_models().items():
        print(f"Training candidate model: {name}")

        model = Pipeline([
            ("preprocess", preprocessor),
            ("classifier", clf),
        ])

        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)

        results[name] = {
            "model": model,
            "metrics": metrics,
        }

        print(name, metrics)

    best_model_name = select_best_model(results)
    best_model = results[best_model_name]["model"]
    best_metrics = results[best_model_name]["metrics"]

    print(f"Selected best model: {best_model_name}")
    print(best_metrics)

    # Calibrate probabilities if dataset is large enough.
    # If the dataset is small, calibration can fail or overfit, so we keep raw model.
    calibrated_model = best_model
    if len(df) >= 80 and y.nunique() == 2:
        try:
            print("Calibrating probability outputs...")
            calibrated_model = CalibratedClassifierCV(
                estimator=best_model,
                method="sigmoid",
                cv=3,
            )
            calibrated_model.fit(X_train, y_train)
        except Exception as exc:
            print(f"Calibration skipped: {exc}")
            calibrated_model = best_model

    # Predict all users
    try:
        all_probs = calibrated_model.predict_proba(X)[:, 1]
    except Exception:
        all_probs = best_model.predict_proba(X)[:, 1]

    prediction_df = df.copy()
    prediction_df["churn_probability"] = all_probs
    prediction_df["risk_level"] = prediction_df["churn_probability"].apply(risk_level)
    prediction_df["risk_reason"] = prediction_df.apply(risk_reason, axis=1)
    prediction_df["recommended_action"] = prediction_df.apply(recommended_action, axis=1)

    out = prediction_df[[
        "user_id",
        "churn_probability",
        "risk_level",
        "recommended_action",
        "risk_reason",
        "country",
        "subscription_plan",
        "days_since_last_watch",
        "total_watch_minutes",
        "avg_completion_rate",
        "buffering_count",
        "payment_failed_count",
        "num_genres_watched",
        "engagement_score",
        "friction_score",
    ]].copy()

    metrics_rows = []
    for name, result in results.items():
        row = result["metrics"].copy()
        row["model_name"] = name
        row["selected_model"] = name == best_model_name
        metrics_rows.append(row)

    metrics_df = pd.DataFrame(metrics_rows)

    importance_df = extract_feature_importance(
        best_model,
        best_model_name,
        numeric_features,
        categorical_features,
    )

    model_package = {
        "model": calibrated_model,
        "base_model": best_model,
        "best_model_name": best_model_name,
        "features": features,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "metrics": best_metrics,
        "all_candidate_metrics": {
            name: result["metrics"]
            for name, result in results.items()
        },
        "risk_thresholds": {
            "high": 0.70,
            "medium": 0.40,
        },
    }

    joblib.dump(model_package, MODEL_PATH)

    reset_ml_tables(engine)

    out.to_sql("churn_predictions", engine, if_exists="append", index=False)
    metrics_df.to_sql("churn_model_metrics", engine, if_exists="append", index=False)
    importance_df.to_sql("churn_feature_importance", engine, if_exists="append", index=False)

    print("==============================================")
    print("Churn model training complete")
    print(f"Best model: {best_model_name}")
    print(json.dumps(best_metrics, indent=2))
    print(f"Saved model to: {MODEL_PATH}")
    print("Saved tables:")
    print("- churn_predictions")
    print("- churn_model_metrics")
    print("- churn_feature_importance")
    print("==============================================")


if __name__ == "__main__":
    main()