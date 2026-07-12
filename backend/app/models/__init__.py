"""ORM models package.

Importing model modules here ensures they are registered on ``Base.metadata``
so tools like Alembic autogenerate and ``Base.metadata.create_all`` can see them.
"""
from app.models.carbon_transaction import (  # noqa: F401
    CarbonTransaction,
    CreatedBy,
    SourceType,
    TransactionStatus,
)
from app.models.category import Category, CategoryStatus, CategoryType  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.emission_factor import (  # noqa: F401
    ActivityType,
    EmissionFactor,
    FactorStatus,
)

__all__ = [
    "ActivityType",
    "CarbonTransaction",
    "Category",
    "CategoryStatus",
    "CategoryType",
    "CreatedBy",
    "Department",
    "EmissionFactor",
    "FactorStatus",
    "SourceType",
    "TransactionStatus",
]
