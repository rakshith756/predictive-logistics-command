# Predictive Logistics Command
### AI-Enabled Forward Supply Chain Decision Support System

A complete Smart India Hackathon academic prototype demonstrating **MONITOR → ANALYZE → PREDICT → ALERT → EXPLAIN → RECOMMEND → SIMULATE → RESUPPLY** using 100% synthetic fictional logistics data.

> **DEMONSTRATION SYSTEM — ALL DATA IS SYNTHETIC AND FICTIONAL. NOT FOR REAL-WORLD OPERATIONAL USE.**

## Run
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

The SQLite database is initialized automatically. To regenerate the synthetic dataset, run `python database/seed.py`.

## Architecture
Browser (Bootstrap/Chart.js/Leaflet) → Flask REST API → Services → Prediction/Risk/Recommendation engines → SQLite.

## Intelligence
The baseline is an explainable Linear Regression forecast over 30 days of synthetic consumption. MAE/R² are calculated and a prototype confidence estimate is derived from recent prediction error. Risk combines inventory buffer, shortage window, trend, convoy delay and synthetic weather impact. Recommendations use a transparent planning-horizon formula and never return negative quantities.

## SIH Demo
1. Start the application.
2. Open Dashboard.
3. Click **RUN SIH DEMO**.
4. Unit Charlie is the deliberately coherent scenario: increasing fuel demand, constrained stock, delayed inbound fuel and elevated synthetic weather impact.
5. Open AI Prediction to show the calculated shortage window, explanation, route and resupply recommendation.
6. Apply **SIMULATE RESUPPLY** or use What-If Simulator to demonstrate risk reduction.

## Fallbacks and limitations
- All data is synthetic; there is no real operational or military data.
- Weather is local synthetic fallback data; no API key is required.
- OpenStreetMap tiles require network access for the basemap; the application itself remains usable if tiles are unavailable.
- The ML model is a transparent prototype, not a production forecasting system.
- The simulation is deterministic/local and intended for demonstration only.

## Tests
Run `pytest -q`.
