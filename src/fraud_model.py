import pandas as pd
import os

from sklearn.ensemble import IsolationForest

# Project path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Feature file
FEATURES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "transactions",
    "transaction_features.csv"
)

# Load features
df = pd.read_csv(FEATURES_FILE)

print("Transactions loaded:", len(df))

# Features used by the AI model
features = [
    "transaction_amount",
    "average_customer_amount",
    "amount_ratio",
    "transaction_count_1h",
    "transaction_count_24h",
    "merchant_frequency",
    "device_frequency",
    "location_change",
    "hour_deviation"
]

X = df[features]

# Create Isolation Forest model
model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

# Train model
model.fit(X)

# Generate anomaly predictions
df["anomaly_prediction"] = model.predict(X)

# Generate anomaly score
df["anomaly_score"] = model.decision_function(X)

# Convert prediction to fraud flag
df["fraud_flag"] = (
    df["anomaly_prediction"] == -1
).astype(int)

# Save results
OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "transactions",
    "fraud_predictions.csv"
)

df.to_csv(OUTPUT_FILE, index=False)

print("Fraud model completed!")
print("Fraud predictions saved to:", OUTPUT_FILE)

print("\nNormal transactions:", (df["fraud_flag"] == 0).sum())
print("Potential anomalies:", (df["fraud_flag"] == 1).sum())