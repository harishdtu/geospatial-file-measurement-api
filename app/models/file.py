from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class FileRecord(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: uuid4().hex)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="uploaded")
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    crs: Mapped[str | None] = mapped_column(String(256), nullable=True)
    feature_count: Mapped[int] = mapped_column(Integer, default=0)
    feature_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    measurement_crs: Mapped[str | None] = mapped_column(String(256), nullable=True)
    measurement_unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    measurement_summary: Mapped[str | None] = mapped_column(String(2048), nullable=True)
