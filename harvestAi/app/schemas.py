from pydantic import BaseModel
from typing import Any, Dict, List


class InventoryExpiryRequest(BaseModel):
    # accepts list OR dict {"inventory":[...], "current_date":"YYYY-MM-DD"}
    payload: Any


class InventoryRequest(BaseModel):
    # forwarded to DS backend /predictions/inventory
    payload: Dict[str, Any]


class CashflowRequest(BaseModel):
    # list of rows matching your dataset columns
    transactions: List[Dict[str, Any]]


class AnomalyRequest(BaseModel):
    # accepts {"expenses":[...]} or {"data":{"expenses":[...]}}
    payload: Dict[str, Any]