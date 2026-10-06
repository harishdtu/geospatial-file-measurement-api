from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Geospatial File Measurement API"
    app_version: str = "1.0.0"
    app_description: str = (
        "FastAPI service for validating geospatial files, extracting features, and "
        "returning area and length measurements with correct CRS handling."
    )
    environment: str = "development"
    database_url: str = Field(
        default="sqlite:///./geospatial.db",
        validation_alias="DATABASE_URL",
    )
    upload_dir: str = Field(default="data/uploads", validation_alias="UPLOAD_DIR")
    processed_dir: str = Field(default="data/processed", validation_alias="PROCESSED_DIR")
    max_upload_size_mb: int = Field(default=50, validation_alias="MAX_UPLOAD_SIZE_MB")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
