"""Business logic for manually logging CarbonTransaction records."""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.carbon_transaction import (
    CarbonTransaction,
    CreatedBy,
    SourceType,
    TransactionStatus,
)
from app.models.department import Department
from app.models.emission_factor import EmissionFactor
from app.repositories.carbon_transaction_repository import CarbonTransactionRepository
from app.schemas.carbon_transaction import CarbonTransactionCreateManual, DepartmentCarbonSummary


class CarbonTransactionError(Exception):
    pass


class CarbonTransactionNotFoundError(CarbonTransactionError):
    pass


class CarbonTransactionValidationError(CarbonTransactionError):
    pass


class CarbonTransactionService:
    def __init__(self, db: Session):
        self.repo = CarbonTransactionRepository(db)

    def list_transactions(
        self,
        *,
        department_id: Optional[int] = None,
        source_type: Optional[SourceType] = None,
        status: Optional[TransactionStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[CarbonTransaction]:
        return self.repo.list(
            department_id=department_id,
            source_type=source_type,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

    def summarize_by_department(
        self,
        *,
        source_type: Optional[SourceType] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[DepartmentCarbonSummary]:
        rows = self.repo.aggregate_by_department(
            source_type=source_type, date_from=date_from, date_to=date_to
        )
        return [
            DepartmentCarbonSummary(
                department_id=department_id,
                department_name=department_name,
                transaction_count=count,
                total_co2e=total_co2e,
            )
            for department_id, department_name, count, total_co2e in rows
        ]

    def get_transaction(self, transaction_id: int) -> CarbonTransaction:
        transaction = self.repo.get(transaction_id)
        if transaction is None:
            raise CarbonTransactionNotFoundError(f"Carbon transaction {transaction_id} not found")
        return transaction

    def create_manual_transaction(self, payload: CarbonTransactionCreateManual) -> CarbonTransaction:
        self._ensure_department(payload.department_id)
        factor = self._ensure_active_factor(payload.emission_factor_id, payload.transaction_date)

        transaction = CarbonTransaction(
            department_id=payload.department_id,
            source_type=payload.source_type,
            transaction_date=payload.transaction_date,
            emission_factor_id=factor.id,
            emission_factor=factor,
            source_reference=payload.source_reference,
            notes=payload.notes,
            created_by=CreatedBy.MANUAL,
            status=TransactionStatus.CONFIRMED,
        )
        # Setting factor_value then quantity derives co2e via the model's property setters.
        transaction.factor_value = factor.co2e_per_unit
        transaction.quantity = payload.quantity
        return self.repo.create(transaction)

    def _ensure_department(self, department_id: Optional[int]) -> Optional[Department]:
        if department_id is None:
            return None
        department = self.repo.db.get(Department, department_id)
        if department is None:
            raise CarbonTransactionValidationError(f"Department {department_id} not found")
        return department

    def _ensure_active_factor(self, emission_factor_id: int, transaction_date: date) -> EmissionFactor:
        factor = self.repo.db.get(EmissionFactor, emission_factor_id)
        if factor is None:
            raise CarbonTransactionValidationError(
                f"Emission factor {emission_factor_id} not found"
            )
        if not factor.is_effective_on(transaction_date):
            raise CarbonTransactionValidationError(
                f"Emission factor '{factor.factor_code}' is not active as of {transaction_date}"
            )
        return factor
