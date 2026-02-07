# Quickstart Guide: Todo AI Chatbot

## Overview
This guide provides the essential information to get the Todo AI Chatbot up and running. The system follows MCP-first architecture with stateless server design.

## Prerequisites
- Python 3.11+
- PostgreSQL database
- OpenAI API key
- MCP server environment

## Setup Steps

### 1. Environment Setup
```bash
# Clone the repository
git clone <repo-url>
cd <repo-directory>

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration
```bash
# Set up PostgreSQL database
createdb todo_chatbot_dev

# Configure environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/todo_chatbot_dev"
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. Run Database Migrations
```bash
# Apply database schema
python -m backend.src.models.migrate
```

### 4. Start the Services
```bash
# Start the main API server
python -m backend.src.api.main

# In another terminal, start the MCP server
python -m backend.src.mcp_tools.server
```

## Key Components

### MCP Tools
The system exposes the following MCP tools for AI agent consumption:
- `add_task`: Create new tasks
- `list_tasks`: Retrieve tasks with filtering
- `complete_task`: Mark tasks as completed
- `delete_task`: Remove tasks
- `update_task`: Modify task details

### API Endpoints
- `POST /api/{user_id}/chat`: Main chat interface

## Testing the System
```bash
# Send a test message
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

## Architecture Notes
- **Stateless Design**: Each request loads conversation state from the database
- **MCP-First**: All operations go through MCP tools
- **Multi-Tenant**: User isolation via user_id scoping
- **Persistent Storage**: All data stored in PostgreSQL

## Troubleshooting
- If the server returns 500 errors, check that the MCP server is running
- If conversations don't persist, verify database connection settings
- If AI responses are slow, check OpenAI API key and rate limits