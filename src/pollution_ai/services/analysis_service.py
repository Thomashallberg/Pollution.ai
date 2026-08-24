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

    @staticmethod
    def build_spatial_anomaly_response(
        results,
        pollutant,
        date,
        unit,
    ):
        anomaly_result = AnalysisService.build_spatial_anomaly_result(
            results=results,
            pollutant=pollutant,
            date=date,
            unit=unit,
        )

        if anomaly_result is None:
            return None

        return anomaly_result.to_dict()