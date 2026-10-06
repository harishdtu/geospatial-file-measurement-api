from pathlib import Path

from fastapi import UploadFile

from app.core.exceptions import FileValidationError


def validate_upload_filename(filename: str) -> str:
    if not filename:
        raise FileValidationError("No filename was provided in the upload.")

    suffix = Path(filename).suffix.lower()
    if suffix not in {".zip", ".kml", ".kmz"}:
        raise FileValidationError(
            "Unsupported file type. Please upload a .zip containing a shapefile or a .kml file."
        )
    return suffix


def validate_upload_file(file: UploadFile) -> None:
    if file is None:
        raise FileValidationError("No file was provided.")
    if file.filename is None or file.filename == "":
        raise FileValidationError("Uploaded file is missing a filename.")
    validate_upload_filename(file.filename)
