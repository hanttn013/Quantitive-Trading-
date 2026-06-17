from fastapi import APIRouter, Query

from .. import repository
from ..schemas import Account, AppContext

router = APIRouter(prefix="/api", tags=["context"])


@router.get("/context", response_model=AppContext)
def get_context(
    environment: str = Query(default="Paper"),
    account_id: str = Query(default="acc-demo"),
) -> AppContext:
    return repository.context(environment=environment, account_id=account_id)


@router.get("/accounts", response_model=list[Account])
def get_accounts() -> list[Account]:
    return repository.accounts()

