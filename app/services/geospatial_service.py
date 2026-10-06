from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd

from app.core.exceptions import FileValidationError, GeospatialProcessingError
from app.services.crs_service import CRSService
from app.services.measurement_service import MeasurementService


class GeospatialService:
    def __init__(self) -> None:
        self.measurement_service = MeasurementService()

    @staticmethod
    def find_shapefile(base_path: Path) -> Path:
        shapefiles = sorted(base_path.rglob("*.shp"))
        if not shapefiles:
            raise FileValidationError("No shapefile was found in the uploaded archive.")
        return shapefiles[0]

    @staticmethod
    def load_geodataframe(file_path: Path, file_type: str) -> gpd.GeoDataFrame:
        try:
            if file_type == "zip":
                actual_path = GeospatialService.find_shapefile(file_path)
            else:
                actual_path = file_path
            gdf = gpd.read_file(str(actual_path))
        except Exception as exc:  # pragma: no cover - behavior is exercised by tests
            raise GeospatialProcessingError(
                f"Unable to parse the supplied geospatial file: {exc}"
            ) from exc

        if gdf.empty:
            raise GeospatialProcessingError("The file does not contain any features.")
        if gdf.crs is None:
            raise GeospatialProcessingError(
                "The file does not have a defined CRS and cannot be measured safely."
            )

        return gdf

    @staticmethod
    def determine_measurement_crs(gdf: gpd.GeoDataFrame) -> str:
        return CRSService.determine_measurement_crs(gdf).to_string()

    def process_file(self, file_path: Path, file_type: str) -> dict[str, Any]:
        gdf = self.load_geodataframe(file_path, file_type)
        measurement_crs, area_unit, features = self.measurement_service.compute_measurements(gdf)

        return {
            "source_crs": gdf.crs.to_string() if gdf.crs else None,
            "measurement_crs": measurement_crs,
            "length_unit": "m",
            "area_unit": area_unit,
            "features": features,
            "feature_count": len(features),
        }
