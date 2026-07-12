"""Auto emission calculation API routes (ingestion + review queue)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.pending_auto_calculation import PendingStatus
from app.repositories.pending_auto_calculation_repository import (
    PendingAutoCalculationRepository,
)
from app.schemas.auto_emission import (
    IngestOutcome,
    PendingAutoCalculationRead,
    SourceRecordIngest,
)
from app.services.auto_emission_service import (
    AutoEmissionService,
    AutoEmissionValidationError,
)

router = APIRouter(prefix="/auto-calculation", tags=["auto-calculation"])


def get_auto_emission_service(db: Session = Depends(get_db)) -> AutoEmissionService:
    return AutoEmissionService(db)


@router.post("/ingest", response_model=IngestOutcome)
def ingest_source_record(
    payload: SourceRecordIngest,
    service: AutoEmissionService = Depends(get_auto_emission_service),
):
    """Ingest one source record.

    An ERP webhook/cron posts a source record here whenever it is created or
    edited; the engine creates/updates/flags accordingly (no-op if the feature
    is disabled).
    """
    try:
        outcome = service.ingest(payload)
        service.db.commit()
        return outcome
    except AutoEmissionValidationError as exc:
        service.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/pending", response_model=list[PendingAutoCalculationRead])
def list_pending(
    status_filter: Optional[PendingStatus] = Query(default=PendingStatus.PENDING, alias="status"),
    db: Session = Depends(get_db),
):
    return PendingAutoCalculationRepository(db).list(status=status_filter)


@router.post("/pending/{pending_id}/retry", response_model=IngestOutcome)
def retry_pending(
    pending_id: int,
    service: AutoEmissionService = Depends(get_auto_emission_service),
):
    """Re-run the engine for a parked record after configuration is fixed."""
    try:
        outcome = service.retry_pending(pending_id)
        service.db.commit()
        return outcome
    except AutoEmissionValidationError as exc:
        service.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
