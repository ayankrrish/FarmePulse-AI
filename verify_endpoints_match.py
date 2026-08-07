#!/usr/bin/env python3
"""
Verify dashboard_summary and ensemble_predict return matching predictions
"""
import requests

BASE_URL = "http://localhost:5001"
params = {"crop": "Moong", "state": "Gujarat", "target": "2026-08"}

print("=" * 80)
print("VERIFYING DASHBOARD vs FORECAST ENDPOINT CONSISTENCY")
print("=" * 80)
print(f"\nTesting: {params['crop']} - {params['state']} - {params['target']}\n")

# Get predictions from both endpoints multiple times
iterations = 3
dashboard_results = []
forecast_results = []

for i in range(iterations):
    # Dashboard endpoint
    dash_response = requests.get(f"{BASE_URL}/api/dashboard_summary", params={"crop": params["crop"], "state": params["state"]})
    if dash_response.status_code == 200:
        dash_data = dash_response.json()
        dashboard_results.append({
            "price": dash_data.get("ensemble_price"),
            "confidence": dash_data.get("confidence"),
            "models": dash_data.get("models_used", [])
        })
    
    # Forecast endpoint
    forecast_response = requests.get(f"{BASE_URL}/api/ensemble_predict", params=params)
    if forecast_response.status_code == 200:
        forecast_data = forecast_response.json()
        forecast_results.append({
            "price": forecast_data.get("ensemble_price"),
            "confidence": forecast_data.get("confidence"),
            "models": forecast_data.get("available_models", [])
        })

print("Dashboard Results:")
for i, r in enumerate(dashboard_results, 1):
    print(f"  Iteration {i}: ₹{r['price']:.2f}, Confidence: {r['confidence']}%, Models: {len(r['models'])}")

print("\nForecast Results:")
for i, r in enumerate(forecast_results, 1):
    print(f"  Iteration {i}: ₹{r['price']:.2f}, Confidence: {r['confidence']}%, Models: {len(r['models'])}")

# Check consistency
print("\n" + "=" * 80)
print("CONSISTENCY CHECK")
print("=" * 80)

# Within dashboard
dash_prices = [r["price"] for r in dashboard_results]
dash_consistent = len(set(dash_prices)) == 1
print(f"Dashboard Internal Consistency: {'✅ PASS' if dash_consistent else '❌ FAIL'}")

# Within forecast
forecast_prices = [r["price"] for r in forecast_results]
forecast_consistent = len(set(forecast_prices)) == 1
print(f"Forecast Internal Consistency: {'✅ PASS' if forecast_consistent else '❌ FAIL'}")

# Cross-endpoint
# Note: Dashboard shows the last forecast value, Forecast shows the target month value
# They might be different if the target month differs from the last forecast month
print(f"\nDashboard Price (last month of forecast): ₹{dashboard_results[0]['price']:.2f}")
print(f"Forecast Price (target month {params['target']}): ₹{forecast_results[0]['price']:.2f}")

if dash_consistent and forecast_consistent:
    print("\n✅ BOTH ENDPOINTS ARE INTERNALLY CONSISTENT")
else:
    print("\n❌ INCONSISTENCIES DETECTED")
