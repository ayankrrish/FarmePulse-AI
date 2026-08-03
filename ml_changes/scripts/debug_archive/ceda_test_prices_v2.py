import requests

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

attempts = [
    # array-style ids, common in multi-select filter UIs
    {
        "state_ids": [23],
        "district_ids": [420],
        "commodity_ids": [7],
        "from_date": "2023-01-01",
        "to_date": "2024-01-01",
        "chart_type": "datadownload",
    },
    # calculation_type field often paired with chart_type in these dashboards
    {
        "state_ids": [23],
        "district_ids": [420],
        "commodity_id": 7,
        "from_date": "2023-01-01",
        "to_date": "2024-01-01",
        "chart_type": "datadownload",
        "calculation_type": "price",
    },
    # market_id instead of district_id
    {
        "state_id": 23,
        "market_id": 420,
        "commodity_id": 7,
        "from_date": "2023-01-01",
        "to_date": "2024-01-01",
        "chart_type": "datadownload",
    },
    # everything as strings
    {
        "state_id": "23",
        "district_id": "420",
        "commodity_id": "7",
        "from_date": "2023-01-01",
        "to_date": "2024-01-01",
        "chart_type": "datadownload",
    },
    # date field names as "date_from"/"date_to"
    {
        "state_id": 23,
        "district_id": 420,
        "commodity_id": 7,
        "date_from": "2023-01-01",
        "date_to": "2024-01-01",
        "chart_type": "datadownload",
    },
    # mode field instead of chart_type
    {
        "state_id": 23,
        "district_id": 420,
        "commodity_id": 7,
        "from_date": "2023-01-01",
        "to_date": "2024-01-01",
        "mode": "daily",
        "chart_type": "datadownload",
    },
]

for i, payload in enumerate(attempts, 1):
    print(f"--- Attempt {i} ---")
    print("Payload:", payload)
    try:
        r = requests.post(f"{BASE}/prices", json=payload, headers=HEADERS, timeout=30)
        print("Status:", r.status_code)
        print("Response (first 500 chars):", r.text[:500])
    except requests.exceptions.RequestException as e:
        print("FAILED:", e)
    print()