# API Contract: Todo AI Chatbot

## Endpoint: POST /api/{user_id}/chat

### Description
Main chat endpoint that accepts natural language input from users and returns AI-generated responses with appropriate MCP tool invocations.

### Request
**Method**: POST
**Path**: `/api/{user_id}/chat`

**Path Parameters**:
- `user_id` (string, required): Unique identifier for the user

**Request Body**:
```json
{
  "conversation_id": "integer (optional)",
  "message": "string (required)"
}
```

**Request Body Parameters**:
- `conversation_id`: Existing conversation ID (creates new if not provided)
- `message`: Natural language input from user

### Response
**Success Response (200 OK)**:
```json
{
  "conversation_id": "integer",
  "response": "string",
  "tool_calls": [
    {
      "tool_name": "string",
      "parameters": "object",
      "result": "object"
    }
  ]
}
```

**Response Parameters**:
- `conversation_id`: Active conversation ID (newly created or existing)
- `response`: AI assistant message to user
- `tool_calls`: Array of MCP tools invoked during processing

**Error Response (400 Bad Request)**:
```json
{
  "error": "string",
  "message": "string"
}
```

### Example Requests/Responses

**Request**:
```json
{
  "message": "Add a task to buy groceries"
}
```

**Response**:
```json
{
  "conversation_id": 123,
  "response": "I've added the task 'buy groceries' for you.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "parameters": {
        "user_id": "user123",
        "title": "buy groceries",
        "description": null
      },
      "result": {
        "task_id": 456,
        "status": "created",
        "title": "buy groceries"
      }
    }
  ]
}
```

## Authentication
All requests require user authentication via the user_id in the path parameter. Multi-tenant isolation is enforced by ensuring all operations are scoped to the authenticated user.

## Rate Limiting
Requests are rate-limited per user_id to prevent abuse and ensure fair usage across all users.

## Validation
- Request message must not be empty
- User_id must be valid and exist in the system
- Conversation_id must be valid if provided