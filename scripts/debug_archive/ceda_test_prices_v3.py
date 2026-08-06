import requests

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

attempts = [
    # monthly, all districts, Red Gram (Tur) in MP
    {
        "state_id": 23,
        "commodity_id": 7,
        "district_id": 0,
        "calculation_type": "m",
        "start_date": "2020-01-01",
        "end_date": "2025-12-31",
    },
    # try daily granularity
    {
        "state_id": 23,
        "commodity_id": 7,
        "district_id": 0,
        "calculation_type": "d",
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
    },
]

for i, payload in enumerate(attempts, 1):
    print(f"--- Attempt {i} ({payload['calculation_type']}) ---")
    try:
        r = requests.post(f"{BASE}/prices", json=payload, headers=HEADERS, timeout=30)
        print("Status:", r.status_code)
        print("Response (first 1500 chars):", r.text[:1500])
    except requests.exceptions.RequestException as e:
        print("FAILED:", e)
    print()