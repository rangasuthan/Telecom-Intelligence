# 📡 Telecom Network Intelligence System

An end-to-end Data Engineering, Analytics, and Machine Learning system for telecom usage monitoring and congestion prediction.

---

## 🚀 Overview

This project implements a complete pipeline:

- Data ingestion using Airflow  
- Data processing using Apache Spark  
- Data storage using MySQL (Star Schema)  
- Backend APIs using FastAPI  
- Frontend dashboard using React  
- Machine Learning model for congestion prediction  

---

## 🧰 Tech Stack

- Python
- Apache Airflow
- Apache Spark (PySpark)
- MySQL
- FastAPI
- React (Vite)
- Scikit-learn
- Pandas
- NumPy

---

## 📂 Project Structure

```text
telecom-intelligence/
├── airflow/
├── spark/
├── data/
├── warehouse/
├── api/
├── react-app/
├── ml/
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

---

### 2. Install Dependencies

```bash
pip install pandas numpy scikit-learn mysql-connector-python fastapi uvicorn pyspark joblib
```

---

### 3. Setup MySQL

```sql
CREATE DATABASE telecom_db;
USE telecom_db;
```

Run schema:

```sql
SOURCE warehouse/schema.sql;
```

---

### 4. Setup React Environment Variable

Create file:

```text
react-app/.env
```

Add:

```env
VITE_API_BASE=http://localhost:8000
```

---

## ▶️ Phase 3 — Data Engineering

Start Airflow:

```bash
airflow standalone
```

Place input files:

```text
data/landing/*.csv
```

Trigger DAG:

```text
telecom_pipeline
```

Run Spark (optional):

```bash
spark-submit spark/telecom_pipeline.py
```

Load warehouse:

```bash
spark-submit warehouse/load_warehouse.py
```

Warehouse tables:

- fact_usage
- dim_time
- dim_region

---

## ▶️ Phase 4 — FastAPI Backend

Start API:

```bash
uvicorn api.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000/docs
```

Endpoints:

- /usage/summary
- /usage/region/{region}
- /usage/peak
- /predict-usage-risk

---

## ▶️ Phase 5 — React Frontend

Start frontend:

```bash
cd react-app
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Features:

- Usage Dashboard
- Region Explorer
- Peak Traffic
- Prediction Module

---

## ▶️ Phase 6 — Machine Learning

Feature Engineering:

```bash
python ml/feature_engineering.py
```

Output:

```text
ml/features.csv
```

Train Model:

```bash
python ml/train_model.py
```

Output:

```text
ml/model.pkl
```

Prediction Example:

```json
{
  "region": "Centro",
  "avg_usage": 1200,
  "growth_rate": 0.15,
  "variability": 0.30
}
```

Response:

```json
{
  "congestion_risk": "HIGH",
  "anomaly_flag": true,
  "score": 0.87
}
```

Batch Scoring:

```bash
python ml/batch_score.py
```

Output:

```text
ml/batch_predictions.csv
```

---

## 🧠 Machine Learning Details

Model: Random Forest Classifier

Features:

- avg_usage
- growth_rate
- variability
- peak_ratio

Labeling Strategy:

- Top 90% → HIGH
- 60–90% → MEDIUM
- Below 60% → LOW

---

## ⚠️ Common Issues

### CORS Error

Enable CORS in FastAPI.

### `model.pkl` Not Found

```bash
python ml/train_model.py
```

### Port Already in Use

```bash
kill -9 $(lsof -t -i:8000)
```

---

## ✅ Final Outcome

- Airflow pipeline working
- Spark processing completed
- Warehouse populated
- FastAPI backend functional
- React dashboard connected
- ML prediction integrated

---

## 👨‍💻 Author

Sri Rangasuthan T
