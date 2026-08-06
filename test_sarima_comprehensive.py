#!/usr/bin/env python3
"""
Comprehensive SARIMA Testing Script
Tests all crop/state combinations and reports success rate
"""
import requests
import json
from collections import defaultdict

# Base URL
BASE_URL = "http://127.0.0.1:5000"

# All combinations to test
COMBINATIONS = [
    # Chana
    ("Chana", "Madhya Pradesh"),
    ("Chana", "Maharashtra"),
    ("Chana", "Rajasthan"),
    ("Chana", "Andhra Pradesh"),
    ("Chana", "Karnataka"),
    ("Chana", "Uttar Pradesh"),
    ("Chana", "Gujarat"),
    ("Chana", "Telangana"),
    
    # Moong
    ("Moong", "Rajasthan"),
    ("Moong", "Maharashtra"),
    ("Moong", "Andhra Pradesh"),
    ("Moong", "Karnataka"),
    ("Moong", "Madhya Pradesh"),
    ("Moong", "Orissa"),
    ("Moong", "Tamil Nadu"),
    
    # Tur
    ("Tur", "Maharashtra"),
    ("Tur", "Karnataka"),
    ("Tur", "Madhya Pradesh"),
    ("Tur", "Gujarat"),
    ("Tur", "Andhra Pradesh"),
    ("Tur", "Telangana"),
    ("Tur", "Rajasthan"),
    ("Tur", "Uttar Pradesh"),
]

def test_sarima():
    """Test SARIMA on all combinations"""
    results = []
    status_counts = defaultdict(int)
    
    print("=" * 80)
    print("SARIMA COMPREHENSIVE TEST")
    print("=" * 80)
    print(f"\nTesting {len(COMBINATIONS)} crop/state combinations...\n")
    
    for i, (crop, state) in enumerate(COMBINATIONS, 1):
        try:
            # Make API request
            response = requests.get(
                f"{BASE_URL}/api/ensemble_predict",
                params={"crop": crop, "state": state},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract SARIMA info
                sarima_prediction = None
                sarima_status = "unknown"
                
                # Check model_status
                if "model_status" in data:
                    sarima_status = data["model_status"].get("SARIMA", "unknown")
                
                # Check predictions
                if "predictions" in data:
                    for pred in data["predictions"]:
                        if pred.get("model") == "SARIMA":
                            sarima_prediction = pred.get("prediction")
                            break
                
                # Determine result
                if sarima_prediction is not None:
                    result = "✅ SUCCESS"
                    status = "success"
                elif sarima_status == "convergence_failed":
                    result = "⚠️  CONVERGENCE_FAILED"
                    status = "convergence_failed"
                elif sarima_status == "error: TypeError":
                    result = "❌ ERROR"
                    status = "error"
                else:
                    result = f"❓ {sarima_status.upper()}"
                    status = sarima_status
                
                status_counts[status] += 1
                
                results.append({
                    "crop": crop,
                    "state": state,
                    "prediction": sarima_prediction,
                    "status": sarima_status,
                    "result": result
                })
                
                print(f"{i:2d}. {crop:6s} / {state:20s} -> {result:30s} | pred={sarima_prediction}")
            else:
                print(f"{i:2d}. {crop:6s} / {state:20s} -> HTTP {response.status_code}")
                status_counts["http_error"] += 1
        
        except Exception as e:
            print(f"{i:2d}. {crop:6s} / {state:20s} -> EXCEPTION: {e}")
            status_counts["exception"] += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total combinations tested: {len(COMBINATIONS)}")
    print(f"\nStatus breakdown:")
    for status, count in sorted(status_counts.items()):
        percentage = (count / len(COMBINATIONS)) * 100
        print(f"  {status:25s}: {count:2d} ({percentage:5.1f}%)")
    
    success_rate = (status_counts.get("success", 0) / len(COMBINATIONS)) * 100
    print(f"\n{'SUCCESS RATE':25s}: {success_rate:5.1f}%")
    
    # Detailed results by crop
    print("\n" + "=" * 80)
    print("RESULTS BY CROP")
    print("=" * 80)
    
    for crop in ["Chana", "Moong", "Tur"]:
        crop_results = [r for r in results if r["crop"] == crop]
        successes = sum(1 for r in crop_results if r["prediction"] is not None)
        total = len(crop_results)
        rate = (successes / total * 100) if total > 0 else 0
        
        print(f"\n{crop}:")
        print(f"  Success rate: {successes}/{total} ({rate:.1f}%)")
        
        # Show failures
        failures = [r for r in crop_results if r["prediction"] is None]
        if failures:
            print(f"  Failures:")
            for f in failures:
                print(f"    - {f['state']:20s}: {f['status']}")
    
    print("\n" + "=" * 80)
    print("Check Flask logs for diagnostic messages showing:")
    print("  - Which SARIMA configurations were tried")
    print("  - Why each configuration failed")
    print("  - Convergence warnings from statsmodels")
    print("=" * 80)
    
    return results, status_counts

if __name__ == "__main__":
    test_sarima()
