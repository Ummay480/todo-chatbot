---
id: 1
title: Create Todo AI Chatbot Spec
stage: spec
date: 2026-01-13
surface: agent
model: claude-haiku-4-5-20251001
feature: todo-ai-chatbot
branch: 1-todo-ai-chatbot
user: user
command: /sp.specify "Todo AI Chatbot (Basic Level) specification"
labels: ["spec", "todo-ai-chatbot", "mcp", "ai-agent"]
links:
  spec: specs/1-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-todo-ai-chatbot/spec.md
 - specs/1-todo-ai-chatbot/checklists/requirements.md
tests:
 - null
---

## Prompt

"/specs/phase-iii-todo-ai-chatbot.spec.md
It follows Spec-Driven Development, MCP-First, and Stateless Server laws.
No implementation, no plans, no tasks — SPEC ONLY ✅

📘 Phase III Specification
Todo AI Chatbot (Basic Level)
Spec Version: 1.0.0
Status: Draft
Phase: III
Constitution: .specify/memory/constitution.md (v1.0.1)
Workflow: Agentic Dev Stack (Spec → Plan → Tasks → Implement)
Manual Coding: ❌ Forbidden

1. Objective
Design and specify an AI-powered Todo Chatbot that allows users to manage todo items using natural language, implemented via:

OpenAI Agents SDK for AI reasoning

Official MCP SDK for tool exposure

Stateless FastAPI backend

Persistent state via Neon PostgreSQL

The system must allow users to:

Create, list, update, complete, and delete todos

Resume conversations after server restarts

Interact only through conversational chat

2. Scope
Included
Conversational Todo management

MCP tool-driven task operations

Stateless chat processing

Database-backed conversation memory

ChatKit-based frontend

Excluded
Voice input

Reminders / notifications

Task prioritization or tagging

Multi-user collaboration

3. Architecture Constraints (Non-Negotiable)
Rule    Requirement
MCP-First    All task operations MUST be MCP tools
Stateless Server    No in-memory session state
Single Chat Endpoint    One POST endpoint for chat
Tool Isolation    Tools cannot call each other
DB Persistence    All state stored in PostgreSQL
Agent Authority    Agent decides tool usage

4. Technology Stack
Component    Technology
Frontend    OpenAI ChatKit
Backend    Python FastAPI
AI Framework    OpenAI Agents SDK
MCP Server    Official MCP SDK
ORM    SQLModel
Database    Neon Serverless PostgreSQL
Auth    Better Auth

5. High-Level Architecture
bash
Copy code
ChatKit UI
   │
   ▼
POST /api/{user_id}/chat
   │
   ▼
OpenAI Agent Runner
   │
   ▼
MCP Server (Tools)
   │
   ▼
Neon PostgreSQL
State Flow Rule:

The server MUST reconstruct state on every request from the database.

6. Data Models
Task
Field    Type
id    integer
user_id    string
title    string
description    string (optional)
completed    boolean
created_at    datetime
updated_at    datetime

Conversation
Field    Type
id    integer
user_id    string
created_at    datetime
updated_at    datetime

Message
Field    Type
id    integer
conversation_id    integer
user_id    string
role    enum(user, assistant)
content    text
created_at    datetime

7. API Specification
Chat Endpoint
POST /api/{user_id}/chat

Request
Field    Required    Description
conversation_id    No    Existing conversation ID
message    Yes    Natural language input

Response
Field    Description
conversation_id    Active conversation ID
response    AI assistant message
tool_calls    MCP tools invoked

8. MCP Tool Specifications
add_task
Purpose: Create a new task

Parameters

user_id (string, required)

title (string, required)

description (string, optional)

Returns

task_id

status

title

list_tasks
Purpose: Retrieve tasks

Parameters

user_id (string, required)

status (optional: all | pending | completed)

Returns

Array of task objects

complete_task
Purpose: Mark task as completed

Parameters

user_id (string, required)

task_id (integer, required)

Returns

task_id

status

title

delete_task
Purpose: Remove a task

Parameters

user_id (string, required)

task_id (integer, required)

Returns

task_id

status

title

update_task
Purpose: Modify task title or description

Parameters

user_id (string, required)

task_id (integer, required)

title (optional)

description (optional)

Returns

task_id

status

title

9. Agent Behavior Specification
User Intent    Agent Action
Add task    Call add_task
List tasks    Call list_tasks
Complete task    Call complete_task
Delete task    Call delete_task
Update task    Call update_task
Ambiguous delete    List → confirm → delete

Mandatory Rules
Always confirm successful actions

Gracefully handle task-not-found errors

Never fabricate task IDs

Use tools ONLY when required

10. Stateless Conversation Flow
Receive user message

Load conversation + messages from DB

Append new user message

Run OpenAI Agent with MCP tools

Persist assistant response

Return response to client

Discard all in-memory state

11. Natural Language Coverage
The agent must correctly interpret:

"Add a task to buy groceries"

"What's pending?"

"Mark task 3 complete"

"Delete the meeting task"

"Change task 1 to call mom"

"What have I completed?"

12. Error Handling Requirements
Scenario    Expected Behavior
Task not found    Friendly error message
Invalid ID    Ask for clarification
Empty list    Inform user
Tool failure    Explain + retry suggestion

13. Deliverables
bash
Copy code
/frontend     → ChatKit UI
/backend      → FastAPI + Agents + MCP
/specs        → Spec files (this document)
/migrations   → SQL migrations
README.md
14. Acceptance Criteria
✅ All task actions via natural language
✅ MCP tools used exclusively
✅ Server fully stateless
✅ Conversations survive restarts
✅ Action confirmations shown
✅ Constitution fully respected

15. Spec Completion Statement
This specification is constitution-compliant, implementation-agnostic, and ready for:

bash
Copy code
/sp.plan"

## Response snapshot

"Created specification for Todo AI Chatbot (Basic Level) following the constitution requirements. The specification includes:

- User stories for basic todo management, conversation continuity, and advanced operations
- Functional requirements focused on user value without implementation details
- Key entities (Task, Conversation, Message) described at business level
- Success criteria with measurable outcomes
- Edge cases and error handling considerations

The specification adheres to the MCP-first and stateless server architecture principles while focusing on user value rather than implementation details."

## Outcome

- ✅ Impact: Created constitution-compliant specification for Todo AI Chatbot
- 🧪 Tests: No tests required for specification phase
- 📁 Files: specs/1-todo-ai-chatbot/spec.md and checklist created
- 🔁 Next prompts: Ready for /sp.plan to create implementation plan
- 🧠 Reflection: Specification balances user needs with architectural constraints

## Evaluation notes (flywheel)

- Failure modes observed: None - specification follows template correctly
- Graders run and results (PASS/FAIL): PASS - All required sections completed
- Prompt variant (if applicable): Standard specification creation
- Next experiment (smallest change to try): Proceed with /sp.plan to create implementation plan