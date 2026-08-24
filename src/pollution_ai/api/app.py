from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from pollution_ai.api.schemas import (
    Pollutant,
    SpatialAnomalyResponse,
    SpatialCellResponse,
)
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "pollution-ai",
    }


@app.get(
    "/api/anomalies/spatial",
    response_model=SpatialAnomalyResponse,
)
def get_spatial_anomaly(
    pollutant: Pollutant = Query(
        default=Pollutant.CH4,
    ),
):
    pollutant_value = pollutant.value
    pollutant_config = POLLUTANTS[pollutant_value]

    file_path = (
        f"stockholm_spatial_baseline_"
        f"{pollutant_value.lower()}.json"
    )

    return AnalysisService.load_spatial_anomaly_response(
        file_path=file_path,
        pollutant=pollutant_value,
        date="2026-05-09",
        unit=pollutant_config["unit"],
    )


@app.get(
    "/api/spatial/cells",
    response_model=list[SpatialCellResponse],
)
def get_spatial_cells(
    pollutant: Pollutant = Query(
        default=Pollutant.CH4,
    ),
):
    pollutant_value = pollutant.value

    file_path = (
        f"stockholm_spatial_baseline_"
        f"{pollutant_value.lower()}.json"
    )

    return AnalysisService.load_spatial_cells(
        file_path=file_path,
    )