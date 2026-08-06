"""
FarmPulse AI - Arrival Quantity Feature Test
Merges price and quantity data, then runs Random Forest WITH and WITHOUT
arrival_qty as a feature, using the same time-based split as before, to
directly measure whether this new signal actually helps.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

PRICE_FILE = "../../data/processed/ceda_cleaned_data.csv"
QTY_FILE = "../../data/raw/ceda_quantities_data.csv"
TEST_MONTHS = 12

price_df = pd.read_csv(PRICE_FILE, parse_dates=["date"])
price_df = price_df.dropna(subset=["modal_price"])

qty_df = pd.read_csv(QTY_FILE, parse_dates=["date"])

merged = pd.merge(price_df, qty_df, on=["state", "crop_label", "date"], how="left")
print(f"Merged dataset: {len(merged)} rows, "
      f"{merged['arrival_qty'].notna().sum()} have arrival_qty data "
      f"({merged['arrival_qty'].isna().sum()} missing)")

# Build features per state-crop series
feature_frames = []
for (state, crop), group in merged.groupby(["state", "crop_label"]):
    group = group.sort_values("date").copy()
    group["lag_1m"] = group["modal_price"].shift(1)
    group["lag_3m"] = group["modal_price"].shift(3)
    group["lag_12m"] = group["modal_price"].shift(12)
    group["rolling_3m_avg"] = group["modal_price"].shift(1).rolling(3).mean()
    group["month"] = group["date"].dt.month
    group["quarter"] = group["date"].dt.quarter
    # Arrival quantity features - current month's arrival + trend
    group["qty_lag_1m"] = group["arrival_qty"].shift(1)
    group["qty_rolling_3m"] = group["arrival_qty"].shift(1).rolling(3).mean()
    feature_frames.append(group)

df = pd.concat(feature_frames, ignore_index=True)

BASE_FEATURES = ["lag_1m", "lag_3m", "lag_12m", "rolling_3m_avg", "month", "quarter"]
QTY_FEATURES = ["qty_lag_1m", "qty_rolling_3m"]

results = []

for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop].copy()

    for feature_set_name, feature_cols in [
        ("WITHOUT_quantity", BASE_FEATURES),
        ("WITH_quantity", BASE_FEATURES + QTY_FEATURES),
    ]:
        clean_df = crop_df.dropna(subset=feature_cols + ["modal_price"])

        train_frames, test_frames = [], []
        for state in clean_df["state"].unique():
            state_rows = clean_df[clean_df["state"] == state].sort_values("date")
            if len(state_rows) <= TEST_MONTHS + 10:
                continue
            train_frames.append(state_rows.iloc[:-TEST_MONTHS])
            test_frames.append(state_rows.iloc[-TEST_MONTHS:])

        if not test_frames:
            print(f"{crop} ({feature_set_name}): not enough data, skipping")
            continue

        train_df = pd.concat(train_frames)
        test_df = pd.concat(test_frames)

        X_train, y_train = train_df[feature_cols], train_df["modal_price"]
        X_test, y_test = test_df[feature_cols], test_df["modal_price"]

        model = RandomForestRegressor(n_estimators=300, max_depth=5, min_samples_leaf=10,
                                       random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        results.append({"crop": crop, "feature_set": feature_set_name,
                         "n_rows": len(clean_df), "RMSE": round(rmse, 2),
                         "MAE": round(mae, 2), "R2": round(r2, 4)})

results_df = pd.DataFrame(results)
print("\n" + "=" * 60)
print("RESULTS: WITH vs WITHOUT arrival quantity feature")
print("=" * 60)
print(results_df.to_string(index=False))
results_df.to_csv("../../results/arrival_quantity_ab_test.csv", index=False)
print("\nSaved to results/arrival_quantity_ab_test.csv")