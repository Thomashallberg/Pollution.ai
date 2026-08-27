type SpatialCell = {
    row: number
    col: number
    bbox: number[]
    pollutant: string
    observed_value: number | null
    baseline_mean: number | null
    baseline_std: number | null
    valid_observations: number
    z_score: number | null
    severity: string | null
}

type Coverage = {
    valid_cells: number
    total_cells: number
    coverage_percent: number
}

type AnalysisSummaryProps = {
    cells: SpatialCell[]
    pollutant: "CH4" | "NO2"
    coverage: Coverage | null
}


function getSeverityColor(
    severity: string | null | undefined,
) {
    switch (severity) {
        case "extreme":
            return "#dc2626"

        case "high":
            return "#f97316"

        case "moderate":
            return "#eab308"

        case "low":
            return "#22c55e"

        default:
            return "#f8fafc"
    }
}


function getCoverageStatus(
    validCells: number,
    totalCells: number,
) {
    if (totalCells === 0) {
        return "Unavailable"
    }

    if (validCells < 10) {
        return "Unavailable"
    }

    const percentage =
        (validCells / totalCells) * 100

    if (percentage >= 75) {
        return "Excellent"
    }

    if (percentage >= 50) {
        return "Good"
    }

    if (percentage >= 25) {
        return "Limited"
    }

    return "Poor"
}


function AnalysisSummary({
    cells,
    pollutant,
    coverage,
}: AnalysisSummaryProps) {
    const validCells = cells.filter(
        (cell) => cell.z_score !== null,
    )

    const strongest =
        validCells.length > 0
            ? validCells.reduce(
                (current, cell) =>
                    (
                        cell.z_score
                        ?? -Infinity
                    ) >
                        (
                            current.z_score
                            ?? -Infinity
                        )
                        ? cell
                        : current,
            )
            : null

    const pollutantLabel =
        pollutant === "CH4"
            ? "Methane (CH₄)"
            : "Nitrogen dioxide (NO₂)"

    return (
        <section className="analysis-summary">
            <div className="summary-heading">
                <div>
                    <span>
                        Analysis summary
                    </span>

                    <h2>
                        {pollutantLabel}
                    </h2>
                </div>
            </div>

            <div className="summary-grid">
                <div className="summary-card">
                    <span>
                        Strongest anomaly
                    </span>

                    <strong
                        style={{
                            color:
                                getSeverityColor(
                                    strongest?.severity,
                                ),
                        }}
                    >
                        {
                            strongest?.severity
                            ?? "N/A"
                        }
                    </strong>
                </div>

                <div className="summary-card">
                    <span>
                        Highest z-score
                    </span>

                    <strong>
                        {
                            strongest?.z_score
                                !== null &&
                                strongest?.z_score
                                !== undefined
                                ? strongest.z_score
                                    .toFixed(2)
                                : "N/A"
                        }
                    </strong>
                </div>

                <div className="summary-card">
                    <span>
                        Satellite coverage
                    </span>

                    <strong>
                        {
                            coverage
                                ? `${coverage.valid_cells} / ${coverage.total_cells}`
                                : "N/A"
                        }
                    </strong>

                    {coverage && (
                        <small>
                            {
                                coverage
                                    .coverage_percent
                                    .toFixed(2)
                            }
                            {"% · "}
                            {
                                getCoverageStatus(
                                    coverage.valid_cells,
                                    coverage.total_cells,
                                )
                            }
                        </small>
                    )}
                </div>
            </div>
        </section>
    )
}


export default AnalysisSummary