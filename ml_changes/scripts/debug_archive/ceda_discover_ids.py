"""
CEDA Agmarknet API discovery script.
Finds the exact commodity_id and state_id values we need before
pulling historical price data.
"""

import requests

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

TARGET_STATES = [
    "Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh",
    "Karnataka", "Telangana", "Andhra Pradesh", "Gujarat",
]

CROP_KEYWORDS = ["tur", "arhar", "moong", "gram", "chana", "pigeon", "green gram"]


def get_states():
    r = requests.get(f"{BASE}/states", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def get_commodities():
    r = requests.get(f"{BASE}/commodities", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


print("Fetching states list...")
states = get_states()
print(f"Total states returned: {len(states)}\n")
print("Matching our 8 target states:")
matched_states = {}
for s in states:
    name = s.get("name") or s.get("state_name") or str(s)
    for target in TARGET_STATES:
        if target.lower() in str(name).lower():
            print(f"  {target}  ->  {s}")
            matched_states[target] = s

print("\n" + "=" * 60)
print("Fetching commodities list...")
commodities = get_commodities()
print(f"Total commodities returned: {len(commodities)}\n")
print("Matching pulse-related commodities:")
for c in commodities:
    name = c.get("name") or c.get("display_name") or str(c)
    if any(k in str(name).lower() for k in CROP_KEYWORDS):
        print(" -", c)