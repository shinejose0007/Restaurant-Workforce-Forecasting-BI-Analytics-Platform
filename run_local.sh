#!/usr/bin/env bash
set -e

echo "=============================================="
echo "Restaurant Workforce Forecasting Analytics App"
echo "=============================================="

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_all.py
streamlit run app/streamlit_app.py
