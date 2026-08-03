import requests

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

attempts = [
    # Madhya Pradesh + Bengal Gram (Chana) - MP is a top Chana producer
    {"state_id": 23, "commodity_id": 6, "district_id": 0,
     "calculation_type": "m", "start_date": "2022-01-01", "end_date": "2025-12-31"},
    # Maharashtra + Red Gram (Tur) - Maharashtra is a top Tur producer
    {"state_id": 27, "commodity_id": 7, "district_id": 0,
     "calculation_type": "m", "start_date": "2022-01-01", "end_date": "2025-12-31"},
    # Rajasthan + Green Gram (Moong) - Rajasthan is a top Moong producer
    {"state_id": 8, "commodity_id": 9, "district_id": 0,
     "calculation_type": "m", "start_date": "2022-01-01", "end_date": "2025-12-31"},
]

for i, payload in enumerate(attempts, 1):
    print(f"--- Attempt {i}: state={payload['state_id']}, commodity={payload['commodity_id']} ---")
    try:
        r = requests.post(f"{BASE}/prices", json=payload, headers=HEADERS, timeout=30)
        print("Status:", r.status_code)
        print("Response (first 1000 chars):", r.text[:1000])
    except requests.exceptions.RequestException as e:
        print("FAILED:", e)
    print()