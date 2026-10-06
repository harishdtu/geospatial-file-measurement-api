from __future__ import annotations

from typing import Any

import geopandas as gpd
from shapely.geometry import mapping

from app.core.exceptions import GeospatialProcessingError
from app.services.crs_service import CRSService
from app.utils.geometry import normalize_value


class MeasurementService:
    @staticmethod
    def compute_measurements(gdf: gpd.GeoDataFrame) -> tuple[str, str, list[dict[str, Any]]]:
        if gdf.empty:
            raise GeospatialProcessingError("No features were found in the uploaded file.")

        measurement_crs = CRSService.determine_measurement_crs(gdf)
        projected_gdf = gdf.to_crs(measurement_crs)
        length_unit = "m"
        area_unit = "m²"
        results: list[dict[str, Any]] = []

        for feature_id, row in projected_gdf.iterrows():
            geom = row.geometry
            feature_record: dict[str, Any] = {
                "feature_id": int(feature_id),
                "geometry_type": geom.geom_type if geom is not None else "Unknown",
                "geometry": mapping(geom) if geom is not None else {},
                "crs": gdf.crs.to_string() if gdf.crs else None,
                "properties": {
                    key: normalize_value(value)
                    for key, value in row.drop(labels=[projected_gdf.geometry.name]).items()
                },
                "measurement": None,
                "measurement_type": None,
                "measurement_unit": None,
                "unsupported_reason": None,
            }

            if geom is None or geom.is_empty:
                feature_record["unsupported_reason"] = "Geometry is empty or missing."
                results.append(feature_record)
                continue

            if geom.geom_type in {"Polygon", "MultiPolygon"}:
                feature_record["measurement"] = float(geom.area)
                feature_record["measurement_type"] = "area"
                feature_record["measurement_unit"] = area_unit
            elif geom.geom_type in {"LineString", "MultiLineString", "LinearRing"}:
                feature_record["measurement"] = float(geom.length)
                feature_record["measurement_type"] = "length"
                feature_record["measurement_unit"] = length_unit
            elif geom.geom_type in {"Point", "MultiPoint"}:
                feature_record["measurement"] = None
                feature_record["measurement_type"] = "point"
                feature_record["measurement_unit"] = None
            else:
                feature_record["unsupported_reason"] = (
                    f"Geometry type '{geom.geom_type}' is not supported for measurement."
                )

            results.append(feature_record)

        return measurement_crs.to_string(), area_unit, results
