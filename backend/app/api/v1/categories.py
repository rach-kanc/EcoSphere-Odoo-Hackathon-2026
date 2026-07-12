"""Category API routes."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.category import CategoryStatus, CategoryType
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import (
    CategoryNotFoundError,
    CategoryService,
    CategoryTypeNotAllowedError,
)

router = APIRouter(prefix="/categories", tags=["categories"])


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


@router.get("", response_model=list[CategoryRead])
def list_categories(
    category_type: Optional[CategoryType] = Query(default=None, alias="type"),
    status: Optional[CategoryStatus] = None,
    service: CategoryService = Depends(get_category_service),
):
    return service.list_categories(category_type=category_type, status=status)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    try:
        category = service.create_category(payload)
        service.repo.db.commit()
        return category
    except CategoryTypeNotAllowedError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    try:
        category = service.update_category(category_id, payload)
        service.repo.db.commit()
        return category
    except CategoryNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CategoryTypeNotAllowedError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
):
    try:
        service.delete_category(category_id)
        service.repo.db.commit()
    except CategoryNotFoundError as exc:
        service.repo.db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
