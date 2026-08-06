import requests
import json

BASE = "https://agmarknet.ceda.ashoka.edu.in/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

print("=" * 60)
print("RAW /states response:")
print("=" * 60)
r = requests.get(f"{BASE}/states", headers=HEADERS, timeout=30)
print("Status code:", r.status_code)
print("Raw text (first 2000 chars):")
print(r.text[:2000])

print("\n" + "=" * 60)
print("RAW /commodities response:")
print("=" * 60)
r2 = requests.get(f"{BASE}/commodities", headers=HEADERS, timeout=30)
print("Status code:", r2.status_code)
print("Raw text (first 2000 chars):")
print(r2.text[:2000])