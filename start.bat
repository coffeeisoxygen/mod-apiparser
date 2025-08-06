@echo off
set ENV_PATH=.env.example

REM Step 0: Check if uv is installed
uv --version >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [!] 'uv' is not installed or not in PATH.
    exit /b 1
)

REM Step 1: Setup virtual env & sync
uv sync
IF %ERRORLEVEL% NEQ 0 (
    echo [!] Failed to sync virtual environment.
    exit /b %ERRORLEVEL%
)

REM Step 2: Run env_checker (always run)
uv run scripts/env_input.py
IF %ERRORLEVEL% NEQ 0 (
    echo [!] env_checker.py failed.
    exit /b %ERRORLEVEL%
)

REM check apakah accounts.yaml sudah ada, jika belum buat,
REM Step 3: Jalankan FastAPI in development mode
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

REM Untuk priduction mode, uncomment the following line:
REM uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
