#!/usr/bin/env python3
"""
Test API status response to verify SARIMA configuration is exposed
"""
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard'))
os.chdir('dashboard')

from app import _collect_all_forecasts, CONTEXT_DF, TUR_CONTEXT_DF

def test_api_status():
    """Test that model status correctly exposes SARIMA configuration"""
    
    print("=" * 80)
    print("API STATUS VERIFICATION")
    print("=" * 80)
    
    # Test case 1: Chana with 12 months (should use ARIMA fallback)
    print("\nTest 1: Chana / Madhya Pradesh (12 months data)")
    print("-" * 80)
    
    crop = "Chana"
    state = "Madhya Pradesh"
    state_rows = CONTEXT_DF[
        (CONTEXT_DF["state"] == state) & (CONTEXT_DF["crop_label"] == crop)
    ].sort_values("date")
    
    prices = state_rows["modal_price"].values
    print(f"Data length: {len(prices)} months")
    
    forecasts_dict, status_dict = _collect_all_forecasts(crop, state, state_rows, prices, steps=3)
    
    print(f"\nSARIMA status: {status_dict.get('SARIMA', 'NOT FOUND')}")
    
    if "SARIMA" in forecasts_dict:
        print(f"SARIMA forecast: {[round(p, 2) for p in forecasts_dict['SARIMA']]}")
    else:
        print("SARIMA forecast: None")
    
    # Verify status shows fallback
    if "fallback" in status_dict.get("SARIMA", ""):
        print("✅ Status correctly indicates ARIMA fallback")
    else:
        print("⚠️  Status does not indicate fallback - may be misleading")
    
    # Test case 2: Tur with 4 months (should fail)
    print("\n\nTest 2: Tur / Maharashtra (4 months data)")
    print("-" * 80)
    
    crop = "Tur"
    state = "Maharashtra"
    state_rows = TUR_CONTEXT_DF[TUR_CONTEXT_DF["state"] == state].sort_values("date")
    
    prices = state_rows["modal_price"].values
    print(f"Data length: {len(prices)} months")
    
    forecasts_dict, status_dict = _collect_all_forecasts(crop, state, state_rows, prices, steps=3)
    
    print(f"\nSARIMA status: {status_dict.get('SARIMA', 'NOT FOUND')}")
    
    if "SARIMA" in forecasts_dict:
        print(f"SARIMA forecast: {[round(p, 2) for p in forecasts_dict['SARIMA']]}")
    else:
        print("SARIMA forecast: None")
    
    # Verify status shows convergence_failed
    if status_dict.get("SARIMA") == "convergence_failed":
        print("✅ Status correctly indicates convergence_failed")
    else:
        print(f"⚠️  Unexpected status: {status_dict.get('SARIMA')}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nThe model_status field in API responses now shows:")
    print("  - For 12-month data: 'success (fallback: ARIMA(1,1,1))'")
    print("  - For <12-month data: 'convergence_failed'")
    print("\nThis clearly indicates to users that:")
    print("  1. SARIMA predictions are actually ARIMA fallbacks (no seasonality)")
    print("  2. True SARIMA requires 24-36 months of data")
    print("  3. Current data (12 months) is insufficient for seasonal models")
    print("=" * 80)

if __name__ == "__main__":
    test_api_status()
