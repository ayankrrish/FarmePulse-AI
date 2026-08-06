#!/usr/bin/env python3
"""
Check actual data lengths for all crop/state combinations
"""
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard'))
os.chdir('dashboard')

from app import CONTEXT_DF, TUR_CONTEXT_DF

combinations = [
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
    
    # Tur
    ("Tur", "Maharashtra", TUR_CONTEXT_DF),
    ("Tur", "Karnataka", TUR_CONTEXT_DF),
]

print("=" * 80)
print("DATA LENGTH ANALYSIS")
print("=" * 80)
print(f"\n{'Crop':<8} {'State':<20} {'Length':<10} {'Eligible Configs'}")
print("-" * 80)

for crop, state, df in combinations:
    if crop == "Tur":
        rows = df[df["state"] == state].sort_values("date")
    else:
        rows = df[(df["state"] == state) & (df["crop_label"] == crop)].sort_values("date")
    
    if rows.empty:
        continue
    
    length = len(rows)
    
    # Determine eligible configs
    if length >= 36:
        eligible = "All (full seasonal)"
    elif length >= 24:
        eligible = "Configs 4-9 (seasonal no D, ARIMA)"
    elif length >= 12:
        eligible = "Configs 7-9 (ARIMA only)"
    else:
        eligible = "None (insufficient)"
    
    print(f"{crop:<8} {state:<20} {length:<10} {eligible}")

print("\n" + "=" * 80)
print("CONFIGURATION REQUIREMENTS")
print("=" * 80)
print("1-3.   SARIMA with seasonal differencing (D=1): Requires 36+ months")
print("4-6.   SARIMA without seasonal differencing (D=0): Requires 24+ months")
print("7-9.   ARIMA (no seasonality): Requires 12+ months")
print("=" * 80)
