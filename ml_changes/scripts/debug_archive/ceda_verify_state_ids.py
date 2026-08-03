import requests

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# Standard Census 2011 state codes for our 8 target states
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

for state_name, state_id in STATE_IDS.items():
    r = requests.get(f"{BASE}/districts", params={"state_id": state_id},
                      headers=HEADERS, timeout=30)
    print(f"{state_name} (id={state_id}): status={r.status_code}")
    print("  ", r.text[:300])
    print()