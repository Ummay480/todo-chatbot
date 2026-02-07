# Data Model: Todo AI Chatbot

## Entity: Task
**Description**: Represents a todo item with user-specific data

**Fields**:
- `id`: integer (primary key, auto-increment)
- `user_id`: string (foreign key to user, required for multi-tenant isolation)
- `title`: string (task title, required, max 255 chars)
- `description`: string (optional task description, max 1000 chars)
- `completed`: boolean (task completion status, default false)
- `created_at`: datetime (timestamp when task was created)
- `updated_at`: datetime (timestamp when task was last updated)

**Validation Rules**:
- Title must not be empty
- User_id must exist and be valid
- Created_at and updated_at are automatically managed

**State Transitions**:
- `pending` → `completed` (via complete_task MCP tool)
- `completed` → `pending` (via update_task MCP tool with completed=false)

## Entity: Conversation
**Description**: Represents a user chat session with timestamps

**Fields**:
- `id`: integer (primary key, auto-increment)
- `user_id`: string (foreign key to user, required for multi-tenant isolation)
- `created_at`: datetime (timestamp when conversation was started)
- `updated_at`: datetime (timestamp when conversation was last active)

**Validation Rules**:
- User_id must exist and be valid
- Created_at is set on creation
- Updated_at is automatically updated on any interaction

## Entity: Message
**Description**: Represents individual conversation exchanges with content and timestamps

**Fields**:
- `id`: integer (primary key, auto-increment)
- `conversation_id`: integer (foreign key to conversation, required)
- `user_id`: string (foreign key to user, required for multi-tenant isolation)
- `role`: enum (user or assistant, required)
- `content`: text (message content, required)
- `created_at`: datetime (timestamp when message was created)

**Validation Rules**:
- Conversation_id must exist
- User_id must exist and be valid
- Role must be either 'user' or 'assistant'
- Content must not be empty
- Created_at is automatically managed

## Relationships
- Conversation (1) → Messages (many) via conversation_id foreign key
- User (1) → Conversations (many) via user_id foreign key
- User (1) → Tasks (many) via user_id foreign key
- User (1) → Messages (many) via user_id foreign key

## Indexes
- Index on user_id for all entities (for multi-tenant queries)
- Index on conversation_id for Message entity (for conversation retrieval)
- Index on completed field for Task entity (for filtering)
- Index on updated_at for Conversation entity (for recent conversations)