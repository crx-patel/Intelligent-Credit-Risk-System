import joblib
import sklearn
import numpy
import sys

print("Current Environment Versions 👇")
print("Python:", sys.version)
print("NumPy:", numpy.__version__)
print("Scikit-learn:", sklearn.__version__)

print("\nLoading model info...\n")

model = joblib.load("models/scaler.pkl")

# Try to print metadata
if hasattr(model, "__module__"):
    print("Model module:", model.__module__)

if hasattr(model, "__class__"):
    print("Model class:", model.__class__)

print("\nDone ✅")