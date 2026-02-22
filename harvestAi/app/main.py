from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder

from app.schemas import InventoryExpiryRequest, InventoryRequest, CashflowRequest, AnomalyRequest
from app.backend_client import post_cashflow, post_inventory, post_anomalies, BackendError

from app.logic.inventory_expiry_tracker import check_inventory_expiry
from app.logic.cashflow_logic import validate_transaction, summarize_cashflow
from app.logic.expense_anomaly import validate_expense_payload, detect_expense_anomalies

app = FastAPI(title="harvestAi Integration API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


# 1) Local Inventory Expiry Tracker (YOUR model)
@app.post("/run/inventory-expiry")
def run_inventory_expiry(req: InventoryExpiryRequest):
    result = check_inventory_expiry(req.payload)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Invalid inventory input"))
    return result


# 2) Forward inventory to DS backend
@app.post("/run/inventory")
def run_inventory(req: InventoryRequest):
    payload = jsonable_encoder(req.payload)
    try:
        ds = post_inventory(payload)
    except BackendError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return {"posted_to_backend": True, "backend_response": ds}


# 3) Cashflow: validate + summarize + send to DS backend
@app.post("/run/cashflow")
def run_cashflow(req: CashflowRequest):
    txs = jsonable_encoder(req.transactions)

    valid = []
    skipped = []
    for i, tx in enumerate(txs):
        ok, msg = validate_transaction(tx, i)
        if ok:
            valid.append(tx)
        else:
            skipped.append({"index": i, "transaction_id": tx.get("transaction_id"), "reason": msg})

    if not valid:
        raise HTTPException(status_code=400, detail={"message": "No valid transactions", "skipped": skipped})

    summary = summarize_cashflow(valid)
    ds_payload = {"transactions": valid, "summary": summary}

    try:
        ds = post_cashflow(ds_payload)
    except BackendError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    return {
        "posted_to_backend": True,
        "local_summary": summary,
        "skipped_transactions": skipped,
        "backend_response": ds,
    }


# 4A) Expense anomalies - LOCAL model (instant result)
@app.post("/run/anomalies-local")
def run_anomalies_local(req: AnomalyRequest):
    payload = jsonable_encoder(req.payload)

    ok, msg = validate_expense_payload(payload)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    return detect_expense_anomalies(payload)


# 4B) Expense anomalies - Forward to DS backend
@app.post("/run/anomalies")
def run_anomalies(req: AnomalyRequest):
    payload = jsonable_encoder(req.payload)

    ok, msg = validate_expense_payload(payload)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    try:
        ds = post_anomalies(payload)
    except BackendError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    return {"posted_to_backend": True, "backend_response": ds}