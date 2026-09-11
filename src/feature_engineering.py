
import pandas as pd
import numpy as np
import os
# Project path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Transaction file path
TRANSACTIONS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "transactions",
    "transactions.csv"
)

# Load transactions
df = pd.read_csv(TRANSACTIONS_FILE)

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

print("Transactions loaded:", len(df))
# Feature 1: Transaction amount
df["transaction_amount"] = df["amount"]

print(df[["transaction_id", "transaction_amount"]].head())
# Feature 2: Average transaction amount for each customer
df["average_customer_amount"] = (
    df.groupby("customer_id")["transaction_amount"]
      .transform("mean")
)

print(
    df[
        ["customer_id", "transaction_amount", "average_customer_amount"]
    ].head()
)
# Feature 3: Transaction amount compared with customer's average
df["amount_ratio"] = (
    df["transaction_amount"] /
    df["average_customer_amount"]
)

print(
    df[
        [
            "customer_id",
            "transaction_amount",
            "average_customer_amount",
            "amount_ratio"
        ]
    ].head()
)
# Feature 4: Transaction count in the previous 1 hour
df = df.sort_values(["customer_id", "timestamp"])

df["transaction_count_1h"] = (
    df.groupby("customer_id")
      .rolling("1h", on="timestamp")["transaction_id"]
      .count()
      .reset_index(level=0, drop=True)
      .values
)

# Feature 5: Transaction count in the previous 24 hours
df["transaction_count_24h"] = (
    df.groupby("customer_id")
      .rolling("24h", on="timestamp")["transaction_id"]
      .count()
      .reset_index(level=0, drop=True)
      .values
)

# Feature 6: Merchant frequency for each customer
df["merchant_frequency"] = (
    df.groupby(["customer_id", "merchant_id"])["transaction_id"]
      .transform("count")
)

# Feature 7: Device frequency for each customer
df["device_frequency"] = (
    df.groupby(["customer_id", "device_id"])["transaction_id"]
      .transform("count")
)

# Feature 8: Location change
df["previous_location"] = (
    df.groupby("customer_id")["location"]
      .shift(1)
)

df["location_change"] = (
    (df["location"] != df["previous_location"])
    .astype(int)
)

# First transaction has no previous location
df["location_change"] = df["location_change"].fillna(0)

# Feature 9: Hour deviation
df["transaction_hour"] = df["timestamp"].dt.hour

customer_average_hour = (
    df.groupby("customer_id")["transaction_hour"]
      .transform("mean")
)

df["hour_deviation"] = abs(
    df["transaction_hour"] - customer_average_hour
)

# Remove temporary columns
df.drop(
    columns=["previous_location", "transaction_hour"],
    inplace=True
)

# Save engineered features
FEATURES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "transactions",
    "transaction_features.csv"
)

df.to_csv(FEATURES_FILE, index=False)

print("Feature engineering completed!")
print("Features saved to:", FEATURES_FILE)

print("\nCreated features:")
print([
    "transaction_amount",
    "average_customer_amount",
    "amount_ratio",
    "transaction_count_1h",
    "transaction_count_24h",
    "merchant_frequency",
    "device_frequency",
    "location_change",
    "hour_deviation"
])