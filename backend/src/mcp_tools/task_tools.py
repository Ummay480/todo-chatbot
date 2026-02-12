"""
MCP Tools for Task Operations
These functions are designed to be used as tools by the OpenAI agent
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

def add_task_tool(db: Session, user_id: int, title: str, description: Optional[str] = None,
                  priority: str = "medium", due_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a new task to the user's todo list.

    Args:
        db: Database session
        user_id: ID of the user
        title: Task title (required)
        description: Optional task description
        priority: Task priority (low, medium, high)
        due_date: Optional due date in ISO format (YYYY-MM-DD)

    Returns:
        Dictionary with task details
    """
    from ..services.task_service import TaskService

    task_service = TaskService(db)

    # Parse due_date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date)
        except ValueError:
            pass

    try:
        task = task_service.create_task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=parsed_due_date
        )
        return {
            "success": True,
            "message": f"Task '{title}' added successfully",
            "task": task
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to add task: {str(e)}"
        }


def list_tasks_tool(db: Session, user_id: int, filter_type: str = "all") -> Dict[str, Any]:
    """
    List tasks for the user.

    Args:
        db: Database session
        user_id: ID of the user
        filter_type: Filter type - "all", "pending", or "completed"

    Returns:
        Dictionary with list of tasks
    """
    from ..services.task_service import TaskService

    task_service = TaskService(db)

    try:
        tasks = task_service.list_tasks(user_id, filter_type)
        stats = task_service.get_task_statistics(user_id)

        return {
            "success": True,
            "filter": filter_type,
            "tasks": tasks,
            "statistics": stats,
            "message": f"Found {len(tasks)} {filter_type} task(s)"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to list tasks: {str(e)}"
        }


def complete_task_tool(db: Session, user_id: int, task_id: int) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        db: Database session
        user_id: ID of the user
        task_id: ID of the task to complete

    Returns:
        Dictionary with updated task details
    """
    from ..services.task_service import TaskService

    task_service = TaskService(db)

    try:
        task = task_service.complete_task(task_id, user_id)
        if task:
            return {
                "success": True,
                "message": f"Task '{task['title']}' marked as completed",
                "task": task
            }
        else:
            return {
                "success": False,
                "message": "Task not found"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to complete task: {str(e)}"
        }


def delete_task_tool(db: Session, user_id: int, task_id: int) -> Dict[str, Any]:
    """
    Delete a task.

    Args:
        db: Database session
        user_id: ID of the user
        task_id: ID of the task to delete

    Returns:
        Dictionary with deletion status
    """
    from ..services.task_service import TaskService

    task_service = TaskService(db)

    try:
        # Get task details before deletion
        task = task_service.get_task(task_id, user_id)
        if not task:
            return {
                "success": False,
                "message": "Task not found"
            }

        title = task['title']
        success = task_service.delete_task(task_id, user_id)

        if success:
            return {
                "success": True,
                "message": f"Task '{title}' deleted successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to delete task"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to delete task: {str(e)}"
        }


def update_task_tool(db: Session, user_id: int, task_id: int,
                     title: Optional[str] = None, description: Optional[str] = None,
                     priority: Optional[str] = None, due_date: Optional[str] = None,
                     completed: Optional[bool] = None) -> Dict[str, Any]:
    """
    Update a task's details.

    Args:
        db: Database session
        user_id: ID of the user
        task_id: ID of the task to update
        title: New task title
        description: New task description
        priority: New priority (low, medium, high)
        due_date: New due date in ISO format
        completed: New completion status

    Returns:
        Dictionary with updated task details
    """
    from ..services.task_service import TaskService

    task_service = TaskService(db)

    try:
        # Build update dictionary
        updates = {}
        if title is not None:
            updates['title'] = title
        if description is not None:
            updates['description'] = description
        if priority is not None:
            updates['priority'] = priority
        if due_date is not None:
            try:
                updates['due_date'] = datetime.fromisoformat(due_date)
            except ValueError:
                pass
        if completed is not None:
            updates['completed'] = completed
            if completed:
                updates['completed_at'] = datetime.utcnow()
            else:
                updates['completed_at'] = None

        if not updates:
            return {
                "success": False,
                "message": "No updates provided"
            }

        task = task_service.update_task(task_id, user_id, **updates)

        if task:
            return {
                "success": True,
                "message": f"Task '{task['title']}' updated successfully",
                "task": task
            }
        else:
            return {
                "success": False,
                "message": "Task not found"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to update task: {str(e)}"
        }


def get_task_statistics_tool(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get task statistics for the user.

    Args:
        db: Database session
        user_id: ID of the user

    Returns:
        Dictionary with task statistics
    """
    from ..services.task_service import TaskService

    task_service = TaskService(db)

    try:
        stats = task_service.get_task_statistics(user_id)
        return {
            "success": True,
            "statistics": stats,
            "message": f"You have {stats['total']} total tasks: {stats['completed']} completed, {stats['pending']} pending"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get statistics: {str(e)}"
        }
