import requests

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

r = requests.get(f"{BASE}/commodities", headers=HEADERS, timeout=30)
commodities = r.json().get("data", [])
print(f"Total commodities: {len(commodities)}\n")

keywords = ["tur", "arhar", "pigeon", "red gram", "gram", "dal", "pulse"]
print("ALL matches for pulse-related keywords (full list, not truncated):")
for c in commodities:
    name = c.get("commodity_disp_name", "")
    if any(k in name.lower() for k in keywords):
        print(" -", c)