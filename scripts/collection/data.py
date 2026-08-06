"""
FarmPulse AI - Data Collection Script
Pulls daily mandi price data for Tur/Arhar, Moong, and Chana (Bengal Gram)
across 10 target states from the data.gov.in API.

BEFORE RUNNING:
1. Register a free account at https://data.gov.in
2. Go to "My Account" -> "Generate API Key" and copy your key
3. Paste it into API_KEY below

Dataset used: "Current Daily Price of Various Commodities from Various Markets (Mandi)"
Resource ID: 9ef84268-d588-465a-a308-a864a43d0070
"""

import requests
import pandas as pd
import time
import os

# ----------------------------
# CONFIG
# ----------------------------
API_KEY = "579b464db66ec23bdd00000145ccdafbbc434eae76c41ec8385ddcee"
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

# The 8 target states (Chhattisgarh and Bihar dropped - no pulse arrivals
# in the current-daily-price dataset for these on test runs; can revisit
# later using historical CEDA data if needed)
STATES = [
    "Madhya Pradesh",
    "Maharashtra",
    "Rajasthan",
    "Uttar Pradesh",
    "Karnataka",
    "Telangana",
    "Andhra Pradesh",
    "Gujarat",
]

# Commodity names as they ACTUALLY appear in the API (verified by direct query)
CROPS = {
    "Tur": "Red gram/Arhar/Tur(whole)",
    "Moong": "Green Gram(Moong)(Whole)",
    "Chana": "Bengal Gram(Gram)(Whole)",
}

RECORDS_PER_PAGE = 1000  # max allowed per request
OUTPUT_FILE = "farmpulse_raw_data.csv"

# Government APIs sometimes hang/stall on the default python-requests
# User-Agent instead of returning a clean error - a browser-like header fixes it.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def fetch_records(state, crop_name, offset=0):
    """Fetch one page of records for a given state + crop."""
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": RECORDS_PER_PAGE,
        "offset": offset,
        "filters[state]": state,
        "filters[commodity]": crop_name,
    }
    response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def collect_all_data():
    all_rows = []

    for state in STATES:
        for crop_label, crop_api_name in CROPS.items():
            offset = 0
            print(f"Fetching: {state} - {crop_label} ...")

            while True:
                try:
                    data = fetch_records(state, crop_api_name, offset)
                except requests.exceptions.RequestException as e:
                    print(f"  Request failed for {state}/{crop_label} at offset {offset}: {e}")
                    break

                records = data.get("records", [])
                if not records:
                    break

                for r in records:
                    r["crop_label"] = crop_label  # tag with our clean crop name
                all_rows.extend(records)

                total_available = int(data.get("total", 0))
                offset += RECORDS_PER_PAGE

                print(f"  fetched {min(offset, total_available)}/{total_available}")

                if offset >= total_available:
                    break

                time.sleep(0.5)  # be polite to the API

    return pd.DataFrame(all_rows)


def clean_data(df):
    """Basic cleanup: rename columns, parse dates, drop bad rows."""
    if df.empty:
        print("No data collected - check API key and filters.")
        return df

    # Standardize column names (API sometimes returns them lowercase/spaced differently)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    rename_map = {
        "state": "state",
        "district": "district",
        "market": "mandi",
        "commodity": "commodity",
        "variety": "variety",
        "arrival_date": "date",
        "min_price": "min_price",
        "max_price": "max_price",
        "modal_price": "modal_price",
        "crop_label": "crop_label",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Keep only relevant columns if present
    keep_cols = [c for c in
                 ["state", "district", "mandi", "crop_label", "commodity", "variety",
                  "date", "min_price", "max_price", "modal_price"]
                 if c in df.columns]
    df = df[keep_cols]

    # Convert numeric columns
    for col in ["min_price", "max_price", "modal_price"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Parse dates (Agmarknet format is usually DD/MM/YYYY)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")

    # Drop rows with missing price or date
    df = df.dropna(subset=["modal_price", "date"])

    # Remove obvious duplicates
    df = df.drop_duplicates()

    return df


if __name__ == "__main__":
    print("Starting FarmPulse AI data collection...\n")
    raw_df = collect_all_data()
    clean_df = clean_data(raw_df)

    clean_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nDone. {len(clean_df)} clean rows saved to {OUTPUT_FILE}")
    print(clean_df.head())