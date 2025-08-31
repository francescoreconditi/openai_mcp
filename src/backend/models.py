from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    use_tools: bool = Field(default=True, description="Whether to use MCP tools")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    tools_used: Optional[List[str]] = Field(default=None, description="List of MCP tools used")
    metadata: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    name: str = Field(..., description="Tool name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    
    
class ToolResponse(BaseModel):
    tool_name: str = Field(..., description="Tool name")
    result: Any = Field(..., description="Tool execution result")
    error: Optional[str] = Field(None, description="Error message if tool execution failed")
    

class Conversation(BaseModel):
    id: str = Field(..., description="Unique conversation ID")
    messages: List[Message] = Field(default_factory=list, description="List of messages")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None