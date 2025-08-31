import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models import ChatRequest, ChatResponse, MessageRole
from .openai_client import OpenAIClient
from .mcp_client import MCPClient
from .conversation_manager import ConversationManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()
conversation_manager = ConversationManager()
openai_client = OpenAIClient(settings)
mcp_client = MCPClient(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up backend server...")
    yield
    logger.info("Shutting down backend server...")
    await mcp_client.close()


app = FastAPI(
    title="Chatbot Backend",
    description="Backend API for OpenAI and MCP integration",
    version="0.1.0",
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
    return {"status": "healthy", "service": "chatbot-backend"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not request.conversation_id:
            conversation_id = conversation_manager.create_conversation()
        else:
            conversation_id = request.conversation_id
            if not conversation_manager.get_conversation(conversation_id):
                conversation_id = conversation_manager.create_conversation()
        
        conversation_manager.add_message(
            conversation_id,
            MessageRole.USER,
            request.message
        )
        
        messages = conversation_manager.get_messages(conversation_id)
        
        tools_used = []
        
        if request.use_tools:
            tools = await mcp_client.get_available_tools()
            openai_tools = mcp_client.convert_tools_to_openai_format(tools)
            
            response_content, tool_calls = await openai_client.generate_response(
                messages,
                openai_tools,
                use_tools=True
            )
            
            if tool_calls:
                # Add assistant message with tool calls
                conversation_manager.add_message(
                    conversation_id,
                    MessageRole.ASSISTANT,
                    response_content or "",
                    metadata={"tool_calls": [{"name": tc.name, "arguments": tc.arguments} for tc in tool_calls]}
                )
                
                for tool_call in tool_calls:
                    tool_response = await mcp_client.execute_tool(tool_call)
                    tools_used.append(tool_call.name)
                    
                    if not tool_response.error:
                        # Add tool response message
                        conversation_manager.add_message(
                            conversation_id,
                            MessageRole.TOOL,
                            str(tool_response.result),
                            metadata={"tool_name": tool_response.tool_name}
                        )
                
                # Get updated messages and generate final response
                messages = conversation_manager.get_messages(conversation_id)
                response_content, _ = await openai_client.generate_response(
                    messages,
                    tools=None,
                    use_tools=False
                )
        else:
            response_content, _ = await openai_client.generate_response(
                messages,
                tools=None,
                use_tools=False
            )
        
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
    return conversation_manager.list_conversations()


@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str):
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
    if conversation_manager.delete_conversation(conversation_id):
        return {"message": "Conversation deleted successfully"}
    raise HTTPException(status_code=404, detail="Conversation not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )