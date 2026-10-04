"""Minimal Windows device heartbeat agent for JARVIS.

This is a starter implementation for Milestone 2. It sends device telemetry
using the authenticated registration flow and then emits a heartbeat.
"""

from __future__ import annotations

import json
import os
import platform
import time
from typing import Any

import requests

SERVER_URL = os.getenv("JARVIS_SERVER_URL", "http://localhost:8000")
DEVICE_ID = os.getenv("JARVIS_DEVICE_ID", "windows-laptop-demo")
DEVICE_NAME = os.getenv("JARVIS_DEVICE_NAME", "Windows Laptop")
APP_VERSION = os.getenv("JARVIS_APP_VERSION", "0.1.0")


def register_device() -> str:
    payload = {
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "device_type": "windows",
        "os_name": platform.platform(),
        "app_version": APP_VERSION,
    }

    response = requests.post(f"{SERVER_URL}/api/auth/register-device", json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["device"]["token"]


def send_heartbeat(token: str) -> None:
    payload: dict[str, Any] = {
        "device_id": DEVICE_ID,
        "os_name": platform.platform(),
        "app_version": APP_VERSION,
        "status_message": "online",
        "connection_type": "wifi",
        "battery_level": 82,
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{SERVER_URL}/api/devices/heartbeat",
        json=payload,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    token = register_device()
    while True:
        send_heartbeat(token)
        time.sleep(30)
