import pandas as pd
from predict import predict_usage_risk

df = pd.read_csv("ml/features.csv")

results = []

for _, row in df.iterrows():
    pred = predict_usage_risk(row.to_dict())

    results.append({
        "region": row["region_name"],
        "prediction": pred["congestion_risk"],
        "score": pred["score"],
        "anomaly": pred["anomaly_flag"]
    })

out = pd.DataFrame(results)

out.to_csv("ml/batch_predictions.csv", index=False)

print("✅ Batch predictions saved!")
