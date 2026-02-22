from typing import Dict, Any, List, Tuple, Optional
from statistics import median

_MAD_SCALE = 1.4826


def _get_expenses(payload: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    if isinstance(payload.get("data"), dict) and isinstance(payload["data"].get("expenses"), list):
        return payload["data"]["expenses"]
    if isinstance(payload.get("expenses"), list):
        return payload["expenses"]
    return None


def validate_expense_payload(payload: Dict[str, Any]) -> Tuple[bool, str]:
    expenses = _get_expenses(payload)
    if not isinstance(expenses, list) or len(expenses) == 0:
        return False, "Expected 'expenses' as a non-empty list (either at top-level or inside data)."

    for i, e in enumerate(expenses):
        if not isinstance(e, dict):
            return False, f"Expense at index {i} must be an object"
        if "amount" not in e:
            return False, f"Expense at index {i} missing 'amount'"
        try:
            amt = float(e["amount"])
            if amt < 0:
                return False, f"Expense at index {i} amount must be >= 0"
        except (TypeError, ValueError):
            return False, f"Expense at index {i} amount must be a number"

    return True, ""


def detect_expense_anomalies(payload: Dict[str, Any], z_threshold: float = 3.5) -> Dict[str, Any]:
    expenses = _get_expenses(payload) or []
    amounts = [float(e["amount"]) for e in expenses]

    if len(amounts) < 5:
        if not amounts:
            return {"status": "error", "message": "No expenses provided."}
        max_amt = max(amounts)
        anomalies = []
        for e in expenses:
            amt = float(e["amount"])
            if amt == max_amt and max_amt > 0:
                anomalies.append({**e, "anomaly_score": None, "reason": "Highest expense (insufficient data for stats)"})
        return {
            "status": "success",
            "summary": {"count": len(expenses), "anomalies": len(anomalies), "method": "fallback-max"},
            "anomalies": anomalies,
        }

    med = median(amounts)
    abs_dev = [abs(x - med) for x in amounts]
    mad = median(abs_dev)

    denom = (_MAD_SCALE * mad) if mad != 0 else 1e-9

    anomalies = []
    for e in expenses:
        amt = float(e["amount"])
        score = (amt - med) / denom
        if score >= z_threshold:
            anomalies.append(
                {**e, "anomaly_score": round(score, 3), "reason": f"Unusually high expense (robust z >= {z_threshold})"}
            )

    return {
        "status": "success",
        "summary": {
            "count": len(expenses),
            "anomalies": len(anomalies),
            "median_amount": round(med, 2),
            "mad": round(mad, 2),
            "method": "robust-mad-zscore",
            "z_threshold": z_threshold,
        },
        "anomalies": anomalies,
    }