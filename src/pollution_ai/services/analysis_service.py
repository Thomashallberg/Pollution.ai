from pollution_ai.analysis.spatial_anomaly_detector import (
    build_anomaly_result,
    find_strongest_spatial_anomaly,
)


class AnalysisService:
    @staticmethod
    def build_spatial_anomaly_result(
        results,
        pollutant,
        date,
        unit,
    ):
        strongest = find_strongest_spatial_anomaly(results)

        return build_anomaly_result(
            strongest=strongest,
            pollutant=pollutant,
            date=date,
            unit=unit,
        )