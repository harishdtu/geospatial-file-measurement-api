class AppError(Exception):
    """Base application exception."""


class FileValidationError(AppError):
    """Raised when an uploaded file is invalid."""


class GeospatialProcessingError(AppError):
    """Raised when a geospatial file cannot be processed."""


class FileNotFoundError(AppError):
    """Raised when a requested uploaded file record cannot be found."""
