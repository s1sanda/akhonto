# JARVIS setup guide

## Repository layout

```text
jarvis/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── security.md
│   └── setup.md
├── server/
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py
│       ├── db.py
│       ├── auth.py
│       ├── config.py
│       └── models/
├── web/
│   └── dashboard/
│       ├── index.html
│       ├── styles.css
│       └── app.js
└── .gitignore
```

## Local server setup

```bash
cd jarvis/server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Useful checks

```bash
curl http://127.0.0.1:8000/api/health
curl -X POST http://127.0.0.1:8000/api/auth/register-device -H "Content-Type: application/json" -d '{"device_name":"Laptop","device_type":"windows","device_id":"dev-001"}'
```

## Notes

- this milestone uses a local SQLite database for development convenience
- production deployments should move to PostgreSQL and store secrets in environment variables
- no private keys, tokens, or passwords should be committed to the repository
