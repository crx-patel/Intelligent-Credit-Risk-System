import joblib

# List of model files (adjust if needed)
files = [
    "models/scaler.pkl",
    "models/model.pkl",
    "models/threshold.pkl",
    "models/fraud_model.pkl",
    "models/fraud_scaler.pkl",
    "models/fraud_thresholds.pkl"
]

for file in files:
    try:
        obj = joblib.load(file)
        joblib.dump(obj, file)
        print(f"Fixed: {file}")
    except Exception as e:
        print(f"Skipped: {file} -> {e}")