from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import JWT_ALGORITHM, JWT_SECRET_KEY


def create_device_token(device_id: str) -> str:
    payload = {
        "sub": device_id,
        "role": "device",
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
