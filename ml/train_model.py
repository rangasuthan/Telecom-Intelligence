import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


# -------------------------
# LOAD FEATURES
# -------------------------
df = pd.read_csv("ml/features.csv")

X = df[["avg_usage", "growth_rate", "variability", "peak_ratio"]]
y = df["label"]


# -------------------------
# TRAIN TEST SPLIT
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("✅ Data split completed")


# -------------------------
# MODEL TRAINING
# -------------------------
model = RandomForestClassifier()

model.fit(X_train, y_train)

print("✅ Model trained")


# -------------------------
# EVALUATION
# -------------------------
y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))


# -------------------------
# SAVE MODEL
# -------------------------
joblib.dump(model, "ml/model.pkl")

print("💾 model.pkl saved successfully!")
