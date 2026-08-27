import argparse
import json
from datetime import date
from pathlib import Path

from pollution_ai.analysis.spatial_anomaly_detector import (
    build_anomaly_result,
    calculate_spatial_z_score,
    find_strongest_spatial_anomaly,
)
from pollution_ai.config.pollutants import POLLUTANTS


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Build a spatial pollution anomaly result "
            "using reusable baseline statistics."
        )
    )

    parser.add_argument(
        "--pollutant",
        choices=POLLUTANTS.keys(),
        required=True,
        help="Pollutant to analyse.",
    )

    parser.add_argument(
        "--date",
        required=True,
        help="Analysis date in YYYY-MM-DD format.",
    )

    return parser.parse_args()


def parse_analysis_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            "Date must use YYYY-MM-DD format."
        ) from error


def load_json(file_path: Path):
    with file_path.open(
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_existing_results(
    output_file: Path,
):
    if not output_file.exists():
        return []

    return load_json(output_file)


def save_results(
    output_file: Path,
    results,
):
    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )


def build_baseline_lookup(
    baseline_stats,
):
    return {
        (
            result["row"],
            result["col"],
        ): result
        for result in baseline_stats
    }


def main():
    args = parse_arguments()

    analysis_date = (
        parse_analysis_date(
            args.date
        ).isoformat()
    )

    pollutant = args.pollutant
    pollutant_config = POLLUTANTS[pollutant]

    source_file = Path(
        "stockholm_spatial_"
        f"{pollutant.lower()}_"
        f"{analysis_date}.json"
    )

    baseline_file = Path(
        "stockholm_baseline_stats_"
        f"{pollutant.lower()}.json"
    )

    output_file = Path(
        "stockholm_spatial_baseline_"
        f"{pollutant.lower()}_"
        f"{analysis_date}.json"
    )

    if not source_file.exists():
        raise FileNotFoundError(
            "Spatial source data does not exist: "
            f"{source_file}"
        )

    if not baseline_file.exists():
        raise FileNotFoundError(
            "Baseline statistics do not exist: "
            f"{baseline_file}"
        )

    spatial_cells = load_json(
        source_file
    )

    baseline_stats = load_json(
        baseline_file
    )

    baseline_lookup = build_baseline_lookup(
        baseline_stats
    )

    results = load_existing_results(
        output_file
    )

    completed_cells = {
        (
            result["row"],
            result["col"],
        )
        for result in results
    }

    print(
        f"Existing {pollutant} baseline cells: "
        f"{len(completed_cells)}/"
        f"{len(spatial_cells)}"
    )

    for cell in spatial_cells:
        key = (
            cell["row"],
            cell["col"],
        )

        if key in completed_cells:
            continue

        baseline = baseline_lookup.get(
            key
        )

        observed = cell["value"]

        if baseline is None:
            result = {
                "row": cell["row"],
                "col": cell["col"],
                "bbox": cell["bbox"],
                "pollutant": pollutant,
                "observed_value": observed,
                "baseline_mean": None,
                "baseline_std": None,
                "valid_observations": 0,
                "z_score": None,
            }

        else:
            mean = baseline[
                "baseline_mean"
            ]

            std = baseline[
                "baseline_std"
            ]

            valid_observations = baseline[
                "valid_observations"
            ]

            z_score = (
                calculate_spatial_z_score(
                    observed,
                    mean,
                    std,
                )
            )

            result = {
                "row": cell["row"],
                "col": cell["col"],
                "bbox": cell["bbox"],
                "pollutant": pollutant,
                "observed_value": observed,
                "baseline_mean": mean,
                "baseline_std": std,
                "valid_observations": (
                    valid_observations
                ),
                "z_score": z_score,
            }

        results.append(result)

        save_results(
            output_file=output_file,
            results=results,
        )

        if (
            len(results) % 8 == 0
            or len(results)
            == len(spatial_cells)
        ):
            print(
                f"Processed "
                f"{len(results)}/"
                f"{len(spatial_cells)} cells"
            )

    valid_results = [
        result
        for result in results
        if result["z_score"] is not None
    ]

    strongest = (
        find_strongest_spatial_anomaly(
            results
        )
    )

    anomaly_result = build_anomaly_result(
        strongest=strongest,
        pollutant=pollutant,
        date=analysis_date,
        unit=pollutant_config["unit"],
    )

    print()

    print(
        f"Valid {pollutant} baseline cells: "
        f"{len(valid_results)}/"
        f"{len(results)}"
    )

    if anomaly_result is not None:
        print(
            f"Strongest {pollutant} "
            f"spatial anomaly: "
            f"row={strongest['row']} "
            f"col={strongest['col']}"
        )

        print(
            f"Observed {pollutant}: "
            f"{anomaly_result.observed_value:.2e} "
            f"{anomaly_result.unit}"
        )

        print(
            "Baseline mean: "
            f"{anomaly_result.baseline_mean:.2e} "
            f"{anomaly_result.unit}"
        )

        print(
            "Z-score: "
            f"{anomaly_result.z_score:.2f}"
        )

        print(
            "Approximate center: "
            f"{anomaly_result.latitude:.4f}, "
            f"{anomaly_result.longitude:.4f}"
        )

    print(
        f"Saved {output_file}"
    )


if __name__ == "__main__":
    main()