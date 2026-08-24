from fastapi import FastAPI, HTTPException, Query

from pollution_ai.config.pollutants import POLLUTANTS
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
def get_spatial_anomaly(
    pollutant: str = Query(default="CH4"),
):
    pollutant = pollutant.upper()

    if pollutant not in POLLUTANTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported pollutant: {pollutant}",
        )

    pollutant_config = POLLUTANTS[pollutant]

    file_path = (
        f"stockholm_spatial_baseline_"
        f"{pollutant.lower()}.json"
    )

    return AnalysisService.load_spatial_anomaly_response(
        file_path=file_path,
        pollutant=pollutant,
        date="2026-05-09",
        unit=pollutant_config["unit"],
    )