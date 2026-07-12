"""Business logic for emission-factor mapping configuration (auto calc, issue #7)."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.carbon_transaction import SourceType
from app.models.emission_factor_mapping import EmissionFactorMapping
from app.repositories.emission_factor_mapping_repository import (
    EmissionFactorMappingRepository,
)
from app.schemas.auto_emission import (
    EmissionFactorMappingCreate,
    EmissionFactorMappingUpdate,
)


class EmissionFactorMappingError(Exception):
    pass


class EmissionFactorMappingNotFoundError(EmissionFactorMappingError):
    pass


class EmissionFactorMappingConflictError(EmissionFactorMappingError):
    pass


class EmissionFactorMappingService:
    def __init__(self, db: Session):
        self.repo = EmissionFactorMappingRepository(db)

    def list_mappings(
        self,
        *,
        source_type: Optional[SourceType] = None,
        is_active: Optional[bool] = None,
    ) -> list[EmissionFactorMapping]:
        return self.repo.list(source_type=source_type, is_active=is_active)

    def get_mapping(self, mapping_id: int) -> EmissionFactorMapping:
        mapping = self.repo.get(mapping_id)
        if mapping is None:
            raise EmissionFactorMappingNotFoundError(f"Mapping {mapping_id} not found")
        return mapping

    def create_mapping(self, payload: EmissionFactorMappingCreate) -> EmissionFactorMapping:
        existing = self.repo.find(payload.source_type, payload.match_key)
        if existing is not None:
            raise EmissionFactorMappingConflictError(
                f"A mapping for {payload.source_type.value}/'{payload.match_key}' already exists"
            )
        mapping = EmissionFactorMapping(
            source_type=payload.source_type,
            match_key=payload.match_key,
            factor_code=payload.factor_code,
            is_active=payload.is_active,
        )
        return self.repo.create(mapping)

    def update_mapping(
        self, mapping_id: int, payload: EmissionFactorMappingUpdate
    ) -> EmissionFactorMapping:
        mapping = self.get_mapping(mapping_id)
        update_data = payload.model_dump(exclude_unset=True)

        new_match_key = update_data.get("match_key", mapping.match_key)
        if new_match_key != mapping.match_key:
            clash = self.repo.find(mapping.source_type, new_match_key)
            if clash is not None and clash.id != mapping.id:
                raise EmissionFactorMappingConflictError(
                    f"A mapping for {mapping.source_type.value}/'{new_match_key}' already exists"
                )

        for field in ("match_key", "factor_code", "is_active"):
            if field in update_data:
                setattr(mapping, field, update_data[field])
        self.repo.db.flush()
        return mapping

    def delete_mapping(self, mapping_id: int) -> None:
        mapping = self.get_mapping(mapping_id)
        self.repo.delete(mapping)
