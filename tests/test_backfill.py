from datetime import date
from pathlib import Path

import pytest

from pollution_ai.analysis.backfill import (
    BackfillItem,
    CELLS_PER_ANALYSIS,
    build_backfill_plan,
    execute_backfill_plan,
    get_analysis_file,
    get_observation_file,
    iter_dates,
    parse_date,
)


def test_parse_date():
    result = parse_date(
        "2026-05-09"
    )

    assert result == date(
        2026,
        5,
        9,
    )


def test_parse_date_rejects_invalid_format():
    with pytest.raises(
        ValueError,
        match="Dates must use YYYY-MM-DD format.",
    ):
        parse_date(
            "09-05-2026"
        )


def test_iter_dates_includes_entire_range():
    result = list(
        iter_dates(
            date(2026, 5, 9),
            date(2026, 5, 12),
        )
    )

    assert result == [
        date(2026, 5, 9),
        date(2026, 5, 10),
        date(2026, 5, 11),
        date(2026, 5, 12),
    ]


def test_observation_file_name():
    result = get_observation_file(
        "CH4",
        date(2026, 5, 10),
    )

    assert result.name == (
        "stockholm_spatial_ch4_"
        "2026-05-10.json"
    )


def test_analysis_file_name():
    result = get_analysis_file(
        "NO2",
        date(2026, 5, 10),
    )

    assert result.name == (
        "stockholm_spatial_baseline_no2_"
        "2026-05-10.json"
    )


def test_request_estimate_per_day():
    assert CELLS_PER_ANALYSIS == 64

    days_requiring_observations = 3

    estimated_requests = (
        days_requiring_observations
        * CELLS_PER_ANALYSIS
    )

    assert estimated_requests == 192


def test_build_backfill_plan_marks_complete_as_skip(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    analysis_file = (
        tmp_path
        / "stockholm_spatial_baseline_ch4_2026-05-09.json"
    )

    analysis_file.write_text(
        "[]",
        encoding="utf-8",
    )

    plan = build_backfill_plan(
        pollutant="CH4",
        from_date=date(2026, 5, 9),
        to_date=date(2026, 5, 9),
    )

    assert plan[0].status == "SKIP"


def test_build_backfill_plan_marks_cached_observation_as_analyse(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    observation_file = (
        tmp_path
        / "stockholm_spatial_ch4_2026-05-09.json"
    )

    observation_file.write_text(
        """
[
    {
        "row": 0,
        "col": 0,
        "bbox": [
            17.6,
            59.1,
            17.7,
            59.2
        ],
        "value": 1900.0
    }
]
""".strip(),
        encoding="utf-8",
    )

    plan = build_backfill_plan(
        pollutant="CH4",
        from_date=date(2026, 5, 9),
        to_date=date(2026, 5, 9),
    )

    assert plan[0].status == "ANALYSE"


def test_build_backfill_plan_marks_missing_data_as_fetch(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    plan = build_backfill_plan(
        pollutant="CH4",
        from_date=date(2026, 5, 9),
        to_date=date(2026, 5, 9),
    )

    assert plan[0].status == "FETCH"


def test_build_backfill_plan_marks_empty_observation_as_unavailable(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    observation_file = (
        tmp_path
        / "stockholm_spatial_ch4_2026-05-11.json"
    )

    observation_file.write_text(
        """
[
    {
        "row": 0,
        "col": 0,
        "bbox": [
            17.6,
            59.1,
            17.7,
            59.2
        ],
        "value": null
    }
]
""".strip(),
        encoding="utf-8",
    )

    plan = build_backfill_plan(
        pollutant="CH4",
        from_date=date(2026, 5, 11),
        to_date=date(2026, 5, 11),
    )

    assert plan[0].status == "UNAVAILABLE"


def test_execute_backfill_plan_skips_complete(
    monkeypatch,
):
    analysis_calls = []
    baseline_calls = []

    monkeypatch.setattr(
        "pollution_ai.analysis.backfill.run_spatial_analysis",
        lambda **kwargs: analysis_calls.append(
            kwargs
        ),
    )

    monkeypatch.setattr(
        "pollution_ai.analysis.backfill.run_spatial_baseline",
        lambda **kwargs: baseline_calls.append(
            kwargs
        ),
    )

    plan = [
        BackfillItem(
            analysis_date=date(2026, 5, 9),
            status="SKIP",
            observation_file=Path(
                "observation.json"
            ),
            analysis_file=Path(
                "analysis.json"
            ),
        )
    ]

    execute_backfill_plan(
        plan=plan,
        pollutant="CH4",
    )

    assert analysis_calls == []
    assert baseline_calls == []


def test_execute_backfill_plan_skips_unavailable(
    monkeypatch,
):
    analysis_calls = []
    baseline_calls = []

    monkeypatch.setattr(
        "pollution_ai.analysis.backfill.run_spatial_analysis",
        lambda **kwargs: analysis_calls.append(
            kwargs
        ),
    )

    monkeypatch.setattr(
        "pollution_ai.analysis.backfill.run_spatial_baseline",
        lambda **kwargs: baseline_calls.append(
            kwargs
        ),
    )

    plan = [
        BackfillItem(
            analysis_date=date(2026, 5, 11),
            status="UNAVAILABLE",
            observation_file=Path(
                "observation.json"
            ),
            analysis_file=Path(
                "analysis.json"
            ),
        )
    ]

    execute_backfill_plan(
        plan=plan,
        pollutant="CH4",
    )

    assert analysis_calls == []
    assert baseline_calls == []


def test_execute_backfill_plan_analyses_cached_observation(
    monkeypatch,
):
    analysis_calls = []
    baseline_calls = []

    monkeypatch.setattr(
        "pollution_ai.analysis.backfill.run_spatial_analysis",
        lambda **kwargs: analysis_calls.append(
            kwargs
        ),
    )

    monkeypatch.setattr(
        "pollution_ai.analysis.backfill.run_spatial_baseline",
        lambda **kwargs: baseline_calls.append(
            kwargs
        ),
    )

    plan = [
        BackfillItem(
            analysis_date=date(2026, 5, 10),
            status="ANALYSE",
            observation_file=Path(
                "observation.json"
            ),
            analysis_file=Path(
                "analysis.json"
            ),
        )
    ]

    execute_backfill_plan(
        plan=plan,
        pollutant="NO2",
    )

    assert analysis_calls == []

    assert baseline_calls == [
        {
            "pollutant": "NO2",
            "analysis_date": "2026-05-10",
        }
    ]


def test_execute_backfill_plan_fetches_then_analyses(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    calls = []

    observation_file = (
        tmp_path
        / "stockholm_spatial_ch4_2026-05-11.json"
    )

    def fake_spatial_analysis(**kwargs):
        calls.append(
            (
                "analysis",
                kwargs,
            )
        )

        observation_file.write_text(
            """
[
    {
        "row": 0,
        "col": 0,
        "bbox": [
            17.6,
            59.1,
            17.7,
            59.2
        ],
        "value": 1900.0
    }
]
""".strip(),
            encoding="utf-8",
        )

    def fake_spatial_baseline(**kwargs):
        calls.append(
            (
                "baseline",
                kwargs,
            )
        )

    monkeypatch.setattr(
        "pollution_ai.analysis.backfill.run_spatial_analysis",
        fake_spatial_analysis,
    )

    monkeypatch.setattr(
        "pollution_ai.analysis.backfill.run_spatial_baseline",
        fake_spatial_baseline,
    )

    plan = [
        BackfillItem(
            analysis_date=date(2026, 5, 11),
            status="FETCH",
            observation_file=observation_file,
            analysis_file=(
                tmp_path
                / "stockholm_spatial_baseline_ch4_2026-05-11.json"
            ),
        )
    ]

    execute_backfill_plan(
        plan=plan,
        pollutant="CH4",
    )

    assert calls == [
        (
            "analysis",
            {
                "pollutant": "CH4",
                "analysis_date": "2026-05-11",
            },
        ),
        (
            "baseline",
            {
                "pollutant": "CH4",
                "analysis_date": "2026-05-11",
            },
        ),
    ]