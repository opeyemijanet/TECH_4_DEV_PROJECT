# Food Intelligence AI Logic (Data Science Team)

This repo contains the **rule-based AI logic** for the capstone MVP (backend-agnostic).
It is designed to be plugged into **Django/FastAPI/Node** backend services.

## What it covers
- Inventory expiry risk alerts
- Expense anomaly alerts (spend spikes vs 7-day baseline)
- Cashflow risk alerts (simple rules)
- Explainable messages (human-friendly alert wording)

## Table of Contents (requested by Cybersecurity)
1. Data Models (JSON Schema)
2. Sample/Dummy Data Requirements
3. Aggregated Data Outputs
4. Business Rules & Logic

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python demo.py
```

This will:
- generate dummy inputs in `examples/dummy_inputs.json`
- generate alerts in `examples/generated_alerts.json`
- print alerts to the console

## How backend should integrate

**Event-driven (recommended MVP):**
1) Backend saves a new transaction / inventory item
2) Backend calls the rule function
3) If an alert dict is returned, backend saves it to the `alerts` table
4) Mobile reads alerts through `GET /alerts`

Example (pseudo-code):

```python
from intelligence.rules import evaluate_expense_anomaly

alert = evaluate_expense_anomaly(today_total=4000, last_7_days_totals=[1100,1200,1000,1300,1050,1150,1250])
if alert:
    save_alert_to_db(alert)
```

## Security notes (for cybersecurity review)
This module makes security review easier by making explicit:
- which fields are used for decision-making
- what aggregated outputs are produced
- what thresholds trigger alerts

Recommended MVP controls to apply in backend:
- JWT authentication
- role-based access control (who can view cashflow totals)
- audit logs for transaction edits/deletes (protect baselines)
- strict input validation (no negative amounts, sensible dates)
- rate limiting on transaction creation to prevent alert spam

---
