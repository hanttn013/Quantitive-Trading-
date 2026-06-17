from fastapi import APIRouter, Depends

from ..services import copilot
from ..settings import Settings, get_settings

router = APIRouter(prefix="/api/copilot", tags=["copilot"])


@router.get("/health")
def get_copilot_health(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return copilot.health(settings)


@router.post("/chat")
def chat(payload: dict[str, object], settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return copilot.chat(payload, settings)


@router.post("/commands/simulate")
def simulate_command(payload: dict[str, object]) -> dict[str, object]:
    return copilot.command_result("simulated", payload)


@router.post("/commands/confirm")
def confirm_command(payload: dict[str, object]) -> dict[str, object]:
    return copilot.command_result("confirmed", payload)


@router.post("/commands/reject")
def reject_command(payload: dict[str, object]) -> dict[str, object]:
    return copilot.command_result("rejected", payload)

