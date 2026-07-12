"""Data access helpers for EmissionFactorMapping records."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.carbon_transaction import SourceType
from app.models.emission_factor_mapping import EmissionFactorMapping


class EmissionFactorMappingRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        *,
        source_type: Optional[SourceType] = None,
        is_active: Optional[bool] = None,
    ) -> list[EmissionFactorMapping]:
        query = self.db.query(EmissionFactorMapping)
        if source_type is not None:
            query = query.filter(EmissionFactorMapping.source_type == source_type)
        if is_active is not None:
            query = query.filter(EmissionFactorMapping.is_active == is_active)
        return query.order_by(
            EmissionFactorMapping.source_type.asc(), EmissionFactorMapping.match_key.asc()
        ).all()

    def get(self, mapping_id: int) -> Optional[EmissionFactorMapping]:
        return self.db.get(EmissionFactorMapping, mapping_id)

    def find(
        self, source_type: SourceType, match_key: str
    ) -> Optional[EmissionFactorMapping]:
        return (
            self.db.query(EmissionFactorMapping)
            .filter(
                EmissionFactorMapping.source_type == source_type,
                EmissionFactorMapping.match_key == match_key,
            )
            .one_or_none()
        )

    def create(self, mapping: EmissionFactorMapping) -> EmissionFactorMapping:
        self.db.add(mapping)
        self.db.flush()
        return mapping

    def delete(self, mapping: EmissionFactorMapping) -> None:
        self.db.delete(mapping)
