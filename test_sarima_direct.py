#!/usr/bin/env python3
"""
Direct SARIMA Testing - bypasses Flask server
Tests SARIMA function directly on sample data
"""
import sys
import os
import pandas as pd
import numpy as np

# Add dashboard to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard'))

# Import after path setup
os.chdir('dashboard')

# Now we can import from app
from app import forecast_sarima, CONTEXT_DF, TUR_CONTEXT_DF

def test_sarima_direct():
    """Test SARIMA directly on real data"""
    
    print("=" * 80)
    print("DIRECT SARIMA TESTING - ALL COMBINATIONS")
    print("=" * 80)
    
    # Test ALL 23 combinations
    test_cases = [
        # Chana
        ("Chana", "Madhya Pradesh", CONTEXT_DF),
        ("Chana", "Maharashtra", CONTEXT_DF),
        ("Chana", "Rajasthan", CONTEXT_DF),
        ("Chana", "Andhra Pradesh", CONTEXT_DF),
        ("Chana", "Karnataka", CONTEXT_DF),
        ("Chana", "Uttar Pradesh", CONTEXT_DF),
        ("Chana", "Gujarat", CONTEXT_DF),
        ("Chana", "Telangana", CONTEXT_DF),
        
        # Moong
        ("Moong", "Rajasthan", CONTEXT_DF),
        ("Moong", "Maharashtra", CONTEXT_DF),
        ("Moong", "Andhra Pradesh", CONTEXT_DF),
        ("Moong", "Karnataka", CONTEXT_DF),
        ("Moong", "Madhya Pradesh", CONTEXT_DF),
        ("Moong", "Orissa", CONTEXT_DF),
        ("Moong", "Tamil Nadu", CONTEXT_DF),
        
        # Tur
        ("Tur", "Maharashtra", TUR_CONTEXT_DF),
        ("Tur", "Karnataka", TUR_CONTEXT_DF),
        ("Tur", "Madhya Pradesh", TUR_CONTEXT_DF),
        ("Tur", "Gujarat", TUR_CONTEXT_DF),
        ("Tur", "Andhra Pradesh", TUR_CONTEXT_DF),
        ("Tur", "Telangana", TUR_CONTEXT_DF),
        ("Tur", "Rajasthan", TUR_CONTEXT_DF),
        ("Tur", "Uttar Pradesh", TUR_CONTEXT_DF),
    ]
    
    results = []
    
    for i, (crop, state, df) in enumerate(test_cases, 1):
        # Get data
        if crop == "Tur":
            state_rows = df[df["state"] == state].sort_values("date")
        else:
            state_rows = df[
                (df["state"] == state) & (df["crop_label"] == crop)
            ].sort_values("date")
        
        if state_rows.empty:
            print(f"{i:2d}. {crop:6s} / {state:20s} -> ❌ NO DATA")
            results.append((crop, state, "no_data", None, 0, None))
            continue
        
        prices = state_rows["modal_price"].values
        data_length = len(prices)
        
        # Test forecast (suppress output during loop)
        try:
            result = forecast_sarima(prices, steps=3)
            forecast, config_name = result if result else (None, None)
            
            if forecast is not None:
                status_icon = "✅"
                status = "success"
                forecast_str = f"{config_name} → {[round(p, 2) for p in forecast[:1]]}"
            else:
                status_icon = "⚠️ "
                status = "convergence_failed"
                forecast_str = "all configs failed"
                config_name = None
            
            results.append((crop, state, status, forecast, data_length, config_name))
        
        except Exception as e:
            status_icon = "❌"
            status = f"error: {type(e).__name__}"
            forecast_str = str(e)[:50]
            results.append((crop, state, status, None, data_length, None))
        
        print(f"{i:2d}. {crop:6s} / {state:20s} | {data_length:3d} months -> {status_icon} {forecast_str}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r[2] == "success")
    convergence_failed = sum(1 for r in results if r[2] == "convergence_failed")
    insufficient_data = sum(1 for r in results if r[2] == "convergence_failed" and r[4] < 12)
    total_count = len(results)
    
    print(f"\nTotal combinations:     {total_count}")
    print(f"Successes:              {success_count} ({success_count / total_count * 100:.1f}%)")
    print(f"Convergence failed:     {convergence_failed} ({convergence_failed / total_count * 100:.1f}%)")
    print(f"  - Insufficient data:  {insufficient_data} (< 12 months)")
    print(f"  - True convergence:   {convergence_failed - insufficient_data}")
    
    print(f"\nSuccess rate: {success_count / total_count * 100:.1f}%")
    
    # Group by crop
    print("\n" + "=" * 80)
    print("RESULTS BY CROP")
    print("=" * 80)
    
    for crop in ["Chana", "Moong", "Tur"]:
        crop_results = [r for r in results if r[0] == crop]
        successes = sum(1 for r in crop_results if r[2] == "success")
        total = len(crop_results)
        rate = (successes / total * 100) if total > 0 else 0
        
        print(f"\n{crop}:")
        print(f"  Success: {successes}/{total} ({rate:.1f}%)")
        
        # Show data lengths
        data_lengths = [r[4] for r in crop_results]
        if data_lengths:
            print(f"  Data range: {min(data_lengths)}-{max(data_lengths)} months")
        
        # Show configs used
        configs_used = [r[5] for r in crop_results if r[5] is not None]
        if configs_used:
            from collections import Counter
            config_counts = Counter(configs_used)
            print(f"  Configurations used:")
            for cfg, count in config_counts.most_common():
                print(f"    - {cfg}: {count} times")
    
    return results

if __name__ == "__main__":
    test_sarima_direct()
