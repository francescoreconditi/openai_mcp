"""
Hybrid MCP server that supports both FastMCP (for Claude) and REST API (for backend)
"""
import asyncio
import json
from contextlib import asynccontextmanager
from typing import Dict, Any, List
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .fastmcp_server import mcp as fastmcp_server
from .models import Tool, ExecuteToolRequest, ExecuteToolResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Extract tools from FastMCP server
async def get_fastmcp_tools() -> List[Tool]:
    """Extract tools from FastMCP server and convert to our Tool model"""
    tools = []
    
    # Get tools from FastMCP using the correct async API
    fastmcp_tools = await fastmcp_server.get_tools()
    
    for tool_name, function_tool in fastmcp_tools.items():
        # Extract tool info from FunctionTool
        description = function_tool.description or f"Tool: {tool_name}"
        
        # Get the actual function to extract parameters
        actual_func = fastmcp_server._tool_manager._tools[tool_name].fn
        
        # Build parameter schema from type annotations
        parameters = {
            "type": "object", 
            "properties": {},
            "required": []
        }
        
        # Extract parameters from function signature
        import inspect
        sig = inspect.signature(actual_func)
        for param_name, param in sig.parameters.items():
            param_type = "string"  # default
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"
            
            # Extract description from docstring if available
            param_desc = f"Parameter: {param_name}"
            if actual_func.__doc__:
                # Simple extraction from docstring
                import re
                doc_lines = actual_func.__doc__.split('\n')
                for line in doc_lines:
                    if param_name in line and ':' in line:
                        param_desc = line.split(':', 1)[1].strip()
                        break
            
            parameters["properties"][param_name] = {
                "type": param_type,
                "description": param_desc
            }
            
            # Check if parameter has no default (required)
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
        
        tool = Tool(
            name=tool_name,
            description=description.split('\n')[0].strip(),  # First line as description
            parameters=parameters
        )
        tools.append(tool)
    
    return tools

async def execute_fastmcp_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Execute a tool using FastMCP"""
    try:
        # Get the actual function and call it directly
        if name in fastmcp_server._tool_manager._tools:
            tool = fastmcp_server._tool_manager._tools[name]
            func = tool.fn
            
            # Call the function with arguments
            if asyncio.iscoroutinefunction(func):
                result = await func(**arguments)
            else:
                result = func(**arguments)
            
            logger.info(f"Executed tool '{name}' successfully")
            return result
        else:
            raise ValueError(f"Tool '{name}' not found")
    except Exception as e:
        logger.error(f"Error executing tool '{name}': {str(e)}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting hybrid MCP server...")
    yield
    logger.info("Shutting down hybrid MCP server...")

# Create FastAPI app for REST API compatibility
app = FastAPI(
    title="Hybrid MCP Server",
    description="MCP server with FastMCP tools and REST API compatibility",
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
    return {"status": "healthy", "service": "hybrid-mcp-server"}

# MCP Standard SSE endpoint
@app.get("/sse")
async def mcp_sse_endpoint():
    """
    Standard MCP Server-Sent Events endpoint.
    This provides MCP protocol over HTTP streaming.
    """
    async def event_stream():
        """Generate SSE events for MCP protocol"""
        # Initial connection event
        yield f"data: {{\"type\": \"connection\", \"status\": \"connected\"}}\n\n"
        
        # Send available tools
        tools = await get_fastmcp_tools()
        tools_data = {
            "type": "tools",
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
                for tool in tools
            ]
        }
        yield f"data: {json.dumps(tools_data)}\n\n"
        
        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield f"data: {{\"type\": \"ping\"}}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/tools", response_model=List[Tool])
async def get_tools():
    """Get available tools"""
    tools = await get_fastmcp_tools()
    logger.info(f"Returning {len(tools)} available tools")
    return tools

@app.post("/tools/execute", response_model=ExecuteToolResponse)
async def execute_tool(request: ExecuteToolRequest):
    """Execute a tool"""
    try:
        logger.info(f"Executing tool: {request.name}")
        result = await execute_fastmcp_tool(request.name, request.arguments)
        return ExecuteToolResponse(result=result)
    except ValueError as e:
        logger.error(f"Tool not found: {request.name}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing tool {request.name}: {str(e)}")
        return ExecuteToolResponse(error=str(e))

@app.get("/tools/{tool_name}")
async def get_tool_details(tool_name: str):
    """Get details for a specific tool"""
    tools = await get_fastmcp_tools()
    tool = next((t for t in tools if t.name == tool_name), None)
    
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.parameters
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.mcp_server.hybrid_server:app",
        host="localhost",
        port=8001,
        reload=True
    )