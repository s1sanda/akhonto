from __future__ import annotations

import os

APP_ENV = os.getenv("APP_ENV", "development")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

if APP_ENV == "production" and not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY must be set in production")

if not JWT_SECRET_KEY:
    JWT_SECRET_KEY = "development-secret-change-me"
