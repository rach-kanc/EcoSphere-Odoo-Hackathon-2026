"""EmissionFactorMapping API routes (auto calculation configuration)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.carbon_transaction import SourceType
from app.schemas.auto_emission import (
    EmissionFactorMappingCreate,
    EmissionFactorMappingRead,
    EmissionFactorMappingUpdate,
)
from app.services.emission_factor_mapping_service import (
    EmissionFactorMappingConflictError,
    EmissionFactorMappingNotFoundError,
    EmissionFactorMappingService,
)

router = APIRouter(prefix="/emission-factor-mappings", tags=["emission-factor-mappings"])


def get_mapping_service(db: Session = Depends(get_db)) -> EmissionFactorMappingService:
    return EmissionFactorMappingService(db)


@router.get("", response_model=list[EmissionFactorMappingRead])
def list_mappings(
    source_type: Optional[SourceType] = None,
    is_active: Optional[bool] = None,
    service: EmissionFactorMappingService = Depends(get_mapping_service),
):
    return service.list_mappings(source_type=source_type, is_active=is_active)


@router.post("", response_model=EmissionFactorMappingRead, status_code=status.HTTP_201_CREATED)
def create_mapping(
    payload: EmissionFactorMappingCreate,
    service: EmissionFactorMappingService = Depends(get_mapping_service),
):
    try:
        mapping = service.create_mapping(payload)
        service.repo.db.commit()
        return mapping
    except EmissionFactorMappingConflictError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.put("/{mapping_id}", response_model=EmissionFactorMappingRead)
def update_mapping(
    mapping_id: int,
    payload: EmissionFactorMappingUpdate,
    service: EmissionFactorMappingService = Depends(get_mapping_service),
):
    try:
        mapping = service.update_mapping(mapping_id, payload)
        service.repo.db.commit()
        return mapping
    except EmissionFactorMappingNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EmissionFactorMappingConflictError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mapping(
    mapping_id: int,
    service: EmissionFactorMappingService = Depends(get_mapping_service),
):
    try:
        service.delete_mapping(mapping_id)
        service.repo.db.commit()
    except EmissionFactorMappingNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
