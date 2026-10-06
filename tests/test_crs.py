from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient
from tests.conftest import build_polygon_shapefile_zip

client = TestClient(app)


def test_geographic_crs_is_reprojected_for_measurement(tmp_path) -> None:
    zip_path = build_polygon_shapefile_zip(tmp_path)

    with zip_path.open("rb") as uploaded_file:
        upload_response = client.post(
            "/api/files/",
            files={"file": (zip_path.name, uploaded_file, "application/zip")},
        )

    assert upload_response.status_code == 201, upload_response.text
    file_id = upload_response.json()["id"]

    response = client.get(f"/api/files/{file_id}/measurements/")
    body = response.json()

    assert response.status_code == 200, response.text
    assert "EPSG:" in body["measurement_crs"]
    assert body["measurement_crs"] != "EPSG:4326"
    assert body["length_unit"] == "m"
    assert body["area_unit"] == "m²"
