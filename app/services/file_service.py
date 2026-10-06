from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, FileValidationError, GeospatialProcessingError
from app.models.file import FileRecord
from app.repositories.file_repository import FileRepository
from app.services.geospatial_service import GeospatialService
from app.services.storage_service import StorageService
from app.utils.file_validation import validate_upload_file


class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = FileRepository(db)
        self.storage_service = StorageService()
        self.geospatial_service = GeospatialService()

    def _resolve_file_type(self, filename: str) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix == ".zip":
            return "zip"
        if suffix in {".kml", ".kmz"}:
            return "kml"
        raise FileValidationError(
            "Unsupported file type. Please upload a zipped shapefile or KML file."
        )

    def create_file_record(self, upload_file: UploadFile) -> FileRecord:
        validate_upload_file(upload_file)
        file_id = uuid.uuid4().hex
        file_type = self._resolve_file_type(upload_file.filename or "")

        stored_path = self.storage_service.save_upload(upload_file, file_id)
        record = FileRecord(
            id=file_id,
            original_name=upload_file.filename or "upload",
            stored_name=stored_path.name,
            file_type=file_type,
            content_type=upload_file.content_type,
            file_size=stored_path.stat().st_size,
            storage_path=str(stored_path),
            status="uploaded",
        )
        self.repository.create(record)

        try:
            if file_type == "zip":
                extracted_dir = self.storage_service.extract_zip(stored_path, file_id)
                gdf_path = extracted_dir
            else:
                gdf_path = stored_path

            processed = self.geospatial_service.process_file(gdf_path, file_type)
            record.crs = processed["source_crs"]
            record.feature_count = processed["feature_count"]
            record.feature_summary = processed["features"]
            record.measurement_crs = processed["measurement_crs"]
            record.measurement_unit = f"{processed['length_unit']} / {processed['area_unit']}"
            record.measurement_summary = (
                f"Projected measurement CRS: {processed['measurement_crs']}. "
                f"Length units: {processed['length_unit']}; area units: {processed['area_unit']}."
            )
            record.status = "processed"
            record.processed_at = datetime.now(timezone.utc)
            self.repository.update(record)
        except AppError:
            raise
        except Exception as exc:  # pragma: no cover - explicit cleanup is included in tests
            record.status = "failed"
            record.measurement_summary = str(exc)
            self.repository.update(record)
            raise GeospatialProcessingError(f"Processing failed: {exc}") from exc

        return record

    def get_record(self, record_id: str) -> FileRecord | None:
        return self.repository.get_by_id(record_id)

    def get_measurements(self, record_id: str) -> dict[str, Any]:
        record = self.get_record(record_id)
        if record is None:
            raise FileValidationError(f"File with id '{record_id}' was not found.")
        features = record.feature_summary or []
        return {
            "file_id": record.id,
            "file_name": record.original_name,
            "source_crs": record.crs,
            "measurement_crs": record.measurement_crs or record.crs or "unknown",
            "length_unit": "m",
            "area_unit": "m²",
            "features": features,
        }
