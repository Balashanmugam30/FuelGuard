"""
FuelGuard AI - Fraud Detection Engine
Handles fuel delivery analysis, fraud detection, and risk assessment.
"""

import random


# --- Thresholds ---
FRAUD_THRESHOLD = 0.03        # liters
MEDIUM_RISK_THRESHOLD = 0.07  # liters


def generate_delivered_fuel(requested_fuel: float) -> float:
    """
    Simulate the actual fuel delivered by the pump.
    Returns a value between 85% of the requested amount and the full amount.
    Occasionally delivers the exact amount (no fraud).
    """
    lower_bound = round(requested_fuel * 0.85, 4)
    delivered = round(random.uniform(lower_bound, requested_fuel), 4)
    return delivered


def calculate_shortage(requested: float, delivered: float) -> dict:
    """
    Calculate the difference and shortage percentage between
    requested and delivered fuel.
    """
    difference = round(requested - delivered, 4)
    if requested > 0:
        shortage_pct = round((difference / requested) * 100, 2)
    else:
        shortage_pct = 0.0
    return {
        "difference": difference,
        "shortage_percentage": shortage_pct,
    }


def detect_fraud(difference: float) -> bool:
    """Return True if the shortage exceeds the fraud threshold."""
    return difference > FRAUD_THRESHOLD


def assess_risk(difference: float) -> dict:
    """
    Determine risk level and generate a matching risk score.

    Risk bands:
        Low    — shortage <= 0.03 L  → score  0-30
        Medium — shortage <= 0.07 L  → score 31-70
        High   — shortage  > 0.07 L  → score 71-100
    """
    if difference <= FRAUD_THRESHOLD:
        risk_level = "Low"
        risk_score = random.randint(0, 30)
    elif difference <= MEDIUM_RISK_THRESHOLD:
        risk_level = "Medium"
        risk_score = random.randint(31, 70)
    else:
        risk_level = "High"
        risk_score = random.randint(71, 100)
    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
    }


def analyze_transaction(requested_fuel: float, delivered_fuel: float) -> dict:
    """
    Run the full fraud-analysis pipeline on a single transaction.
    Returns a dict with shortage info, fraud flag, and risk assessment.
    """
    shortage = calculate_shortage(requested_fuel, delivered_fuel)
    fraud = detect_fraud(shortage["difference"])
    risk = assess_risk(shortage["difference"])

    return {
        "requested_fuel": requested_fuel,
        "delivered_fuel": delivered_fuel,
        **shortage,
        "fraud_detected": fraud,
        **risk,
    }
