from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_rejects_unsupported_file_type() -> None:
    response = client.post(
        "/api/files/",
        files={"file": ("notes.txt", b"not a geospatial file", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_rejects_zip_without_shapefile(tmp_path) -> None:
    archive_path = tmp_path / "bad.zip"
    archive_path.write_bytes(b"this is not a shapefile archive")

    with archive_path.open("rb") as uploaded_file:
        response = client.post(
            "/api/files/",
            files={"file": (archive_path.name, uploaded_file, "application/zip")},
        )

    assert response.status_code == 400
    assert "valid shapefile" in response.json()["detail"]
