"""ORM models package.

Importing model modules here ensures they are registered on ``Base.metadata``
so tools like Alembic autogenerate and ``Base.metadata.create_all`` can see them.
"""
from app.models.emission_factor import (  # noqa: F401
    ActivityType,
    EmissionFactor,
    FactorStatus,
)
from app.models.category import Category, CategoryStatus, CategoryType  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.csr_activity import CSRActivity, CSRActivityStatus  # noqa: F401

__all__ = [
    "ActivityType",
    "EmissionFactor",
    "FactorStatus",
    "Category",
    "CategoryStatus",
    "CategoryType",
    "Department",
    "CSRActivity",
    "CSRActivityStatus",
]
