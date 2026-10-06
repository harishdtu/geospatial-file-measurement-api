from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient
from tests.conftest import build_polygon_shapefile_zip

client = TestClient(app)


def test_file_information_endpoint(tmp_path) -> None:
    zip_path = build_polygon_shapefile_zip(tmp_path)

    with zip_path.open("rb") as uploaded_file:
        upload_response = client.post(
            "/api/files/",
            files={"file": (zip_path.name, uploaded_file, "application/zip")},
        )

    file_id = upload_response.json()["id"]
    response = client.get(f"/api/files/{file_id}")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["id"] == file_id
    assert body["original_name"] == zip_path.name
    assert body["feature_count"] == 1
    assert body["measurement_crs"] is not None
