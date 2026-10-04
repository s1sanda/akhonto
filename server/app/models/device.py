from __future__ import annotations

from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    device_name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    os_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=True)
    battery_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(100), nullable=True)
    connection_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_seen: Mapped[str] = mapped_column(String(255), nullable=True)
    status_message: Mapped[str | None] = mapped_column(String(255), nullable=True)
