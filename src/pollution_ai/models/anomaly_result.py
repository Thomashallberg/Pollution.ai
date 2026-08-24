from dataclasses import asdict, dataclass


@dataclass
class AnomalyResult:
    pollutant: str
    date: str
    latitude: float
    longitude: float
    observed_value: float
    baseline_mean: float
    z_score: float
    unit: str
    severity: str

    def to_dict(self) -> dict:
        return asdict(self)