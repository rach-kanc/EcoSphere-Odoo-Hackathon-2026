"""CarbonTransaction API routes."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.carbon_transaction import SourceType, TransactionStatus
from app.schemas.carbon_transaction import (
    CarbonTransactionCreateManual,
    CarbonTransactionRead,
    DepartmentCarbonSummary,
)
from app.services.carbon_transaction_service import (
    CarbonTransactionNotFoundError,
    CarbonTransactionService,
    CarbonTransactionValidationError,
)

router = APIRouter(prefix="/carbon-transactions", tags=["carbon-transactions"])


def get_carbon_transaction_service(db: Session = Depends(get_db)) -> CarbonTransactionService:
    return CarbonTransactionService(db)


@router.get("", response_model=list[CarbonTransactionRead])
def list_carbon_transactions(
    department_id: Optional[int] = None,
    source_type: Optional[SourceType] = None,
    status_filter: Optional[TransactionStatus] = Query(default=None, alias="status"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    service: CarbonTransactionService = Depends(get_carbon_transaction_service),
):
    return service.list_transactions(
        department_id=department_id,
        source_type=source_type,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/summary/by-department", response_model=list[DepartmentCarbonSummary])
def summarize_carbon_transactions_by_department(
    source_type: Optional[SourceType] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    service: CarbonTransactionService = Depends(get_carbon_transaction_service),
):
    """Aggregated CO2e totals per department (issue #8).

    Drill-down to the underlying transactions uses the existing
    ``GET /carbon-transactions?department_id=...`` list endpoint.
    """
    return service.summarize_by_department(
        source_type=source_type, date_from=date_from, date_to=date_to
    )


@router.get("/{transaction_id}", response_model=CarbonTransactionRead)
def get_carbon_transaction(
    transaction_id: int,
    service: CarbonTransactionService = Depends(get_carbon_transaction_service),
):
    try:
        return service.get_transaction(transaction_id)
    except CarbonTransactionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=CarbonTransactionRead, status_code=status.HTTP_201_CREATED)
def create_manual_carbon_transaction(
    payload: CarbonTransactionCreateManual,
    service: CarbonTransactionService = Depends(get_carbon_transaction_service),
):
    try:
        transaction = service.create_manual_transaction(payload)
        service.repo.db.commit()
        return transaction
    except CarbonTransactionValidationError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
