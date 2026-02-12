"""
Tool definitions for OpenAI function calling
These definitions describe the tools available to the AI agent
"""

TASK_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the user's todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority level of the task"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Optional due date in ISO format (YYYY-MM-DD)"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List tasks for the user with optional filtering",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter_type": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status: all, pending, or completed"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to complete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task from the todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's details",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "New priority level"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in ISO format (YYYY-MM-DD)"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "New completion status"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_task_statistics",
            "description": "Get statistics about the user's tasks (total, completed, pending)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
