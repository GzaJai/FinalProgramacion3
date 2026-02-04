from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository for User entity with email lookup"""

    def __init__(self, session: Session):
        super().__init__(model=User, session=session)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address
        
        Args:
            email: User's email address
            
        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        return self.session.scalars(stmt).first()

    def email_exists(self, email: str) -> bool:
        """
        Check if email already exists in database
        
        Args:
            email: Email to check
            
        Returns:
            True if email exists, False otherwise
        """
        stmt = select(User.id).where(User.email == email)
        return self.session.scalars(stmt).first() is not None