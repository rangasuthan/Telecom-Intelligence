from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from ml.predict import predict_usage_risk

app = FastAPI(title="Telecom API", version="1.0")


# -------------------------
# DB CONNECTION
# -------------------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="telecom_db"
    )


# -------------------------
# MODELS
# -------------------------
class UsageSummary(BaseModel):
    total_calls: int
    total_sms: int
    total_internet_mb: float
    peak_hour: int
    busiest_region: str


class HourlyEntry(BaseModel):
    hour: int
    calls: int
    sms: int
    internet_mb: float


class RegionUsage(BaseModel):
    region: str
    hourly_distribution: list[HourlyEntry]
    trend: list[float]


class PeakTraffic(BaseModel):
    top_hours: list[dict]
    top_regions: list[dict]


class MLFeatures(BaseModel):
    region: str
    avg_usage: float
    growth_rate: float
    variability: float
    peak_ratio: float


class PredictionRequest(BaseModel):
    region: str
    avg_usage: float
    growth_rate: float
    variability: float


class PredictionResponse(BaseModel):
    congestion_risk: str
    anomaly_flag: bool
    score: float


# -------------------------
# ROOT ENDPOINT (optional)
# -------------------------
@app.get("/")
def home():
    return {"message": "Telecom API running. Go to /docs"}


# -------------------------
# API 1 — SUMMARY ✅ FIXED
# -------------------------
@app.get("/usage/summary", response_model=UsageSummary)
def usage_summary():
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                SUM(call_count),
                SUM(sms_count),
                SUM(internet_mb)
            FROM fact_usage
        """)
        total_calls, total_sms, total_internet = cursor.fetchone()

        cursor.execute("""
            SELECT t.hour, SUM(f.call_count)
            FROM fact_usage f
            JOIN dim_time t ON f.time_id = t.time_id
            GROUP BY t.hour
            ORDER BY SUM(f.call_count) DESC
            LIMIT 1
        """)
        peak_hour = cursor.fetchone()[0]

        cursor.execute("""
            SELECT r.region_name, SUM(f.call_count)
            FROM fact_usage f
            JOIN dim_region r ON f.region_id = r.region_id
            GROUP BY r.region_name
            ORDER BY SUM(f.call_count) DESC
            LIMIT 1
        """)
        busiest_region = cursor.fetchone()[0]

        return UsageSummary(
            total_calls=int(total_calls or 0),   # ✅ FIX
            total_sms=int(total_sms or 0),       # ✅ FIX
            total_internet_mb=float(total_internet or 0),
            peak_hour=int(peak_hour),
            busiest_region=busiest_region
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# API 2 — REGION USAGE
# -------------------------
@app.get("/usage/region/{region}", response_model=RegionUsage)
def region_usage(region: str):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT t.hour, f.call_count, f.sms_count, f.internet_mb
        FROM fact_usage f
        JOIN dim_region r ON f.region_id = r.region_id
        JOIN dim_time t ON f.time_id = t.time_id
        WHERE r.region_name = %s
        ORDER BY t.hour
    """, (region,))

    rows = cursor.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="Region not found")

    hourly = [
        HourlyEntry(
            hour=row["hour"],
            calls=int(row["call_count"] or 0),
            sms=int(row["sms_count"] or 0),
            internet_mb=float(row["internet_mb"] or 0)
        )
        for row in rows
    ]

    trend = [float(row["internet_mb"] or 0) for row in rows]

    return RegionUsage(
        region=region,
        hourly_distribution=hourly,
        trend=trend
    )


# -------------------------
# API 3 — PEAK TRAFFIC
# -------------------------
@app.get("/usage/peak", response_model=PeakTraffic)
def peak_traffic():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT t.hour, SUM(f.internet_mb) AS total_usage
        FROM fact_usage f
        JOIN dim_time t ON f.time_id = t.time_id
        GROUP BY t.hour
        ORDER BY total_usage DESC
        LIMIT 5
    """)
    top_hours = cursor.fetchall()

    cursor.execute("""
        SELECT r.region_name AS region, SUM(f.internet_mb) AS total_usage
        FROM fact_usage f
        JOIN dim_region r ON f.region_id = r.region_id
        GROUP BY r.region_name
        ORDER BY total_usage DESC
        LIMIT 5
    """)
    top_regions = cursor.fetchall()

    return PeakTraffic(top_hours=top_hours, top_regions=top_regions)


# -------------------------
# API 4 — ML FEATURES
# -------------------------
@app.get("/usage/features/{region}", response_model=MLFeatures)
def features(region: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            AVG(internet_mb),
            STDDEV(internet_mb),
            MAX(internet_mb) / NULLIF(AVG(internet_mb),0)
        FROM fact_usage f
        JOIN dim_region r ON f.region_id = r.region_id
        WHERE r.region_name = %s
    """, (region,))

    avg_usage, variability, peak_ratio = cursor.fetchone()

    if avg_usage is None:
        raise HTTPException(status_code=404, detail="Region not found")

    growth_rate = round((peak_ratio or 1) / 10, 4)

    return MLFeatures(
        region=region,
        avg_usage=float(avg_usage),
        growth_rate=growth_rate,
        variability=float(variability or 0),
        peak_ratio=float(peak_ratio or 0)
    )


# -------------------------
# API 5 — PREDICTION
# -------------------------

@app.post("/predict-usage-risk")
def predict_api(req: PredictionRequest):
    return predict_usage_risk(req.dict())


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ allow all (easy for dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
