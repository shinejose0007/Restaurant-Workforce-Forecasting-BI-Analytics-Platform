"""Build the complete local project data pipeline.

Run:
    python scripts/build_all.py
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_DATA_PATH, FEATURE_DATA_PATH, PREDICTIONS_PATH, POWERBI_DIR
from src.generate_data import GenerationConfig, generate_restaurant_data
from src.prepare_features import prepare_features
from src.train_model import train_model
from src.recommendations import generate_recommendations
from src.powerbi_export import export_powerbi_tables


def main():
    print("Step 1/5: Generating synthetic restaurant operations data...")
    df = generate_restaurant_data(GenerationConfig(n_restaurants=60, start_date="2024-01-01", end_date="2024-12-31"))
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"  -> {RAW_DATA_PATH} ({len(df):,} rows)")

    print("Step 2/5: Preparing features...")
    feat = prepare_features(RAW_DATA_PATH, FEATURE_DATA_PATH)
    print(f"  -> {FEATURE_DATA_PATH} ({feat.shape[0]:,} rows, {feat.shape[1]} columns)")

    print("Step 3/5: Training forecasting model...")
    train_model(FEATURE_DATA_PATH)
    print(f"  -> {PREDICTIONS_PATH}")

    print("Step 4/5: Generating recommendations...")
    generate_recommendations()

    print("Step 5/5: Exporting Power BI tables...")
    export_powerbi_tables()
    print(f"  -> {POWERBI_DIR}")

    print("\nBuild complete. Start the dashboard with:")
    print("streamlit run app/streamlit_app.py")


if __name__ == "__main__":
    main()
