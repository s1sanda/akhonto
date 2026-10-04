from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import create_device_token
from app.db import Base, ensure_sqlite_schema, engine, get_db
from app.models.device import Device
from app.models.file_record import FileRecord
from app.models.notification import Notification

ensure_sqlite_schema()
Base.metadata.create_all(bind=engine)

STORAGE_ROOT = Path(__file__).resolve().parent.parent / "storage"
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="JARVIS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return """
    <html>
      <head>
        <title>JARVIS Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
          body { font-family: Arial, sans-serif; margin: 0; background: #0b1020; color: #e5eefb; }
          .shell { max-width: 1100px; margin: 40px auto; padding: 24px; }
          .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
          .card { background: #121a2d; border: 1px solid #2a3a5f; border-radius: 14px; padding: 20px; }
          .badge { background: #0ec997; color: #032b20; padding: 5px 10px; border-radius: 999px; font-weight: bold; }
          h1 { margin-top: 0; }
        </style>
      </head>
      <body>
        <div class="shell">
          <h1>JARVIS</h1>
          <div class="badge">System OK</div>
          <div class="grid" style="margin-top: 24px;">
            <div class="card">
              <h3>Devices</h3>
              <p>Registered devices: 0</p>
            </div>
            <div class="card">
              <h3>Files</h3>
              <p>Transfers and cloud storage</p>
            </div>
            <div class="card">
              <h3>VPN</h3>
              <p>WireGuard status</p>
            </div>
            <div class="card">
              <h3>Assistant</h3>
              <p>Permissions and tool routing</p>
            </div>
          </div>
        </div>
      </body>
    </html>
    """


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "jarvis", "version": "0.1.0"}


@app.post("/api/auth/register-device")
def register_device(payload: dict, db: Annotated[Session, Depends(get_db)]) -> dict:
    device_id = payload.get("device_id")
    device_name = payload.get("device_name")
    device_type = payload.get("device_type")
    os_name = payload.get("os_name")
    app_version = payload.get("app_version")

    if not device_id or not device_name or not device_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="device_id, device_name, and device_type are required",
        )

    existing = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="device already registered",
        )

    device = Device(
        device_id=device_id,
        device_name=device_name,
        device_type=device_type,
        os_name=os_name,
        app_version=app_version,
        is_online=True,
        last_seen=datetime.now(timezone.utc).isoformat(),
        status_message="registered",
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    return {
        "message": "device registered",
        "device": {
            "id": device.id,
            "device_id": device.device_id,
            "device_name": device.device_name,
            "device_type": device.device_type,
            "os_name": device.os_name,
            "app_version": device.app_version,
            "token": create_device_token(device.device_id),
        },
    }


@app.post("/api/devices/heartbeat")
def heartbeat(payload: dict, db: Annotated[Session, Depends(get_db)]) -> dict:
    device_id = payload.get("device_id")
    if not device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="device_id is required",
        )

    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="device not found",
        )

    device.is_online = True
    device.last_seen = datetime.now(timezone.utc).isoformat()
    device.battery_level = payload.get("battery_level", device.battery_level)
    device.ip_address = payload.get("ip_address", device.ip_address)
    device.connection_type = payload.get("connection_type", device.connection_type)
    device.os_name = payload.get("os_name", device.os_name)
    device.app_version = payload.get("app_version", device.app_version)
    device.status_message = payload.get("status_message", "online")

    db.commit()
    db.refresh(device)

    return {
        "message": "heartbeat received",
        "device": {
            "device_id": device.device_id,
            "device_name": device.device_name,
            "is_online": device.is_online,
            "last_seen": device.last_seen,
            "battery_level": device.battery_level,
            "ip_address": device.ip_address,
            "connection_type": device.connection_type,
        },
    }


@app.get("/api/devices")
def list_devices(db: Annotated[Session, Depends(get_db)]) -> dict:
    devices = db.execute(select(Device)).scalars().all()
    return {
        "devices": [
            {
                "id": d.id,
                "device_id": d.device_id,
                "device_name": d.device_name,
                "device_type": d.device_type,
                "os_name": d.os_name,
                "app_version": d.app_version,
                "is_online": d.is_online,
                "battery_level": d.battery_level,
                "ip_address": d.ip_address,
                "connection_type": d.connection_type,
                "last_seen": d.last_seen,
                "status_message": d.status_message,
            }
            for d in devices
        ]
    }


@app.post("/api/files/upload")
async def upload_file(
    device_id: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="device not found",
        )

    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file name is required",
        )

    safe_name = f"{uuid4().hex}_{file.filename}"
    device_dir = STORAGE_ROOT / device_id
    device_dir.mkdir(parents=True, exist_ok=True)
    storage_path = device_dir / safe_name

    content = await file.read()
    storage_path.write_bytes(content)

    record = FileRecord(
        device_id=device_id,
        original_name=file.filename,
        stored_name=safe_name,
        storage_path=str(storage_path),
        mime_type=file.content_type,
        size_bytes=len(content),
        status="uploaded",
        uploaded_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "file uploaded",
        "file": {
            "id": record.id,
            "device_id": record.device_id,
            "original_name": record.original_name,
            "stored_name": record.stored_name,
            "mime_type": record.mime_type,
            "size_bytes": record.size_bytes,
            "status": record.status,
            "uploaded_at": record.uploaded_at,
        },
    }


@app.get("/api/files")
def list_files(
    db: Annotated[Session, Depends(get_db)],
    device_id: str | None = None,
) -> dict:
    query = select(FileRecord)
    if device_id:
        query = query.where(FileRecord.device_id == device_id)

    files = db.execute(query).scalars().all()
    return {
        "files": [
            {
                "id": item.id,
                "device_id": item.device_id,
                "original_name": item.original_name,
                "stored_name": item.stored_name,
                "mime_type": item.mime_type,
                "size_bytes": item.size_bytes,
                "status": item.status,
                "uploaded_at": item.uploaded_at,
            }
            for item in files
        ]
    }


@app.post("/api/notifications")
def create_notification(
    payload: dict,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    device_id = payload.get("device_id")
    title = payload.get("title")
    message = payload.get("message")

    if not title or not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="title and message are required",
        )

    if device_id:
        device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="device not found",
            )

    details = payload.get("details") or payload.get("metadata")
    notification = Notification(
        device_id=device_id,
        title=title,
        message=message,
        severity=payload.get("severity", "info"),
        channel=payload.get("channel", "system"),
        event_type=payload.get("event_type", "system"),
        details=json.dumps(details) if details is not None else None,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    return {
        "message": "notification created",
        "notification": {
            "id": notification.id,
            "device_id": notification.device_id,
            "title": notification.title,
            "message": notification.message,
            "severity": notification.severity,
            "channel": notification.channel,
            "event_type": notification.event_type,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
            "details": json.loads(notification.details) if notification.details else None,
        },
    }


@app.get("/api/notifications")
def list_notifications(
    db: Annotated[Session, Depends(get_db)],
    device_id: str | None = None,
) -> dict:
    query = select(Notification)
    if device_id:
        query = query.where(Notification.device_id == device_id)
    query = query.order_by(Notification.created_at.desc())

    notifications = db.execute(query).scalars().all()
    return {
        "notifications": [
            {
                "id": item.id,
                "device_id": item.device_id,
                "title": item.title,
                "message": item.message,
                "severity": item.severity,
                "channel": item.channel,
                "event_type": item.event_type,
                "is_read": item.is_read,
                "created_at": item.created_at,
                "details": json.loads(item.details) if item.details else None,
            }
            for item in notifications
        ]
    }


@app.get("/api/transfers")
def list_transfers(db: Annotated[Session, Depends(get_db)]) -> dict:
    return list_files(db=db)


@app.get("/api/files/{file_id}/download")
def download_file(file_id: int, db: Annotated[Session, Depends(get_db)]) -> FileResponse:
    record = db.execute(select(FileRecord).where(FileRecord.id == file_id)).scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="file not found",
        )

    file_path = Path(record.storage_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="stored file missing",
        )

    return FileResponse(
        path=file_path,
        filename=record.original_name,
        media_type=record.mime_type or "application/octet-stream",
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
