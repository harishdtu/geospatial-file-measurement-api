from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient
from tests.conftest import build_line_kml, build_polygon_shapefile_zip

client = TestClient(app)


def test_polygon_measurement_is_positive(tmp_path) -> None:
    zip_path = build_polygon_shapefile_zip(tmp_path)

    with zip_path.open("rb") as uploaded_file:
        upload_response = client.post(
            "/api/files/",
            files={"file": (zip_path.name, uploaded_file, "application/zip")},
        )

    file_id = upload_response.json()["id"]
    response = client.get(f"/api/files/{file_id}/measurements/")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["measurement_crs"] != "EPSG:4326"
    assert body["area_unit"] == "m²"
    assert body["features"][0]["measurement_type"] == "area"
    assert body["features"][0]["measurement"] > 0


def test_line_measurement_is_positive(tmp_path) -> None:
    kml_path = build_line_kml(tmp_path)

    with kml_path.open("rb") as uploaded_file:
        upload_response = client.post(
            "/api/files/",
            files={"file": (kml_path.name, uploaded_file, "application/vnd.google-earth.kml+xml")},
        )

    file_id = upload_response.json()["id"]
    response = client.get(f"/api/files/{file_id}/measurements/")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["features"][0]["measurement_type"] == "length"
    assert body["features"][0]["measurement"] > 0
    assert body["features"][0]["measurement_unit"] == "m"
