# FarmPulse AI 🌾

**AI-Powered Agricultural Price Intelligence Platform**

An ensemble machine learning system for forecasting pulse crop prices (Chana, Moong, Tur) across Indian mandis. Built for farmers, traders, and agricultural analysts.

> Final Year Engineering Project — Phase II

---

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Training Models](#training-models)
- [API Documentation](#api-documentation)
- [Data Pipeline](#data-pipeline)

---

## ✨ Features

### Prediction Engine
- **6 ML Models**: Random Forest, LSTM, GRU, XGBoost, ARIMA/SARIMA, Prophet
- **Weighted Ensemble**: Combines all available models using inverse-RMSE weighting
- **Confidence Scoring**: Prediction reliability based on model agreement
- **Multi-horizon Forecasting**: 1-month to 24-month ahead predictions

### Dashboard
- **Real-time Analytics**: Current price, predicted price, trend direction
- **Interactive Charts**: Plotly.js with zoom, hover tooltips, range selection
- **MSP Alerts**: Green/Yellow/Red alerts against Minimum Support Price
- **Market Comparison**: Rank states by predicted price, identify best markets
- **Profit Estimator**: Revenue and profit calculations with cost analysis
- **Recommendation Engine**: Actionable advice (Hold/Sell/Monitor) based on predictions

### Data Pipeline
- **Feature Engineering**: Lag features, rolling averages, momentum, volatility, seasonality, trend direction, harvest season flags, normalization, outlier detection
- **3 Crops**: Chana (Chickpea), Moong (Green Gram), Tur (Pigeon Pea)
- **8 States**: Andhra Pradesh, Gujarat, Karnataka, Madhya Pradesh, Maharashtra, Rajasthan, Telangana, Uttar Pradesh

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask (Python) |
| ML Models | scikit-learn, TensorFlow/Keras, XGBoost, statsmodels, Prophet |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Plotly.js |
| Data | Pandas, NumPy |
| Data Source | CEDA Agmarknet, data.gov.in |
| Deployment | Localhost (no cloud dependencies) |

---

## 🏗️ Architecture

```
Historical CSV Data
       │
       ▼
  Data Cleaning (clean_ceda_data.py)
       │
       ▼
  Feature Engineering (feature_engineering.py)
       │
       ▼
  Model Training (train_*.py scripts)
       │
       ▼
  Model Selection (model_selection_v2.py)
       │
       ▼
  Pipeline Finalization (finalize_pipeline.py)
       │
       ▼
  Flask Backend (app.py)
       │
       ├── /api/predict          → Single model prediction
       ├── /api/ensemble_predict → Weighted ensemble
       ├── /api/recommendation   → Actionable advice
       ├── /api/msp_alert        → MSP status
       ├── /api/market_comparison→ Cross-state analysis
       ├── /api/profit_estimate  → Revenue calculator
       ├── /api/dashboard_summary→ Aggregated metrics
       └── /api/model_metrics    → Model performance
       │
       ▼
  Interactive Dashboard (Plotly.js)
```

---

## 📁 Project Structure

```
ml_changes/
├── dashboard/                    # Flask application
│   ├── app.py                    # Main backend — all routes
│   ├── config.py                 # Centralized configuration
│   ├── services/                 # Business logic modules
│   │   ├── ensemble.py           # Weighted ensemble predictor
│   │   ├── recommendation.py     # Action recommendation engine
│   │   ├── msp_alerts.py         # MSP alert system
│   │   ├── market_comparison.py  # Cross-state comparison
│   │   └── profit_calculator.py  # Revenue/profit analysis
│   ├── static/                   # Frontend assets
│   │   ├── css/style.css         # Design system
│   │   └── js/
│   │       ├── app.js            # Application logic
│   │       └── charts.js         # Plotly chart configs
│   └── templates/
│       ├── index.html            # Main template
│       └── index_legacy.html     # Original template (backup)
│
├── data/
│   ├── raw/                      # Original collected data
│   │   ├── ceda_historical_data.csv
│   │   ├── ceda_quantities_data.csv
│   │   └── farmpulse_raw_data.csv
│   └── processed/                # Cleaned & model-ready data
│       ├── ceda_cleaned_data.csv
│       ├── farmpulse_model_ready.csv
│       ├── latest_context_all.csv
│       └── tur_latest_context.csv
│
├── models/                       # Trained model files
│   ├── final_pipeline_config.json
│   ├── lstm_model_*.keras
│   ├── rf_model_*.joblib
│   ├── tur_final_model.joblib
│   ├── gru_model_*.keras         # After training
│   └── xgb_model_*.joblib        # After training
│
├── scripts/
│   ├── modeling/                  # Training scripts
│   │   ├── feature_engineering.py
│   │   ├── train_random_forest.py
│   │   ├── train_random_forest_v2.py
│   │   ├── train_lstm.py
│   │   ├── train_arima.py
│   │   ├── train_sarima.py
│   │   ├── train_xgboost.py      # NEW
│   │   ├── train_gru.py          # NEW
│   │   ├── train_prophet.py      # NEW
│   │   ├── final_model_selection.py
│   │   ├── model_selection_v2.py
│   │   ├── finalize_pipeline.py
│   │   └── train_final_tur_model.py
│   ├── collection/                # Data collection scripts
│   ├── eda/                       # Exploratory analysis
│   └── debug_archive/             # Archived debug scripts
│
├── results/                       # Model evaluation results
│   ├── arima_results.csv
│   ├── lstm_results.csv
│   ├── sarima_results.csv
│   ├── rf_v2_vs_naive_results.csv
│   ├── model_selection.json
│   └── model_selection_per_state.json
│
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Steps

1. **Clone or extract the project**
   ```bash
   cd ml_changes
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate       # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Train missing models** (optional — the app works without them)
   ```bash
   cd scripts/modeling
   python train_xgboost.py
   python train_gru.py
   python train_prophet.py
   cd ../..
   ```

---

## ▶️ Running the Application

```bash
cd dashboard
python app.py
```

Open your browser to: **http://127.0.0.1:5000**

The application loads all models and data at startup. You should see:
```
INFO | Loading pipeline config and context data...
INFO | Startup complete. Models and data loaded.
 * Running on http://127.0.0.1:5000
```

---

## 🧠 Training Models

All training scripts are in `scripts/modeling/`. Each script:
- Reads from `data/processed/`
- Uses a 12-month holdout test split
- Saves models to `models/`
- Saves evaluation results to `results/`

| Script | Model | Output |
|--------|-------|--------|
| `train_random_forest_v2.py` | Random Forest | `models/rf_model_v2_*.joblib` |
| `train_lstm.py` | LSTM | `models/lstm_model_*.keras` |
| `train_arima.py` | ARIMA | `results/arima_results.csv` |
| `train_sarima.py` | SARIMA | `results/sarima_results.csv` |
| `train_xgboost.py` | XGBoost | `models/xgb_model_*.joblib` |
| `train_gru.py` | GRU | `models/gru_model_*.keras` |
| `train_prophet.py` | Prophet | `results/prophet_results.csv` |
| `train_final_tur_model.py` | Tur RF | `models/tur_final_model.joblib` |

---

## 📡 API Documentation

All endpoints return JSON. Base URL: `http://127.0.0.1:5000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/config` | GET | Available crops and states |
| `/api/predict` | GET | Single-model prediction |
| `/api/ensemble_predict` | GET | Weighted ensemble prediction |
| `/api/recommendation` | GET | Actionable advice |
| `/api/msp_alert` | GET | MSP alert status |
| `/api/market_comparison` | GET | Cross-state comparison |
| `/api/profit_estimate` | GET | Revenue/profit calculation |
| `/api/dashboard_summary` | GET | Aggregated dashboard metrics |
| `/api/model_metrics` | GET | Model performance comparison |

### Example Request
```
GET /api/ensemble_predict?crop=Chana&state=Gujarat
```

### Common Parameters
- `crop` — Crop name (Chana, Moong, Tur)
- `state` — State name (e.g., Gujarat, Maharashtra)
- `target_date` — Optional forecast target (YYYY-MM format)

---

## 🔄 Data Pipeline

```
1. Raw Data Collection
   └── scripts/collection/ → data/raw/

2. Data Cleaning
   └── clean_ceda_data.py → data/processed/ceda_cleaned_data.csv

3. Feature Engineering
   └── scripts/modeling/feature_engineering.py → data/processed/farmpulse_model_ready.csv
   Features: lags (1,3,6,12m), rolling averages, month, quarter,
   YoY change, momentum, volatility, trend, harvest season, normalization

4. Model Training
   └── scripts/modeling/train_*.py → models/

5. Model Selection
   └── model_selection_v2.py → results/model_selection_per_state.json

6. Pipeline Finalization
   └── finalize_pipeline.py → models/final_pipeline_config.json

7. Dashboard
   └── dashboard/app.py → http://127.0.0.1:5000
```

---

## 📜 License

This project is developed as a Final Year Engineering Project.

## 👥 Authors

FarmPulse AI Team

---

*Built with ❤️ for Indian farmers*
