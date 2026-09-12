import sys
import json
import sqlite3
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC_DIR))

from risk_engine import calculate_final_risk
from api.case_manager import attach_case_data


DB_PATH = r"data\security\cases.db"


db = sqlite3.connect(DB_PATH)

rows = db.execute(
    """
    SELECT case_id, customer_id
    FROM cases
    """
).fetchall()

print(f"Cases to recalculate: {len(rows)}")

for case_id, customer_id in rows:
    print(f"Processing {case_id} -> {customer_id}")

    try:
        risk = calculate_final_risk(customer_id)

        attach_case_data(
            case_id=case_id,
            field="risk_data",
            data=json.dumps(risk, default=str),
        )

        print(
            f"  UPDATED: {risk['final_risk_level']} "
            f"({risk['final_risk_score']})"
        )

    except Exception as e:
        print(f"  ERROR: {e}")

db.close()

print("DONE")