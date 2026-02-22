from typing import Dict, Any, List, Tuple
from datetime import datetime

REQUIRED_TX_FIELDS = ["current_balance", "transaction_id", "date", "type", "amount", "category", "description"]
ALLOWED_TYPES = {"income", "expense"}


def _parse_iso_date(date_str: str) -> None:
    s = str(date_str).replace("Z", "+00:00")
    datetime.fromisoformat(s)


def validate_transaction(tx: Dict[str, Any], index: int) -> Tuple[bool, str]:
    for f in REQUIRED_TX_FIELDS:
        if f not in tx:
            return False, f"Transaction at index {index} missing '{f}'"

    ttype = str(tx["type"]).lower()
    if ttype not in ALLOWED_TYPES:
        return False, f"Transaction {tx.get('transaction_id')}: type must be 'income' or 'expense'"

    try:
        float(tx["amount"])
    except (TypeError, ValueError):
        return False, f"Transaction {tx.get('transaction_id')}: amount must be a number"

    try:
        _parse_iso_date(tx["date"])
    except Exception:
        return False, f"Transaction {tx.get('transaction_id')}: invalid date format"

    return True, ""


def summarize_cashflow(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    income = 0.0
    expense = 0.0
    expense_by_category: Dict[str, float] = {}

    for tx in transactions:
        amt = float(tx["amount"])
        ttype = str(tx["type"]).lower()
        cat = str(tx.get("category") or "unknown")

        if ttype == "income":
            income += amt
        else:
            expense += amt
            expense_by_category[cat] = expense_by_category.get(cat, 0.0) + amt

    top_cats = sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "transaction_count": len(transactions),
        "total_income": round(income, 2),
        "total_expense": round(expense, 2),
        "net_cashflow": round(income - expense, 2),
        "top_expense_categories": [{"category": c, "amount": round(a, 2)} for c, a in top_cats],
    }