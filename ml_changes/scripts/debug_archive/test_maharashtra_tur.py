import requests

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# First get Maharashtra's district list so we can find Latur's real ID
r = requests.get(f"{BASE}/districts", params={"state_id": 27}, headers=HEADERS, timeout=30)
districts = r.json().get("data", [])
print("Maharashtra districts (looking for Latur, Nagpur, Akola - major Tur belts):")
target_districts = {}
for d in districts:
    name = d.get("census_district_name", "")
    if name.lower() in ["latur", "nagpur", "akola", "amravati", "yavatmal"]:
        print(" -", d)
        target_districts[name] = d.get("census_district_id")

print("\nTesting Tur (commodity_id=7) in each of these districts:")
for name, district_id in target_districts.items():
    payload = {
        "state_id": 27,
        "commodity_id": 7,
        "district_id": district_id,
        "calculation_type": "m",
        "start_date": "2015-01-01",
        "end_date": "2025-12-31",
    }
    resp = requests.post(f"{BASE}/prices", json=payload, headers=HEADERS, timeout=45)
    data = resp.json().get("data", [])
    print(f"  {name} (id={district_id}): {len(data)} records")
    if data:
        print("    sample:", data[0])