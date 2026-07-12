"""API dependencies (Database, Auth, etc.)."""
from collections.abc import Generator

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User


def get_db() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Mock dependency for the hackathon. 
    In a real app, this would extract the JWT token from the Authorization header,
    decode it, and fetch the user. For now, we return 'jane.smith@ecosphere.dev',
    who is a standard employee with some XP already.
    """
    # Using jane.smith for testing gamification as she's an employee with XP
    user = db.query(User).filter(User.email == "jane.smith@ecosphere.dev").first()
    if not user:
        # Fallback to the first user if seed data changed
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=401, detail="No users found in database.")
    return user


def get_current_manager(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that ensures the current user is a manager (for approvals)."""
    # For demo purposes, we'll fetch the ESG Manager
    # In a real app, we'd check current_user.role
    from app.models.user import UserRole
    if current_user.role not in [UserRole.SYSTEM_ADMIN, UserRole.ESG_MANAGER, UserRole.DEPT_MANAGER]:
        raise HTTPException(status_code=403, detail="Manager access required.")
    return current_user
