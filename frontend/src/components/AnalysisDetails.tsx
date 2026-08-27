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

type SpatialAnomaly = {
    pollutant: string
    date: string
    latitude: number
    longitude: number
    observed_value: number
    baseline_mean: number
    z_score: number
    deviation_percent: number | null
    unit: string
    severity: string
}

type AnalysisDetailsProps = {
    cells: SpatialCell[]
    pollutant: "CH4" | "NO2"
    anomaly: SpatialAnomaly | null
}


function formatValue(
    value: number,
    pollutant: "CH4" | "NO2",
) {
    if (pollutant === "NO2") {
        return value.toExponential(2)
    }

    return value.toFixed(2)
}


function formatDifference(
    observed: number,
    baseline: number,
    pollutant: "CH4" | "NO2",
) {
    const difference =
        observed - baseline

    const prefix =
        difference > 0
            ? "+"
            : ""

    if (pollutant === "NO2") {
        return (
            `${prefix}` +
            `${difference.toExponential(2)}`
        )
    }

    return (
        `${prefix}` +
        `${difference.toFixed(2)}`
    )
}


function formatDeviation(
    value: number | null,
) {
    if (value === null) {
        return "N/A"
    }

    const prefix =
        value > 0
            ? "+"
            : ""

    return (
        `${prefix}` +
        `${value.toFixed(2)}%`
    )
}


function AnalysisDetails({
    cells,
    pollutant,
    anomaly,
}: AnalysisDetailsProps) {
    const validCells = cells.filter(
        (cell) => cell.z_score !== null,
    )

    const anomalousCells =
        validCells.filter(
            (cell) =>
                cell.severity === "moderate" ||
                cell.severity === "high" ||
                cell.severity === "extreme",
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

    const unit =
        pollutant === "CH4"
            ? "ppb"
            : "mol/m²"

    const deviationDirection =
        anomaly?.deviation_percent !== null &&
            anomaly?.deviation_percent !== undefined
            ? anomaly.deviation_percent >= 0
                ? "above baseline"
                : "below baseline"
            : null

    return (
        <section className="analysis-details">
            {anomaly && (
                <div className="comparison-panel">
                    <div className="comparison-heading">
                        <span>
                            Strongest anomaly
                        </span>

                        <h3>
                            Observed vs baseline
                        </h3>
                    </div>

                    <div className="comparison-grid">
                        <div className="comparison-item">
                            <span>
                                Observed
                            </span>

                            <strong>
                                {formatValue(
                                    anomaly.observed_value,
                                    pollutant,
                                )}{" "}
                                {unit}
                            </strong>
                        </div>

                        <div className="comparison-item">
                            <span>
                                Baseline
                            </span>

                            <strong>
                                {formatValue(
                                    anomaly.baseline_mean,
                                    pollutant,
                                )}{" "}
                                {unit}
                            </strong>
                        </div>

                        <div className="comparison-item">
                            <span>
                                Difference
                            </span>

                            <strong>
                                {formatDifference(
                                    anomaly.observed_value,
                                    anomaly.baseline_mean,
                                    pollutant,
                                )}{" "}
                                {unit}
                            </strong>
                        </div>

                        <div className="comparison-item">
                            <span>
                                Deviation
                            </span>

                            <strong>
                                {formatDeviation(
                                    anomaly.deviation_percent,
                                )}
                            </strong>

                            {deviationDirection && (
                                <small>
                                    {
                                        deviationDirection
                                    }
                                </small>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <div className="additional-statistics">
                <div className="comparison-heading">
                    <span>
                        Analysis details
                    </span>

                    <h3>
                        Additional statistics
                    </h3>
                </div>

                <div className="comparison-grid">
                    <div className="comparison-item">
                        <span>
                            Anomalous cells
                        </span>

                        <strong>
                            {
                                anomalousCells.length
                            }
                            {" / "}
                            {
                                validCells.length
                            }
                        </strong>
                    </div>

                    <div className="comparison-item">
                        <span>
                            Observations
                        </span>

                        <strong>
                            {
                                strongest
                                    ?.valid_observations
                                ?? "N/A"
                            }
                        </strong>
                    </div>
                </div>
            </div>
        </section>
    )
}


export default AnalysisDetails