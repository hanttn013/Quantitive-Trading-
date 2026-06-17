from fastapi import APIRouter

from .. import repository
from ..schemas import Alert, AuditEntry, Integration, RiskRule, RolePermission

router = APIRouter(prefix="/api", tags=["operations"])


@router.get("/alerts", response_model=list[Alert])
def get_alerts() -> list[Alert]:
    return repository.alerts()


@router.get("/audit-logs", response_model=list[AuditEntry])
def get_audit_logs() -> list[AuditEntry]:
    return repository.audit_logs()


@router.get("/integrations", response_model=list[Integration])
def get_integrations() -> list[Integration]:
    return repository.integrations()


@router.get("/settings/roles", response_model=list[RolePermission])
def get_roles() -> list[RolePermission]:
    return repository.roles()


@router.get("/risk/rules", response_model=list[RiskRule])
def get_risk_rules() -> list[RiskRule]:
    return repository.risk_rules()


@router.post("/alerts/{alert_id}/ack")
def ack_alert(alert_id: str) -> dict[str, str]:
    return {"id": alert_id, "status": "Ack"}


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: str) -> dict[str, str]:
    return {"id": alert_id, "status": "Resolved"}


@router.post("/integrations/{integration_id}/reconnect")
def reconnect_integration(integration_id: str) -> dict[str, str]:
    return {"id": integration_id, "status": "Reconnect requested"}


@router.post("/integrations/{integration_id}/test")
def test_integration(integration_id: str) -> dict[str, str]:
    return {"id": integration_id, "status": "Test passed"}

