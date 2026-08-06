"""
Targeted retry for combinations that returned 0 or suspiciously few rows
in the first pass - merges results into the existing ceda_historical_data.csv
instead of overwriting it.
"""

import requests
import pandas as pd
import time
import os

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

STATE_IDS = {
    "Madhya Pradesh": 23, "Maharashtra": 27, "Rajasthan": 8, "Uttar Pradesh": 9,
    "Karnataka": 29, "Telangana": 36, "Andhra Pradesh": 28, "Gujarat": 24,
}
CROP_IDS = {"Tur": 7, "Moong": 9, "Chana": 6}

START_DATE = "2015-01-01"
END_DATE = "2025-12-31"
OUTPUT_FILE = "ceda_historical_data.csv"

# Combinations to retry: the confirmed zeros, plus ALL Tur combos since those
# counts were suspiciously low across every state (likely partial failures)
RETRY_TARGETS = [
    ("Maharashtra", "Tur"),
    ("Gujarat", "Moong"),
    ("Uttar Pradesh", "Tur"),
    ("Uttar Pradesh", "Moong"),
    ("Madhya Pradesh", "Tur"),
    ("Rajasthan", "Tur"),
    ("Karnataka", "Tur"),
    ("Telangana", "Tur"),
    ("Andhra Pradesh", "Tur"),
    ("Gujarat", "Tur"),
]

MAX_RETRIES = 5
RETRY_DELAY = 10
BETWEEN_REQUESTS_DELAY = 6


def fetch_prices(state_id, commodity_id):
    payload = {
        "state_id": state_id, "commodity_id": commodity_id, "district_id": 0,
        "calculation_type": "m", "start_date": START_DATE, "end_date": END_DATE,
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(f"{BASE}/prices", json=payload, headers=HEADERS, timeout=60)
            r.raise_for_status()
            return r.json().get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"    attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    print("    giving up after max retries.")
    return []


def main():
    all_new_rows = []

    for state_name, crop_label in RETRY_TARGETS:
        state_id = STATE_IDS[state_name]
        commodity_id = CROP_IDS[crop_label]
        print(f"Retrying: {state_name} - {crop_label} ...")
        records = fetch_prices(state_id, commodity_id)
        print(f"  got {len(records)} monthly records")

        for rec in records:
            all_new_rows.append({
                "state": state_name,
                "crop_label": crop_label,
                "month": rec.get("t"),
                "min_price": rec.get("p_min"),
                "max_price": rec.get("p_max"),
                "modal_price": rec.get("p_modal"),
            })

        time.sleep(BETWEEN_REQUESTS_DELAY)

    new_df = pd.DataFrame(all_new_rows)
    if new_df.empty:
        print("\nNo new data retrieved on retry.")
        return

    new_df["date"] = pd.to_datetime(new_df["month"], format="%Y-%m", errors="coerce")
    new_df = new_df.dropna(subset=["date", "modal_price"])
    new_df = new_df[["state", "crop_label", "date", "min_price", "max_price", "modal_price"]]

    if os.path.exists(OUTPUT_FILE):
        existing_df = pd.read_csv(OUTPUT_FILE, parse_dates=["date"])
        combined = pd.concat([existing_df, new_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=["state", "crop_label", "date"], keep="last")
    else:
        combined = new_df

    combined = combined.sort_values(["state", "crop_label", "date"])
    combined.to_csv(OUTPUT_FILE, index=False)

    print(f"\nDone. File now has {len(combined)} total rows.")
    print("\nRows per state x crop (updated):")
    print(combined.groupby(["state", "crop_label"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main()