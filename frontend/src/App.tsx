import { useState } from "react"

import "./App.css"

import PollutionMap from "./components/PollutionMap"


type Pollutant = "CH4" | "NO2"


function App() {
  const [pollutant, setPollutant] =
    useState<Pollutant>("CH4")

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

        <section className="map-panel">
          <PollutionMap
            pollutant={pollutant}
          />
        </section>
      </main>
    </div>
  )
}


export default App