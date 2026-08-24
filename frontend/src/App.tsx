import { useEffect, useState } from "react"

import "./App.css"

import AnalysisSummary from "./components/AnalysisSummary"
import PollutionMap from "./components/PollutionMap"


type Pollutant = "CH4" | "NO2"

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


function App() {
  const [pollutant, setPollutant] =
    useState<Pollutant>("CH4")

  const [cells, setCells] =
    useState<SpatialCell[]>([])

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
    <div className="app">
      <header className="header">
        <div>
          <h1>Pollution.ai</h1>
          <p>
            Satellite-based pollution anomaly detection
          </p>
        </div>

        <div className="status">
          <span className="status-dot" />
          API connected
        </div>
      </header>

      <main className="dashboard">
        <section className="controls">
          <div>
            <label htmlFor="pollutant">
              Pollutant
            </label>

            <select
              id="pollutant"
              value={pollutant}
              onChange={(event) =>
                setPollutant(
                  event.target.value as Pollutant,
                )
              }
            >
              <option value="CH4">
                Methane (CH₄)
              </option>

              <option value="NO2">
                Nitrogen dioxide (NO₂)
              </option>
            </select>
          </div>

          <div className="analysis-info">
            <span>Analysis date</span>
            <strong>2026-05-09</strong>
          </div>
        </section>

        <AnalysisSummary
          cells={cells}
          pollutant={pollutant}
        />

        <section className="map-panel">
          <PollutionMap
            pollutant={pollutant}
            cells={cells}
          />
        </section>
      </main>
    </div>
  )
}


export default App