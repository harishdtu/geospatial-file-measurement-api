from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FileValidationError


class StorageService:
    def __init__(self, root_dir: str | Path | None = None):
        self.root_dir = Path(root_dir or settings.upload_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, uploaded_file: UploadFile, file_id: str) -> Path:
        filename = uploaded_file.filename or "upload"
        target_dir = self.root_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        safe_name = f"{file_id}_{filename}"
        target_path = target_dir / safe_name
        with target_path.open("wb") as destination:
            shutil.copyfileobj(uploaded_file.file, destination)
        return target_path

    def extract_zip(self, archive_path: Path, file_id: str) -> Path:
        extraction_dir = self.root_dir / f"{file_id}_extracted"
        extraction_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(archive_path) as archive:
                members = archive.infolist()
                for member in members:
                    target = Path(member.filename)
                    if target.is_absolute() or ".." in target.parts:
                        raise FileValidationError(
                            "Archive contains an unsafe path traversal entry."
                        )

                    extracted_path = extraction_dir / target
                    if not extracted_path.resolve().is_relative_to(
                        extraction_dir.resolve()
                    ):
                        raise FileValidationError(
                            "Archive contains an unsafe path traversal entry."
                        )

                archive.extractall(extraction_dir)
        except zipfile.BadZipFile as exc:
            raise FileValidationError("The .zip file does not contain a valid shapefile.") from exc

        if not any(path.suffix.lower() == ".shp" for path in extraction_dir.rglob("*.shp")):
            raise FileValidationError("The .zip file does not contain a valid shapefile.")
        return extraction_dir
