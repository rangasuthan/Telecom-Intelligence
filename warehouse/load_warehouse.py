import pandas as pd
import mysql.connector
import glob

# connect MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="telecom_db"
)

cursor = conn.cursor()

#  read parquet files
files = glob.glob("../data/processed/usage_data/**/*.parquet", recursive=True)

dfs = []
for f in files[:50]:   # limit files
    df = pd.read_parquet(f)
    dfs.append(df)

data = pd.concat(dfs, ignore_index=True)

#  control size
data = data.head(200000)

print("========== BEFORE LOAD ==========")
print(f"Rows going into FACT table: {len(data)}")

#  CLEAN REGION DATA (VERY IMPORTANT FIX)
data['region_name'] = data['region_name'].fillna("Unknown").astype(str).str.strip()
data['city'] = data['city'].fillna("Unknown").astype(str).str.strip()

#  ---------- STEP 1: DIM_TIME ----------

data['datetime'] = pd.to_datetime(data['datetime'])

dim_time = data[['datetime']].drop_duplicates().copy()

dim_time['date'] = dim_time['datetime'].dt.date
dim_time['hour'] = dim_time['datetime'].dt.hour
dim_time['day'] = dim_time['datetime'].dt.day
dim_time['month'] = dim_time['datetime'].dt.month
dim_time['weekday'] = dim_time['datetime'].dt.day_name()

dim_time = dim_time.drop(columns=['datetime']).drop_duplicates()

print("\n========== DIM TIME ==========")
print(f" dim_time rows: {len(dim_time)}")

# insert dim_time
time_map = {}

for _, row in dim_time.iterrows():
    cursor.execute("""
        INSERT INTO dim_time (date, hour, day, month, weekday)
        VALUES (%s, %s, %s, %s, %s)
    """, tuple(row))

    time_id = cursor.lastrowid
    key = (row['date'], row['hour'])
    time_map[key] = time_id

conn.commit()

#  ---------- STEP 2: DIM_REGION ----------

dim_region = data[['region_name', 'city']].drop_duplicates()

print("\n========== DIM REGION ==========")
print(f"dim_region rows: {len(dim_region)}")

region_map = {}

for _, row in dim_region.iterrows():
    cursor.execute("""
        INSERT INTO dim_region (region_name, city)
        VALUES (%s, %s)
    """, tuple(row))

    region_id = cursor.lastrowid
    key = (row['region_name'], row['city'])
    region_map[key] = region_id

conn.commit()

# ---------- STEP 3: FACT TABLE ----------

data['date'] = data['datetime'].dt.date
data['hour'] = data['datetime'].dt.hour

batch_size = 5000
rows = []
inserted_count = 0

print("\n========== FACT LOAD START ==========")

for i, row in enumerate(data.itertuples(index=False), start=1):

    # FIXED REGION MAPPING
    region_key = (str(row.region_name).strip(), str(row.city).strip())
    region_id = region_map.get(region_key)

    time_id = time_map.get((row.date, row.hour))

    # skip invalid mappings
    if region_id is None or time_id is None:
        continue

    # NULL-safe calculations
    call_count = (row.callin or 0) + (row.callout or 0)
    sms_count = (row.smsin or 0) + (row.smsout or 0)
    internet = row.internet or 0

    rows.append((
        time_id,
        region_id,
        int(call_count),
        int(sms_count),
        float(internet)
    ))

    # batch insert
    if len(rows) >= batch_size:
        cursor.executemany("""
            INSERT INTO fact_usage
            (time_id, region_id, call_count, sms_count, internet_mb)
            VALUES (%s, %s, %s, %s, %s)
        """, rows)

        conn.commit()

        inserted_count += len(rows)
        print(f" Inserted batch: {len(rows)} | Total: {inserted_count}")

        rows = []

    #  progress log
    if i % 20000 == 0:
        print(f"⏳ Processed: {i}")

#  insert remaining
if rows:
    cursor.executemany("""
        INSERT INTO fact_usage
        (time_id, region_id, call_count, sms_count, internet_mb)
        VALUES (%s, %s, %s, %s, %s)
    """, rows)

    conn.commit()
    inserted_count += len(rows)

#  FINAL SUMMARY
print("\n========== FINAL LOAD SUMMARY ==========")
print(f" Rows intended: {len(data)}")
print(f" Rows inserted: {inserted_count}")

cursor.close()
conn.close()