"""
Chat API endpoint for natural language task management
Integrates OpenAI API with MCP tools for conversational interface
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
from openai import OpenAI

from ...database.connection import get_db
from ...middleware.auth_middleware import get_current_user
from ...models.User import User
from ...services.conversation_service import ConversationService
from ...mcp_tools.task_tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool,
    get_task_statistics_tool
)
from ...mcp_tools.tool_definitions import TASK_TOOLS

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# System prompt for the AI assistant
SYSTEM_PROMPT = """You are a helpful AI assistant for managing todo tasks. You can help users:
- Add new tasks to their todo list
- View their tasks (all, pending, or completed)
- Mark tasks as completed
- Update task details (title, description, priority, due date)
- Delete tasks
- Get statistics about their tasks

Be conversational, friendly, and helpful. When users ask to do something with their tasks, use the appropriate tools.
Always confirm actions and provide clear feedback about what was done.

When listing tasks, format them nicely and include relevant details like priority and due dates.
If a user's request is ambiguous, ask clarifying questions."""


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    tool_calls: Optional[List[Dict[str, Any]]] = None


def execute_tool_call(tool_name: str, arguments: Dict[str, Any], db: Session, user_id: int) -> Dict[str, Any]:
    """Execute a tool call and return the result"""

    tool_functions = {
        "add_task": add_task_tool,
        "list_tasks": list_tasks_tool,
        "complete_task": complete_task_tool,
        "delete_task": delete_task_tool,
        "update_task": update_task_tool,
        "get_task_statistics": get_task_statistics_tool
    }

    if tool_name not in tool_functions:
        return {"success": False, "message": f"Unknown tool: {tool_name}"}

    try:
        # Add db and user_id to arguments
        result = tool_functions[tool_name](db=db, user_id=user_id, **arguments)
        return result
    except Exception as e:
        return {"success": False, "message": f"Error executing {tool_name}: {str(e)}"}


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the chatbot and get a response.
    The chatbot uses OpenAI's function calling to manage tasks.
    """

    # Check for OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key or openai_api_key == "your-openai-api-key-here":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file"
        )

    # Initialize OpenAI client
    client = OpenAI(api_key=openai_api_key)

    conversation_service = ConversationService(db)

    # Get or create conversation
    if request.conversation_id:
        conversation = conversation_service.get_conversation(request.conversation_id, current_user.id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation_id = request.conversation_id
    else:
        conversation = conversation_service.get_or_create_latest_conversation(current_user.id)
        conversation_id = conversation["id"]

    # Save user message
    conversation_service.add_message(conversation_id, current_user.id, "user", request.message)

    # Get conversation history
    history = conversation_service.get_conversation_history(conversation_id, current_user.id, limit=20)

    # Build messages for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history
    for msg in history[:-1]:  # Exclude the message we just added
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current user message
    messages.append({"role": "user", "content": request.message})

    try:
        # Call OpenAI API with function calling
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            messages=messages,
            tools=TASK_TOOLS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message
        tool_calls_info = []

        # Handle tool calls if any
        if assistant_message.tool_calls:
            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute the tool
                tool_result = execute_tool_call(function_name, function_args, db, current_user.id)
                tool_calls_info.append({
                    "function": function_name,
                    "arguments": function_args,
                    "result": tool_result
                })

                # Add tool call and result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": tool_call.function.arguments
                        }
                    }]
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            # Get final response after tool execution
            final_response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                messages=messages
            )

            assistant_reply = final_response.choices[0].message.content
        else:
            assistant_reply = assistant_message.content

        # Save assistant response
        conversation_service.add_message(conversation_id, current_user.id, "assistant", assistant_reply)

        return ChatResponse(
            response=assistant_reply,
            conversation_id=conversation_id,
            tool_calls=tool_calls_info if tool_calls_info else None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all conversations for the current user"""
    conversation_service = ConversationService(db)
    conversations = conversation_service.list_conversations(current_user.id)
    return {"conversations": conversations}


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with its messages"""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_conversation(conversation_id, current_user.id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    conversation_service = ConversationService(db)
    success = conversation_service.delete_conversation(conversation_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted successfully"}
