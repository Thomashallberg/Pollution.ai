import { useEffect, useState } from "react"
import {
    MapContainer,
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


function PollutionMap({
    pollutant,
}: PollutionMapProps) {
    const [cells, setCells] = useState<SpatialCell[]>([])

    useEffect(() => {
        fetch(
            `http://127.0.0.1:8000/api/spatial/cells?pollutant=${pollutant}`,
        )
            .then((response) => {
                if (!response.ok) {
                    throw new Error(
                        "Failed to fetch spatial cells",
                    )
                }

                return response.json()
            })
            .then((data: SpatialCell[]) => {
                setCells(data)
            })
            .catch((error) => {
                console.error(error)
            })
    }, [pollutant])

    return (
        <MapContainer
            center={[59.3293, 18.0686]}
            zoom={10}
            scrollWheelZoom={true}
            className="pollution-map"
        >
            <MapResizer />

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

                return (
                    <Rectangle
                        key={`${cell.row}-${cell.col}`}
                        bounds={[
                            [minLat, minLon],
                            [maxLat, maxLon],
                        ]}
                        pathOptions={{
                            color: getSeverityColor(
                                cell.severity,
                            ),
                            fillColor: getSeverityColor(
                                cell.severity,
                            ),
                            fillOpacity: 0.35,
                            weight: 1,
                        }}
                    />
                )
            })}
        </MapContainer>
    )
}


export default PollutionMap