@echo off
REM filepath: c:\Users\YOGA\project\otomax\mod-apiparser\start.bat

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

REM =============================================================================
REM FUTURE FEATURES (COMMENTED OUT - ADD WHEN NEEDED)
REM =============================================================================

REM Future: Environment validation before startup
REM echo [*] Validating environment configuration...
REM uv run scripts/env_input.py validate
REM IF %ERRORLEVEL% NEQ 0 (
REM     echo [!] Environment validation failed.
REM     exit /b %ERRORLEVEL%
REM )

REM Future: Automatic backup of current config before updates
REM echo [*] Creating configuration backup...
REM uv run scripts/env_input.py backup

REM Future: Key rotation check (weekly/monthly)
REM echo [*] Checking if key rotation is needed...
REM uv run scripts/env_input.py check-key-rotation
REM IF %ERRORLEVEL% EQU 2 (
REM     echo [!] Keys need rotation. Run: uv run scripts/env_input.py rotate-keys
REM )

REM Future: Database migration (when switching from YAML to DB)
REM echo [*] Running database migrations...
REM uv run scripts/migrate.py
REM IF %ERRORLEVEL% NEQ 0 (
REM     echo [!] Database migration failed.
REM     exit /b %ERRORLEVEL%
REM )

REM Future: Health check before startup
REM echo [*] Running pre-startup health checks...
REM uv run scripts/health_check.py
REM IF %ERRORLEVEL% NEQ 0 (
REM     echo [!] Health check failed. Check logs.
REM     exit /b %ERRORLEVEL%
REM )

REM Future: Load testing configuration (for production)
REM if "%APP_ENV%"=="production" (
REM     echo [*] Loading production optimizations...
REM     uv run scripts/prod_optimize.py
REM )

REM Future: Automatic SSL certificate check (for production HTTPS)
REM if "%APP_ENV%"=="production" (
REM     echo [*] Checking SSL certificates...
REM     uv run scripts/ssl_check.py
REM     IF %ERRORLEVEL% NEQ 0 (
REM         echo [!] SSL certificate issues detected.
REM     )
REM )

REM Future: Monitor and logging setup
REM echo [*] Initializing monitoring and logging...
REM uv run scripts/setup_monitoring.py

REM Future: Container deployment (Docker/Podman)
REM if "%DEPLOY_MODE%"=="container" (
REM     echo [*] Starting in container mode...
REM     docker-compose up -d
REM     exit /b %ERRORLEVEL%
REM )

REM Future: Multi-instance setup (load balancer)
REM if "%APP_ENV%"=="production" (
REM     if "%MULTI_INSTANCE%"=="true" (
REM         echo [*] Starting multiple instances...
REM         start "Instance-1" uv run uvicorn src.main:app --host 0.0.0.0 --port 8001
REM         start "Instance-2" uv run uvicorn src.main:app --host 0.0.0.0 --port 8002
REM         start "Instance-3" uv run uvicorn src.main:app --host 0.0.0.0 --port 8003
REM         echo [*] Load balancer on port 8000...
REM         uv run uvicorn src.load_balancer:app --host 0.0.0.0 --port 8000
REM     )
REM )

REM Future: Development tools (auto-restart on file changes)
REM if "%APP_ENV%"=="development" (
REM     if "%DEV_TOOLS%"=="enabled" (
REM         echo [*] Starting with development tools...
REM         start "Hot-Reload" uv run watchdog --reload
REM         start "Type-Check" uv run mypy --watch
REM         start "Format-Check" uv run ruff check --watch
REM     )
REM )

REM Future: Performance profiling (development)
REM if "%PROFILING%"=="enabled" (
REM     echo [*] Starting with profiling enabled...
REM     uv run py-spy record -o profile.svg -- python -m uvicorn src.main:app
REM )

REM Future: Test runner before startup (CI/CD integration)
REM if "%RUN_TESTS%"=="true" (
REM     echo [*] Running test suite...
REM     uv run pytest
REM     IF %ERRORLEVEL% NEQ 0 (
REM         echo [!] Tests failed. Aborting startup.
REM         exit /b %ERRORLEVEL%
REM     )
REM )
