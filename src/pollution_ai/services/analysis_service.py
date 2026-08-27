import json
import re
from pathlib import Path

from pollution_ai.analysis.anomaly_detector import (
    classify_severity,
)
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
        strongest = (
            find_strongest_spatial_anomaly(
                results
            )
        )

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
        anomaly_result = (
            AnalysisService
            .build_spatial_anomaly_result(
                results=results,
                pollutant=pollutant,
                date=date,
                unit=unit,
            )
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

        return (
            AnalysisService
            .build_spatial_anomaly_response(
                results=results,
                pollutant=pollutant,
                date=date,
                unit=unit,
            )
        )

    @staticmethod
    def load_spatial_cells(
        file_path,
    ):
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

    @staticmethod
    def get_spatial_file_path(
        pollutant: str,
        analysis_date: str,
    ) -> Path:
        return Path(
            "stockholm_spatial_baseline_"
            f"{pollutant.lower()}_"
            f"{analysis_date}.json"
        )

    @staticmethod
    def get_available_analysis_dates(
        pollutant: str,
    ) -> list[str]:
        pattern = re.compile(
            rf"stockholm_spatial_baseline_"
            rf"{pollutant.lower()}_"
            r"(\d{4}-\d{2}-\d{2})\.json$"
        )

        dates = set()

        for path in Path(".").glob(
            "stockholm_spatial_baseline_*.json"
        ):
            match = pattern.fullmatch(
                path.name
            )

            if match:
                dates.add(
                    match.group(1)
                )

        return sorted(dates)

    @staticmethod
    def calculate_coverage(
        results,
    ) -> dict:
        total_cells = len(results)

        valid_cells = sum(
            result.get(
                "observed_value"
            )
            is not None
            for result in results
        )

        if total_cells == 0:
            coverage_percent = 0.0
        else:
            coverage_percent = round(
                (
                    valid_cells
                    / total_cells
                )
                * 100,
                2,
            )

        return {
            "valid_cells": valid_cells,
            "total_cells": total_cells,
            "coverage_percent": (
                coverage_percent
            ),
        }

    @staticmethod
    def load_coverage(
        file_path,
    ) -> dict:
        path = Path(file_path)

        with path.open(
            encoding="utf-8",
        ) as file:
            results = json.load(file)

        return (
            AnalysisService
            .calculate_coverage(
                results
            )
        )