from pydantic import BaseModel


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