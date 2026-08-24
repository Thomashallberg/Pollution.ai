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
    unit: str
    severity: str