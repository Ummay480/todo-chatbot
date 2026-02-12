from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.Task import Task

class TaskRepository:
    """Repository for Task data access operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, title: str, description: Optional[str] = None,
               priority: str = "medium", due_date: Optional[datetime] = None) -> Task:
        """Create a new task"""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            completed=False
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        """Get a task by ID for a specific user"""
        return self.db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

    def get_all_by_user(self, user_id: int, completed: Optional[bool] = None) -> List[Task]:
        """Get all tasks for a user, optionally filtered by completion status"""
        query = self.db.query(Task).filter(Task.user_id == user_id)

        if completed is not None:
            query = query.filter(Task.completed == completed)

        return query.order_by(Task.created_at.desc()).all()

    def update(self, task_id: int, user_id: int, **kwargs) -> Optional[Task]:
        """Update a task"""
        task = self.get_by_id(task_id, user_id)
        if not task:
            return None

        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task

    def mark_completed(self, task_id: int, user_id: int) -> Optional[Task]:
        """Mark a task as completed"""
        task = self.get_by_id(task_id, user_id)
        if not task:
            return None

        task.completed = True
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task

    def mark_incomplete(self, task_id: int, user_id: int) -> Optional[Task]:
        """Mark a task as incomplete"""
        task = self.get_by_id(task_id, user_id)
        if not task:
            return None

        task.completed = False
        task.completed_at = None
        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task_id: int, user_id: int) -> bool:
        """Delete a task"""
        task = self.get_by_id(task_id, user_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

    def count_by_user(self, user_id: int, completed: Optional[bool] = None) -> int:
        """Count tasks for a user"""
        query = self.db.query(Task).filter(Task.user_id == user_id)

        if completed is not None:
            query = query.filter(Task.completed == completed)

        return query.count()
