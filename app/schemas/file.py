from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class FileSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    original_name: str
    stored_name: str
    file_type: str
    content_type: str | None = None
    file_size: int
    status: str
    uploaded_at: datetime
    processed_at: datetime | None = None
    crs: str | None = None
    feature_count: int = 0
    feature_summary: list[dict[str, Any]] | None = None
    measurement_crs: str | None = None
    measurement_unit: str | None = None
    measurement_summary: str | None = None


class FileUploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    original_name: str
    file_type: str
    file_size: int
    status: str
    uploaded_at: datetime
    feature_count: int
    crs: str | None = None
    measurement_crs: str | None = None
    measurement_unit: str | None = None


class FileDetailResponse(FileUploadResponse):
    stored_name: str
    content_type: str | None = None
    processed_at: datetime | None = None
    feature_summary: list[dict[str, Any]] | None = None
    measurement_summary: str | None = None
