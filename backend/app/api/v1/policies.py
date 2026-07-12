"""Policy API routes."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.policy import PolicyStatus, PolicyType
from app.schemas.policy import (
    PolicyAcknowledgementCreate,
    PolicyAcknowledgementRead,
    PolicyCreate,
    PolicyRead,
    PolicyUpdate,
)
from app.services.policy_service import (
    PolicyAlreadyAcknowledgedError,
    PolicyNotFoundError,
    PolicyService,
    PolicyValidationError,
)

router = APIRouter(prefix="/policies", tags=["policies"])


def get_policy_service(db: Session = Depends(get_db)) -> PolicyService:
    return PolicyService(db)


@router.get("", response_model=list[PolicyRead])
def list_policies(
    policy_type: Optional[PolicyType] = Query(default=None, alias="type"),
    status: Optional[PolicyStatus] = None,
    service: PolicyService = Depends(get_policy_service),
):
    return service.list_policies(policy_type=policy_type, status=status)


@router.get("/pending", response_model=list[PolicyRead])
def list_pending_policies(
    user_id: int = Query(..., description="The ID of the employee to check"),
    service: PolicyService = Depends(get_policy_service),
):
    return service.list_pending_policies(user_id)


@router.get("/{policy_id}", response_model=PolicyRead)
def get_policy(
    policy_id: int,
    service: PolicyService = Depends(get_policy_service),
):
    try:
        return service.get_policy(policy_id)
    except PolicyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=PolicyRead, status_code=status.HTTP_201_CREATED)
def create_policy(
    payload: PolicyCreate,
    service: PolicyService = Depends(get_policy_service),
):
    try:
        policy = service.create_policy(payload)
        service.repo.db.commit()
        return policy
    except PolicyValidationError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{policy_id}", response_model=PolicyRead)
def update_policy(
    policy_id: int,
    payload: PolicyUpdate,
    service: PolicyService = Depends(get_policy_service),
):
    try:
        policy = service.update_policy(policy_id, payload)
        service.repo.db.commit()
        return policy
    except PolicyNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PolicyValidationError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{policy_id}/acknowledge", response_model=PolicyAcknowledgementRead, status_code=status.HTTP_201_CREATED)
def acknowledge_policy(
    policy_id: int,
    payload: PolicyAcknowledgementCreate,
    user_id: int = Query(..., description="The ID of the employee acknowledging the policy"),
    service: PolicyService = Depends(get_policy_service),
):
    try:
        ack = service.acknowledge_policy(user_id=user_id, policy_id=policy_id, signature_text=payload.signature_text)
        service.repo.db.commit()
        return ack
    except PolicyNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (PolicyValidationError, PolicyAlreadyAcknowledgedError) as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
