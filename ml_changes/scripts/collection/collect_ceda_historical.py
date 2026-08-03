"""
FarmPulse AI - CEDA Historical Data Collection
Pulls monthly historical price data (min/max/modal) for Tur, Moong, and Chana
across 8 target states, going back several years - this is the real
training data source for ARIMA/LSTM.
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
    "Madhya Pradesh": 23,
    "Maharashtra": 27,
    "Rajasthan": 8,
    "Uttar Pradesh": 9,
    "Karnataka": 29,
    "Telangana": 36,
    "Andhra Pradesh": 28,
    "Gujarat": 24,
}

CROP_IDS = {
    "Tur": 7,      # Red Gram
    "Moong": 9,    # Green Gram (Moong)(Whole)
    "Chana": 6,    # Bengal Gram (Gram)(Whole)
}

START_DATE = "2015-01-01"
END_DATE = "2025-12-31"
OUTPUT_FILE = "../../data/raw/ceda_historical_data.csv"

MAX_RETRIES = 3
RETRY_DELAY = 5      # seconds, if a request fails
BETWEEN_REQUESTS_DELAY = 3  # seconds, to avoid overloading their server


def fetch_prices(state_id, commodity_id):
    payload = {
        "state_id": state_id,
        "commodity_id": commodity_id,
        "district_id": 0,  # 0 = state-wide aggregate
        "calculation_type": "m",  # monthly
        "start_date": START_DATE,
        "end_date": END_DATE,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(f"{BASE}/prices", json=payload, headers=HEADERS, timeout=45)
            r.raise_for_status()
            return r.json().get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"    attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    print("    giving up on this combination after max retries.")
    return []


def collect_all():
    all_rows = []

    for state_name, state_id in STATE_IDS.items():
        for crop_label, commodity_id in CROP_IDS.items():
            print(f"Fetching: {state_name} - {crop_label} ...")
            records = fetch_prices(state_id, commodity_id)
            print(f"  got {len(records)} monthly records")

            for rec in records:
                all_rows.append({
                    "state": state_name,
                    "crop_label": crop_label,
                    "month": rec.get("t"),
                    "min_price": rec.get("p_min"),
                    "max_price": rec.get("p_max"),
                    "modal_price": rec.get("p_modal"),
                })

            time.sleep(BETWEEN_REQUESTS_DELAY)

    return pd.DataFrame(all_rows)


def clean_data(df):
    if df.empty:
        return df

    # Convert "YYYY-MM" to an actual date (first of the month)
    df["date"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    df = df.dropna(subset=["date", "modal_price"])
    df = df.drop_duplicates(subset=["state", "crop_label", "date"])
    df = df.sort_values(["state", "crop_label", "date"])
    df = df[["state", "crop_label", "date", "min_price", "max_price", "modal_price"]]
    return df


if __name__ == "__main__":
    print("Starting CEDA historical data collection...\n")
    raw_df = collect_all()
    clean_df = clean_data(raw_df)

    if clean_df.empty:
        print("\nNo data collected - something went wrong.")
    else:
        clean_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nDone. {len(clean_df)} rows saved to {OUTPUT_FILE}")
        print(f"Date range: {clean_df['date'].min().date()} to {clean_df['date'].max().date()}")
        print("\nRows per state x crop:")
        print(clean_df.groupby(["state", "crop_label"]).size().unstack(fill_value=0))