# Research: Todo AI Chatbot Implementation

## Decision: MCP-First Architecture with OpenAI Agents SDK
**Rationale**: The constitution requires MCP-first architecture for standardized, auditable interfaces. OpenAI Agents SDK provides native support for tool calling, which aligns perfectly with the requirement to expose task operations as MCP tools.

**Alternatives considered**:
- Direct API calls without MCP tools (violates constitution)
- Custom AI framework without tool calling (violates constitution)

## Decision: Stateless Server Design with PostgreSQL
**Rationale**: The constitution mandates stateless server architecture for horizontal scaling, resilience, and testability. PostgreSQL provides reliable persistence for conversation history and task data across service interruptions.

**Alternatives considered**:
- In-memory session storage (violates constitution)
- File-based persistence (less scalable than database)

## Decision: FastAPI for Backend Framework
**Rationale**: FastAPI is a modern Python web framework that supports async operations, has excellent performance characteristics, and integrates well with the required technology stack (SQLModel, PostgreSQL).

**Alternatives considered**:
- Flask (less performant, fewer built-in features)
- Django (heavier than needed for API-only service)

## Decision: SQLModel for ORM
**Rationale**: SQLModel combines SQLAlchemy and Pydantic, providing type safety and validation while maintaining compatibility with the Python ecosystem. It's specifically mentioned in the constitution as mandatory.

**Alternatives considered**:
- Pure SQLAlchemy (no Pydantic integration)
- Tortoise ORM (async-only, doesn't match constitution requirement)

## Decision: MCP Tool Design Patterns
**Rationale**: MCP tools will follow single responsibility principle with clear parameter schemas and return types. Each tool handles one action (add_task, list_tasks, etc.) and returns structured JSON with consistent status fields.

**Implementation approach**:
- Each tool follows verb-noun naming convention
- Tools return structured data with clear field types
- Tools handle errors gracefully with status messages
- Tools support user_id for multi-tenant isolation

## Decision: Conversation Flow Architecture
**Rationale**: The stateless architecture requires that each request reconstructs conversation context from the database. The flow will be: receive message → load conversation state → run agent with MCP tools → persist response → return result.

**Implementation approach**:
- Each API call fetches all required context from database
- No in-memory state between requests
- Conversation continuity maintained through database persistence