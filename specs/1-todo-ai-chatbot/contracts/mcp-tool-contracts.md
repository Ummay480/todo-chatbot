# MCP Tool Contracts: Todo AI Chatbot

## Tool: add_task

### Purpose
Create a new task for the specified user.

### Parameters
```json
{
  "user_id": "string (required)",
  "title": "string (required)",
  "description": "string (optional)"
}
```

### Returns
```json
{
  "task_id": "integer",
  "status": "string (created)",
  "title": "string"
}
```

### Example Input
```json
{
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

### Example Output
```json
{
  "task_id": 5,
  "status": "created",
  "title": "Buy groceries"
}
```

---

## Tool: list_tasks

### Purpose
Retrieve tasks from the list with optional filtering by status.

### Parameters
```json
{
  "user_id": "string (required)",
  "status": "string (optional: all, pending, completed)"
}
```

### Returns
```json
{
  "tasks": [
    {
      "id": "integer",
      "title": "string",
      "completed": "boolean",
      "description": "string"
    }
  ]
}
```

### Example Input
```json
{
  "user_id": "user123",
  "status": "pending"
}
```

### Example Output
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "completed": false,
    "description": "Milk, eggs, bread"
  }
]
```

---

## Tool: complete_task

### Purpose
Mark a task as complete.

### Parameters
```json
{
  "user_id": "string (required)",
  "task_id": "integer (required)"
}
```

### Returns
```json
{
  "task_id": "integer",
  "status": "string (completed)",
  "title": "string"
}
```

### Example Input
```json
{
  "user_id": "user123",
  "task_id": 3
}
```

### Example Output
```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom"
}
```

---

## Tool: delete_task

### Purpose
Remove a task from the list.

### Parameters
```json
{
  "user_id": "string (required)",
  "task_id": "integer (required)"
}
```

### Returns
```json
{
  "task_id": "integer",
  "status": "string (deleted)",
  "title": "string"
}
```

### Example Input
```json
{
  "user_id": "user123",
  "task_id": 2
}
```

### Example Output
```json
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task"
}
```

---

## Tool: update_task

### Purpose
Modify task title or description.

### Parameters
```json
{
  "user_id": "string (required)",
  "task_id": "integer (required)",
  "title": "string (optional)",
  "description": "string (optional)"
}
```

### Returns
```json
{
  "task_id": "integer",
  "status": "string (updated)",
  "title": "string"
}
```

### Example Input
```json
{
  "user_id": "user123",
  "task_id": 1,
  "title": "Buy groceries and fruits"
}
```

### Example Output
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

---

## Error Handling

All MCP tools follow the same error handling pattern:

### Error Response Format
```json
{
  "error": {
    "type": "string",
    "message": "string",
    "status": "string (error)"
  }
}
```

### Common Error Types
- `invalid_user_id`: When user_id is malformed or doesn't exist
- `invalid_task_id`: When task_id is malformed or doesn't exist for the user
- `missing_required_parameter`: When required parameters are not provided
- `access_denied`: When user tries to access resources they don't own