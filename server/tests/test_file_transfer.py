from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_and_list_file() -> None:
    device_id = f"file-test-device-{uuid4().hex[:8]}"

    # Device must exist before file upload in this milestone.
    register_response = client.post(
        "/api/auth/register-device",
        json={
            "device_id": device_id,
            "device_name": "Transfer Test Device",
            "device_type": "windows",
        },
    )
    assert register_response.status_code == 200

    upload_response = client.post(
        "/api/files/upload",
        data={"device_id": device_id},
        files={"file": ("hello.txt", b"hello from jarvis", "text/plain")},
    )
    assert upload_response.status_code == 200, upload_response.text
    payload = upload_response.json()
    assert payload["file"]["original_name"] == "hello.txt"
    assert payload["file"]["size_bytes"] == len(b"hello from jarvis")

    list_response = client.get(f"/api/files?device_id={device_id}")
    assert list_response.status_code == 200, list_response.text
    files = list_response.json()["files"]
    assert any(item["original_name"] == "hello.txt" for item in files)

    download_response = client.get(f"/api/files/{payload['file']['id']}/download")
    assert download_response.status_code == 200, download_response.text
    assert download_response.content == b"hello from jarvis"
