from __future__ import annotations

import zipfile
from pathlib import Path

import geopandas as gpd
from app.main import app
from fastapi.testclient import TestClient
from shapely.geometry import LineString, Point, Polygon


def build_polygon_shapefile_zip(tmp_path: Path) -> Path:
    polygon = Polygon(
        [
            (0.0, 0.0),
            (0.0, 0.01),
            (0.01, 0.01),
            (0.01, 0.0),
            (0.0, 0.0),
        ]
    )
    gdf = gpd.GeoDataFrame(
        {"name": ["sample"], "type": ["polygon"]},
        geometry=[polygon],
        crs="EPSG:4326",
    )
    shapefile_dir = tmp_path / "polygon_input"
    shapefile_dir.mkdir()
    gdf.to_file(shapefile_dir / "polygon_input.shp", driver="ESRI Shapefile")

    archive_path = tmp_path / "polygon_input.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in shapefile_dir.iterdir():
            archive.write(item, arcname=item.name)
    return archive_path


def build_line_kml(tmp_path: Path) -> Path:
    line = LineString([(0.0, 0.0), (0.01, 0.01)])
    gdf = gpd.GeoDataFrame(
        {"name": ["sample_line"], "type": ["road"]},
        geometry=[line],
        crs="EPSG:4326",
    )
    file_path = tmp_path / "line_input.kml"
    gdf.to_file(file_path, driver="KML")
    return file_path


def build_point_kml(tmp_path: Path) -> Path:
    point = Point(10.0, 20.0)
    gdf = gpd.GeoDataFrame(
        {"name": ["sample_point"], "type": ["point"]},
        geometry=[point],
        crs="EPSG:4326",
    )
    file_path = tmp_path / "point_input.kml"
    gdf.to_file(file_path, driver="KML")
    return file_path


def get_client():
    return TestClient(app)
