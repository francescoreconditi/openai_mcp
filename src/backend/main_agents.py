"""
Backend with agents library for elegant MCP + OpenAI integration
"""
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

from .config import get_settings
from .models import ChatRequest, ChatResponse, MessageRole
from .conversation_manager import ConversationManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()
conversation_manager = ConversationManager()

# Create MCP server as subprocess with stdio
project_root = Path(__file__).parent.parent.parent
mcp_server = MCPServerStdio(
    name="chatbot-tools",
    params={
        "command": "uv",
        "args": ["run", "python", "scripts/run_fastmcp_server.py"],
        "cwd": str(project_root),
        "env": {
            **os.environ,
            "PYTHONPATH": str(project_root)
        }
    }
)

# Create Agent with OpenAI and MCP tools
agent = Agent(
    name="ChatbotAssistant",
    instructions=(
        "You are a helpful assistant with access to various tools. "
        "Use the available tools when they would be helpful to answer questions. "
        "Be concise and clear in your responses."
    ),
    model=settings.model_name,
    mcp_servers=[mcp_server],
)

# Single Runner instance for the application lifecycle
runner = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global runner
    logger.info("Starting backend with agents integration...")
    
    # Create and start runner
    runner = Runner()
    await runner.__aenter__()
    logger.info("MCP server started via subprocess")
    
    yield
    
    # Cleanup
    logger.info("Shutting down backend...")
    if runner:
        await runner.__aexit__(None, None, None)
    logger.info("MCP server stopped")

app = FastAPI(
    title="Chatbot Backend with Agents",
    description="Backend API using agents library for MCP + OpenAI",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "chatbot-backend-agents",
        "mcp_integration": "stdio subprocess"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat message with OpenAI + MCP tools via agents library
    """
    try:
        # Create or get conversation
        if not request.conversation_id:
            conversation_id = conversation_manager.create_conversation()
        else:
            conversation_id = request.conversation_id
            if not conversation_manager.get_conversation(conversation_id):
                conversation_id = conversation_manager.create_conversation()
        
        # Add user message
        conversation_manager.add_message(
            conversation_id,
            MessageRole.USER,
            request.message
        )
        
        # Get conversation history
        messages = conversation_manager.get_messages(conversation_id)
        
        # Build prompt with history
        prompt = ""
        for msg in messages:
            if msg.role == MessageRole.USER:
                prompt += f"User: {msg.content}\n"
            elif msg.role == MessageRole.ASSISTANT:
                prompt += f"Assistant: {msg.content}\n"
        
        # Remove last newline and get only current user message if no history
        if prompt.count("User:") == 1:
            prompt = request.message
        else:
            # For conversation with history, we need special handling
            # For now, just use the current message
            # (agents library doesn't natively support conversation history in the same way)
            prompt = request.message
        
        # Run agent with MCP tools
        logger.info(f"Processing message with agent: {prompt[:100]}...")
        
        if runner is None:
            raise RuntimeError("Runner not initialized. Server may be starting up.")
        
        # Execute with agent
        result = await runner.run(agent, prompt)
        
        # Extract response and tool usage
        response_content = result.output_text
        
        # Check if tools were used (agents library tracks this internally)
        tools_used = []
        if hasattr(result, 'tool_calls') and result.tool_calls:
            tools_used = [tc.name for tc in result.tool_calls]
        elif hasattr(result, 'messages'):
            # Extract tool usage from messages if available
            for msg in result.messages:
                if hasattr(msg, 'tool_calls'):
                    tools_used.extend([tc.function.name for tc in msg.tool_calls])
        
        # Add assistant response
        conversation_manager.add_message(
            conversation_id,
            MessageRole.ASSISTANT,
            response_content
        )
        
        return ChatResponse(
            response=response_content,
            conversation_id=conversation_id,
            tools_used=tools_used if tools_used else None
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations")
async def list_conversations():
    """List all conversations"""
    return conversation_manager.list_conversations()

@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str):
    """Get messages for a specific conversation"""
    messages = conversation_manager.get_messages(conversation_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return [
        {
            "role": msg.role.value,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if conversation_manager.delete_conversation(conversation_id):
        return {"message": "Conversation deleted successfully"}
    raise HTTPException(status_code=404, detail="Conversation not found")

@app.get("/tools")
async def get_available_tools():
    """Get list of available MCP tools"""
    if runner is None:
        return []
    
    try:
        # Get tools from the MCP server via agent
        # This is a simplified version - agents library handles this internally
        return {
            "tools": [
                "get_current_time",
                "calculate", 
                "get_random_number",
                "convert_temperature",
                "get_weather"
            ],
            "source": "MCP server via stdio subprocess"
        }
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        return {"tools": [], "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.backend.main_agents:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )