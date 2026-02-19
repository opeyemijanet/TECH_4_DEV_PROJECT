# 1) Data Models (JSON Schema-like)

TRANSACTION_MODEL = {
    "id": "integer",
    "type": "INCOME | EXPENSE",
    "category": "string",
    "amount": "number",
    "transaction_date": "YYYY-MM-DD",
    "note": "string (optional)"
}

INVENTORY_ITEM_MODEL = {
    "id": "integer",
    "name": "string",
    "quantity": "integer",
    "unit": "string",
    "unit_cost": "number",
    "received_date": "YYYY-MM-DD",
    "expiry_date": "YYYY-MM-DD"
}

ALERT_MODEL = {
    "id": "integer (optional; typically set by DB)",
    "alert_type": "EXPIRY | EXPENSE_ANOMALY | CASHFLOW_RISK",
    "severity": "LOW | MEDIUM | HIGH | CRITICAL",
    "title": "string",
    "message": "string",
    "status": "OPEN | ACKNOWLEDGED | RESOLVED",
    "related_model": "string (optional)",
    "related_id": "integer (optional)",
    "created_at": "timestamp (set by backend)",
    "extra": "object (optional)"
}

# 3) Aggregated Data Outputs (what the intelligence produces)

AGGREGATED_OUTPUTS = {
    "expense_anomaly": {
        "baseline_7_day_avg": "number",
        "today_total": "number",
        "ratio_to_average": "number",
        "severity": "MEDIUM|HIGH|CRITICAL or null",
        "message": "string or null"
    },
    "inventory_expiry": {
        "item_id": "integer",
        "days_left": "integer",
        "expiry_label": "SAFE|WARNING|URGENT|EXPIRED",
        "severity": "LOW|MEDIUM|HIGH|CRITICAL"
    },
    "cashflow_risk": {
        "today_income": "number",
        "today_expense": "number",
        "today_cash_balance": "number",
        "min_cash_buffer": "number",
        "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
        "message": "string"
    }
}
