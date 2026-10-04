# JARVIS server

This is the initial API and database skeleton for the JARVIS platform.

## Features included in this milestone

- FastAPI application skeleton
- SQLite-backed local database configuration
- device model and registry endpoints
- authentication scaffolding for future token-based device auth
- health endpoint for monitoring
- a basic dashboard HTML shell

## Run locally

```bash
cd jarvis/server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Current endpoints

- GET /api/health
- POST /api/auth/register-device
- GET /api/devices

## Security note

This is intentionally minimal and deliberately does not expose sensitive actions yet. The next milestone will add real device heartbeat and permission checks.
