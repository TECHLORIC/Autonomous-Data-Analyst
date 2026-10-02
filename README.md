## Autonomous Data Analyst

Autonomous Data Analyst is a full-stack SaaS platform for answering natural-language questions over user-uploaded CSV, XLSX, and JSON datasets. The application utilizes a LangGraph orchestrator to autonomously generate constrained execution plans, utilizing read-only DuckDB for SQL analysis and a secure, isolated Docker Sandbox for advanced Machine Learning (Python).

### Current status

The application is **Production-Ready**. It supports:
- Next.js React Frontend UI.
- FastAPI backend with JWT Authentication.
- Secure, containerized Python Sandbox with `scikit-learn` and `statsmodels`.
- Celery background workers and Redis queues for asynchronous analysis.
- Object Storage (S/ 3 Local storage fallback).
- Advanced Analytics Report Generation (HTML).
- Enterprise Observability (Prometheus Metrics & JSON Structured Logging).
- Security Hardening (SlowAPI Rate Limiting, HTTP Host checking).

### Run Locally (Development)

1. Copy `.env.example` to `.env` and set `GROQ_API_KEY` and a strong `POSTGRES_PASSWORD`.
2. Run `docker compose up --build`.
3. Open the FastAPI documentation at `http://localhost:8000/docs`.

### Deploying to Production

The platform is fully containerized for deployment on any Docker-compatible server (AWS EC2, DigitalOcean, etc.).

1. Copy `.env.example` to `.env` and set `GROQ_API_KEY`, `POSTGRES_PASSWORD`, and your `JWT_SECRET`.
2. Start the distributed system:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```
3. The Next.js frontend is available on port `3000`. The FastAPI backend is on port `8000`. Prometheus metrics are available at `http://localhost:8000/metrics`.

### Verification

GitHub Actions automatically runs `ruff` linting, `pytest`, and Next.js frontend builds on all pushes to `main`. To run locally:
- Backend: `cd backend && pytest`
- Frontend: `cd frontend && npm run lint && npm run build`
