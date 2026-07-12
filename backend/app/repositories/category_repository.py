"""Data access helpers for Category records."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.category import Category, CategoryStatus, CategoryType


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        *,
        category_type: Optional[CategoryType] = None,
        status: Optional[CategoryStatus] = None,
    ) -> list[Category]:
        query = self.db.query(Category)
        if category_type is not None:
            query = query.filter(Category.type == category_type)
        if status is not None:
            query = query.filter(Category.status == status)
        return query.order_by(Category.name.asc(), Category.id.asc()).all()

    def get(self, category_id: int) -> Optional[Category]:
        return self.db.get(Category, category_id)

    def get_by_name_and_type(
        self, name: str, category_type: CategoryType
    ) -> Optional[Category]:
        return (
            self.db.query(Category)
            .filter(Category.name == name, Category.type == category_type)
            .one_or_none()
        )

    def create(self, category: Category) -> Category:
        self.db.add(category)
        self.db.flush()
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
