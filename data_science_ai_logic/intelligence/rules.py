from datetime import date
from .models import Alert
from .aggregates import mean, safe_ratio

# ============================================================
# 4) Business Rules & Logic
# ============================================================

# -------------------------
# INVENTORY EXPIRY LOGIC
# -------------------------
def inventory_expiry_label(days_left: int) -> str:
    """Maps remaining days to a label."""
    if days_left <= 0:
        return "EXPIRED"
    if days_left <= 2:
        return "URGENT"
    if days_left <= 5:
        return "WARNING"
    return "SAFE"

def inventory_expiry_severity(label: str) -> str:
    """Maps label to alert severity."""
    return {
        "SAFE": "LOW",
        "WARNING": "MEDIUM",
        "URGENT": "HIGH",
        "EXPIRED": "CRITICAL",
    }[label]

def evaluate_inventory_item(item_id: int, name: str, expiry_date: date):
    """Return an expiry alert dict for a single item, or None if SAFE."""
    today = date.today()
    days_left = (expiry_date - today).days
    label = inventory_expiry_label(days_left)
    severity = inventory_expiry_severity(label)

    # MVP choice: only alert when not SAFE
    if label == "SAFE":
        return None

    if label == "EXPIRED":
        msg = f"{name} is expired. Take action immediately."
    else:
        msg = f"{name} expires in {max(days_left,0)} day(s). Consider prioritizing sale/usage to reduce waste."

    return Alert(
        alert_type="EXPIRY",
        severity=severity,
        title="Inventory expiry alert",
        message=msg,
        related_model="InventoryItem",
        related_id=item_id,
        extra={"days_left": days_left, "expiry_label": label}
    ).to_dict()

def evaluate_inventory_items(items):
    """Evaluate a list of inventory items.

    items: list of dicts with keys: id, name, expiry_date (as date)
    """
    alerts = []
    for it in items:
        a = evaluate_inventory_item(it["id"], it["name"], it["expiry_date"])
        if a:
            alerts.append(a)
    return alerts


# -------------------------
# EXPENSE ANOMALY LOGIC
# -------------------------
def evaluate_expense_anomaly(today_total: float, last_7_days_totals: list[float]):
    """Detect unusually high spending using a simple baseline.

    Baseline = mean(last 7 days)
    Severity thresholds (ratio = today / baseline):
      >= 3.0x -> CRITICAL
      >= 2.0x -> HIGH
      >= 1.5x -> MEDIUM
      else -> no alert
    """
    baseline = mean(last_7_days_totals)
    if baseline <= 0:
        return None

    r = safe_ratio(today_total, baseline)

    if r >= 3.0:
        sev = "CRITICAL"
    elif r >= 2.0:
        sev = "HIGH"
    elif r >= 1.5:
        sev = "MEDIUM"
    else:
        return None

    msg = f"Today's expenses are {r:.1f}× higher than your 7-day average."

    return Alert(
        alert_type="EXPENSE_ANOMALY",
        severity=sev,
        title="Unusual spending detected",
        message=msg,
        related_model="DailyExpense",
        extra={
            "today_total": today_total,
            "baseline_7_day_avg": baseline,
            "ratio_to_average": r
        }
    ).to_dict()


# -------------------------
# CASHFLOW RISK LOGIC
# -------------------------
def evaluate_cashflow_risk(
    last_7_days_income_totals: list[float],
    last_7_days_expense_totals: list[float],
    today_income: float,
    today_expense: float,
    min_cash_buffer: float,
    today_cash_balance: float
):
    """Rule-based cashflow risk scoring.

    Rules:
    - If cash balance < min buffer -> CRITICAL
    - If expenses > income for last 3 consecutive days -> HIGH
    - If today expense > today income -> MEDIUM
    - else -> LOW
    """
    deficits_last_3 = 0
    for i in range(1, 4):
        if len(last_7_days_income_totals) >= i and len(last_7_days_expense_totals) >= i:
            if last_7_days_expense_totals[-i] > last_7_days_income_totals[-i]:
                deficits_last_3 += 1

    if today_cash_balance < min_cash_buffer:
        sev = "CRITICAL"
        msg = "Cash balance is below your minimum buffer. Immediate action recommended."
    elif deficits_last_3 == 3:
        sev = "HIGH"
        msg = "Expenses exceeded income for 3 consecutive days. Cashflow risk is high."
    elif today_expense > today_income:
        sev = "MEDIUM"
        msg = "Today's expenses are higher than today's income. Monitor cashflow closely."
    else:
        sev = "LOW"
        msg = "Cashflow looks stable today."

    return Alert(
        alert_type="CASHFLOW_RISK",
        severity=sev,
        title="Cashflow risk status",
        message=msg,
        related_model="CashflowSummary",
        extra={
            "today_income": today_income,
            "today_expense": today_expense,
            "today_cash_balance": today_cash_balance,
            "min_cash_buffer": min_cash_buffer
        }
    ).to_dict()
