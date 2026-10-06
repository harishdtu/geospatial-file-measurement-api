from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.file import FileRecord


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, record: FileRecord) -> FileRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, record_id: str) -> FileRecord | None:
        return self.db.query(FileRecord).filter(FileRecord.id == record_id).first()

    def update(self, record: FileRecord) -> FileRecord:
        record.processed_at = record.processed_at or datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(record)
        return record

    def serialize_file_record(self, record: FileRecord) -> dict[str, Any]:
        return {
            "id": record.id,
            "original_name": record.original_name,
            "stored_name": record.stored_name,
            "file_type": record.file_type,
            "content_type": record.content_type,
            "file_size": record.file_size,
            "storage_path": record.storage_path,
            "status": record.status,
            "uploaded_at": record.uploaded_at.isoformat() if record.uploaded_at else None,
            "processed_at": record.processed_at.isoformat() if record.processed_at else None,
            "crs": record.crs,
            "feature_count": record.feature_count,
            "feature_summary": record.feature_summary,
            "measurement_crs": record.measurement_crs,
            "measurement_unit": record.measurement_unit,
            "measurement_summary": record.measurement_summary,
        }
