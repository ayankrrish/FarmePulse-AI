import requests
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

NEW_TUR_ID = 49

for state_name, state_id in STATE_IDS.items():
    payload = {
        "state_id": state_id,
        "commodity_id": NEW_TUR_ID,
        "district_id": 0,
        "calculation_type": "m",
        "start_date": "2015-01-01",
        "end_date": "2025-12-31",
    }
    try:
        r = requests.post(f"{BASE}/prices", json=payload, headers=HEADERS, timeout=45)
        data = r.json().get("data", [])
        print(f"{state_name}: {len(data)} records", end="")
        if data:
            print(f"  |  first: {data[-1]['t']}  last: {data[0]['t']}")
        else:
            print()
    except requests.exceptions.RequestException as e:
        print(f"{state_name}: FAILED - {e}")
    time.sleep(4)