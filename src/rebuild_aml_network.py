import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRANSACTIONS_DIR = os.path.join(DATA_DIR, "transactions")

CUSTOMERS_FILE = os.path.join(
    DATA_DIR, "customers", "customers.csv"
)

ACCOUNTS_FILE = os.path.join(
    DATA_DIR, "accounts", "accounts.csv"
)

TRANSACTIONS_FILE = os.path.join(
    TRANSACTIONS_DIR, "transactions.csv"
)

OUTPUT_FILE = os.path.join(
    TRANSACTIONS_DIR,
    "aml_network_pattern_results.csv"
)


print("Loading data...")

customers = pd.read_csv(CUSTOMERS_FILE)
accounts = pd.read_csv(ACCOUNTS_FILE)
transactions = pd.read_csv(TRANSACTIONS_FILE)


# ---------------------------------------------------------
# Normalize IDs
# ---------------------------------------------------------

customers["customer_id"] = customers["customer_id"].astype(str)
accounts["customer_id"] = accounts["customer_id"].astype(str)
transactions["customer_id"] = transactions["customer_id"].astype(str)


# ---------------------------------------------------------
# Customer-level network metrics
# ---------------------------------------------------------

results = []

for customer_id in customers["customer_id"]:

    customer_accounts = accounts[
        accounts["customer_id"] == customer_id
    ]

    customer_transactions = transactions[
        transactions["customer_id"] == customer_id
    ]

    account_count = len(customer_accounts)
    transaction_count = len(customer_transactions)

    merchant_count = (
        customer_transactions["merchant_id"]
        .dropna()
        .nunique()
    )

    device_count = (
        customer_transactions["device_id"]
        .dropna()
        .nunique()
    )

    # -----------------------------------------------------
    # Shared devices
    # A device is shared if it is used by >1 customer.
    # -----------------------------------------------------

    shared_device_count = 0

    customer_devices = (
        customer_transactions["device_id"]
        .dropna()
        .unique()
    )

    for device_id in customer_devices:

        users = (
            transactions[
                transactions["device_id"] == device_id
            ]["customer_id"]
            .dropna()
            .nunique()
        )

        if users > 1:
            shared_device_count += 1


    # -----------------------------------------------------
    # Suspicious transactions
    # -----------------------------------------------------

    suspicious_transaction_count = len(
        customer_transactions[
            customer_transactions["is_suspicious"] == 1
        ]
    )


    # -----------------------------------------------------
    # Network risk score
    #
    # Deterministic score based on observable network
    # characteristics.
    # -----------------------------------------------------

    network_risk_score = 0

    network_risk_score += min(
        account_count * 5,
        15
    )

    network_risk_score += min(
        merchant_count,
        20
    )

    network_risk_score += min(
        device_count * 2,
        20
    )

    network_risk_score += min(
        shared_device_count * 15,
        30
    )

    network_risk_score += min(
        suspicious_transaction_count * 2,
        30
    )

    network_risk_score = min(
        network_risk_score,
        100
    )


    if network_risk_score >= 70:
        network_risk_level = "HIGH"
    elif network_risk_score >= 30:
        network_risk_level = "MEDIUM"
    else:
        network_risk_level = "LOW"


    results.append({
        "customer_id": customer_id,
        "account_count": account_count,
        "transaction_count": transaction_count,
        "merchant_count": merchant_count,
        "device_count": device_count,
        "shared_device_count": shared_device_count,
        "network_risk_score": network_risk_score,
        "network_risk_level": network_risk_level
    })


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

result_df = pd.DataFrame(results)

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("Network pattern dataset rebuilt successfully.")
print(f"Rows: {len(result_df)}")
print(f"Output: {OUTPUT_FILE}")
