@echo off
REM filepath:

REM Step 0: Check if uv is installed
uv --version >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [!] 'uv' is not installed or not in PATH.
    exit /b 1
)

REM Step 1: Setup virtual env & sync
echo [*] Setting up virtual environment...
uv sync
IF %ERRORLEVEL% NEQ 0 (
    echo [!] Failed to sync virtual environment.
    exit /b %ERRORLEVEL%
)

REM Step 2: Run enhanced env setup (only if needed)
echo [*] Checking environment configuration...
uv run scripts/env_input.py show-info
uv run scripts/env_input.py env-setup
IF %ERRORLEVEL% NEQ 0 (
    echo [!] Environment setup failed.
    exit /b %ERRORLEVEL%
)

REM Step 3: Create secrets directory if not exists
if not exist "secrets\keys" mkdir "secrets\keys"

REM Step 4: Set development environment (default)
if not defined APP_ENV set APP_ENV=development

REM Step 5: Start application based on environment
echo [*] Starting application in %APP_ENV% mode...
if "%APP_ENV%"=="production" (
    echo [*] Starting in production mode...
    uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
) else (
    echo [*] Starting in development mode...
    uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
)
