import joblib
import pandas as pd

for crop in ["chana", "moong", "tur"]:
    bundle = joblib.load(f"rf_model_{crop}.joblib")
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]

    importances = pd.Series(model.feature_importances_, index=feature_cols)
    importances = importances.sort_values(ascending=False)

    print(f"\n{crop.upper()} - Top 10 feature importances:")
    print(importances.head(10).to_string())

    state_importance_total = importances[[c for c in feature_cols if c.startswith("state_")]].sum()
    print(f"  Combined importance of ALL state dummy columns: {state_importance_total:.4f}")