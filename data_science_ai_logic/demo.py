import json
from pathlib import Path
from intelligence.dummy_data import generate_dummy_inputs
from intelligence.rules import (
    evaluate_inventory_items,
    evaluate_expense_anomaly,
    evaluate_cashflow_risk,
)

def main():
    data = generate_dummy_inputs(seed=42)

    inv_alerts = evaluate_inventory_items(data["inventory_items"])

    exp_alert = evaluate_expense_anomaly(
        today_total=data["today_expense_total"],
        last_7_days_totals=data["last_7_days_expense_totals"],
    )

    cash_alert = evaluate_cashflow_risk(
        last_7_days_income_totals=data["last_7_days_income_totals"],
        last_7_days_expense_totals=data["last_7_days_expense_totals_cf"],
        today_income=data["today_income_total"],
        today_expense=data["today_expense_total"],
        min_cash_buffer=data["min_cash_buffer"],
        today_cash_balance=data["today_cash_balance"],
    )

    alerts = inv_alerts + ([exp_alert] if exp_alert else []) + ([cash_alert] if cash_alert else [])

    print("\n=== GENERATED ALERTS ===")
    for a in alerts:
        print(f"- [{a['severity']}] {a['alert_type']}: {a['message']}")

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    # JSON can't serialize date objects directly; convert via default=str
    (out_dir / "dummy_inputs.json").write_text(json.dumps(data, default=str, indent=2))
    (out_dir / "generated_alerts.json").write_text(json.dumps(alerts, indent=2))

    print("\nWrote examples/")
    print("- examples/dummy_inputs.json")
    print("- examples/generated_alerts.json")

if __name__ == "__main__":
    main()
