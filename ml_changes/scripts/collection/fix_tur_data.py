"""
Pulls the CORRECT Tur data (commodity_id=49, "Arhar (Tur/Red Gram)(Whole)")
for all 8 states, with patient retries. Then removes the old broken
commodity_id=7 Tur rows from ceda_historical_data.csv and replaces them
with this real data.
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

TUR_ID = 49
START_DATE = "2015-01-01"
END_DATE = "2025-12-31"
OUTPUT_FILE = "ceda_historical_data.csv"

MAX_RETRIES = 5
RETRY_DELAY = 15          # longer wait on failure
BETWEEN_REQUESTS_DELAY = 10  # longer wait between states


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
    new_rows = []

    for state_name, state_id in STATE_IDS.items():
        print(f"Fetching correct Tur data: {state_name} ...")
        records = fetch_prices(state_id, TUR_ID)
        print(f"  got {len(records)} monthly records")

        for rec in records:
            new_rows.append({
                "state": state_name,
                "crop_label": "Tur",
                "month": rec.get("t"),
                "min_price": rec.get("p_min"),
                "max_price": rec.get("p_max"),
                "modal_price": rec.get("p_modal"),
            })

        time.sleep(BETWEEN_REQUESTS_DELAY)

    new_df = pd.DataFrame(new_rows)
    if new_df.empty:
        print("\nNo new Tur data retrieved - stopping without touching existing file.")
        return

    new_df["date"] = pd.to_datetime(new_df["month"], format="%Y-%m", errors="coerce")
    new_df = new_df.dropna(subset=["date", "modal_price"])
    new_df = new_df[["state", "crop_label", "date", "min_price", "max_price", "modal_price"]]

    if os.path.exists(OUTPUT_FILE):
        existing_df = pd.read_csv(OUTPUT_FILE, parse_dates=["date"])
        # Drop ALL old Tur rows (they were from the wrong/discontinued commodity_id=7)
        existing_df = existing_df[existing_df["crop_label"] != "Tur"]
        combined = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined = new_df

    combined = combined.drop_duplicates(subset=["state", "crop_label", "date"], keep="last")
    combined = combined.sort_values(["state", "crop_label", "date"])
    combined.to_csv(OUTPUT_FILE, index=False)

    print(f"\nDone. File now has {len(combined)} total rows.")
    print("\nRows per state x crop (final):")
    print(combined.groupby(["state", "crop_label"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main()