import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)


class UsageProcessor:

    def __init__(self):
        self.df = None

    # ✅ Load CSV file
    def load_data(self, path):
        try:
            self.df = pd.read_csv(path)
            logging.info(f"Data loaded successfully with {len(self.df)} rows")
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            raise

    # ✅ Clean & transform data
    def clean_data(self):
        try:
            df = self.df

            # ✅ Convert datetime
            df['timestamp'] = pd.to_datetime(df['datetime'], errors='coerce')

            # ✅ Drop missing timestamps
            df = df.dropna(subset=['timestamp'])

            # ✅ Create unified metrics
            df['call_count'] = df['callin'] + df['callout']
            df['sms_count'] = df['smsin'] + df['smsout']
            df['internet_usage'] = df['internet']

            # ✅ Rename region column
            df['grid_id'] = df['CellID']

            # ✅ Convert numeric safely
            for col in ['call_count', 'sms_count', 'internet_usage']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # ✅ Remove invalid rows
            df = df[
                (df['call_count'] >= 0) &
                (df['sms_count'] >= 0) &
                (df['internet_usage'] >= 0)
            ]

            # ✅ Drop rows with NaN after conversion
            df = df.dropna(subset=['call_count', 'sms_count', 'internet_usage'])

            # ✅ Extract time features
            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.date

            # ✅ Remove duplicates
            df = df.drop_duplicates()

            self.df = df

            logging.info("Data cleaning completed successfully")

        except Exception as e:
            logging.error(f"Error in cleaning data: {e}")
            raise

    # ✅ Compute daily totals
    def compute_daily_usage(self):
        try:
            daily_usage = self.df.groupby('day')[
                ['call_count', 'sms_count', 'internet_usage']
            ].sum().reset_index()

            logging.info("Daily usage computed")
            return daily_usage

        except Exception as e:
            logging.error(f"Error computing daily usage: {e}")
            raise

    # ✅ Compute KPIs
    def compute_kpis(self):
        try:
            df = self.df

            # ✅ Total usage per region
            region_usage = df.groupby('grid_id')['internet_usage'].sum().reset_index()

            # ✅ Average usage per hour
            hourly_avg = df.groupby('hour')['internet_usage'].mean().reset_index()

            # ✅ Peak usage hour
            peak_hour = hourly_avg.loc[hourly_avg['internet_usage'].idxmax()]['hour']

            logging.info("KPI computation completed")

            return {
                "region_usage": region_usage,
                "hourly_avg": hourly_avg,
                "peak_hour": peak_hour
            }

        except Exception as e:
            logging.error(f"Error computing KPIs: {e}")
            raise


# ✅ ✅ Task 1.3 — Mock API function
def call_plan_api(customer_id):
    """
    Simulated API call to GET /plans/customer/{id}
    """

    mock_response = {
        "customer_id": customer_id,
        "plan_name": "Unlimited 5G",
        "data_limit_gb": 100,
        "sms_limit": "Unlimited",
        "call_limit": "Unlimited",
        "validity": "28 days"
    }

    return mock_response

'''
script to run in python shell :
from python.usage_processor import UsageProcessor, call_plan_api

processor = UsageProcessor()

# Load your dataset
processor.load_data("data/landing/sms-call-internet-mi-2013-11-01.csv")

# Clean data
processor.clean_data()

# Compute daily usage
daily = processor.compute_daily_usage()
print(daily.head())

# Compute KPIs
kpis = processor.compute_kpis()
print("Peak Hour:", kpis['peak_hour'])

# Test API
print(call_plan_api(101))
'''