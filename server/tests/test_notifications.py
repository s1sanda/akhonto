from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_list_notifications() -> None:
    device_id = f"notify-device-{uuid4().hex[:8]}"

    register_response = client.post(
        "/api/auth/register-device",
        json={
            "device_id": device_id,
            "device_name": "Notification Test Device",
            "device_type": "windows",
        },
    )
    assert register_response.status_code == 200

    create_response = client.post(
        "/api/notifications",
        json={
            "device_id": device_id,
            "title": "Battery low",
            "message": "Battery level dropped below 10%.",
            "severity": "warning",
            "channel": "mobile",
            "event_type": "battery",
        },
    )
    assert create_response.status_code == 200, create_response.text
    payload = create_response.json()
    assert payload["notification"]["title"] == "Battery low"
    assert payload["notification"]["severity"] == "warning"

    list_response = client.get(f"/api/notifications?device_id={device_id}")
    assert list_response.status_code == 200, list_response.text
    notifications = list_response.json()["notifications"]
    assert any(item["title"] == "Battery low" for item in notifications)
