# Geospatial File Measurement API

A production-quality FastAPI service for validating uploaded geospatial files, extracting features, and returning measurements for supported geometry types. The service accepts KML files and ZIP archives containing Shapefiles, processes feature metadata, and computes measurement values in a projected CRS instead of directly using geographic latitude/longitude degrees.

## Project overview

This project is designed as a small but professional geospatial backend for file-based spatial analysis. It accepts geospatial uploads, validates them, stores metadata in SQLite, extracts geometric features, and returns per-feature measurement results with proper CRS metadata.

## Features

- Upload of KML files
- Upload of ZIP archives containing Shapefiles
- Validation of upload type and archive contents
- Safe file handling and ZIP traversal protection
- Feature extraction with geometry metadata and attributes
- Automatic CRS detection and safe reprojection for measurement calculations
- Measurement support for:
  - Polygon / MultiPolygon -> area
  - LineString / MultiLineString -> length
  - Point / MultiPoint -> no measurement
  - Unsupported geometries -> returned without crashing
- SQLite-backed metadata persistence
- FastAPI OpenAPI docs and ReDoc UI
- Dockerized local execution

## FastAPI setup

### Prerequisites

- Python 3.12+
- pip
- Docker and Docker Compose (optional)

### Local setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   . .venv/bin/activate   # Linux/macOS
   # or .\.venv\Scripts\activate  # Windows PowerShell
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment file:
   ```bash
   copy .env.example .env
   ```
   or on Linux/macOS:
   ```bash
   cp .env.example .env
   ```

4. Start the app:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Open the API docs:
   - Swagger: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Supported inputs

### Supported KML files

- `.kml` files are accepted directly.
- The file is validated and parsed with GeoPandas.
- Feature attributes and geometries are returned in the API response.

### Supported ZIP Shapefiles

- `.zip` archives are accepted as long as they contain a valid Shapefile set.
- Required shapefile components such as `.shp`, `.shx`, `.dbf`, and `.prj` are expected in the archive.
- The service rejects archives that do not contain a valid shapefile or contain unsafe path traversal entries.

## API endpoints

### Health

```bash
GET /health
```

Response:
```json
{"status": "ok"}
```

### Upload file

```bash
POST /api/files/
```

Multipart form data:
- `file`: uploaded KML or ZIP shapefile archive

Example:
```bash
curl -X POST "http://localhost:8000/api/files/" \
  -F "file=@sample.zip"
```

### File metadata

```bash
GET /api/files/{id}
```

Returns uploader metadata, file summary, CRS, feature count, and measurement summary.

### Measurements

```bash
GET /api/files/{id}/measurements/
```

Returns per-feature measurement details including:
- feature ID/index
- geometry type
- geometry JSON
- CRS
- properties
- measurement values
- unsupported geometry reasons when applicable

## Measurement behavior

- Polygon -> area
- LineString -> length
- Point -> no measurement
- Unsupported geometries -> gracefully handled without crashing

Examples:
- A polygon returns a computed area in square meters (`m²`)
- A line returns a computed length in meters (`m`)
- A point returns `measurement: null` with a `measurement_type` of `point`

## CRS handling

The service does not calculate area or length directly from raw geographic degrees.

For geographic CRS such as EPSG:4326:

1. The file is inspected for its source CRS.
2. A suitable projected CRS is selected based on the geometry centroid and local coordinate space.
3. The features are reprojected into that CRS.
4. Length and area are computed in projected units.
5. The response exposes the measurement CRS and units clearly.

This avoids invalid results caused by measuring angular coordinates directly.

## Architecture

The application is organized into a clean service-oriented structure:

- `app/main.py`: FastAPI application bootstrap
- `app/api/routes/files.py`: API route layer
- `app/services/file_service.py`: orchestration logic for uploads and processing
- `app/services/geospatial_service.py`: file parsing and feature extraction
- `app/services/measurement_service.py`: geometry measurement calculations
- `app/services/crs_service.py`: CRS detection and reprojection strategy
- `app/services/storage_service.py`: upload persistence and ZIP extraction
- `app/repositories/file_repository.py`: SQLite repository layer
- `app/models/file.py`: file metadata model
- `app/schemas/`: Pydantic schemas for validation and responses
- `app/utils/`: validation and geometry helpers
- `tests/`: end-to-end validation suite

## File processing flow

1. A multipart upload is received through the API.
2. The uploaded file name is validated for supported extensions.
3. ZIP archives are checked for valid shapefile contents and unsafe entries.
4. The file is saved to the configured upload directory.
5. GeoPandas reads the geospatial file and validates CRS presence.
6. Each feature is converted into a normalized structure containing:
   - feature index
   - geometry type
   - geometry representation
   - CRS
   - properties
7. The metadata is stored in SQLite.
8. The file record is returned with processing status and measurement details.

## Measurement calculation flow

1. Determine source CRS from the uploaded dataset.
2. If the source CRS is geographic, select an appropriate projected CRS.
3. Reproject geometry to the projected CRS.
4. Evaluate geometry type:
   - polygon -> area
   - line -> length
   - point -> no measurement
   - unsupported geometry -> mark as unsupported
5. Return feature measurement details plus measurement CRS / units.

## Design decisions

- FastAPI was chosen because the assignment explicitly requires it.
- SQLite was used for metadata persistence to keep setup simple and reproducible without PostGIS.
- GeoPandas + Shapely + PyProj provide the core geospatial functionality.
- Validation is performed early to prevent bad uploads, malformed archives, and unsafe extraction paths.
- Architecture stays intentionally small and maintainable to support a professional engineering review.

## Security considerations

- ZIP archives are validated to block path traversal attempts.
- Only supported file types are accepted.
- No secrets are stored in source files.
- Local SQLite databases and uploaded test artifacts are excluded from source control.
- The service never writes absolute local paths into the code or environment configuration.

## Testing

The project includes automated tests for:

- app health
- upload validation
- ZIP shapefile uploads
- KML uploads
- file metadata retrieval
- measurement calculation
- CRS reprojection
- unsupported file rejection

Run tests with:
```bash
pytest -q
```

Run lint:
```bash
ruff check app tests
```

Run compile check:
```bash
python -m compileall app
```

## Docker setup

Build the image:
```bash
docker build -t geospatial-file-measurement-api .
```

Run with Docker Compose:
```bash
docker compose up --build
```

The app will be available at:
```text
http://localhost:8000
```

## Learning and future scope

### Learning

This project reinforces the importance of:

- measuring geometries in projected coordinate systems rather than raw degrees
- safe file handling for uploaded archives
- validating geospatial input before processing
- keeping backend services simple, testable, and review-friendly

### Future scope

Possible improvements include:

- batch uploads
- custom user-selected projected CRS
- richer metadata export
- asynchronous long-running processing for large datasets
- support for additional geospatial formats

## License

This project is provided for educational and assignment use. Adapt it to your organization’s policy requirements as needed.
