import requests

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# Same payload schema as /prices, discovered earlier from browser devtools
payload = {
    "state_id": 23,       # Madhya Pradesh
    "commodity_id": 6,    # Bengal Gram (Chana)
    "district_id": 0,     # state-wide aggregate
    "calculation_type": "m",
    "start_date": "2020-01-01",
    "end_date": "2021-12-31",
}

import time

for attempt in range(1, 4):
    try:
        r = requests.post(f"{BASE}/quantities", json=payload, headers=HEADERS, timeout=60)
        print("Status:", r.status_code)
        print("Response (first 1500 chars):")
        print(r.text[:1500])
        break
    except requests.exceptions.RequestException as e:
        print(f"Attempt {attempt}/3 failed: {e}")
        if attempt < 3:
            time.sleep(10)