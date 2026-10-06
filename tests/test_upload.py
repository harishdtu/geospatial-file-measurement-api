from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient
from tests.conftest import build_line_kml, build_polygon_shapefile_zip

client = TestClient(app)


def test_upload_shapefile_zip(tmp_path) -> None:
    zip_path = build_polygon_shapefile_zip(tmp_path)

    with zip_path.open("rb") as uploaded_file:
        response = client.post(
            "/api/files/",
            files={"file": (zip_path.name, uploaded_file, "application/zip")},
        )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["file_type"] == "zip"
    assert body["feature_count"] == 1
    assert body["crs"] == "EPSG:4326"
    assert body["measurement_crs"] is not None


def test_upload_kml_file(tmp_path) -> None:
    kml_path = build_line_kml(tmp_path)

    with kml_path.open("rb") as uploaded_file:
        response = client.post(
            "/api/files/",
            files={"file": (kml_path.name, uploaded_file, "application/vnd.google-earth.kml+xml")},
        )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["file_type"] == "kml"
    assert body["feature_count"] == 1
