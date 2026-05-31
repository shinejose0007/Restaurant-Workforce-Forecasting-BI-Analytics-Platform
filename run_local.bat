@echo off
echo ==============================================
echo Restaurant Workforce Forecasting Analytics App
echo ==============================================

IF NOT EXIST .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo Building data, model and Power BI exports...
python scripts\build_all.py

echo Starting Streamlit app...
streamlit run app\streamlit_app.py
pause
