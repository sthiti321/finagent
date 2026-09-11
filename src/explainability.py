import os
import pandas as pd
import shap

from sklearn.ensemble import IsolationForest


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FEATURES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "transactions",
    "transaction_features.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(FEATURES_FILE)

print("=" * 70)
print("V8 — ML EXPLAINABILITY")
print("=" * 70)

print("\nTransactions loaded:", len(df))


# ============================================================
# FEATURES USED BY THE FRAUD MODEL
# ============================================================

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


# ============================================================
# TRAIN THE SAME ISOLATION FOREST MODEL
# ============================================================

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

model.fit(X)


# ============================================================
# SHAP EXPLAINER
# ============================================================

print("\nCreating SHAP explainer...")

explainer = shap.TreeExplainer(model)

# Explain first transaction
sample = X.iloc[[0]]

shap_values = explainer.shap_values(sample)

values = shap_values[0]


# ============================================================
# RISK SCORE
# ============================================================

anomaly_score = model.decision_function(sample)[0]

# Convert anomaly score into a simple 0–100 risk score.
# Lower Isolation Forest scores indicate more anomalous behavior.

risk_score = max(
    0,
    min(
        100,
        (0.5 - anomaly_score) * 100
    )
)


# ============================================================
# DISPLAY SHAP FACTORS
# ============================================================

explanations = pd.DataFrame({
    "feature": features,
    "shap_value": values
})

explanations["absolute_value"] = (
    explanations["shap_value"].abs()
)

explanations = explanations.sort_values(
    "absolute_value",
    ascending=False
)


print("\nTransaction index:", sample.index[0])

print(
    f"\nRisk Score: {risk_score:.2f}/100"
)

print("\nTop contributing factors:")
print("-" * 70)


for _, row in explanations.head(5).iterrows():

    feature = row["feature"]
    shap_value = row["shap_value"]

    sign = "+" if shap_value >= 0 else ""

    print(
        f"{feature:<30} {sign}{shap_value:.4f}"
    )


# ============================================================
# ACTUAL TRANSACTION VALUES
# ============================================================

print("\nTransaction feature values:")
print("-" * 70)

for feature in features:

    print(
        f"{feature:<30} {sample.iloc[0][feature]}"
    )


print("\n" + "=" * 70)
print("SHAP EXPLANATION COMPLETED")
print("=" * 70)