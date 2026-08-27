import { useEffect, useState } from "react"

import "./App.css"

import AnalysisDatePicker from "./components/AnalysisDatePicker"
import AnalysisDetails from "./components/AnalysisDetails"
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

type Coverage = {
  pollutant: string
  date: string
  valid_cells: number
  total_cells: number
  coverage_percent: number
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


function App() {
  const [pollutant, setPollutant] =
    useState<Pollutant>("CH4")

  const [availableDates, setAvailableDates] =
    useState<string[]>([])

  const [analysisDate, setAnalysisDate] =
    useState("")

  const [cells, setCells] =
    useState<SpatialCell[]>([])

  const [coverage, setCoverage] =
    useState<Coverage | null>(null)

  const [anomaly, setAnomaly] =
    useState<SpatialAnomaly | null>(null)

  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    const loadAvailableDates = async () => {
      setError(null)
      setAvailableDates([])
      setAnalysisDate("")
      setCells([])
      setCoverage(null)
      setAnomaly(null)

      try {
        const response = await fetch(
          `http://127.0.0.1:8000/api/analysis/dates` +
          `?pollutant=${pollutant}`,
        )

        if (!response.ok) {
          throw new Error(
            "Failed to load available analysis dates",
          )
        }

        const data: {
          dates: string[]
        } = await response.json()

        setAvailableDates(data.dates)

        if (data.dates.length > 0) {
          setAnalysisDate(data.dates[0])
        }
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message)
        } else {
          setError(
            "Failed to load available analysis dates",
          )
        }
      }
    }

    loadAvailableDates()
  }, [pollutant])

  useEffect(() => {
    if (!analysisDate) {
      return
    }

    const loadAnalysis = async () => {
      setError(null)
      setCoverage(null)
      setAnomaly(null)

      try {
        const [
          cellsResponse,
          coverageResponse,
          anomalyResponse,
        ] = await Promise.all([
          fetch(
            `http://127.0.0.1:8000/api/spatial/cells` +
            `?pollutant=${pollutant}` +
            `&date=${analysisDate}`,
          ),

          fetch(
            `http://127.0.0.1:8000/api/analysis/coverage` +
            `?pollutant=${pollutant}` +
            `&date=${analysisDate}`,
          ),

          fetch(
            `http://127.0.0.1:8000/api/anomalies/spatial` +
            `?pollutant=${pollutant}` +
            `&date=${analysisDate}`,
          ),
        ])

        if (!cellsResponse.ok) {
          const data =
            await cellsResponse.json()

          throw new Error(
            data.detail ??
            "Failed to fetch spatial cells",
          )
        }

        if (!coverageResponse.ok) {
          const data =
            await coverageResponse.json()

          throw new Error(
            data.detail ??
            "Failed to fetch analysis coverage",
          )
        }

        if (!anomalyResponse.ok) {
          const data =
            await anomalyResponse.json()

          throw new Error(
            data.detail ??
            "Failed to fetch spatial anomaly",
          )
        }

        const cellsData: SpatialCell[] =
          await cellsResponse.json()

        const coverageData: Coverage =
          await coverageResponse.json()

        const anomalyData: SpatialAnomaly =
          await anomalyResponse.json()

        setCells(cellsData)
        setCoverage(coverageData)
        setAnomaly(anomalyData)
      } catch (error) {
        setCells([])
        setCoverage(null)
        setAnomaly(null)

        if (error instanceof Error) {
          setError(error.message)
        } else {
          setError(
            "Failed to fetch analysis data",
          )
        }
      }
    }

    loadAnalysis()
  }, [pollutant, analysisDate])

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>
            Pollution Anomaly Detection
          </h1>

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

          <div className="date-control">
            <label>
              Analysis date
            </label>

            <AnalysisDatePicker
              availableDates={availableDates}
              selectedDate={analysisDate}
              onDateChange={setAnalysisDate}
            />
          </div>
        </section>

        {error ? (
          <section className="analysis-error">
            <strong>
              Analysis unavailable
            </strong>

            <span>
              {error}
            </span>
          </section>
        ) : (
          <>
            <AnalysisSummary
              cells={cells}
              pollutant={pollutant}
              coverage={coverage}
            />

            <section className="map-panel">
              <PollutionMap
                pollutant={pollutant}
                cells={cells}
                anomaly={anomaly}
              />
            </section>

            <AnalysisDetails
              cells={cells}
              pollutant={pollutant}
              anomaly={anomaly}
            />
          </>
        )}
      </main>
    </div>
  )
}


export default App