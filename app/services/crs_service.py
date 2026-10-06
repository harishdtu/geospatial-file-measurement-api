from __future__ import annotations

import geopandas as gpd
from pyproj import CRS, Transformer


class CRSService:
    @staticmethod
    def determine_measurement_crs(gdf: gpd.GeoDataFrame) -> CRS:
        source_crs = CRS.from_user_input(gdf.crs)
        if not source_crs.is_geographic:
            return source_crs

        centroid = gdf.union_all().centroid
        if centroid.is_empty:
            return CRS.from_epsg(3857)

        lon, lat = centroid.x, centroid.y
        if source_crs.to_epsg() not in (None, 4326):
            transformer = Transformer.from_crs(source_crs, CRS.from_epsg(4326), always_xy=True)
            lon, lat = transformer.transform(lon, lat)

        zone = int((lon + 180) / 6) + 1
        epsg_code = 32600 + zone if lat >= 0 else 32700 + zone
        return CRS.from_epsg(epsg_code)

    @staticmethod
    def project_geometry_dataframe(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        target_crs = CRSService.determine_measurement_crs(gdf)
        return gdf.to_crs(target_crs)
