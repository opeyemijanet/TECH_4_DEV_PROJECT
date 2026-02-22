import requests
from typing import Dict, Any

BASE_URL = "http://18.175.213.46:3000"


class BackendError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"{status_code}: {message}")


def _post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    try:
        r = requests.post(url, json=payload, timeout=30)
    except requests.RequestException as e:
        raise BackendError(502, f"Backend request failed: {str(e)}")

    if r.status_code >= 400:
        raise BackendError(r.status_code, r.text or "No response body")

    try:
        return r.json()
    except ValueError:
        return {"raw": r.text}


def post_cashflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _post("/predictions/cashflow", payload)


def post_inventory(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _post("/predictions/inventory", payload)


def post_anomalies(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _post("/predictions/anomalies", payload)