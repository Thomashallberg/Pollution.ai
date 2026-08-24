import { useEffect } from "react"
import {
    MapContainer,
    Popup,
    Rectangle,
    TileLayer,
    useMap,
} from "react-leaflet"

import "leaflet/dist/leaflet.css"


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


type PollutionMapProps = {
    pollutant: "CH4" | "NO2"
    cells: SpatialCell[]
}


function MapResizer() {
    const map = useMap()

    useEffect(() => {
        const resizeMap = () => {
            map.invalidateSize()
        }

        resizeMap()

        const timeout = window.setTimeout(
            resizeMap,
            100,
        )

        window.addEventListener(
            "resize",
            resizeMap,
        )

        return () => {
            window.clearTimeout(timeout)

            window.removeEventListener(
                "resize",
                resizeMap,
            )
        }
    }, [map])

    return null
}


function getSeverityColor(
    severity: string | null,
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
            return "#64748b"
    }
}


function MapLegend() {
    const items = [
        {
            label: "Low",
            color: "#22c55e",
        },
        {
            label: "Moderate",
            color: "#eab308",
        },
        {
            label: "High",
            color: "#f97316",
        },
        {
            label: "Extreme",
            color: "#dc2626",
        },
        {
            label: "No anomaly",
            color: "#64748b",
        },
    ]

    return (
        <div className="map-legend">
            <strong>Anomaly severity</strong>

            {items.map((item) => (
                <div
                    className="legend-item"
                    key={item.label}
                >
                    <span
                        className="legend-color"
                        style={{
                            backgroundColor: item.color,
                        }}
                    />

                    <span>{item.label}</span>
                </div>
            ))}
        </div>
    )
}


function formatValue(
    value: number | null,
    pollutant: "CH4" | "NO2",
) {
    if (value === null) {
        return "N/A"
    }

    if (pollutant === "NO2") {
        return value.toExponential(2)
    }

    return value.toFixed(2)
}


function formatZScore(
    value: number | null,
) {
    if (value === null) {
        return "N/A"
    }

    return value.toFixed(2)
}


function getUnit(
    pollutant: "CH4" | "NO2",
) {
    if (pollutant === "CH4") {
        return "ppb"
    }

    return "mol/m²"
}


function PollutionMap({
    pollutant,
    cells,
}: PollutionMapProps) {
    const unit = getUnit(pollutant)

    return (
        <MapContainer
            center={[59.3293, 18.0686]}
            zoom={10}
            scrollWheelZoom={true}
            className="pollution-map"
        >
            <MapResizer />
            <MapLegend />

            <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {cells.map((cell) => {
                const [
                    minLon,
                    minLat,
                    maxLon,
                    maxLat,
                ] = cell.bbox

                const color = getSeverityColor(
                    cell.severity,
                )

                return (
                    <Rectangle
                        key={`${cell.row}-${cell.col}`}
                        bounds={[
                            [minLat, minLon],
                            [maxLat, maxLon],
                        ]}
                        pathOptions={{
                            color,
                            fillColor: color,
                            fillOpacity: 0.35,
                            weight: 1,
                        }}
                    >
                        <Popup>
                            <div className="cell-popup">
                                <strong>
                                    {pollutant === "CH4"
                                        ? "Methane (CH₄)"
                                        : "Nitrogen dioxide (NO₂)"}
                                </strong>

                                <hr />

                                <div>
                                    Observed:{" "}
                                    <strong>
                                        {formatValue(
                                            cell.observed_value,
                                            pollutant,
                                        )}{" "}
                                        {unit}
                                    </strong>
                                </div>

                                <div>
                                    Baseline:{" "}
                                    <strong>
                                        {formatValue(
                                            cell.baseline_mean,
                                            pollutant,
                                        )}{" "}
                                        {unit}
                                    </strong>
                                </div>

                                <div>
                                    Z-score:{" "}
                                    <strong>
                                        {formatZScore(
                                            cell.z_score,
                                        )}
                                    </strong>
                                </div>

                                <div>
                                    Severity:{" "}
                                    <strong>
                                        {cell.severity ?? "N/A"}
                                    </strong>
                                </div>

                                <div>
                                    Observations:{" "}
                                    <strong>
                                        {cell.valid_observations}
                                    </strong>
                                </div>
                            </div>
                        </Popup>
                    </Rectangle>
                )
            })}
        </MapContainer>
    )
}


export default PollutionMap