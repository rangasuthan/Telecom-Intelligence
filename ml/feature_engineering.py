import pandas as pd
import mysql.connector
import numpy as np


# -------------------------
# LOAD DATA FROM MYSQL
# -------------------------
def get_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="telecom_db"
    )

    query = """
        SELECT 
            r.region_name,
            t.date,
            t.hour,
            f.call_count,
            f.sms_count,
            f.internet_mb
        FROM fact_usage f
        JOIN dim_time t ON f.time_id = t.time_id
        JOIN dim_region r ON f.region_id = r.region_id
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df


# -------------------------
# FEATURE ENGINEERING
# -------------------------
def build_features(df):

    df["total_usage"] = (
        df["call_count"] + df["sms_count"] + df["internet_mb"]
    )

    features = df.groupby("region_name").agg(
        avg_usage=("total_usage", "mean"),
        variability=("total_usage", "std"),
        peak_usage=("total_usage", "max")
    ).reset_index()

    # Peak ratio
    features["peak_ratio"] = features["peak_usage"] / features["avg_usage"]

    # Growth rate
    features["growth_rate"] = features["avg_usage"].pct_change().fillna(0)

    # -------------------------
    # LABEL CREATION
    # -------------------------
    p90 = features["avg_usage"].quantile(0.9)
    p60 = features["avg_usage"].quantile(0.6)

    def label(x):
        if x > p90:
            return "HIGH"
        elif x > p60:
            return "MEDIUM"
        else:
            return "LOW"

    features["label"] = features["avg_usage"].apply(label)

    return features


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":

    print("📥 Loading data from MySQL...")
    df = get_data()

    print("⚙️ Building features...")
    features = build_features(df)

    print("💾 Saving features.csv...")
    features.to_csv("ml/features.csv", index=False)

    print("✅ features.csv created successfully!")