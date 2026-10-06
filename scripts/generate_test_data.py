from __future__ import annotations

import zipfile
from pathlib import Path

import geopandas as gpd
from shapely.geometry import LineString, Polygon


def create_sample_data(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    polygon_gdf = gpd.GeoDataFrame(
        {"name": ["square"], "area_label": ["demo"]},
        geometry=[
            Polygon(
                [
                    (0.0, 0.0),
                    (0.0, 0.01),
                    (0.01, 0.01),
                    (0.01, 0.0),
                    (0.0, 0.0),
                ]
            )
        ],
        crs="EPSG:4326",
    )
    polygon_dir = output_dir / "polygon_example"
    polygon_dir.mkdir(exist_ok=True)
    polygon_gdf.to_file(polygon_dir / "polygon_example.shp", driver="ESRI Shapefile")

    line_gdf = gpd.GeoDataFrame(
        {"name": ["road"]},
        geometry=[LineString([(0.0, 0.0), (0.01, 0.01)])],
        crs="EPSG:4326",
    )
    line_dir = output_dir / "line_example"
    line_dir.mkdir(exist_ok=True)
    line_gdf.to_file(line_dir / "line_example.shp", driver="ESRI Shapefile")

    polygon_kml = output_dir / "polygon_example.kml"
    polygon_gdf.to_file(polygon_kml, driver="KML")

    zip_output = output_dir / "polygon_example.zip"
    with zipfile.ZipFile(zip_output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in polygon_dir.iterdir():
            archive.write(item, arcname=item.name)

    print(f"Created fixtures in: {output_dir}")


if __name__ == "__main__":
    create_sample_data(Path(__file__).resolve().parent / "generated_data")
