import requests
import json

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# Test with Madhya Pradesh (state_id=23), a district we just confirmed (Bhind=420),
# and Red Gram / Tur (commodity_id=7)
payload_attempts = [
    {
        "state_id": 23,
        "district_id": 420,
        "commodity_id": 7,
        "from_date": "2023-01-01",
        "to_date": "2024-01-01",
        "chart_type": "datadownload",
    },
    {
        "state_id": 23,
        "census_district_id": 420,
        "commodity_id": 7,
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "chart_type": "datadownload",
    },
]

for i, payload in enumerate(payload_attempts, 1):
    print(f"--- Attempt {i} ---")
    print("Payload:", payload)
    try:
        r = requests.post(f"{BASE}/prices", json=payload, headers=HEADERS, timeout=30)
        print("Status:", r.status_code)
        print("Response (first 1000 chars):", r.text[:1000])
    except requests.exceptions.RequestException as e:
        print("FAILED:", e)
    print()