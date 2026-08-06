"""
FarmPulse AI - CEDA Arrival Quantity Collection
Pulls monthly arrival quantity (supply volume) data for all 8 states x 3
crops - the same structure as collect_ceda_historical.py, but hitting
/quantities instead of /prices. This becomes a new feature: higher
arrivals typically push prices down, lower arrivals push them up.
"""

import requests
import pandas as pd
import time

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

# Using the CORRECT commodity IDs - id 49 for Tur (the continuous series
# discovered earlier), not the discontinued id 7
CROP_IDS = {"Tur": 49, "Moong": 9, "Chana": 6}

START_DATE = "2015-01-01"
END_DATE = "2025-12-31"
OUTPUT_FILE = "../../data/raw/ceda_quantities_data.csv"

MAX_RETRIES = 5
RETRY_DELAY = 15
BETWEEN_REQUESTS_DELAY = 8


def fetch_quantities(state_id, commodity_id):
    payload = {
        "state_id": state_id, "commodity_id": commodity_id, "district_id": 0,
        "calculation_type": "m", "start_date": START_DATE, "end_date": END_DATE,
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(f"{BASE}/quantities", json=payload, headers=HEADERS, timeout=60)
            r.raise_for_status()
            return r.json().get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"    attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    print("    giving up after max retries.")
    return []


def main():
    all_rows = []

    for state_name, state_id in STATE_IDS.items():
        for crop_label, commodity_id in CROP_IDS.items():
            print(f"Fetching quantities: {state_name} - {crop_label} ...")
            records = fetch_quantities(state_id, commodity_id)
            print(f"  got {len(records)} monthly records")

            for rec in records:
                all_rows.append({
                    "state": state_name,
                    "crop_label": crop_label,
                    "month": rec.get("t"),
                    "arrival_qty": rec.get("qty"),
                })

            time.sleep(BETWEEN_REQUESTS_DELAY)

    df = pd.DataFrame(all_rows)
    if df.empty:
        print("\nNo data collected.")
        return

    df["date"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    df = df.dropna(subset=["date", "arrival_qty"])
    df = df[["state", "crop_label", "date", "arrival_qty"]]
    df = df.sort_values(["state", "crop_label", "date"])

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nDone. {len(df)} rows saved to {OUTPUT_FILE}")
    print("\nRows per state x crop:")
    print(df.groupby(["state", "crop_label"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main()