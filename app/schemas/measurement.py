from typing import Any

from pydantic import BaseModel, ConfigDict


class MeasurementFeature(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feature_id: int
    geometry_type: str
    geometry: dict[str, Any]
    crs: str | None = None
    properties: dict[str, Any]
    measurement: float | None = None
    measurement_type: str | None = None
    measurement_unit: str | None = None
    unsupported_reason: str | None = None


class MeasurementResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_id: str
    file_name: str
    source_crs: str | None = None
    measurement_crs: str
    length_unit: str = "m"
    area_unit: str = "m²"
    features: list[MeasurementFeature]
