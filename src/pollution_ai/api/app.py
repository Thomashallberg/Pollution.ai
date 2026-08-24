from datetime import date

from fastapi import FastAPI, HTTPException, Query
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


AVAILABLE_ANALYSIS_DATE = date(2026, 5, 9)


def validate_analysis_date(
    analysis_date: date,
) -> None:
    if analysis_date != AVAILABLE_ANALYSIS_DATE:
        raise HTTPException(
            status_code=404,
            detail=(
                "No cached analysis data available "
                f"for {analysis_date.isoformat()}."
            ),
        )


def get_spatial_file_path(
    pollutant: Pollutant,
) -> str:
    return (
        "stockholm_spatial_baseline_"
        f"{pollutant.value.lower()}.json"
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
    analysis_date: date = Query(
        default=AVAILABLE_ANALYSIS_DATE,
        alias="date",
    ),
):
    validate_analysis_date(
        analysis_date,
    )

    pollutant_value = pollutant.value
    pollutant_config = POLLUTANTS[pollutant_value]

    return AnalysisService.load_spatial_anomaly_response(
        file_path=get_spatial_file_path(
            pollutant,
        ),
        pollutant=pollutant_value,
        date=analysis_date.isoformat(),
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
    analysis_date: date = Query(
        default=AVAILABLE_ANALYSIS_DATE,
        alias="date",
    ),
):
    validate_analysis_date(
        analysis_date,
    )

    return AnalysisService.load_spatial_cells(
        file_path=get_spatial_file_path(
            pollutant,
        ),
    )