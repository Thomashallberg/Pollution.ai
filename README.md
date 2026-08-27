# Pollution Anomaly Detection

Satellite-based pollution anomaly detection over Stockholm using Copernicus Sentinel-5P data.

The application collects spatial pollution observations, compares them with historical baselines, detects statistical anomalies, and visualizes the results on an interactive map.

## Demo

![Pollution Anomaly Detection dashboard](docs/anomaly.gif)

## Features

- Analysis of methane (CH₄) and nitrogen dioxide (NO₂)
- Copernicus Sentinel-5P satellite data
- Spatial pollution analysis using an 8×8 grid
- Historical baseline comparison
- Z-score based anomaly detection
- Anomaly severity classification
- Satellite coverage reporting
- Interactive map visualization
- Historical analysis backfilling
- REST API for analysis results
- Automated backend tests

## How It Works

The analysis pipeline divides the Stockholm region into an 8×8 spatial grid.

For each grid cell, satellite observations are retrieved from Copernicus Sentinel-5P and compared with historical observations for the same location.

The system then calculates a z-score:

```text
z = (observed value - baseline mean) / baseline standard deviation
```

Higher z-scores indicate that the current pollution measurement differs more strongly from its historical baseline.

Anomalies are classified into severity levels and displayed geographically on the interactive map.

```text
Copernicus Sentinel-5P
        │
        ▼
Spatial observations
        │
        ▼
Historical baseline
        │
        ▼
Statistical anomaly detection
        │
        ▼
FastAPI
        │
        ▼
React dashboard
        │
        ▼
Interactive Leaflet map
```

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- NumPy
- Requests / OAuth 2.0
- Pytest

### Frontend

- React
- TypeScript
- Vite
- React Leaflet
- Leaflet

### Data

- Copernicus Data Space Ecosystem
- Sentinel-5P

## API

The FastAPI backend exposes endpoints for accessing available analysis dates, spatial cells, anomaly results, and satellite coverage.

Examples:

```text
GET /health

GET /api/analysis/dates?pollutant=CH4

GET /api/spatial/cells?pollutant=CH4&date=2026-05-09

GET /api/anomalies/spatial?pollutant=CH4&date=2026-05-09

GET /api/analysis/coverage?pollutant=CH4&date=2026-05-09
```

Interactive API documentation is available through Swagger when the backend is running:

```text
http://127.0.0.1:8000/docs
```

## Running the Backend

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project:

```bash
pip install -e .
```

Create a `.env` file containing your Copernicus credentials:

```text
COPERNICUS_CLIENT_ID=your_client_id
COPERNICUS_CLIENT_SECRET=your_client_secret
```

Start the API:

```bash
uvicorn pollution_ai.api.app:app --reload
```

## Running the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The development server will display the local URL for the dashboard.

## Running Tests

Run the backend test suite with:

```bash
pytest
```

Build the frontend with:

```bash
cd frontend
npm run build
```

## Historical Backfill

Historical analysis can be planned without making Copernicus requests:

```bash
python -m pollution_ai.analysis.backfill \
  --pollutant CH4 \
  --from 2026-05-01 \
  --to 2026-05-10 \
  --dry-run
```

To execute the backfill:

```bash
python -m pollution_ai.analysis.backfill \
  --pollutant CH4 \
  --from 2026-05-01 \
  --to 2026-05-10 \
  --execute
```

The backfill process reuses cached observations and completed analyses whenever possible to avoid unnecessary API requests.

## Project Structure

```text
pollution_poc/
├── docs/
│   └── anomaly.gif
├── frontend/
│   └── src/
│       └── components/
├── src/
│   └── pollution_ai/
│       ├── analysis/
│       ├── api/
│       ├── config/
│       ├── integrations/
│       ├── models/
│       └── services/
├── tests/
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Roadmap

Development is ongoing. Planned improvements and new features are tracked through GitHub Issues.

Potential areas include:

- Historical anomaly trends
- Additional analysis and visualization capabilities
- Improved data availability handling
- Deployment
- Expanded documentation

## Contributing

Contributions are welcome.

If you would like to improve the project, fix a bug, or implement a feature:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Add or update tests where appropriate.
5. Open a pull request.

For larger changes, consider opening an issue first to discuss the proposed implementation.

## Disclaimer

This project is intended for software development, experimentation, and exploratory analysis.

The anomaly results represent statistical differences from historical satellite observations and should not be interpreted as official air-quality alerts or measurements from ground-based monitoring stations.