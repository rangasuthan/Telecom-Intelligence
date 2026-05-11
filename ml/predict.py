import joblib
import numpy as np
import os


# -------------------------
# LOAD MODEL (SAFE PATH)
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

model = joblib.load(MODEL_PATH)


# -------------------------
# PREDICTION FUNCTION
# -------------------------
def predict_usage_risk(features: dict) -> dict:

    try:
        values = np.array([[
            features["avg_usage"],
            features["growth_rate"],
            features["variability"],
            features.get("peak_ratio", 1.0)
        ]])

        prediction = model.predict(values)[0]
        probability = float(max(model.predict_proba(values)[0]))

        return {
            "congestion_risk": prediction,
            "anomaly_flag": features["variability"] > 0.5,
            "score": round(probability, 3)
        }

    except Exception as e:
        return {"error": str(e)}
