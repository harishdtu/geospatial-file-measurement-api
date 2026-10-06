from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.db.database import get_db
from app.schemas.error import ErrorResponse
from app.schemas.file import FileDetailResponse, FileUploadResponse
from app.schemas.measurement import MeasurementResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/api", tags=["files", "measurements"])


@router.post(
    "/files/",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
)
async def upload_file(
    file: UploadFile = File(...),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> FileUploadResponse:
    try:
        service = FileService(db)
        record = service.create_file_record(file)
        return FileUploadResponse(
            id=record.id,
            original_name=record.original_name,
            file_type=record.file_type,
            file_size=record.file_size,
            status=record.status,
            uploaded_at=record.uploaded_at,
            feature_count=record.feature_count,
            crs=record.crs,
            measurement_crs=record.measurement_crs,
            measurement_unit=record.measurement_unit,
        )
    except AppError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # pragma: no cover - safety net
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get(
    "/files/{file_id}",
    response_model=FileDetailResponse,
    responses={404: {"model": ErrorResponse, "description": "File not found"}},
)
async def get_file_detail(file_id: str, db: Session = Depends(get_db)) -> FileDetailResponse:  # noqa: B008
    service = FileService(db)
    record = service.get_record(file_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found.",
        )

    return FileDetailResponse(
        id=record.id,
        original_name=record.original_name,
        stored_name=record.stored_name,
        file_type=record.file_type,
        content_type=record.content_type,
        file_size=record.file_size,
        status=record.status,
        uploaded_at=record.uploaded_at,
        processed_at=record.processed_at,
        feature_count=record.feature_count,
        crs=record.crs,
        measurement_crs=record.measurement_crs,
        measurement_unit=record.measurement_unit,
        feature_summary=record.feature_summary,
        measurement_summary=record.measurement_summary,
    )


@router.get(
    "/files/{file_id}/measurements/",
    response_model=MeasurementResponse,
    responses={404: {"model": ErrorResponse, "description": "File not found"}},
)
async def get_file_measurements(file_id: str, db: Session = Depends(get_db)) -> MeasurementResponse:  # noqa: B008
    service = FileService(db)
    record = service.get_record(file_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found.",
        )

    measurements = record.feature_summary or []
    return MeasurementResponse(
        file_id=record.id,
        file_name=record.original_name,
        source_crs=record.crs,
        measurement_crs=record.measurement_crs or record.crs or "unknown",
        length_unit="m",
        area_unit="m²",
        features=[
            {
                "feature_id": feature.get("feature_id", 0),
                "geometry_type": feature.get("geometry_type", "Unknown"),
                "geometry": feature.get("geometry", {}),
                "crs": feature.get("crs"),
                "properties": feature.get("properties", {}),
                "measurement": feature.get("measurement"),
                "measurement_type": feature.get("measurement_type"),
                "measurement_unit": feature.get("measurement_unit"),
                "unsupported_reason": feature.get("unsupported_reason"),
            }
            for feature in measurements
        ],
    )
