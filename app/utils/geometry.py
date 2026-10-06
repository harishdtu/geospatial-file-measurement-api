from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from shapely.geometry import base


def normalize_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Mapping):
        return {str(k): normalize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize_value(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            return str(value)
    return str(value)


def geometry_to_geojson(geom: base.BaseGeometry) -> dict[str, Any]:
    if geom is None or geom.is_empty:
        return {"type": "GeometryCollection", "coordinates": []}
    return {
        "type": geom.geom_type,
        "coordinates": geom.coords[:] if hasattr(geom, "coords") else [],
    }
