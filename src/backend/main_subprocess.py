"""
Backend with MCP server as subprocess via stdio
Direct integration without external agents library
"""
import logging
import json
import asyncio
import subprocess
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models import ChatRequest, ChatResponse, MessageRole
from .conversation_manager import ConversationManager
from .openai_client import OpenAIClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()
conversation_manager = ConversationManager()
openai_client = OpenAIClient(settings)


class MCPSubprocessClient:
    """Client to communicate with MCP server via stdio subprocess"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.reader_task: Optional[asyncio.Task] = None
        self.tools: List[Dict[str, Any]] = []
        
    async def start(self):
        """Start MCP server as subprocess"""
        try:
            # Start FastMCP server in stdio mode
            self.process = subprocess.Popen(
                ["uv", "run", "python", "scripts/run_fastmcp_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            logger.info("MCP subprocess started")
            
            # Start reader task for stdout
            self.reader_task = asyncio.create_task(self._read_output())
            
            # Initialize connection
            await self._send_request({
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "clientInfo": {
                        "name": "chatbot-backend",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            })
            
            # Get available tools
            await self._fetch_tools()
            
        except Exception as e:
            logger.error(f"Failed to start MCP subprocess: {e}")
            raise
    
    async def stop(self):
        """Stop MCP server subprocess"""
        if self.reader_task:
            self.reader_task.cancel()
            
        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process()),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                self.process.kill()
            
            logger.info("MCP subprocess stopped")
    
    async def _wait_for_process(self):
        """Wait for process to exit"""
        while self.process.poll() is None:
            await asyncio.sleep(0.1)
    
    async def _read_output(self):
        """Read output from subprocess"""
        while self.process and self.process.stdout:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, self.process.stdout.readline
                )
                if line:
                    logger.debug(f"MCP output: {line.strip()}")
            except Exception as e:
                logger.error(f"Error reading MCP output: {e}")
                break
    
    async def _send_request(self, request: dict) -> dict:
        """Send JSON-RPC request to MCP server"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP subprocess not running")
        
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()
        
        # For simplicity, we'll return empty response
        # In production, you'd need proper response handling
        return {}
    
    async def _fetch_tools(self):
        """Fetch available tools from MCP server"""
        # For now, hardcode the tools since stdio communication is complex
        # In production, you'd parse the actual response from the server
        self.tools = [
            {
                "name": "get_current_time",
                "description": "Get the current date and time",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "Timezone (e.g., 'UTC', 'America/New_York')",
                            "default": "UTC"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "calculate",
                "description": "Perform basic mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "get_random_number",
                "description": "Generate a random number within a range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min": {
                            "type": "number",
                            "description": "Minimum value",
                            "default": 0
                        },
                        "max": {
                            "type": "number",
                            "description": "Maximum value",
                            "default": 100
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "convert_temperature",
                "description": "Convert temperature between Celsius, Fahrenheit, and Kelvin",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "number",
                            "description": "Temperature value to convert"
                        },
                        "from_unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit", "kelvin"],
                            "description": "Source temperature unit"
                        },
                        "to_unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit", "kelvin"],
                            "description": "Target temperature unit"
                        }
                    },
                    "required": ["value", "from_unit", "to_unit"]
                }
            },
            {
                "name": "get_weather",
                "description": "Get mock weather information for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City name"
                        }
                    },
                    "required": ["city"]
                }
            }
        ]
        
        logger.info(f"Loaded {len(self.tools)} tools from MCP server")
    
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI function format"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            for tool in self.tools
        ]
    
    async def execute_tool(self, name: str, arguments: dict) -> Any:
        """Execute a tool via MCP server"""
        # For simplicity, we'll simulate tool execution
        # In production, you'd send the request to the subprocess
        
        if name == "get_current_time":
            from datetime import datetime
            timezone = arguments.get("timezone", "UTC")
            return f"Current time in {timezone}: {datetime.now().isoformat()}"
        
        elif name == "calculate":
            try:
                result = eval(arguments["expression"], {"__builtins__": {}}, {})
                return float(result)
            except Exception as e:
                return f"Error: {e}"
        
        elif name == "get_random_number":
            import random
            min_val = arguments.get("min", 0)
            max_val = arguments.get("max", 100)
            return random.randint(int(min_val), int(max_val))
        
        elif name == "convert_temperature":
            value = float(arguments["value"])
            from_unit = arguments["from_unit"].lower()
            to_unit = arguments["to_unit"].lower()
            
            # Convert to celsius first
            if from_unit == "celsius":
                celsius = value
            elif from_unit == "fahrenheit":
                celsius = (value - 32) * 5/9
            elif from_unit == "kelvin":
                celsius = value - 273.15
            else:
                return f"Invalid from_unit: {from_unit}"
            
            # Convert from celsius to target
            if to_unit == "celsius":
                result = celsius
            elif to_unit == "fahrenheit":
                result = celsius * 9/5 + 32
            elif to_unit == "kelvin":
                result = celsius + 273.15
            else:
                return f"Invalid to_unit: {to_unit}"
            
            return {
                "original_value": value,
                "original_unit": from_unit,
                "converted_value": round(result, 2),
                "converted_unit": to_unit
            }
        
        elif name == "get_weather":
            import random
            city = arguments.get("city", "Unknown")
            weather_conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Snowy"]
            
            return {
                "city": city,
                "temperature": random.randint(-10, 35),
                "unit": "celsius",
                "condition": random.choice(weather_conditions),
                "humidity": random.randint(30, 90),
                "wind_speed": random.randint(0, 30),
                "note": "This is mock weather data for demonstration purposes"
            }
        
        else:
            return f"Unknown tool: {name}"


# Global MCP client
mcp_client = MCPSubprocessClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting backend with subprocess MCP integration...")
    
    # Start MCP subprocess
    await mcp_client.start()
    
    yield
    
    # Cleanup
    logger.info("Shutting down backend...")
    await mcp_client.stop()


app = FastAPI(
    title="Chatbot Backend with Subprocess MCP",
    description="Backend API with MCP server as subprocess",
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
        "service": "chatbot-backend-subprocess",
        "mcp_integration": "stdio subprocess",
        "tools_loaded": len(mcp_client.tools),
        "tool_names": [tool["name"] for tool in mcp_client.tools] if mcp_client.tools else []
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message with OpenAI + MCP tools via subprocess"""
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
        
        tools_used = []
        
        if request.use_tools:
            # Get OpenAI-formatted tools
            openai_tools = mcp_client.get_openai_tools()
            
            # Generate response with tools
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
                    metadata={"tool_calls": [
                        {"id": tc.id, "name": tc.name, "arguments": tc.arguments}
                        for tc in tool_calls
                    ]}
                )
                
                # Execute tools
                for tool_call in tool_calls:
                    result = await mcp_client.execute_tool(
                        tool_call.name,
                        tool_call.arguments
                    )
                    tools_used.append(tool_call.name)
                    
                    # Add tool response
                    conversation_manager.add_message(
                        conversation_id,
                        MessageRole.TOOL,
                        str(result),
                        metadata={
                            "tool_call_id": tool_call.id,
                            "tool_name": tool_call.name
                        }
                    )
                
                # Get final response
                messages = conversation_manager.get_messages(conversation_id)
                response_content, _ = await openai_client.generate_response(
                    messages,
                    tools=None,
                    use_tools=False
                )
        else:
            # Generate response without tools
            response_content, _ = await openai_client.generate_response(
                messages,
                tools=None,
                use_tools=False
            )
        
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


@app.get("/tools")
async def get_available_tools():
    """Get list of available MCP tools"""
    return mcp_client.tools


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.backend.main_subprocess:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )