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

type AnalysisSummaryProps = {
    cells: SpatialCell[]
    pollutant: "CH4" | "NO2"
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


function AnalysisSummary({
    cells,
    pollutant,
}: AnalysisSummaryProps) {
    const validCells = cells.filter(
        (cell) => cell.z_score !== null,
    )

    const strongest =
        validCells.length > 0
            ? validCells.reduce((current, cell) =>
                (cell.z_score ?? -Infinity) >
                    (current.z_score ?? -Infinity)
                    ? cell
                    : current,
            )
            : null

    const anomalousCells = validCells.filter(
        (cell) =>
            cell.severity === "moderate" ||
            cell.severity === "high" ||
            cell.severity === "extreme",
    )

    const pollutantLabel =
        pollutant === "CH4"
            ? "Methane (CH₄)"
            : "Nitrogen dioxide (NO₂)"

    return (
        <section className="analysis-summary">
            <div className="summary-heading">
                <div>
                    <span>Analysis summary</span>
                    <h2>{pollutantLabel}</h2>
                </div>

                <div className="summary-count">
                    {validCells.length} valid cells
                </div>
            </div>

            <div className="summary-grid">
                <div className="summary-card">
                    <span>Strongest anomaly</span>

                    <strong
                        style={{
                            color: getSeverityColor(
                                strongest?.severity,
                            ),
                        }}
                    >
                        {strongest?.severity ?? "N/A"}
                    </strong>
                </div>

                <div className="summary-card">
                    <span>Highest z-score</span>

                    <strong>
                        {strongest?.z_score !== null &&
                            strongest?.z_score !== undefined
                            ? strongest.z_score.toFixed(2)
                            : "N/A"}
                    </strong>
                </div>

                <div className="summary-card">
                    <span>Anomalous cells</span>

                    <strong>
                        {anomalousCells.length} / {validCells.length}
                    </strong>
                </div>

                <div className="summary-card">
                    <span>Observations</span>

                    <strong>
                        {strongest?.valid_observations ?? "N/A"}
                    </strong>
                </div>
            </div>
        </section>
    )
}


export default AnalysisSummary