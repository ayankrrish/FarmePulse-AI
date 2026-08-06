# Model Status Codes Reference

## Quick Status Guide

When viewing Model Analytics page, models now show specific status messages instead of "Not provided".

### Status Messages

| Status Message | Meaning | Action Required |
|----------------|---------|-----------------|
| **Working** | Model is generating predictions | None - model is operational |
| **Package not installed** | Required Python package missing | Install package (see below) |
| **Model incompatible (Keras version)** | Model file format mismatch | Retrain model or install compatibility layer |
| **Model not trained** | No model file exists for this crop | Train model using training scripts |
| **Failed to converge** | Statistical model fitting failed | Expected for ARIMA/SARIMA - intermittent |
| **Error: {ErrorType}** | Unexpected error occurred | Check Flask logs for details |

---

## Package Installation

### XGBoost
```bash
pip3 install xgboost>=2.0,<3.0
```

### Prophet
```bash
pip3 install prophet>=1.1
```

---

## Model Compatibility Issues

### GRU Models (Keras Version Mismatch)

**Problem:** GRU models were trained with Keras 2.x but runtime has Keras 3.x

**Solutions:**

**Option A - Retrain (Recommended):**
```bash
cd /Users/jammubestha/Downloads/ml_changes/scripts/modeling
python3 train_gru.py
```

**Option B - Compatibility Layer:**
```bash
pip3 install tf_keras
```
Then update `app.py` line 85 to use `tf_keras.models.load_model()`

**Option C - Downgrade TensorFlow:**
```bash
pip3 install tensorflow==2.15.0
```

---

## API Response Format

The `/api/ensemble_predict` endpoint now returns:

```json
{
  "individual_predictions": {
    "Random Forest": 5234.50,
    "LSTM": 5189.23,
    "XGBoost": null
  },
  "model_status": {
    "Random Forest": "success",
    "LSTM": "success",
    "XGBoost": "environment_missing",
    "GRU": "model_load_failed",
    "Prophet": "environment_missing",
    "SARIMA": "convergence_failed"
  }
}
```

### Status Code Meanings

- `"success"` - Model worked
- `"model_not_found"` - Model file doesn't exist
- `"model_load_failed"` - Model file exists but can't load
- `"environment_missing"` - Required package not installed
- `"convergence_failed"` - Statistical model couldn't fit
- `"error: {Type}"` - Unexpected error

---

## Verification Checklist

After installing packages and/or retraining models:

- [ ] Start Flask server: `python3 app.py`
- [ ] Open http://127.0.0.1:5000
- [ ] Switch to Academic mode
- [ ] Navigate to Model Analytics
- [ ] Check Prediction Summary table
- [ ] Verify status badges show "Working" for installed models
- [ ] Check Flask console for warning messages
- [ ] Check browser console for API response

---

## Expected Model Availability

### Always Available:
- Random Forest ✅
- LSTM ✅
- Naive Baselines ✅

### Requires Package Installation:
- XGBoost (needs xgboost package)
- Prophet (needs prophet package)

### Requires Model Fix:
- GRU (needs Keras compatibility or retraining)

### Intermittent (By Design):
- ARIMA (convergence dependent)
- SARIMA (convergence dependent)

---

Last Updated: 2026-08-05
