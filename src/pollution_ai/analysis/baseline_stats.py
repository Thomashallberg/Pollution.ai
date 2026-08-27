import argparse
import json
from pathlib import Path

from pollution_ai.config.pollutants import POLLUTANTS


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Extract reusable spatial baseline statistics "
            "from an existing analysis."
        )
    )

    parser.add_argument(
        "--pollutant",
        choices=POLLUTANTS.keys(),
        required=True,
    )

    parser.add_argument(
        "--source-date",
        required=True,
        help="Existing baseline date in YYYY-MM-DD format.",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    pollutant = args.pollutant
    source_date = args.source_date

    source_file = Path(
        "stockholm_spatial_baseline_"
        f"{pollutant.lower()}_"
        f"{source_date}.json"
    )

    output_file = Path(
        "stockholm_baseline_stats_"
        f"{pollutant.lower()}.json"
    )

    if not source_file.exists():
        raise FileNotFoundError(
            f"Baseline source does not exist: {source_file}"
        )

    with source_file.open(
        encoding="utf-8",
    ) as file:
        results = json.load(file)

    baseline_stats = []

    for result in results:
        baseline_stats.append(
            {
                "row": result["row"],
                "col": result["col"],
                "bbox": result["bbox"],
                "pollutant": pollutant,
                "baseline_mean": result["baseline_mean"],
                "baseline_std": result["baseline_std"],
                "valid_observations": (
                    result["valid_observations"]
                ),
            }
        )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            baseline_stats,
            file,
            indent=2,
        )

    valid_stats = [
        result
        for result in baseline_stats
        if (
            result["baseline_mean"] is not None
            and result["baseline_std"] is not None
        )
    ]

    print(
        f"Extracted {len(valid_stats)}/"
        f"{len(baseline_stats)} valid "
        f"{pollutant} baseline cells"
    )

    print(
        f"Saved {output_file}"
    )


if __name__ == "__main__":
    main()