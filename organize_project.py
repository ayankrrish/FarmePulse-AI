"""
FarmPulse AI - Project Folder Organizer
Run this ONCE inside your ML_project folder. It creates a clean folder
structure and moves your existing files into the right place.

Resulting structure:
  data/
    raw/            - original collected data
    processed/       - cleaned + model-ready data
  scripts/
    collection/      - the actual data collection scripts you'll reuse
    debug_archive/   - all the one-off debugging/discovery scripts (kept for reference)
    eda/             - exploration/analysis scripts
    modeling/        - feature engineering + model training scripts
  models/            - saved trained models (.joblib)
  results/           - result tables (.csv) and plots (.png)
  reference/         - reference data like the full commodities list
"""

import os
import shutil

FOLDERS = {
    "data/raw": [
        "farmpulse_raw_data.csv",
        "ceda_historical_data.csv",
    ],
    "data/processed": [
        "ceda_cleaned_data.csv",
        "farmpulse_model_ready.csv",
        "gap_report.csv",
    ],
    "scripts/collection": [
        "collect_farmpulse_data.py",
        "data.py",
        "collect_ceda_historical.py",
        "retry_ceda_gaps.py",
        "fix_tur_data.py",
        "cleanup_states.py",
    ],
    "scripts/debug_archive": [
        "test_api_connection.py",
        "test_filters.py",
        "test_headers_fix.py",
        "find_commodity_names.py",
        "ceda_discover_ids.py",
        "ceda_raw_check.py",
        "ceda_verify_state_ids.py",
        "ceda_test_prices_endpoint.py",
        "ceda_test_prices_v2.py",
        "ceda_test_prices_v3.py",
        "ceda_test_prices_v4.py",
        "test_maharashtra_tur.py",
        "full_commodity_search.py",
        "dump_all_commodities.py",
        "test_new_tur_id.py",
        "dumpy_all_commodities.py",
        "dump_all_commodities.py",
    ],
    "scripts/eda": [
        "explore_data.py",
        "explore_ceda_data.py",
        "check_feature_importance.py",
    ],
    "scripts/modeling": [
        "feature_engineering.py",
        "train_random_forest.py",
        "train_random_forest_v2.py",
        "naive_baseline_comparison.py",
        "multi_horizon_comparison.py",
    ],
    "models": [
        "rf_model_chana.joblib",
        "rf_model_moong.joblib",
        "rf_model_tur.joblib",
        "rf_model_v2_chana.joblib",
        "rf_model_v2_moong.joblib",
        "rf_model_v2_tur.joblib",
    ],
    "results": [
        "rf_baseline_results.csv",
        "rf_v2_vs_naive_results.csv",
        "multi_horizon_results.csv",
        "trend_tur.png",
        "trend_moong.png",
        "trend_chana.png",
    ],
    "reference": [
        "all_commodities.json",
    ],
}

moved = 0
skipped = 0

for folder, files in FOLDERS.items():
    os.makedirs(folder, exist_ok=True)
    for filename in files:
        if os.path.exists(filename):
            dest = os.path.join(folder, filename)
            shutil.move(filename, dest)
            print(f"Moved: {filename} -> {folder}/")
            moved += 1
        else:
            skipped += 1

print(f"\nDone. {moved} files moved, {skipped} not found (already moved or never existed - fine).")
print("\nYour project folder is now organized. Going forward:")
print("  - Data collection scripts live in scripts/collection/")
print("  - One-off debugging scripts are archived in scripts/debug_archive/ (safe to ignore)")
print("  - Modeling scripts live in scripts/modeling/")
print("  - Trained models are in models/")
print("  - Result tables and plots are in results/")