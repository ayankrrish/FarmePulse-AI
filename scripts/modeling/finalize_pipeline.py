"""
FarmPulse AI - Final Pipeline Consolidation
Merges everything decided so far into ONE config file the dashboard reads:
  - Chana & Moong: per-state choice of Naive_flat / Naive_trend / LSTM
    (from model_selection_per_state.json)
  - Tur: single RF+arrival_quantity model, used for all states
Also saves the "recent context" data every prediction needs at
inference time (last known prices, needed to compute lags/trend/LSTM
input on demand).
"""

import json
import pandas as pd

PRICE_FILE = "../../data/processed/ceda_cleaned_data.csv"
SELECTION_FILE = "../../results/model_selection_per_state.json"
OUTPUT_CONFIG = "../../models/final_pipeline_config.json"
OUTPUT_CONTEXT = "../../data/processed/latest_context_all.csv"

with open(SELECTION_FILE) as f:
    per_state_selection = json.load(f)

final_config = {"Chana": {}, "Moong": {}, "Tur": {}}

# Chana and Moong: use the per-state selection already computed
for crop in ["Chana", "Moong"]:
    for state, info in per_state_selection.get(crop, {}).items():
        final_config[crop][state] = {
            "method": info["chosen_model"],
            "expected_test_rmse": info["test_rmse"],
            "expected_test_r2": info["test_r2"],
        }

# Tur: single model for all states
STATES = ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh",
          "Karnataka", "Telangana", "Andhra Pradesh", "Gujarat"]
for state in STATES:
    final_config["Tur"][state] = {
        "method": "RF_with_quantity",
        "model_path": "models/tur_final_model.joblib",
        "expected_test_r2": 0.8477,  # from the A/B test result
    }

with open(OUTPUT_CONFIG, "w") as f:
    json.dump(final_config, f, indent=2)

print("Saved final pipeline config to models/final_pipeline_config.json")
print(json.dumps(final_config, indent=2)[:1500], "...\n")

# Save last 12 months per state-crop as "recent context" for live predictions
df = pd.read_csv(PRICE_FILE, parse_dates=["date"])
df = df.dropna(subset=["modal_price"])
recent = df.sort_values("date").groupby(["state", "crop_label"]).tail(12)
recent.to_csv(OUTPUT_CONTEXT, index=False)
print(f"Saved recent context ({len(recent)} rows) to data/processed/latest_context_all.csv")

print("\nPipeline is now finalized. Ready for dashboard integration.")