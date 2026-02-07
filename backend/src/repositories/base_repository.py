from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Base repository class providing common CRUD operations
    """

    def __init__(self, model: T, db_session: Session):
        self.model = model
        self.db_session = db_session

    def create(self, obj: T) -> T:
        """Create a new object in the database"""
        try:
            self.db_session.add(obj)
            self.db_session.commit()
            self.db_session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise e

    def get_by_id(self, id: int) -> Optional[T]:
        """Get an object by its ID"""
        return self.db_session.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all objects with pagination"""
        return self.db_session.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update an object by ID with the provided fields"""
        try:
            obj = self.get_by_id(id)
            if obj:
                for key, value in kwargs.items():
                    setattr(obj, key, value)
                self.db_session.commit()
                self.db_session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise e

    def delete(self, id: int) -> bool:
        """Delete an object by ID"""
        try:
            obj = self.get_by_id(id)
            if obj:
                self.db_session.delete(obj)
                self.db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise e