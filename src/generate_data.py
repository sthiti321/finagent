# ============================================================
# FINAGENT
# Autonomous Financial Crime Investigation Agent
# Complete Data + ML + Behavior + Anomaly + AML Graph Engine
# ============================================================

import os
import random
import pickle
import warnings

import numpy as np
import pandas as pd
import networkx as nx

from faker import Faker

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from xgboost import XGBClassifier


warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

fake = Faker()

random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

CUSTOMERS_DIR = os.path.join(
    DATA_DIR,
    "customers"
)

ACCOUNTS_DIR = os.path.join(
    DATA_DIR,
    "accounts"
)

TRANSACTIONS_DIR = os.path.join(
    DATA_DIR,
    "transactions"
)

MERCHANTS_DIR = os.path.join(
    DATA_DIR,
    "merchants"
)

DEVICES_DIR = os.path.join(
    DATA_DIR,
    "devices"
)

ALERTS_DIR = os.path.join(
    DATA_DIR,
    "alerts"
)

CASES_DIR = os.path.join(
    DATA_DIR,
    "cases"
)


# Create directories
for directory in [
    CUSTOMERS_DIR,
    ACCOUNTS_DIR,
    TRANSACTIONS_DIR,
    MERCHANTS_DIR,
    DEVICES_DIR,
    ALERTS_DIR,
    CASES_DIR
]:
    os.makedirs(
        directory,
        exist_ok=True
    )


# ============================================================
# DATASET SIZES
# ============================================================

NUM_CUSTOMERS = 1000
NUM_ACCOUNTS = 1200
NUM_TRANSACTIONS = 100000
NUM_MERCHANTS = 100
NUM_DEVICES = 1500
NUM_ALERTS = 500
NUM_CASES = 200


# ============================================================
# COMMON VALUES
# ============================================================

cities = [
    "Hyderabad",
    "Mumbai",
    "Delhi",
    "Bangalore",
    "Chennai",
    "Pune",
    "Kolkata",
    "Ahmedabad",
    "Jaipur",
    "Lucknow"
]

occupations = [
    "Engineer",
    "Doctor",
    "Teacher",
    "Business Owner",
    "Student",
    "Consultant",
    "Manager",
    "Accountant",
    "Lawyer",
    "Designer"
]

account_types = [
    "Savings",
    "Current"
]

transaction_types = [
    "Purchase",
    "Transfer",
    "Withdrawal",
    "Deposit",
    "Bill Payment"
]

payment_methods = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking"
]

currencies = [
    "INR"
]


# ============================================================
# 1. GENERATE CUSTOMERS
# ============================================================

print("\n==========================================")
print("1. GENERATING CUSTOMERS")
print("==========================================")

customers = []

for i in range(1, NUM_CUSTOMERS + 1):

    customers.append({

        "customer_id":
            f"CUST{i:05d}",

        "name":
            fake.name(),

        "age":
            random.randint(
                18,
                70
            ),

        "gender":
            random.choice([
                "Male",
                "Female",
                "Other"
            ]),

        "city":
            random.choice(
                cities
            ),

        "occupation":
            random.choice(
                occupations
            ),

        "income":
            round(
                random.uniform(
                    20000,
                    500000
                ),
                2
            ),

        "customer_since":
            fake.date_between(
                start_date="-10y",
                end_date="today"
            )
    })


customers_df = pd.DataFrame(
    customers
)

customers_df.to_csv(
    os.path.join(
        CUSTOMERS_DIR,
        "customers.csv"
    ),
    index=False
)

print(
    "Customers generated:",
    len(customers_df)
)


# ============================================================
# 2. GENERATE ACCOUNTS
# ============================================================

print("\n==========================================")
print("2. GENERATING ACCOUNTS")
print("==========================================")

accounts = []

for i in range(1, NUM_ACCOUNTS + 1):

    customer = random.choice(
        customers
    )

    accounts.append({

        "account_id":
            f"ACC{i:06d}",

        "customer_id":
            customer["customer_id"],

        "account_type":
            random.choice(
                account_types
            ),

        "balance":
            round(
                random.uniform(
                    1000,
                    2000000
                ),
                2
            ),

        "opened_date":
            fake.date_between(
                start_date="-10y",
                end_date="today"
            )
    })


accounts_df = pd.DataFrame(
    accounts
)

accounts_df.to_csv(
    os.path.join(
        ACCOUNTS_DIR,
        "accounts.csv"
    ),
    index=False
)

print(
    "Accounts generated:",
    len(accounts_df)
)


# ============================================================
# 3. GENERATE MERCHANTS
# ============================================================

print("\n==========================================")
print("3. GENERATING MERCHANTS")
print("==========================================")

merchants = []

merchant_categories = [
    "Retail",
    "Restaurant",
    "Travel",
    "Electronics",
    "Healthcare",
    "Entertainment",
    "Online Services",
    "Grocery",
    "Education",
    "Other"
]

for i in range(1, NUM_MERCHANTS + 1):

    merchants.append({

        "merchant_id":
            f"MERCH{i:03d}",

        "merchant_name":
            fake.company(),

        "category":
            random.choice(
                merchant_categories
            ),

        "city":
            random.choice(
                cities
            )
    })


merchants_df = pd.DataFrame(
    merchants
)

merchants_df.to_csv(
    os.path.join(
        MERCHANTS_DIR,
        "merchants.csv"
    ),
    index=False
)

print(
    "Merchants generated:",
    len(merchants_df)
)


# ============================================================
# 4. GENERATE DEVICES
# ============================================================

print("\n==========================================")
print("4. GENERATING DEVICES")
print("==========================================")

devices = []

device_types = [
    "Mobile",
    "Laptop",
    "Tablet"
]

operating_systems = [
    "Android",
    "iOS",
    "Windows",
    "macOS"
]

for i in range(1, NUM_DEVICES + 1):

    customer = random.choice(
        customers
    )

    devices.append({

        "device_id":
            f"DEV{i:06d}",

        "customer_id":
            customer["customer_id"],

        "device_type":
            random.choice(
                device_types
            ),

        "operating_system":
            random.choice(
                operating_systems
            )
    })


devices_df = pd.DataFrame(
    devices
)

devices_df.to_csv(
    os.path.join(
        DEVICES_DIR,
        "devices.csv"
    ),
    index=False
)

print(
    "Devices generated:",
    len(devices_df)
)


# ============================================================
# 5. GENERATE TRANSACTIONS
#
# IMPORTANT:
# destination_account_id is included here.
#
# This allows the AML graph to represent:
#
# Account A --> Account B
#
# which is required for:
# - Fan-in
# - Fan-out
# - Circular transfers
# - Suspicious transaction paths
# - Connected risky accounts
# ============================================================

print("\n==========================================")
print("5. GENERATING TRANSACTIONS")
print("==========================================")

transactions = []

account_list = accounts.copy()

# Map customer -> devices
customer_devices = {}

for device in devices:

    customer_id = device["customer_id"]

    if customer_id not in customer_devices:
        customer_devices[customer_id] = []

    customer_devices[customer_id].append(
        device["device_id"]
    )


for i in range(1, NUM_TRANSACTIONS + 1):

    source_account = random.choice(
        account_list
    )

    source_account_id = (
        source_account["account_id"]
    )

    customer_id = (
        source_account["customer_id"]
    )

    transaction_type = random.choice(
        transaction_types
    )

    # --------------------------------------------------------
    # DEVICE
    # --------------------------------------------------------

    if customer_id in customer_devices:

        device_id = random.choice(
            customer_devices[customer_id]
        )

    else:

        device_id = random.choice(
            devices_df["device_id"].tolist()
        )

    # --------------------------------------------------------
    # DESTINATION ACCOUNT
    #
    # Only transfer transactions get a destination.
    # --------------------------------------------------------

    destination_account_id = None

    if transaction_type == "Transfer":

        destination_account = random.choice(
            account_list
        )

        # Prevent self-transfer
        while (
            destination_account["account_id"]
            == source_account_id
        ):

            destination_account = random.choice(
                account_list
            )

        destination_account_id = (
            destination_account["account_id"]
        )

    # --------------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------------

    year = random.choice([
        2025,
        2026
    ])

    month = random.randint(
        1,
        8
    )

    day = random.randint(
        1,
        28
    )

    hour = random.randint(
        0,
        23
    )

    minute = random.randint(
        0,
        59
    )

    second = random.randint(
        0,
        59
    )

    timestamp = pd.Timestamp(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second
    )

    # --------------------------------------------------------
    # AMOUNT
    # --------------------------------------------------------

    amount = round(
        random.uniform(
            100,
            100000
        ),
        2
    )

    transactions.append({

        "transaction_id":
            f"TXN{i:06d}",

        "customer_id":
            customer_id,

        "account_id":
            source_account_id,

        "destination_account_id":
            destination_account_id,

        "merchant_id":
            random.choice(
                merchants_df[
                    "merchant_id"
                ].tolist()
            ),

        "device_id":
            device_id,

        "timestamp":
            timestamp,

        "amount":
            amount,

        "currency":
            random.choice(
                currencies
            ),

        "location":
            random.choice(
                cities
            ),

        "transaction_type":
            transaction_type,

        "payment_method":
            random.choice(
                payment_methods
            )
    })


transactions_df = pd.DataFrame(
    transactions
)

# ------------------------------------------------------------
# SUSPICIOUS TRANSACTION LABEL
#
# Synthetic rule:
# - Large transaction
# - OR transaction during midnight/early morning
#
# NOTE:
# This is synthetic training data, not a real-world fraud rule.
# ------------------------------------------------------------

transactions_df["timestamp"] = pd.to_datetime(
    transactions_df["timestamp"]
)

transactions_df["is_suspicious"] = (
    (
        transactions_df["amount"]
        > 80000
    )
    |
    (
        transactions_df[
            "timestamp"
        ].dt.hour
        < 5
    )
).astype(int)


transactions_df.to_csv(
    os.path.join(
        TRANSACTIONS_DIR,
        "transactions.csv"
    ),
    index=False
)

print(
    "Transactions generated:",
    len(transactions_df)
)

print(
    "Transfer transactions:",
    (
        transactions_df[
            "transaction_type"
        ]
        == "Transfer"
    ).sum()
)

print(
    "\nSuspicious transaction distribution:"
)

print(
    transactions_df[
        "is_suspicious"
    ].value_counts()
)


# ============================================================
# 6. GENERATE ALERTS
# ============================================================

print("\n==========================================")
print("6. GENERATING ALERTS")
print("==========================================")

alerts = []

suspicious_transactions = transactions_df[
    transactions_df[
        "is_suspicious"
    ] == 1
]

for i in range(
    1,
    NUM_ALERTS + 1
):

    if len(suspicious_transactions) > 0:

        transaction = suspicious_transactions.sample(
            1
        ).iloc[0]

    else:

        transaction = transactions_df.sample(
            1
        ).iloc[0]

    alerts.append({

        "alert_id":
            f"ALERT{i:05d}",

        "customer_id":
            transaction["customer_id"],

        "transaction_id":
            transaction["transaction_id"],

        "alert_type":
            random.choice([
                "High Value Transaction",
                "Unusual Time",
                "Unusual Location",
                "Velocity Alert",
                "AML Alert"
            ]),

        "severity":
            random.choice([
                "LOW",
                "MEDIUM",
                "HIGH"
            ]),

        "created_at":
            transaction["timestamp"],

        "status":
            random.choice([
                "OPEN",
                "UNDER_REVIEW",
                "CLOSED"
            ])
    })


alerts_df = pd.DataFrame(
    alerts
)

alerts_df.to_csv(
    os.path.join(
        ALERTS_DIR,
        "alerts.csv"
    ),
    index=False
)

print(
    "Alerts generated:",
    len(alerts_df)
)


# ============================================================
# 7. GENERATE CASES
# ============================================================

print("\n==========================================")
print("7. GENERATING CASES")
print("==========================================")

cases = []

for i in range(
    1,
    NUM_CASES + 1
):

    customer = random.choice(
        customers
    )

    cases.append({

        "case_id":
            f"CASE{i:05d}",

        "customer_id":
            customer["customer_id"],

        "case_type":
            random.choice([
                "Fraud",
                "AML",
                "Suspicious Activity",
                "Account Takeover"
            ]),

        "priority":
            random.choice([
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL"
            ]),

        "status":
            random.choice([
                "OPEN",
                "INVESTIGATION",
                "CLOSED"
            ]),

        "created_at":
            fake.date_time_between(
                start_date="-1y",
                end_date="now"
            )
    })


cases_df = pd.DataFrame(
    cases
)

cases_df.to_csv(
    os.path.join(
        CASES_DIR,
        "cases.csv"
    ),
    index=False
)

print(
    "Cases generated:",
    len(cases_df)
)


# ============================================================
# 8. MACHINE LEARNING ENGINE
# ============================================================

print("\n==========================================")
print("8. MACHINE LEARNING ENGINE")
print("==========================================")

ml_df = transactions_df.copy()

ml_df["hour"] = (
    ml_df[
        "timestamp"
    ].dt.hour
)

ml_df["day_of_week"] = (
    ml_df[
        "timestamp"
    ].dt.dayofweek
)

ml_df["is_night"] = (
    (
        ml_df["hour"] < 5
    )
    |
    (
        ml_df["hour"] >= 22
    )
).astype(int)


feature_columns = [

    "amount",

    "hour",

    "day_of_week",

    "is_night",

    "location",

    "transaction_type",

    "payment_method",

    "currency"
]


X = ml_df[
    feature_columns
].copy()

y = ml_df[
    "is_suspicious"
].copy()


# One-hot encode categorical columns
X = pd.get_dummies(
    X,
    columns=[
        "location",
        "transaction_type",
        "payment_method",
        "currency"
    ]
)


# Train/test split
X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.20,

    random_state=42,

    stratify=y
)


# ============================================================
# LOGISTIC REGRESSION
# ============================================================

logistic_model = LogisticRegression(
    max_iter=1000
)

logistic_model.fit(
    X_train,
    y_train
)

logistic_predictions = (
    logistic_model.predict(
        X_test
    )
)


# ============================================================
# RANDOM FOREST
# ============================================================

rf_model = RandomForestClassifier(

    n_estimators=100,

    random_state=42,

    n_jobs=-1
)

rf_model.fit(
    X_train,
    y_train
)

rf_predictions = (
    rf_model.predict(
        X_test
    )
)


# ============================================================
# XGBOOST
# ============================================================

xgb_model = XGBClassifier(

    n_estimators=100,

    max_depth=6,

    learning_rate=0.1,

    random_state=42,

    eval_metric="logloss"
)

xgb_model.fit(
    X_train,
    y_train
)

xgb_predictions = (
    xgb_model.predict(
        X_test
    )
)


# ============================================================
# MODEL EVALUATION
# ============================================================

def evaluate_model(
    model_name,
    y_true,
    predictions
):

    accuracy = accuracy_score(
        y_true,
        predictions
    )

    precision = precision_score(
        y_true,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        predictions,
        zero_division=0
    )

    print(
        f"\n{model_name}"
    )

    print(
        f"Accuracy  : {accuracy:.4f}"
    )

    print(
        f"Precision : {precision:.4f}"
    )

    print(
        f"Recall    : {recall:.4f}"
    )

    print(
        f"F1 Score  : {f1:.4f}"
    )


evaluate_model(
    "Logistic Regression",
    y_test,
    logistic_predictions
)

evaluate_model(
    "Random Forest",
    y_test,
    rf_predictions
)

evaluate_model(
    "XGBoost",
    y_test,
    xgb_predictions
)


# ============================================================
# 9. TRANSACTION RISK ENGINE
# ============================================================

print("\n==========================================")
print("9. TRANSACTION RISK ENGINE")
print("==========================================")

fraud_probabilities = (
    xgb_model.predict_proba(
        X_test
    )[:, 1]
)

risk_scores = (
    fraud_probabilities
    * 100
)


def get_risk_level(score):

    if score >= 70:
        return "HIGH"

    elif score >= 30:
        return "MEDIUM"

    else:
        return "LOW"


risk_results = pd.DataFrame({

    "transaction_id":
        ml_df.loc[
            X_test.index,
            "transaction_id"
        ].values,

    "fraud_probability":
        fraud_probabilities,

    "risk_score":
        risk_scores
})


risk_results[
    "risk_level"
] = risk_results[
    "risk_score"
].apply(
    get_risk_level
)


risk_results.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "risk_results.csv"
    ),

    index=False
)


print(
    "Transaction risk results saved."
)


# ============================================================
# 10. CUSTOMER BEHAVIOR ENGINE
# ============================================================

print("\n==========================================")
print("10. CUSTOMER BEHAVIOR ENGINE")
print("==========================================")

behavior_df = transactions_df.copy()

behavior_df["timestamp"] = pd.to_datetime(
    behavior_df["timestamp"]
)

behavior_df["hour"] = (
    behavior_df[
        "timestamp"
    ].dt.hour
)


# ------------------------------------------------------------
# CUSTOMER BASIC PROFILE
# ------------------------------------------------------------

customer_profiles = (

    behavior_df
    .groupby(
        "customer_id"
    )
    .agg(

        average_amount=(
            "amount",
            "mean"
        ),

        median_amount=(
            "amount",
            "median"
        ),

        transaction_frequency=(
            "transaction_id",
            "count"
        )
    )

    .reset_index()
)


# ------------------------------------------------------------
# TYPICAL MERCHANT
# ------------------------------------------------------------

typical_merchant = (

    behavior_df
    .groupby(
        "customer_id"
    )["merchant_id"]
    .agg(
        lambda x:
        x.mode().iloc[0]
        if not x.mode().empty
        else None
    )
    .reset_index(
        name="typical_merchant"
    )
)


# ------------------------------------------------------------
# TYPICAL LOCATION
# ------------------------------------------------------------

typical_location = (

    behavior_df
    .groupby(
        "customer_id"
    )["location"]
    .agg(
        lambda x:
        x.mode().iloc[0]
        if not x.mode().empty
        else None
    )
    .reset_index(
        name="typical_location"
    )
)


# ------------------------------------------------------------
# TYPICAL DEVICE
# ------------------------------------------------------------

typical_device = (

    behavior_df
    .groupby(
        "customer_id"
    )["device_id"]
    .agg(
        lambda x:
        x.mode().iloc[0]
        if not x.mode().empty
        else None
    )
    .reset_index(
        name="typical_device"
    )
)


# ------------------------------------------------------------
# TYPICAL HOUR
# ------------------------------------------------------------

typical_hour = (

    behavior_df
    .groupby(
        "customer_id"
    )["hour"]
    .agg(
        lambda x:
        x.mode().iloc[0]
        if not x.mode().empty
        else None
    )
    .reset_index(
        name="typical_hour"
    )
)


# ------------------------------------------------------------
# MERGE CUSTOMER PROFILE
# ------------------------------------------------------------

customer_profiles = (
    customer_profiles
    .merge(
        typical_merchant,
        on="customer_id",
        how="left"
    )
    .merge(
        typical_location,
        on="customer_id",
        how="left"
    )
    .merge(
        typical_device,
        on="customer_id",
        how="left"
    )
    .merge(
        typical_hour,
        on="customer_id",
        how="left"
    )
)


customer_profiles.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "customer_behavior_profiles.csv"
    ),

    index=False
)


# ============================================================
# CUSTOMER BEHAVIOR DEVIATIONS
# ============================================================

behavior_analysis = (

    behavior_df
    .merge(
        customer_profiles,
        on="customer_id",
        how="left"
    )
)


# ------------------------------------------------------------
# AMOUNT DEVIATION
# ------------------------------------------------------------

behavior_analysis[
    "amount_deviation"
] = (

    behavior_analysis[
        "amount"
    ]

    /

    behavior_analysis[
        "average_amount"
    ]

)


# ------------------------------------------------------------
# LOCATION DEVIATION
# ------------------------------------------------------------

behavior_analysis[
    "location_deviation"
] = (

    behavior_analysis[
        "location"
    ]

    !=

    behavior_analysis[
        "typical_location"
    ]

).astype(int)


# ------------------------------------------------------------
# MERCHANT DEVIATION
# ------------------------------------------------------------

behavior_analysis[
    "merchant_deviation"
] = (

    behavior_analysis[
        "merchant_id"
    ]

    !=

    behavior_analysis[
        "typical_merchant"
    ]

).astype(int)


# ------------------------------------------------------------
# TIME DEVIATION
# ------------------------------------------------------------

behavior_analysis[
    "time_deviation"
] = (

    behavior_analysis[
        "hour"
    ]

    !=

    behavior_analysis[
        "typical_hour"
    ]

).astype(int)


# ============================================================
# VELOCITY ANALYSIS
# ============================================================

print(
    "Calculating transaction velocity..."
)

behavior_analysis = (
    behavior_analysis
    .sort_values(
        [
            "customer_id",
            "timestamp"
        ]
    )
)


# Use rolling one-hour count per customer
velocity_series = (

    behavior_analysis
    .set_index("timestamp")
    .groupby("customer_id")[
        "transaction_id"
    ]
    .rolling("1h")
    .count()
)


velocity_series = (
    velocity_series
    .reset_index()
)


velocity_series.rename(
    columns={
        "transaction_id":
            "transactions_last_hour"
    },
    inplace=True
)


# Merge using customer + timestamp
behavior_analysis = (
    behavior_analysis
    .merge(
        velocity_series[
            [
                "customer_id",
                "timestamp",
                "transactions_last_hour"
            ]
        ],
        on=[
            "customer_id",
            "timestamp"
        ],
        how="left"
    )
)


behavior_analysis[
    "transactions_last_hour"
] = (
    behavior_analysis[
        "transactions_last_hour"
    ]
    .fillna(0)
)


behavior_analysis[
    "velocity_deviation"
] = (

    behavior_analysis[
        "transactions_last_hour"
    ]

    /

    behavior_analysis[
        "transaction_frequency"
    ].replace(
        0,
        1
    )

)


behavior_analysis.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "customer_behavior_analysis.csv"
    ),

    index=False
)


print(
    "Customer behavior analysis saved."
)


# ============================================================
# 11. ISOLATION FOREST ANOMALY DETECTION
# ============================================================

print("\n==========================================")
print("11. ISOLATION FOREST ANOMALY DETECTION")
print("==========================================")

anomaly_features = behavior_analysis[
    [
        "amount",
        "amount_deviation",
        "location_deviation",
        "merchant_deviation",
        "time_deviation",
        "velocity_deviation"
    ]
].copy()


anomaly_features = (

    anomaly_features

    .replace(
        [
            float("inf"),
            float("-inf")
        ],
        0
    )

    .fillna(0)
)


isolation_forest = IsolationForest(

    n_estimators=100,

    contamination=0.05,

    random_state=42
)


isolation_forest.fit(
    anomaly_features
)


behavior_analysis[
    "anomaly_prediction"
] = (

    isolation_forest.predict(
        anomaly_features
    )

)


behavior_analysis[
    "is_anomaly"
] = (

    behavior_analysis[
        "anomaly_prediction"
    ]

    == -1

).astype(int)


behavior_analysis[
    "anomaly_score"
] = (

    -isolation_forest.score_samples(
        anomaly_features
    )

)


behavior_analysis.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "anomaly_detection_results.csv"
    ),

    index=False
)


print(
    "Anomaly detection completed."
)

print(
    "Anomalies detected:",
    behavior_analysis[
        "is_anomaly"
    ].sum()
)


# ============================================================
# 12. AML GRAPH ENGINE
# ============================================================

print("\n==========================================")
print("12. AML GRAPH ENGINE")
print("==========================================")

print(
    "Building financial crime graph..."
)


# ------------------------------------------------------------
# IMPORTANT:
#
# MultiDiGraph is used because:
#
# Account A -> Account B
#
# can happen multiple times.
#
# Direction is important for AML.
# ------------------------------------------------------------

G = nx.MultiDiGraph()


# ============================================================
# CUSTOMER NODES
# ============================================================

for _, row in customers_df.iterrows():

    G.add_node(

        row["customer_id"],

        node_type="Customer",

        name=row["name"],

        city=row["city"],

        occupation=row["occupation"]
    )


# ============================================================
# ACCOUNT NODES
# ============================================================

for _, row in accounts_df.iterrows():

    G.add_node(

        row["account_id"],

        node_type="Account",

        account_type=row["account_type"],

        balance=row["balance"]
    )

    # Customer owns account
    G.add_edge(

        row["customer_id"],

        row["account_id"],

        relationship="OWNS"
    )


# ============================================================
# MERCHANT NODES
# ============================================================

for _, row in merchants_df.iterrows():

    G.add_node(

        row["merchant_id"],

        node_type="Merchant",

        merchant_name=row[
            "merchant_name"
        ],

        category=row[
            "category"
        ]
    )


# ============================================================
# DEVICE NODES
# ============================================================

for _, row in devices_df.iterrows():

    G.add_node(

        row["device_id"],

        node_type="Device",

        customer_id=row[
            "customer_id"
        ],

        device_type=row[
            "device_type"
        ],

        operating_system=row[
            "operating_system"
        ]
    )


# ============================================================
# TRANSACTION NODES + RELATIONSHIPS
# ============================================================

for _, row in transactions_df.iterrows():

    transaction_id = (
        row["transaction_id"]
    )

    source_account = (
        row["account_id"]
    )

    destination_account = (
        row[
            "destination_account_id"
        ]
    )

    merchant_id = (
        row["merchant_id"]
    )

    device_id = (
        row["device_id"]
    )


    # --------------------------------------------------------
    # TRANSACTION NODE
    # --------------------------------------------------------

    G.add_node(

        transaction_id,

        node_type="Transaction",

        amount=float(
            row["amount"]
        ),

        timestamp=str(
            row["timestamp"]
        ),

        transaction_type=(
            row["transaction_type"]
        ),

        is_suspicious=int(
            row["is_suspicious"]
        )
    )


    # --------------------------------------------------------
    # ACCOUNT -> TRANSACTION
    # --------------------------------------------------------

    G.add_edge(

        source_account,

        transaction_id,

        relationship="MADE"
    )


    # --------------------------------------------------------
    # TRANSACTION -> MERCHANT
    # --------------------------------------------------------

    G.add_edge(

        transaction_id,

        merchant_id,

        relationship="PAID_TO"
    )


    # --------------------------------------------------------
    # TRANSACTION -> DEVICE
    # --------------------------------------------------------

    G.add_edge(

        transaction_id,

        device_id,

        relationship="USED_DEVICE"
    )


    # --------------------------------------------------------
    # TRANSFER:
    #
    # SOURCE ACCOUNT
    #       |
    #       v
    # TRANSACTION
    #       |
    #       v
    # DESTINATION ACCOUNT
    # --------------------------------------------------------

    if pd.notna(
        destination_account
    ):

        G.add_edge(

            transaction_id,

            destination_account,

            relationship="TRANSFER_TO"
        )


# ============================================================
# SAVE GRAPH
# ============================================================

graph_path = os.path.join(

    TRANSACTIONS_DIR,

    "aml_graph.gpickle"
)


with open(
    graph_path,
    "wb"
) as f:

    pickle.dump(
        G,
        f
    )


print(
    "AML graph saved:"
)

print(
    graph_path
)

print(
    "Graph nodes:",
    G.number_of_nodes()
)

print(
    "Graph edges:",
    G.number_of_edges()
)


# ============================================================
# 13. SHARED DEVICE DETECTION
# ============================================================

print("\n==========================================")
print("13. SHARED DEVICE DETECTION")
print("==========================================")

device_usage = (

    transactions_df

    .groupby(
        "device_id"
    )["customer_id"]

    .nunique()

    .reset_index(
        name="customer_count"
    )
)


shared_devices = device_usage[
    device_usage[
        "customer_count"
    ] > 1
].copy()


shared_device_df = (

    transactions_df[
        transactions_df[
            "device_id"
        ].isin(
            shared_devices[
                "device_id"
            ]
        )
    ]

    .groupby(
        "device_id"
    )

    .agg(

        customer_count=(
            "customer_id",
            "nunique"
        ),

        customers=(
            "customer_id",
            lambda x:
            ",".join(
                sorted(
                    x.astype(str)
                    .unique()
                )
            )
        ),

        transaction_count=(
            "transaction_id",
            "count"
        )
    )

    .reset_index()
)


shared_device_df.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "shared_devices.csv"
    ),

    index=False
)


print(
    "Shared devices detected:",
    len(shared_device_df)
)


# ============================================================
# 14. ACCOUNT CONNECTION ENGINE
# ============================================================

print("\n==========================================")
print("14. ACCOUNT CONNECTION ENGINE")
print("==========================================")


def get_connected_entities(
    account_id
):

    if account_id not in G:

        return {

            "account_id":
                account_id,

            "customer": [],

            "accounts": [],

            "transactions": [],

            "merchants": [],

            "devices": []
        }


    connected = {

        "account_id":
            account_id,

        "customer": [],

        "accounts": [],

        "transactions": [],

        "merchants": [],

        "devices": []
    }


    # --------------------------------------------------------
    # Find nodes reachable within a small neighborhood
    # --------------------------------------------------------

    for neighbor in G.neighbors(
        account_id
    ):

        node_type = G.nodes[
            neighbor
        ].get(
            "node_type"
        )


        if node_type == "Customer":

            connected[
                "customer"
            ].append(
                neighbor
            )

        elif node_type == "Transaction":

            connected[
                "transactions"
            ].append(
                neighbor
            )


    # --------------------------------------------------------
    # Transaction relationships
    # --------------------------------------------------------

    for transaction_id in connected[
        "transactions"
    ]:

        for neighbor in G.neighbors(
            transaction_id
        ):

            node_type = G.nodes[
                neighbor
            ].get(
                "node_type"
            )

            if node_type == "Merchant":

                connected[
                    "merchants"
                ].append(
                    neighbor
                )

            elif node_type == "Device":

                connected[
                    "devices"
                ].append(
                    neighbor
                )

            elif node_type == "Account":

                connected[
                    "accounts"
                ].append(
                    neighbor
                )


    # Remove duplicates
    for key in connected:

        if isinstance(
            connected[key],
            list
        ):

            connected[key] = sorted(
                list(
                    set(
                        connected[key]
                    )
                )
            )


    return connected


# ============================================================
# 15. TRANSFER GRAPH
# ============================================================

print("\n==========================================")
print("15. BUILDING ACCOUNT TRANSFER GRAPH")
print("==========================================")

transfer_graph = nx.MultiDiGraph()


for _, row in transactions_df.iterrows():

    if (
        row["transaction_type"]
        == "Transfer"
        and
        pd.notna(
            row[
                "destination_account_id"
            ]
        )
    ):

        source = row[
            "account_id"
        ]

        destination = row[
            "destination_account_id"
        ]

        transfer_graph.add_edge(

            source,

            destination,

            transaction_id=(
                row["transaction_id"]
            ),

            amount=float(
                row["amount"]
            ),

            timestamp=str(
                row["timestamp"]
            ),

            is_suspicious=int(
                row["is_suspicious"]
            )
        )


print(
    "Transfer graph nodes:",
    transfer_graph.number_of_nodes()
)

print(
    "Transfer graph edges:",
    transfer_graph.number_of_edges()
)


# ============================================================
# 16. FAN-IN DETECTION
#
# Many accounts -> one account
# ============================================================

print("\n==========================================")
print("16. FAN-IN DETECTION")
print("==========================================")

fan_in_results = []


for account in transfer_graph.nodes():

    incoming_accounts = set(
        transfer_graph.predecessors(
            account
        )
    )


    if len(incoming_accounts) >= 3:

        fan_in_results.append({

            "account_id":
                account,

            "incoming_account_count":
                len(
                    incoming_accounts
                ),

            "incoming_accounts":
                ",".join(
                    sorted(
                        incoming_accounts
                    )
                )
        })


fan_in_df = pd.DataFrame(
    fan_in_results
)


fan_in_df.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "fan_in_results.csv"
    ),

    index=False
)


print(
    "Fan-in accounts detected:",
    len(fan_in_df)
)


# ============================================================
# 17. FAN-OUT DETECTION
#
# One account -> many accounts
# ============================================================

print("\n==========================================")
print("17. FAN-OUT DETECTION")
print("==========================================")

fan_out_results = []


for account in transfer_graph.nodes():

    outgoing_accounts = set(
        transfer_graph.successors(
            account
        )
    )


    if len(outgoing_accounts) >= 3:

        fan_out_results.append({

            "account_id":
                account,

            "outgoing_account_count":
                len(
                    outgoing_accounts
                ),

            "outgoing_accounts":
                ",".join(
                    sorted(
                        outgoing_accounts
                    )
                )
        })


fan_out_df = pd.DataFrame(
    fan_out_results
)


fan_out_df.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "fan_out_results.csv"
    ),

    index=False
)


print(
    "Fan-out accounts detected:",
    len(fan_out_df)
)


# ============================================================
# 18. SUSPICIOUS TRANSFER EDGES
# ============================================================

print("\n==========================================")
print("18. SUSPICIOUS TRANSFER EDGES")
print("==========================================")

suspicious_transfer_edges = []


for source, destination, key, data in (
    transfer_graph.edges(
        keys=True,
        data=True
    )
):

    if (
        data.get(
            "is_suspicious",
            0
        )
        == 1
    ):

        suspicious_transfer_edges.append({

            "source_account":
                source,

            "destination_account":
                destination,

            "transaction_id":
                data.get(
                    "transaction_id"
                ),

            "amount":
                data.get(
                    "amount"
                ),

            "timestamp":
                data.get(
                    "timestamp"
                )
        })


suspicious_transfer_df = pd.DataFrame(
    suspicious_transfer_edges
)


suspicious_transfer_df.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "suspicious_transfer_edges.csv"
    ),

    index=False
)


print(
    "Suspicious transfer edges:",
    len(
        suspicious_transfer_df
    )
)


# ============================================================
# 19. CIRCULAR TRANSFER DETECTION
#
# Example:
#
# A -> B
# B -> C
# C -> A
# ============================================================

print("\n==========================================")
print("19. CIRCULAR TRANSFER DETECTION")
print("==========================================")

# Convert MultiDiGraph to simple DiGraph
# for cycle analysis.

simple_transfer_graph = nx.DiGraph()


for source, destination in transfer_graph.edges():

    simple_transfer_graph.add_edge(
        source,
        destination
    )


circular_flows = []


try:

    cycles = nx.simple_cycles(
        simple_transfer_graph
    )

    cycle_count = 0

    for cycle in cycles:

        # Limit output to manageable number
        if cycle_count >= 500:
            break

        if len(cycle) >= 3:

            circular_flows.append({

                "cycle_id":
                    f"CYCLE{cycle_count + 1:05d}",

                "account_count":
                    len(cycle),

                "accounts":
                    " -> ".join(
                        cycle + [
                            cycle[0]
                        ]
                    )
            })

            cycle_count += 1

except Exception as e:

    print(
        "Cycle detection warning:",
        e
    )


circular_flows_df = pd.DataFrame(
    circular_flows
)


circular_flows_df.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "circular_flows.csv"
    ),

    index=False
)


print(
    "Circular flows detected:",
    len(
        circular_flows_df
    )
)


# ============================================================
# 20. SUSPICIOUS TRANSACTION PATH DETECTION
#
# We look for paths where:
#
# Account A -> Account B -> Account C
#
# and at least one transfer on the path
# is suspicious.
# ============================================================

print("\n==========================================")
print("20. SUSPICIOUS TRANSACTION PATH DETECTION")
print("==========================================")

suspicious_paths = []

# Identify risky accounts first
risky_accounts = set()


for source, destination, data in (
    transfer_graph.edges(
        data=True
    )
):

    if (
        data.get(
            "is_suspicious",
            0
        )
        == 1
    ):

        risky_accounts.add(
            source
        )

        risky_accounts.add(
            destination
        )


# Limit path search to short paths
# to keep computation practical.

for source in risky_accounts:

    if source not in transfer_graph:
        continue

    try:

        paths = nx.single_source_shortest_path(
            transfer_graph,
            source,
            cutoff=3
        )

    except Exception:

        continue


    for destination, path in paths.items():

        if (
            destination == source
            or
            len(path) < 3
        ):
            continue


        path_has_suspicious_edge = False

        path_transactions = []

        # Examine every edge in path
        for i in range(
            len(path) - 1
        ):

            current_account = (
                path[i]
            )

            next_account = (
                path[i + 1]
            )

            edge_data = transfer_graph.get_edge_data(

                current_account,

                next_account
            )


            if edge_data is None:
                continue


            for key, data in edge_data.items():

                transaction_id = data.get(
                    "transaction_id"
                )

                path_transactions.append(
                    transaction_id
                )

                if (
                    data.get(
                        "is_suspicious",
                        0
                    )
                    == 1
                ):

                    path_has_suspicious_edge = True


        if path_has_suspicious_edge:

            suspicious_paths.append({

                "source_account":
                    source,

                "destination_account":
                    destination,

                "path_length":
                    len(path) - 1,

                "account_path":
                    " -> ".join(
                        path
                    ),

                "transactions":
                    ",".join(
                        path_transactions
                    )
            })


# Remove duplicate paths
suspicious_paths_df = pd.DataFrame(
    suspicious_paths
)


if not suspicious_paths_df.empty:

    suspicious_paths_df = (
        suspicious_paths_df
        .drop_duplicates(
            subset=[
                "account_path"
            ]
        )
    )


suspicious_paths_df.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "suspicious_paths.csv"
    ),

    index=False
)


print(
    "Suspicious paths detected:",
    len(
        suspicious_paths_df
    )
)


# ============================================================
# 21. SUSPICIOUS CLUSTER DETECTION
#
# We convert the transfer graph to an undirected graph
# and use NetworkX's built-in greedy modularity algorithm.
# ============================================================

print("\n==========================================")
print("21. SUSPICIOUS CLUSTER DETECTION")
print("==========================================")

cluster_graph = (
    simple_transfer_graph
    .to_undirected()
)


suspicious_clusters = []


if cluster_graph.number_of_nodes() > 0:

    try:

        communities = (
            nx.community
            .greedy_modularity_communities(
                cluster_graph
            )
        )


        cluster_id = 1


        for community in communities:

            community = set(
                community
            )


            # Only keep meaningful clusters
            if len(community) < 2:
                continue


            suspicious_count = 0


            for account in community:

                if account in risky_accounts:

                    suspicious_count += 1


            # A cluster is considered suspicious
            # when it contains at least one risky account.

            if suspicious_count > 0:

                suspicious_clusters.append({

                    "cluster_id":
                        f"CLUSTER{cluster_id:05d}",

                    "cluster_size":
                        len(
                            community
                        ),

                    "suspicious_account_count":
                        suspicious_count,

                    "suspicious_ratio":
                        suspicious_count
                        /
                        len(community),

                    "accounts":
                        ",".join(
                            sorted(
                                community
                            )
                        )
                })


                cluster_id += 1


    except Exception as e:

        print(
            "Cluster detection warning:",
            e
        )


suspicious_clusters_df = pd.DataFrame(
    suspicious_clusters
)


suspicious_clusters_df.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "suspicious_clusters.csv"
    ),

    index=False
)


print(
    "Suspicious clusters detected:",
    len(
        suspicious_clusters_df
    )
)


# ============================================================
# 22. NETWORK RISK SCORE
# ============================================================

print("\n==========================================")
print("22. NETWORK RISK SCORING")
print("==========================================")


# ------------------------------------------------------------
# Suspicious transaction count per account
# ------------------------------------------------------------

suspicious_transaction_counts = (

    transactions_df[
        transactions_df[
            "is_suspicious"
        ] == 1
    ]

    .groupby(
        "account_id"
    )

    .size()

    .to_dict()
)


# ------------------------------------------------------------
# Shared device accounts
# ------------------------------------------------------------

shared_device_accounts = {}


for _, row in shared_device_df.iterrows():

    device_id = row[
        "device_id"
    ]

    customers_using_device = (
        transactions_df[
            transactions_df[
                "device_id"
            ] == device_id
        ]["customer_id"]
        .unique()
        .tolist()
    )


    for customer_id in (
        customers_using_device
    ):

        account_ids = (
            accounts_df[
                accounts_df[
                    "customer_id"
                ] == customer_id
            ]["account_id"]
            .tolist()
        )


        for account_id in account_ids:

            shared_device_accounts[
                account_id
            ] = (
                shared_device_accounts.get(
                    account_id,
                    0
                )
                + 1
            )


# ------------------------------------------------------------
# Suspicious path count
# ------------------------------------------------------------

suspicious_path_counts = {}


if not suspicious_paths_df.empty:

    for account_path in (
        suspicious_paths_df[
            "account_path"
        ]
    ):

        accounts_in_path = (
            account_path.split(
                " -> "
            )
        )

        for account_id in (
            accounts_in_path
        ):

            suspicious_path_counts[
                account_id
            ] = (

                suspicious_path_counts
                .get(
                    account_id,
                    0
                )
                + 1
            )


# ------------------------------------------------------------
# Circular account count
# ------------------------------------------------------------

circular_account_counts = {}


if not circular_flows_df.empty:

    for accounts_string in (
        circular_flows_df[
            "accounts"
        ]
    ):

        accounts_in_cycle = (
            accounts_string
            .split(" -> ")
        )

        # Last element is same as first
        accounts_in_cycle = list(
            set(
                accounts_in_cycle
            )
        )

        for account_id in (
            accounts_in_cycle
        ):

            circular_account_counts[
                account_id
            ] = (

                circular_account_counts
                .get(
                    account_id,
                    0
                )
                + 1
            )


# ------------------------------------------------------------
# Fan-in map
# ------------------------------------------------------------

fan_in_map = {}


if not fan_in_df.empty:

    for _, row in fan_in_df.iterrows():

        fan_in_map[
            row["account_id"]
        ] = row[
            "incoming_account_count"
        ]


# ------------------------------------------------------------
# Fan-out map
# ------------------------------------------------------------

fan_out_map = {}


if not fan_out_df.empty:

    for _, row in fan_out_df.iterrows():

        fan_out_map[
            row["account_id"]
        ] = row[
            "outgoing_account_count"
        ]


# ------------------------------------------------------------
# Cluster map
# ------------------------------------------------------------

cluster_map = {}


if not suspicious_clusters_df.empty:

    for _, row in (
        suspicious_clusters_df.iterrows()
    ):

        cluster_id = row[
            "cluster_id"
        ]

        accounts_in_cluster = (
            row["accounts"]
            .split(",")
        )

        for account_id in (
            accounts_in_cluster
        ):

            cluster_map[
                account_id
            ] = {

                "cluster_id":
                    cluster_id,

                "cluster_size":
                    int(
                        row[
                            "cluster_size"
                        ]
                    ),

                "suspicious_account_count":
                    int(
                        row[
                            "suspicious_account_count"
                        ]
                    )
            }


# ============================================================
# CALCULATE NETWORK RISK
# ============================================================

network_risk_results = []


for account_id in (
    accounts_df[
        "account_id"
    ]
):

    suspicious_transactions = (
        suspicious_transaction_counts
        .get(
            account_id,
            0
        )
    )

    shared_devices_count = (
        shared_device_accounts
        .get(
            account_id,
            0
        )
    )

    suspicious_paths_count = (
        suspicious_path_counts
        .get(
            account_id,
            0
        )
    )

    circular_count = (
        circular_account_counts
        .get(
            account_id,
            0
        )
    )

    fan_in_count = (
        fan_in_map
        .get(
            account_id,
            0
        )
    )

    fan_out_count = (
        fan_out_map
        .get(
            account_id,
            0
        )
    )


    # --------------------------------------------------------
    # NETWORK RISK SCORE
    #
    # Maximum theoretical score is capped at 100.
    # --------------------------------------------------------

    network_score = 0


    # Suspicious transactions
    network_score += min(
        suspicious_transactions * 2,
        30
    )


    # Shared devices
    network_score += min(
        shared_devices_count * 10,
        20
    )


    # Suspicious paths
    network_score += min(
        suspicious_paths_count * 5,
        20
    )


    # Circular transfers
    network_score += min(
        circular_count * 15,
        30
    )


    # Fan-in
    if fan_in_count >= 3:

        network_score += min(
            fan_in_count * 2,
            15
        )


    # Fan-out
    if fan_out_count >= 3:

        network_score += min(
            fan_out_count * 2,
            15
        )


    network_score = min(
        network_score,
        100
    )


    network_risk_level = (
        get_risk_level(
            network_score
        )
    )


    cluster_id = None
    cluster_size = 0


    if account_id in cluster_map:

        cluster_id = (
            cluster_map[
                account_id
            ]["cluster_id"]
        )

        cluster_size = (
            cluster_map[
                account_id
            ]["cluster_size"]
        )


    network_risk_results.append({

        "account_id":
            account_id,

        "suspicious_transaction_count":
            suspicious_transactions,

        "shared_device_count":
            shared_devices_count,

        "suspicious_path_count":
            suspicious_paths_count,

        "circular_flow_count":
            circular_count,

        "fan_in_count":
            fan_in_count,

        "fan_out_count":
            fan_out_count,

        "cluster_id":
            cluster_id,

        "cluster_size":
            cluster_size,

        "network_risk_score":
            network_score,

        "network_risk_level":
            network_risk_level
    })


network_risk_df = pd.DataFrame(
    network_risk_results
)


network_risk_df.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "network_risk_results.csv"
    ),

    index=False
)


print(
    "Network risk scoring completed."
)


# ============================================================
# 23. ACCOUNT INVESTIGATION ENGINE
#
# This is the function we can later connect to:
#
# - CLI
# - FastAPI
# - Streamlit
# - Agent
# - Neo4j
# ============================================================

print("\n==========================================")
print("23. ACCOUNT INVESTIGATION ENGINE")
print("==========================================")


def investigate_account(
    account_id
):

    result = {

        "account_id":
            account_id,

        "customer": [],

        "connected_accounts": [],

        "transactions": [],

        "merchants": [],

        "devices": [],

        "suspicious_transactions": [],

        "suspicious_paths": [],

        "shared_devices": [],

        "circular_flows": [],

        "cluster": None,

        "network_risk_score": 0,

        "network_risk_level":
            "LOW"
    }


    # --------------------------------------------------------
    # Basic connected entities
    # --------------------------------------------------------

    connected = get_connected_entities(
        account_id
    )


    result[
        "customer"
    ] = connected[
        "customer"
    ]

    result[
        "connected_accounts"
    ] = connected[
        "accounts"
    ]

    result[
        "transactions"
    ] = connected[
        "transactions"
    ]

    result[
        "merchants"
    ] = connected[
        "merchants"
    ]

    result[
        "devices"
    ] = connected[
        "devices"
    ]


    # --------------------------------------------------------
    # Suspicious transactions
    # --------------------------------------------------------

    account_transactions = (
        transactions_df[
            transactions_df[
                "account_id"
            ] == account_id
        ]
    )


    suspicious_account_transactions = (
        account_transactions[
            account_transactions[
                "is_suspicious"
            ] == 1
        ]
    )


    result[
        "suspicious_transactions"
    ] = (
        suspicious_account_transactions[
            "transaction_id"
        ]
        .tolist()
    )


    # --------------------------------------------------------
    # Shared devices
    # --------------------------------------------------------

    account_devices = set(

        account_transactions[
            "device_id"
        ]
        .dropna()
        .tolist()

    )


    for device_id in account_devices:

        users = (

            transactions_df[
                transactions_df[
                    "device_id"
                ] == device_id
            ]["customer_id"]

            .dropna()

            .unique()

            .tolist()
        )


        if len(users) > 1:

            result[
                "shared_devices"
            ].append({

                "device_id":
                    device_id,

                "customer_count":
                    len(users),

                "customers":
                    users
            })


    # --------------------------------------------------------
    # Suspicious paths
    # --------------------------------------------------------

    if not suspicious_paths_df.empty:

        mask = (
            suspicious_paths_df[
                "account_path"
            ]
            .str.contains(
                account_id,
                regex=False
            )
        )

        result[
            "suspicious_paths"
        ] = (

            suspicious_paths_df[
                mask
            ]
            .to_dict(
                orient="records"
            )

        )


    # --------------------------------------------------------
    # Circular flows
    # --------------------------------------------------------

    if not circular_flows_df.empty:

        mask = (
            circular_flows_df[
                "accounts"
            ]
            .str.contains(
                account_id,
                regex=False
            )
        )

        result[
            "circular_flows"
        ] = (

            circular_flows_df[
                mask
            ]
            .to_dict(
                orient="records"
            )

        )


    # --------------------------------------------------------
    # Cluster
    # --------------------------------------------------------

    if account_id in cluster_map:

        result[
            "cluster"
        ] = cluster_map[
            account_id
        ]


    # --------------------------------------------------------
    # Network risk
    # --------------------------------------------------------

    risk_row = network_risk_df[
        network_risk_df[
            "account_id"
        ] == account_id
    ]


    if not risk_row.empty:

        row = risk_row.iloc[0]

        result[
            "network_risk_score"
        ] = float(
            row[
                "network_risk_score"
            ]
        )

        result[
            "network_risk_level"
        ] = row[
            "network_risk_level"
        ]


    return result


# ============================================================
# 24. CREATE ACCOUNT INVESTIGATION DATASET
# ============================================================

print("\n==========================================")
print("24. CREATING ACCOUNT INVESTIGATION RESULTS")
print("==========================================")

investigation_results = []


for account_id in (
    accounts_df[
        "account_id"
    ]
):

    investigation = (
        investigate_account(
            account_id
        )
    )


    investigation_results.append({

        "account_id":
            account_id,

        "customer":
            ",".join(
                investigation[
                    "customer"
                ]
            ),

        "connected_account_count":
            len(
                investigation[
                    "connected_accounts"
                ]
            ),

        "transaction_count":
            len(
                investigation[
                    "transactions"
                ]
            ),

        "merchant_count":
            len(
                investigation[
                    "merchants"
                ]
            ),

        "device_count":
            len(
                investigation[
                    "devices"
                ]
            ),

        "suspicious_transaction_count":
            len(
                investigation[
                    "suspicious_transactions"
                ]
            ),

        "suspicious_path_count":
            len(
                investigation[
                    "suspicious_paths"
                ]
            ),

        "shared_device_count":
            len(
                investigation[
                    "shared_devices"
                ]
            ),

        "circular_flow_count":
            len(
                investigation[
                    "circular_flows"
                ]
            ),

        "cluster_id":
            (
                investigation[
                    "cluster"
                ]["cluster_id"]
                if investigation[
                    "cluster"
                ]
                else None
            ),

        "cluster_size":
            (
                investigation[
                    "cluster"
                ]["cluster_size"]
                if investigation[
                    "cluster"
                ]
                else 0
            ),

        "network_risk_score":
            investigation[
                "network_risk_score"
            ],

        "network_risk_level":
            investigation[
                "network_risk_level"
            ]
    })


account_investigation_df = pd.DataFrame(
    investigation_results
)


account_investigation_df.to_csv(

    os.path.join(
        TRANSACTIONS_DIR,
        "account_investigation_results.csv"
    ),

    index=False
)


print(
    "Account investigation results saved."
)


# ============================================================
# 25. SHOW SAMPLE INVESTIGATION
# ============================================================

print("\n==========================================")
print("25. SAMPLE ACCOUNT INVESTIGATION")
print("==========================================")

sample_account = (
    accounts_df[
        "account_id"
    ].iloc[0]
)


sample_result = (
    investigate_account(
        sample_account
    )
)


print(
    "\nAccount:",
    sample_account
)

print(
    "Customer:",
    sample_result[
        "customer"
    ]
)

print(
    "Connected accounts:",
    len(
        sample_result[
            "connected_accounts"
        ]
    )
)

print(
    "Transactions:",
    len(
        sample_result[
            "transactions"
        ]
    )
)

print(
    "Merchants:",
    len(
        sample_result[
            "merchants"
        ]
    )
)

print(
    "Devices:",
    len(
        sample_result[
            "devices"
        ]
    )
)

print(
    "Suspicious transactions:",
    len(
        sample_result[
            "suspicious_transactions"
        ]
    )
)

print(
    "Suspicious paths:",
    len(
        sample_result[
            "suspicious_paths"
        ]
    )
)

print(
    "Shared devices:",
    len(
        sample_result[
            "shared_devices"
        ]
    )
)

print(
    "Circular flows:",
    len(
        sample_result[
            "circular_flows"
        ]
    )
)

print(
    "Cluster:",
    sample_result[
        "cluster"
    ]
)

print(
    "Network risk score:",
    sample_result[
        "network_risk_score"
    ]
)

print(
    "Network risk level:",
    sample_result[
        "network_risk_level"
    ]
)


# ============================================================
# 26. FINAL OUTPUT SUMMARY
# ============================================================

print("\n")
print("============================================================")
print("              FINAGENT PIPELINE COMPLETED")
print("============================================================")

print("\nGenerated files:")

print(
    "1.  customers/customers.csv"
)

print(
    "2.  accounts/accounts.csv"
)

print(
    "3.  transactions/transactions.csv"
)

print(
    "4.  transactions/risk_results.csv"
)

print(
    "5.  transactions/customer_behavior_profiles.csv"
)

print(
    "6.  transactions/customer_behavior_analysis.csv"
)

print(
    "7.  transactions/anomaly_detection_results.csv"
)

print(
    "8.  transactions/aml_graph.gpickle"
)

print(
    "9.  transactions/shared_devices.csv"
)

print(
    "10. transactions/fan_in_results.csv"
)

print(
    "11. transactions/fan_out_results.csv"
)

print(
    "12. transactions/suspicious_transfer_edges.csv"
)

print(
    "13. transactions/circular_flows.csv"
)

print(
    "14. transactions/suspicious_paths.csv"
)

print(
    "15. transactions/suspicious_clusters.csv"
)

print(
    "16. transactions/network_risk_results.csv"
)

print(
    "17. transactions/account_investigation_results.csv"
)

print(
    "18. merchants/merchants.csv"
)

print(
    "19. devices/devices.csv"
)

print(
    "20. alerts/alerts.csv"
)

print(
    "21. cases/cases.csv"
)

print("\n============================================================")
print("                    FINAGENT READY")
print("============================================================")