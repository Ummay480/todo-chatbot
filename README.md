# Todo App Chatbot

An AI-powered todo management system with a natural language chatbot interface. Built with FastAPI, Next.js, and OpenAI's GPT models.

## Overview

This project is a conversational AI assistant that helps users manage their todo tasks through natural language. Instead of clicking buttons and filling forms, users can simply chat with the AI to add, view, update, complete, and delete tasks.

## Key Features

- **Natural Language Interface**: Interact with your todo list using conversational language
- **AI-Powered Task Management**: OpenAI GPT models understand context and intent
- **Function Calling**: AI automatically executes task operations based on user requests
- **Conversation History**: Maintains context across multiple messages
- **User Authentication**: Secure JWT-based authentication with BetterAuth
- **RESTful API**: Clean API architecture with FastAPI
- **Modern Frontend**: Responsive React/Next.js interface with Tailwind CSS

## Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: OpenAI API with function calling
- **Authentication**: JWT tokens with BetterAuth
- **Vector DB** (Optional): Qdrant for conversation context embeddings

### Frontend (TypeScript/Next.js)
- **Framework**: Next.js 14 with App Router
- **UI**: React with Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios

## Project Structure

```
todo-app-chatbot/
├── backend/
│   └── src/
│       ├── api/v1/
│       │   ├── chat_api.py          # Chat endpoint with AI integration
│       │   ├── auth_api.py          # Authentication endpoints
│       │   └── health_api.py        # Health check endpoints
│       ├── models/
│       │   ├── User.py              # User model
│       │   ├── Task.py              # Task model
│       │   ├── Conversation.py      # Conversation model
│       │   └── Message.py           # Message model
│       ├── services/
│       │   ├── task_service.py      # Task business logic
│       │   ├── conversation_service.py
│       │   └── auth_service.py
│       ├── repositories/
│       │   ├── task_repository.py   # Task data access
│       │   ├── conversation_repository.py
│       │   └── message_repository.py
│       ├── mcp_tools/
│       │   ├── task_tools.py        # MCP tool implementations
│       │   └── tool_definitions.py  # OpenAI function definitions
│       ├── database/
│       │   └── connection.py        # Database setup
│       └── main.py                  # FastAPI application
├── frontend/
│   └── apps/web/
│       └── src/
│           ├── app/
│           │   └── page.tsx         # Main chat page
│           └── components/chat/
│               ├── ChatInterface.tsx # Main chat component
│               ├── MessageBubble.tsx # Message display
│               └── InputBox.tsx     # Message input
├── .env.example                     # Environment variables template
├── package.json                     # Root package.json
└── README.md                        # This file
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL database
- OpenAI API key

### 1. Clone and Navigate

```bash
cd D:\AIDD\todo-app-chatbot
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/todo_chatbot"

# OpenAI (Required)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000

# Optional: Qdrant for conversation embeddings
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 3. Backend Setup

```bash
cd backend

# Install dependencies
pip install -e .

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### 4. Frontend Setup

```bash
cd frontend/apps/web

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### Chat Interface

1. Open `http://localhost:3000` in your browser
2. Start chatting with the AI assistant

### Example Conversations

**Adding Tasks:**
```
User: Add a task to buy groceries tomorrow
AI: Task 'Buy groceries tomorrow' added successfully with medium priority.

User: Create a high priority task to finish the project report by Friday
AI: I've added a high priority task "Finish project report" with a due date of Friday.
```

**Viewing Tasks:**
```
User: Show me all my tasks
AI: You have 5 tasks:
1. Buy groceries tomorrow (pending, medium priority)
2. Finish project report (pending, high priority, due Friday)
...

User: What are my pending tasks?
AI: You have 3 pending tasks: ...
```

**Completing Tasks:**
```
User: Mark task 1 as completed
AI: Task 'Buy groceries tomorrow' marked as completed!

User: I finished the project report
AI: Great! I've marked task 2 'Finish project report' as completed.
```

**Updating Tasks:**
```
User: Change the priority of task 3 to high
AI: Task 'Call dentist' priority updated to high.

User: Update task 5 description to include meeting notes
AI: Task updated successfully with the new description.
```

**Deleting Tasks:**
```
User: Delete task 4
AI: Task 'Old reminder' deleted successfully.
```

**Statistics:**
```
User: How many tasks do I have?
AI: You have 5 total tasks: 2 completed and 3 pending.
```

## API Endpoints

### Chat API

**POST** `/api/v1/chat/message`
- Send a message to the chatbot
- Request body: `{ "message": "string", "conversation_id": number | null }`
- Response: `{ "response": "string", "conversation_id": number }`

**GET** `/api/v1/chat/conversations`
- List all conversations for the current user

**GET** `/api/v1/chat/conversations/{id}`
- Get a specific conversation with messages

**DELETE** `/api/v1/chat/conversations/{id}`
- Delete a conversation

### Authentication API

**POST** `/api/v1/auth/register`
- Register a new user

**POST** `/api/v1/auth/login`
- Login and get JWT token

**GET** `/api/v1/auth/profile`
- Get current user profile

## Key Modifications from Original Project

This project was adapted from a petrol pump ledger automation system. Here are the major changes:

### Removed Components
- ❌ OCR services (Tesseract integration)
- ❌ Image processing services
- ❌ Ledger-specific models (LedgerPage, SalesEntry, DailyReport, etc.)
- ❌ Table detection and column identification services
- ❌ PDF/CSV export services
- ❌ Image upload endpoints
- ❌ Dependencies: pillow, opencv-python, tesseract, pandas, numpy

### Added Components
- ✅ Task, Conversation, and Message models
- ✅ OpenAI API integration with function calling
- ✅ MCP tools for task operations
- ✅ Chat API endpoint
- ✅ Conversation management services
- ✅ Chat interface components (React)
- ✅ Natural language processing for task management

### Modified Components
- 🔄 User model (removed pump_name, pump_location fields)
- 🔄 Main application (updated title, description, routes)
- 🔄 Frontend page (replaced ledger UI with chat interface)
- 🔄 Configuration files (updated dependencies and environment variables)

### Retained Components
- ✅ Authentication system (JWT, BetterAuth)
- ✅ Database layer (SQLAlchemy, PostgreSQL)
- ✅ API infrastructure (FastAPI, CORS, middleware)
- ✅ Utilities (logging, monitoring)

## Database Schema

### Users Table
- id, name, email, password_hash, phone_number
- language_preference, is_active
- created_at, updated_at

### Tasks Table
- id, user_id, title, description
- completed, priority, due_date
- created_at, updated_at, completed_at

### Conversations Table
- id, user_id, title
- created_at, updated_at

### Messages Table
- id, conversation_id, user_id
- role (user/assistant), content
- created_at

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend/apps/web
npm test
```

### Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure OpenAI API key is set
- Run `pip install -e .` to install dependencies

### Frontend won't connect to backend
- Verify backend is running on port 8000
- Check CORS settings in backend/src/main.py
- Update API_BASE_URL in ChatInterface.tsx if needed

### AI responses are slow
- OpenAI API calls can take 2-5 seconds
- Consider using gpt-3.5-turbo for faster responses
- Check your OpenAI API rate limits

### Database errors
- Run migrations: `alembic upgrade head`
- Check database connection string
- Verify PostgreSQL user has proper permissions

## Future Enhancements

- [ ] Task categories and tags
- [ ] Recurring tasks
- [ ] Task reminders and notifications
- [ ] Voice input support
- [ ] Mobile app
- [ ] Task sharing and collaboration
- [ ] Advanced analytics and insights
- [ ] Integration with calendar apps
- [ ] Bulk task operations
- [ ] Task templates

## License

MIT

## Support

For issues and questions, please open an issue on the project repository.
