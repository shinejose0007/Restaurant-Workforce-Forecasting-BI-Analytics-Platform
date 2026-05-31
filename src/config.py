from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
POWERBI_DIR = PROJECT_ROOT / "powerbi"
MODELS_DIR = PROJECT_ROOT / "models"

RAW_DATA_PATH = DATA_RAW_DIR / "synthetic_restaurant_operations.csv"
FEATURE_DATA_PATH = DATA_PROCESSED_DIR / "restaurant_features.csv"
PREDICTIONS_PATH = DATA_PROCESSED_DIR / "restaurant_predictions.csv"
RECOMMENDATIONS_PATH = DATA_PROCESSED_DIR / "staffing_recommendations.csv"
MODEL_PATH = MODELS_DIR / "revenue_forecast_model.joblib"
METRICS_PATH = DATA_PROCESSED_DIR / "model_metrics.csv"

RANDOM_SEED = 42
