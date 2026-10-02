# Production Readiness Assessment

## Current implementation

The backend can ingest a supported dataset, create an LLM-backed analysis plan, execute read-only DuckDB SQL and selected deterministic Python operations, validate results, choose a chart specification, and return a concise execution summary. Uploads are streamed to local storage and malformed uploads are removed before an ID is returned. SQL is restricted to a single read-only statement and result rows are capped in DuckDB.

## Important remaining work

This repository is not production-ready yet. Complete these controls before handling real customer data:

- Implement authentication, tenant isolation, and RBAC before exposing dataset or analysis endpoints.
- Replace local uploads with private object storage and persist metadata, ownership, and analysis history in PostgreSQL.
- Replace keyword SQL screening with a parser/AST allowlist and enforce query time, memory, and concurrency limits at the execution boundary.
- Move analysis and report generation to workers with a queue, cancellation, idempotency, and durable run status.
- Use LLM structured outputs backed by versioned Pydantic schemas; add prompt, tool-call, and result audit records.
- Run arbitrary Python only in a network-isolated sandbox with CPU, memory, filesystem, process, and execution-time limits.
- Add rate limiting, CSRF/CORS policy, secure headers, secret management, dependency scanning, telemetry, alerting, backups, and disaster-recovery exercises.
- Build the planned Next.js frontend and end-to-end browser tests.

## Release gates

Production release requires an authenticated end-to-end test suite, security testing for uploads/SQL/sandbox escapes, performance benchmarks with defined SLOs, database migrations and backups, observability dashboards and alerts, and a deployment runbook with rollback procedures.
