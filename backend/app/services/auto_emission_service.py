"""Auto emission calculation engine (issue #7).

Turns an incoming source record (a purchase line, fleet trip, expense, ...) into
a Carbon Transaction automatically:

1. Skip entirely unless the ``auto_calculation_enabled`` toggle is on.
2. Look up the emission-factor mapping for the record's ``(source_type,
   match_key)``.
3. Resolve the active :class:`EmissionFactor` version for the mapped code on the
   transaction date.
4. On success, create (or, for a re-ingested/edited record, update) a
   ``CarbonTransaction`` marked ``Created By = Auto`` — CO2e derived server-side.
5. When no mapping or no active factor is found, park the record in the pending
   review queue instead of dropping it.

Duplicate protection: transactions and pending rows are keyed by
``(source_type, source_record_id)``, so repeated ingestion of the same source
record updates the existing row rather than creating a new one.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.carbon_transaction import CarbonTransaction, CreatedBy, TransactionStatus
from app.models.department import Department
from app.models.emission_factor import EmissionFactor
from app.models.pending_auto_calculation import PendingAutoCalculation, PendingStatus
from app.repositories.carbon_transaction_repository import CarbonTransactionRepository
from app.repositories.emission_factor_mapping_repository import (
    EmissionFactorMappingRepository,
)
from app.repositories.pending_auto_calculation_repository import (
    PendingAutoCalculationRepository,
)
from app.schemas.auto_emission import IngestOutcome, SourceRecordIngest
from app.services.settings_service import SettingsService


class AutoEmissionError(Exception):
    pass


class AutoEmissionValidationError(AutoEmissionError):
    pass


class AutoEmissionDisabledError(AutoEmissionError):
    pass


class AutoEmissionService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = SettingsService(db)
        self.mappings = EmissionFactorMappingRepository(db)
        self.transactions = CarbonTransactionRepository(db)
        self.pending = PendingAutoCalculationRepository(db)

    def ingest(self, payload: SourceRecordIngest) -> IngestOutcome:
        """Process one source record. See module docstring for the flow."""
        if not self.settings.is_auto_calculation_enabled():
            return IngestOutcome(
                status="disabled",
                detail="Auto calculation is disabled; no transaction created.",
            )

        self._ensure_department(payload.department_id)

        mapping = self.mappings.find(payload.source_type, payload.match_key)
        if mapping is None or not mapping.is_active:
            return self._flag(
                payload,
                reason=(
                    f"No active emission-factor mapping for "
                    f"{payload.source_type.value}/'{payload.match_key}'."
                ),
            )

        factor = EmissionFactor.resolve(self.db, mapping.factor_code, payload.transaction_date)
        if factor is None:
            return self._flag(
                payload,
                reason=(
                    f"No active emission factor for code '{mapping.factor_code}' "
                    f"as of {payload.transaction_date}."
                ),
            )

        return self._upsert_transaction(payload, factor)

    # ── internals ──────────────────────────────────────────────────────────
    def _upsert_transaction(
        self, payload: SourceRecordIngest, factor: EmissionFactor
    ) -> IngestOutcome:
        existing = self.transactions.find_auto_by_source(
            payload.source_type, payload.source_record_id
        )
        if existing is not None:
            existing.department_id = payload.department_id
            existing.emission_factor_id = factor.id
            existing.emission_factor = factor
            existing.transaction_date = payload.transaction_date
            existing.source_reference = payload.source_reference
            existing.factor_value = factor.co2e_per_unit
            existing.quantity = payload.quantity
            self._resolve_pending(payload)
            self.db.flush()
            return IngestOutcome(
                status="updated",
                detail="Existing auto transaction updated from edited source record.",
                carbon_transaction_id=existing.id,
            )

        transaction = CarbonTransaction(
            department_id=payload.department_id,
            source_type=payload.source_type,
            source_record_id=payload.source_record_id,
            source_reference=payload.source_reference,
            transaction_date=payload.transaction_date,
            emission_factor_id=factor.id,
            emission_factor=factor,
            created_by=CreatedBy.AUTO,
            status=TransactionStatus.CONFIRMED,
        )
        transaction.factor_value = factor.co2e_per_unit
        transaction.quantity = payload.quantity
        self.transactions.create(transaction)
        self._resolve_pending(payload)
        return IngestOutcome(
            status="created",
            detail="Auto carbon transaction created.",
            carbon_transaction_id=transaction.id,
        )

    def _flag(self, payload: SourceRecordIngest, *, reason: str) -> IngestOutcome:
        existing = self.pending.find_by_source(
            payload.source_type, payload.source_record_id
        )
        if existing is not None:
            existing.source_reference = payload.source_reference
            existing.match_key = payload.match_key
            existing.department_id = payload.department_id
            existing.quantity = payload.quantity
            existing.transaction_date = payload.transaction_date
            existing.reason = reason
            existing.status = PendingStatus.PENDING
            self.db.flush()
            return IngestOutcome(
                status="flagged",
                detail=reason,
                pending_id=existing.id,
            )

        pending = PendingAutoCalculation(
            source_type=payload.source_type,
            source_record_id=payload.source_record_id,
            source_reference=payload.source_reference,
            match_key=payload.match_key,
            department_id=payload.department_id,
            quantity=payload.quantity,
            transaction_date=payload.transaction_date,
            reason=reason,
            status=PendingStatus.PENDING,
        )
        self.pending.create(pending)
        return IngestOutcome(status="flagged", detail=reason, pending_id=pending.id)

    def _resolve_pending(self, payload: SourceRecordIngest) -> None:
        pending = self.pending.find_by_source(
            payload.source_type, payload.source_record_id
        )
        if pending is not None and pending.status is not PendingStatus.RESOLVED:
            pending.status = PendingStatus.RESOLVED

    def _ensure_department(self, department_id: int | None) -> None:
        if department_id is None:
            return
        if self.db.get(Department, department_id) is None:
            raise AutoEmissionValidationError(f"Department {department_id} not found")

    def retry_pending(self, pending_id: int) -> IngestOutcome:
        """Re-run the engine for a parked record (e.g. after adding a mapping)."""
        pending = self.pending.get(pending_id)
        if pending is None:
            raise AutoEmissionValidationError(f"Pending record {pending_id} not found")
        payload = SourceRecordIngest(
            source_type=pending.source_type,
            source_record_id=pending.source_record_id,
            match_key=pending.match_key,
            quantity=pending.quantity,
            transaction_date=pending.transaction_date,
            department_id=pending.department_id,
            source_reference=pending.source_reference,
        )
        return self.ingest(payload)
