import argparse
import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from pollution_ai.analysis.spatial_analysis import (
    run_spatial_analysis,
)
from pollution_ai.analysis.spatial_baseline import (
    run_spatial_baseline,
)
from pollution_ai.config.pollutants import POLLUTANTS


GRID_SIZE = 8
CELLS_PER_ANALYSIS = GRID_SIZE * GRID_SIZE


@dataclass
class BackfillItem:
    analysis_date: date
    status: str
    observation_file: Path
    analysis_file: Path


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Plan or execute spatial pollution "
            "analysis for a range of dates."
        )
    )

    parser.add_argument(
        "--pollutant",
        choices=POLLUTANTS.keys(),
        required=True,
        help="Pollutant to analyse.",
    )

    parser.add_argument(
        "--from",
        dest="from_date",
        required=True,
        help="First date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--to",
        dest="to_date",
        required=True,
        help="Last date in YYYY-MM-DD format.",
    )

    mode = parser.add_mutually_exclusive_group(
        required=True,
    )

    mode.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show the backfill plan without "
            "making any API requests."
        ),
    )

    mode.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Execute the backfill plan. "
            "May make Copernicus API requests."
        ),
    )

    return parser.parse_args()


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            "Dates must use YYYY-MM-DD format."
        ) from error


def iter_dates(
    from_date: date,
    to_date: date,
):
    current_date = from_date

    while current_date <= to_date:
        yield current_date
        current_date += timedelta(days=1)


def get_observation_file(
    pollutant: str,
    analysis_date: date,
) -> Path:
    return Path(
        "stockholm_spatial_"
        f"{pollutant.lower()}_"
        f"{analysis_date.isoformat()}.json"
    )


def get_analysis_file(
    pollutant: str,
    analysis_date: date,
) -> Path:
    return Path(
        "stockholm_spatial_baseline_"
        f"{pollutant.lower()}_"
        f"{analysis_date.isoformat()}.json"
    )


def has_valid_observations(
    observation_file: Path,
) -> bool:
    if not observation_file.exists():
        return False

    with observation_file.open(
        encoding="utf-8",
    ) as file:
        cells = json.load(file)

    return any(
        cell.get("value") is not None
        for cell in cells
    )


def build_backfill_plan(
    pollutant: str,
    from_date: date,
    to_date: date,
) -> list[BackfillItem]:
    if from_date > to_date:
        raise ValueError(
            "from_date must be before "
            "or equal to to_date."
        )

    plan = []

    for analysis_date in iter_dates(
        from_date,
        to_date,
    ):
        observation_file = get_observation_file(
            pollutant,
            analysis_date,
        )

        analysis_file = get_analysis_file(
            pollutant,
            analysis_date,
        )

        if analysis_file.exists():
            status = "SKIP"

        elif observation_file.exists():
            if has_valid_observations(
                observation_file
            ):
                status = "ANALYSE"
            else:
                status = "UNAVAILABLE"

        else:
            status = "FETCH"

        plan.append(
            BackfillItem(
                analysis_date=analysis_date,
                status=status,
                observation_file=observation_file,
                analysis_file=analysis_file,
            )
        )

    return plan


def get_status_label(
    item: BackfillItem,
) -> str:
    if item.status == "SKIP":
        return "SKIP (complete)"

    if item.status == "ANALYSE":
        return "ANALYSE (observation cached)"

    if item.status == "UNAVAILABLE":
        return (
            "UNAVAILABLE "
            "(no valid observations)"
        )

    return "FETCH"


def count_requests(
    plan: list[BackfillItem],
) -> int:
    fetch_days = sum(
        item.status == "FETCH"
        for item in plan
    )

    return (
        fetch_days
        * CELLS_PER_ANALYSIS
    )


def execute_backfill_plan(
    plan: list[BackfillItem],
    pollutant: str,
) -> None:
    for item in plan:
        analysis_date = (
            item.analysis_date.isoformat()
        )

        print()
        print(
            f"[{analysis_date}] "
            f"{get_status_label(item)}"
        )

        if item.status in {
            "SKIP",
            "UNAVAILABLE",
        }:
            continue

        if item.status == "FETCH":
            run_spatial_analysis(
                pollutant=pollutant,
                analysis_date=analysis_date,
            )

            if not has_valid_observations(
                item.observation_file
            ):
                print(
                    "No valid observations found. "
                    "Skipping analysis."
                )
                continue

        run_spatial_baseline(
            pollutant=pollutant,
            analysis_date=analysis_date,
        )


def main():
    args = parse_arguments()

    pollutant = args.pollutant

    from_date = parse_date(
        args.from_date
    )

    to_date = parse_date(
        args.to_date
    )

    plan = build_backfill_plan(
        pollutant=pollutant,
        from_date=from_date,
        to_date=to_date,
    )

    days_requiring_observations = sum(
        item.status == "FETCH"
        for item in plan
    )

    days_requiring_analysis = sum(
        item.status in {
            "FETCH",
            "ANALYSE",
        }
        for item in plan
    )

    unavailable_days = sum(
        item.status == "UNAVAILABLE"
        for item in plan
    )

    estimated_requests = count_requests(
        plan
    )

    print()
    print(
        f"Backfill plan: {pollutant}"
    )

    print(
        f"Range: {from_date} -> {to_date}"
    )

    print()

    for item in plan:
        print(
            f"{item.analysis_date.isoformat()}  "
            f"{get_status_label(item)}"
        )

    print()

    print(
        "Days requiring observations: "
        f"{days_requiring_observations}"
    )

    print(
        "Days requiring analysis: "
        f"{days_requiring_analysis}"
    )

    print(
        "Unavailable days: "
        f"{unavailable_days}"
    )

    print(
        "Estimated maximum observation requests: "
        f"{estimated_requests}"
    )

    if args.dry_run:
        print()
        print(
            "Dry run - no Copernicus "
            "requests made."
        )
        return

    print()
    print(
        "Executing backfill plan..."
    )

    execute_backfill_plan(
        plan=plan,
        pollutant=pollutant,
    )

    print()
    print(
        "Backfill complete."
    )


if __name__ == "__main__":
    main()