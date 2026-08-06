import requests
import json

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

r = requests.get(f"{BASE}/commodities", headers=HEADERS, timeout=30)
commodities = r.json().get("data", [])

with open("all_commodities.json", "w") as f:
    json.dump(commodities, f, indent=2)

print(f"Saved {len(commodities)} commodities to all_commodities.json")

print("\nAll commodities with id > 9 that might be pulse-related (broader keyword net):")
keywords = ["tur", "arhar", "gram", "pigeon", "dal", "pulse", "red"]
for c in commodities:
    if c.get("commodity_id", 0) > 9:
        name = c.get("commodity_disp_name", "")
        if any(k in name.lower() for k in keywords):
            print(" -", c)

print(f"\nHighest commodity_id in the full list: {max(c.get('commodity_id', 0) for c in commodities)}")