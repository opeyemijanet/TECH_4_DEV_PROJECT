from datetime import date, timedelta
import random

# 2) Sample/Dummy Data Requirements
# We include:
# - 7 days of "normal" expenses
# - 1 day of "spike" expenses
# - inventory items with mixed expiry states
# - cashflow totals to trigger different risk levels

def generate_dummy_inputs(seed: int = 42):
    random.seed(seed)
    today = date.today()

    inventory_items = [
        {"id": 1, "name": "Tomatoes", "expiry_date": today + timedelta(days=2)},
        {"id": 2, "name": "Milk", "expiry_date": today + timedelta(days=1)},
        {"id": 3, "name": "Rice", "expiry_date": today + timedelta(days=25)},
        {"id": 4, "name": "Bread", "expiry_date": today - timedelta(days=1)},
    ]

    last_7_days_expense_totals = [random.randint(900, 1300) for _ in range(7)]
    today_expense_total = random.randint(2800, 4500)

    last_7_days_income_totals = [random.randint(1200, 2200) for _ in range(7)]
    last_7_days_expense_totals_cf = [random.randint(1000, 2400) for _ in range(7)]

    today_income = random.randint(900, 1600)
    min_cash_buffer = 1500.0
    today_cash_balance = random.randint(800, 2200)

    return {
        "inventory_items": inventory_items,
        "last_7_days_expense_totals": last_7_days_expense_totals,
        "today_expense_total": float(today_expense_total),

        "last_7_days_income_totals": [float(x) for x in last_7_days_income_totals],
        "last_7_days_expense_totals_cf": [float(x) for x in last_7_days_expense_totals_cf],
        "today_income_total": float(today_income),
        "min_cash_buffer": float(min_cash_buffer),
        "today_cash_balance": float(today_cash_balance),
    }
