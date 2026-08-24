from fastapi import FastAPI

from pollution_ai.services.analysis_service import AnalysisService

from pollution_ai.services.analysis_service import AnalysisService


app = FastAPI(
    title="Pollution.ai API",
    description=(
        "Satellite-based pollution anomaly detection "
        "using Copernicus data."
    ),
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "pollution-ai",
    }

@app.get("/api/anomalies/spatial")
def get_spatial_anomaly():
    results = [
        {
            "row": 0,
            "col": 0,
            "bbox": [17.90, 59.30, 18.00, 59.40],
            "observed_value": 1900.0,
            "baseline_mean": 1880.0,
            "z_score": 1.2,
        },
        {
            "row": 1,
            "col": 1,
            "bbox": [18.00, 59.40, 18.10, 59.50],
            "observed_value": 1950.0,
            "baseline_mean": 1880.0,
            "z_score": 3.48,
        },
    ]

    return AnalysisService.build_spatial_anomaly_response(
        results=results,
        pollutant="CH4",
        date="2026-05-09",
        unit="ppb",
    )