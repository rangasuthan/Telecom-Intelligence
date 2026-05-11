from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp
from pyspark.sql.functions import hour, dayofmonth, sum as _sum
from pyspark.sql.functions import broadcast



def create_session():
    spark = SparkSession.builder \
        .appName("TelecomPipeline") \
        .getOrCreate()

    return spark


def load_data(spark):

    path = "data/landing/sms-call-internet-mi-2013-11-*.csv"

    df = spark.read \
        .option("header", True) \
        .option("inferSchema", True) \
        .csv(path)

    return df


def clean_data(df):

    #  rename columns to snake_case
    df = df.withColumnRenamed("CellID", "cell_id") \
           .withColumnRenamed("countrycode", "country_code")

    #  ensure datetime format (safety)
    df = df.withColumn("datetime", to_timestamp(col("datetime")))

    #  fill nulls with 0
    usage_cols = ["smsin", "smsout", "callin", "callout", "internet"]

    for c in usage_cols:
        df = df.fillna({c: 0})

    #  remove invalid rows (negative values)
    for c in usage_cols:
        df = df.filter(col(c) >= 0)

    return df

def aggregate_data(df):

    #  Extract time info
    df = df.withColumn("hour", hour(col("datetime")))
    df = df.withColumn("day", dayofmonth(col("datetime")))

    #  Add total usage
    df = df.withColumn(
        "total_usage",
        col("smsin") + col("smsout") +
        col("callin") + col("callout") +
        col("internet")
    )

    #  KPI 1 — Calls per hour
    calls_per_hour = df.groupBy("hour") \
        .agg(_sum("callin").alias("total_calls"))

    #  KPI 2 — SMS per region per day
    sms_per_region = df.groupBy("cell_id", "day") \
        .agg(_sum("smsin").alias("total_sms"))

    #  KPI 3 — Internet per day
    internet_per_day = df.groupBy("day") \
        .agg(_sum("internet").alias("total_internet"))

    #  KPI 4 — Top 5 peak hours
    peak_hours = df.groupBy("hour") \
        .agg(_sum("total_usage").alias("usage")) \
        .orderBy(col("usage").desc()) \
        .limit(5)

    summary = df.groupBy("region_name") \
    .agg(_sum("total_usage").alias("total_usage"))

    return calls_per_hour, sms_per_region, internet_per_day, peak_hours, summary

def load_region_mapping(spark):

    path = "data/raw/region_mapping.csv"

    df_region = spark.read \
        .option("header", True) \
        .option("inferSchema", True) \
        .csv(path)

    return df_region

def enrich_with_region(df, df_region):

    df_joined = df.join(
        broadcast(df_region),   # broadcast join
        on="cell_id",
        how="left"
    )

    return df_joined

def write_output(df, summary):

    # Add date column for partitioning
    from pyspark.sql.functions import to_date

    df = df.withColumn("date", to_date(col("datetime")))

    # Write main data
    df.write \
        .mode("overwrite") \
        .partitionBy("date") \
        .parquet("data/processed/usage_data")

    # Write summary (for dashboard later)
    summary.write \
        .mode("overwrite") \
        .parquet("data/processed/summary")


    
def main():
    spark = create_session()

    df = load_data(spark)
    print("-----------Data loaded----------")

    df = clean_data(df)
    print("-----------Data Cleaned---------")

    # column pruning
    df = df.select(
        "cell_id",
        "datetime",
        "smsin",
        "smsout",
        "callin",
        "callout",
        "internet"
    )

    # repartition + cache
    df = df.repartition("cell_id")
    df = df.cache()
    df.count()

    #JOIN BEFORE AGGREGATION
    df_region = load_region_mapping(spark)
    df = enrich_with_region(df, df_region)

    print("-----------Data Enriched---------")

    print("------ Execution Plan ------")
    df.explain()

    # NOW aggregation (correct)
    calls_per_hour, sms_per_region, internet_per_day, peak_hours, summary = aggregate_data(df)

    # write
    write_output(df, summary)

    print(" Data written to Parquet")

    spark.stop()



if __name__ == "__main__":
    main()
