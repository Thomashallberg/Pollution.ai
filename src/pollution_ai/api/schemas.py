from enum import Enum

from pydantic import BaseModel


class Pollutant(str, Enum):
    NO2 = "NO2"
    CH4 = "CH4"


class SpatialAnomalyResponse(BaseModel):
    pollutant: str
    date: str

    latitude: float
    longitude: float

    observed_value: float
    baseline_mean: float

    z_score: float
    deviation_percent: float | None

    unit: str
    severity: str


class SpatialCellResponse(BaseModel):
    row: int
    col: int

    bbox: list[float]

    pollutant: str

    observed_value: float | None
    baseline_mean: float | None
    baseline_std: float | None

    valid_observations: int

    z_score: float | None
    severity: str | None