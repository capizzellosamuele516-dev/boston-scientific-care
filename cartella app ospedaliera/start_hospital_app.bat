@echo off
cd /d C:\Users\user\Desktop\cartella app ospedaliera

REM (se hai una virtualenv)
REM call venv\Scripts\activate

REM Avvia backend FastAPI sulla porta 9000 in una nuova finestra
start "" uvicorn app:app --port 9000

REM Avvia la UI Streamlit (rimane in questa finestra)
streamlit run ui.py
