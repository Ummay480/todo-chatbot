<!--
  SYNC IMPACT REPORT (Phase III Todo AI Chatbot Constitution)
  Version: 1.0.1 (PATCH - update amendment date)
  Date: 2026-01-13

  Changes:
  - Updated amendment date to reflect current maintenance
  - Verified constitution alignment with Todo AI Chatbot requirements

  Templates requiring updates:
  - ✅ plan-template.md: MCP/stateless constraints verified
  - ✅ spec-template.md: MCP tool exposure requirements verified
  - ✅ tasks-template.md: MCP tool boundary organization verified

  All templates aligned with constitution requirements.
-->

# Phase III Todo AI Chatbot Constitution

## Core Principles

### I. MCP-First Architecture
Every feature must expose functionality through the MCP (Model Context Protocol) server as tools. AI agents interact with the system exclusively via MCP tools, never direct database access. This ensures standardization, auditability, and tool composability.

**Rules**:
- All task operations (add, list, complete, delete, update) MUST be MCP tools
- No direct database queries from agent code
- Tool definitions MUST include clear parameter schemas and return types
- Tool names MUST be verb-noun pairs (e.g., `add_task`, `list_tasks`)

**Rationale**: MCP provides a standardized, auditable interface. AI agents become composable tool-users rather than application-specific code.

### II. Stateless Server Architecture
The backend must hold NO conversational or application state. All state persists to the database; every request is independent and reproducible. This enables horizontal scaling, resilience, and simple deployments.

**Rules**:
- Database is the single source of truth
- Each API request must fetch all required context (conversation history, user state)
- No in-memory caches across requests
- Server restarts must not lose conversation continuity
- State transitions MUST be atomic (database transactions)

**Rationale**: Stateless servers are horizontally scalable, fault-tolerant, and testable. Any server instance can handle any request.

### III. Test-First Development (NON-NEGOTIABLE)
Tests MUST be written and approved before implementation begins. Follow Red-Green-Refactor strictly: tests fail → implement → tests pass → refactor.

**Rules**:
- Acceptance tests (Gherkin-style scenarios) written for every user story
- Unit tests for MCP tools and business logic
- Integration tests for database-agent workflows
- No code merged without passing all tests
- Test coverage MUST be measured and tracked per feature

**Rationale**: Tests serve as executable specifications and prevent regressions in a stateless, agent-driven system.

### IV. Spec-Driven Development
Every feature begins with a detailed specification that includes user stories, data model, API contracts, and MCP tool definitions. The spec is the source of truth; implementation follows the spec exactly.

**Rules**:
- specs/<feature>/spec.md MUST define all user stories with priorities (P1, P2, P3)
- specs/<feature>/plan.md MUST define architecture, MCP tool schemas, and data flow
- specs/<feature>/tasks.md MUST organize implementation by user story
- No implementation without approved spec and plan
- Changes to spec/plan MUST be reviewed and documented as amendments

**Rationale**: Specifications prevent scope creep, clarify requirements, and enable asynchronous handoff between design and implementation.

### V. Tool Composition & Chaining
Agents can invoke multiple MCP tools in a single request cycle to achieve complex goals. Tools MUST be composable—output of one tool can inform input to another.

**Rules**:
- Tools MUST return structured data (JSON with clear field types)
- Tool output MUST include enough context for the agent to decide next steps
- Tool errors MUST be clear and actionable
- Agent control flow (if-then, loops) happens in the agent, not in tools

**Rationale**: Composable tools enable agents to handle complex natural language commands (e.g., "delete the meeting task" → list_tasks + delete_task).

### VI. AI Agent Clarity
Agent behavior MUST be predictable and auditable. Natural language commands MUST map to clear, documented tool invocations. Errors and edge cases MUST be handled with explicit error messages.

**Rules**:
- Agent prompt MUST be version-controlled and reviewed
- Tool invocations MUST be logged and included in API responses
- Agent behavior table (user says → agent should) MUST guide all command interpretation
- Graceful error handling for missing tasks, invalid parameters, and user confusion

**Rationale**: AI agents are less transparent than deterministic code. Explicit documentation, logging, and behavior tables ensure users and operators understand what the agent will do.

## Technology Stack Constraints

The following technologies are **mandatory** for this project:

| Component | Technology | Notes |
|-----------|-----------|-------|
| Frontend | OpenAI ChatKit | Deployed to production domain (with allowlist) |
| Backend | Python FastAPI | Async, stateless endpoints |
| AI Framework | OpenAI Agents SDK | Native support for tool calling |
| MCP Server | Official MCP SDK | Exposes tools to agents |
| ORM | SQLModel | SQLAlchemy + Pydantic integration |
| Database | PostgreSQL or SQLite | Persistent state store |

**Constraint**: No substitutions without architectural review and amendment to this constitution.

## MCP Tool Contract Requirements

Every MCP tool MUST conform to these standards:

1. **Clear Purpose**: One tool = one action (single responsibility)
2. **Parameter Schema**: JSON schema with required/optional fields clearly marked
3. **Return Type**: Structured JSON with consistent status field (created, updated, completed, deleted, error)
4. **Error Handling**: Return error status with message, never throw exceptions to agent
5. **Idempotency**: Tool results MUST be consistent across repeated calls with same parameters
6. **Audit Trail**: Tool invocations logged with user_id, timestamp, parameters, result

**Mandatory Tools** (as specified in feature requirements):
- `add_task` (create)
- `list_tasks` (retrieve with filtering)
- `complete_task` (mark done)
- `delete_task` (remove)
- `update_task` (modify)

All tools MUST support user_id as a parameter for multi-tenant isolation.

## Development Workflow

### Phase: Specification
1. User provides feature description (natural language or requirements)
2. AI generates spec.md with prioritized user stories (P1, P2, P3)
3. User reviews and approves spec
4. AI generates plan.md with architecture, MCP tool schemas, data model
5. User reviews and approves plan
6. Team documents ADRs for significant architecture decisions

### Phase: Implementation
1. AI generates tasks.md organized by user story
2. User reviews and approves task breakdown
3. Implementation:
   - Write acceptance tests (Gherkin) for each user story
   - User approves tests before code is written
   - Implement code in Red-Green-Refactor cycles
   - Run all tests; code is not complete until tests pass
4. Code review verifies spec/plan compliance and test coverage
5. Merge to branch only after all checks pass

### Phase: Quality Gates
- All tests must pass (unit, integration, acceptance)
- Code coverage must not decrease
- MCP tools must validate parameters and return structured responses
- Stateless architecture must be verified (no in-memory state)
- Documentation must be updated (README, API docs, agent prompt)

## Governance

**Authority**: This constitution defines non-negotiable principles for all feature development on Phase III Todo AI Chatbot. Any deviation requires explicit amendment and team consensus.

**Amendment Process**:
1. Proposed amendment must be documented with rationale and impact analysis
2. Team review and discussion (async or sync)
3. Record decision as Architecture Decision Record (ADR)
4. Update this constitution with new version number
5. Update all affected templates and documentation

**Version Policy**:
- MAJOR: Principle removals or backward-incompatible redefinitions
- MINOR: New principle added or materially expanded guidance
- PATCH: Clarifications, wording, typo fixes, non-semantic refinements

**Compliance Review**:
- Every spec must declare which principles it adheres to (in spec.md header)
- Every plan must include "Constitution Check" section verifying alignment
- Every PR review must verify tasks were executed per spec/plan
- Quarterly architecture review to assess principle effectiveness

**Dispute Resolution**: If a developer or team member believes a principle hinders the project, they MUST document the concern as an issue. The team then discusses and either updates the constitution or provides written justification for keeping the principle.

---

**Version**: 1.0.1 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-01-13
