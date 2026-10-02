@echo off
echo =======================================================
echo     Initializing Autonomous Data Analyst Stack
echo =======================================================
echo.

if not exist .env (
    echo [INFO] .env file not found, creating from .env.example...
    copy .env.example .env
    echo [WARNING] Please ensure you update GROQ_API_KEY and passwords in .env
)

echo [INFO] Building and starting Docker containers...
docker compose -f docker-compose.prod.yml up -d --build

echo.
echo [INFO] Waiting for backend and database to become ready...
timeout /t 15 /nobreak > nul

echo.
echo [INFO] Running database migrations...
docker exec autonomous-data-analyst-backend alembic upgrade head

echo.
echo =======================================================
echo     Initialization Complete!
echo =======================================================
echo Frontend Application: http://localhost:3000
echo Backend API Docs:     http://localhost:8000/docs
echo Prometheus Metrics:   http://localhost:8000/metrics
echo.
pause
