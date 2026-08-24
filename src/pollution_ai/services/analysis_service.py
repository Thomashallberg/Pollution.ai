import json
from pathlib import Path

from pollution_ai.analysis.anomaly_detector import classify_severity
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

    @staticmethod
    def load_spatial_anomaly_response(
        file_path,
        pollutant,
        date,
        unit,
    ):
        path = Path(file_path)

        with path.open(
            encoding="utf-8",
        ) as file:
            results = json.load(file)

        return AnalysisService.build_spatial_anomaly_response(
            results=results,
            pollutant=pollutant,
            date=date,
            unit=unit,
        )

    @staticmethod
    def load_spatial_cells(file_path):
        path = Path(file_path)

        with path.open(
            encoding="utf-8",
        ) as file:
            results = json.load(file)

        cells = []

        for result in results:
            cell = {
                **result,
                "severity": classify_severity(
                    result.get("z_score")
                ),
            }

            cells.append(cell)

        return cells