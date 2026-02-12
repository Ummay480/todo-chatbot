from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..repositories.task_repository import TaskRepository
from ..models.Task import Task

class TaskService:
    """Service layer for task business logic"""

    def __init__(self, db: Session):
        self.repository = TaskRepository(db)

    def create_task(self, user_id: int, title: str, description: Optional[str] = None,
                    priority: str = "medium", due_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Create a new task"""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        if priority not in ["low", "medium", "high"]:
            priority = "medium"

        task = self.repository.create(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            priority=priority,
            due_date=due_date
        )

        return task.to_dict()

    def get_task(self, task_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific task"""
        task = self.repository.get_by_id(task_id, user_id)
        return task.to_dict() if task else None

    def list_tasks(self, user_id: int, filter_type: str = "all") -> List[Dict[str, Any]]:
        """List tasks with optional filtering"""
        if filter_type == "completed":
            tasks = self.repository.get_all_by_user(user_id, completed=True)
        elif filter_type == "pending":
            tasks = self.repository.get_all_by_user(user_id, completed=False)
        else:  # "all"
            tasks = self.repository.get_all_by_user(user_id)

        return [task.to_dict() for task in tasks]

    def update_task(self, task_id: int, user_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a task"""
        if "title" in kwargs and not kwargs["title"].strip():
            raise ValueError("Task title cannot be empty")

        if "priority" in kwargs and kwargs["priority"] not in ["low", "medium", "high"]:
            kwargs["priority"] = "medium"

        task = self.repository.update(task_id, user_id, **kwargs)
        return task.to_dict() if task else None

    def complete_task(self, task_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Mark a task as completed"""
        task = self.repository.mark_completed(task_id, user_id)
        return task.to_dict() if task else None

    def uncomplete_task(self, task_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Mark a task as incomplete"""
        task = self.repository.mark_incomplete(task_id, user_id)
        return task.to_dict() if task else None

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Delete a task"""
        return self.repository.delete(task_id, user_id)

    def get_task_statistics(self, user_id: int) -> Dict[str, int]:
        """Get task statistics for a user"""
        total = self.repository.count_by_user(user_id)
        completed = self.repository.count_by_user(user_id, completed=True)
        pending = self.repository.count_by_user(user_id, completed=False)

        return {
            "total": total,
            "completed": completed,
            "pending": pending
        }
