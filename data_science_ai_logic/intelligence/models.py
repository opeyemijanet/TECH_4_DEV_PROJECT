from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any

AlertType = Literal["EXPIRY", "EXPENSE_ANOMALY", "CASHFLOW_RISK"]
Severity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
AlertStatus = Literal["OPEN", "ACKNOWLEDGED", "RESOLVED"]

@dataclass
class Alert:
    alert_type: AlertType
    severity: Severity
    title: str
    message: str
    status: AlertStatus = "OPEN"
    related_model: Optional[str] = None
    related_id: Optional[int] = None
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "status": self.status,
            "related_model": self.related_model,
            "related_id": self.related_id,
            "extra": self.extra or {}
        }
