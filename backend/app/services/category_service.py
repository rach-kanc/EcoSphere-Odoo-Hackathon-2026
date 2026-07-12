"""Business logic for Category CRUD."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.category import Category, CategoryStatus, CategoryType
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryError(Exception):
    pass


class CategoryNotFoundError(CategoryError):
    pass


class CategoryTypeNotAllowedError(CategoryError):
    pass


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def list_categories(
        self,
        *,
        category_type: CategoryType | None = None,
        status: CategoryStatus | None = None,
    ) -> list[Category]:
        return self.repo.list(category_type=category_type, status=status)

    def get_category(self, category_id: int) -> Category:
        category = self.repo.get(category_id)
        if category is None:
            raise CategoryNotFoundError(f"Category {category_id} not found")
        return category

    def create_category(self, payload: CategoryCreate) -> Category:
        self._ensure_social_type(payload.type)
        category = Category(
            name=payload.name,
            type=payload.type,
            status=payload.status,
        )
        return self.repo.create(category)

    def update_category(self, category_id: int, payload: CategoryUpdate) -> Category:
        category = self.get_category(category_id)
        if payload.type is not None:
            self._ensure_social_type(payload.type)
            category.type = payload.type
        if payload.name is not None:
            category.name = payload.name
        if payload.status is not None:
            category.status = payload.status
        self.repo.db.flush()
        return category

    def delete_category(self, category_id: int) -> None:
        category = self.get_category(category_id)
        self.repo.delete(category)

    def seed_default_csr_categories(self, names: list[str]) -> list[Category]:
        categories: list[Category] = []
        for name in names:
            existing = self.repo.get_by_name_and_type(name, CategoryType.CSR_ACTIVITY)
            if existing is not None:
                categories.append(existing)
                continue
            categories.append(
                self.repo.create(
                    Category(
                        name=name,
                        type=CategoryType.CSR_ACTIVITY,
                        status=CategoryStatus.ACTIVE,
                    )
                )
            )
        return categories

    @staticmethod
    def _ensure_social_type(category_type: CategoryType) -> None:
        if category_type is not CategoryType.CSR_ACTIVITY:
            raise CategoryTypeNotAllowedError(
                "Categories can only be created or updated with type CSR_ACTIVITY"
            )
