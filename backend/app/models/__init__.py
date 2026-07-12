"""ORM models package.

Importing model modules here ensures they are registered on ``Base.metadata``
so tools like Alembic autogenerate and ``Base.metadata.create_all`` can see them.
"""
from app.models.emission_factor import (  # noqa: F401
    ActivityType,
    EmissionFactor,
    FactorStatus,
)

__all__ = ["ActivityType", "EmissionFactor", "FactorStatus"]
