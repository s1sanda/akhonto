from __future__ import annotations

import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jarvis.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def ensure_sqlite_schema() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    if "devices" in tables:
        columns = {column["name"] for column in inspector.get_columns("devices")}
        additions = {
            "os_name": "VARCHAR(100)",
            "app_version": "VARCHAR(50)",
            "battery_level": "FLOAT",
            "ip_address": "VARCHAR(100)",
            "connection_type": "VARCHAR(50)",
            "status_message": "VARCHAR(255)",
        }

        with engine.begin() as conn:
            for column_name, column_type in additions.items():
                if column_name not in columns:
                    conn.execute(text(f"ALTER TABLE devices ADD COLUMN {column_name} {column_type}"))

    if "notifications" in tables:
        columns = {column["name"] for column in inspector.get_columns("notifications")}
        if "details" not in columns:
            with engine.begin() as conn:
                if "metadata" in columns:
                    conn.execute(text("ALTER TABLE notifications RENAME TO notifications_old"))
                    conn.execute(
                        text(
                            """
                            CREATE TABLE notifications (
                                id INTEGER NOT NULL PRIMARY KEY,
                                device_id VARCHAR(255),
                                title VARCHAR(255) NOT NULL,
                                message TEXT NOT NULL,
                                severity VARCHAR(50) DEFAULT 'info',
                                channel VARCHAR(50) DEFAULT 'system',
                                event_type VARCHAR(100) DEFAULT 'system',
                                is_read BOOLEAN DEFAULT 0,
                                created_at VARCHAR(255) NOT NULL,
                                details TEXT
                            )
                            """
                        )
                    )
                    conn.execute(
                        text(
                            """
                            INSERT INTO notifications (
                                id, device_id, title, message, severity, channel, event_type, is_read, created_at, details
                            )
                            SELECT id, device_id, title, message, severity, channel, event_type, is_read, created_at, metadata
                            FROM notifications_old
                            """
                        )
                    )
                    conn.execute(text("DROP TABLE notifications_old"))
                else:
                    for column_name, column_type in {
                        "device_id": "VARCHAR(255)",
                        "title": "VARCHAR(255)",
                        "message": "TEXT",
                        "severity": "VARCHAR(50)",
                        "channel": "VARCHAR(50)",
                        "event_type": "VARCHAR(100)",
                        "is_read": "BOOLEAN",
                        "created_at": "VARCHAR(255)",
                        "details": "TEXT",
                    }.items():
                        if column_name not in columns:
                            conn.execute(text(f"ALTER TABLE notifications ADD COLUMN {column_name} {column_type}"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
