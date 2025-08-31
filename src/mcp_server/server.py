import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import Tool, ExecuteToolRequest, ExecuteToolResponse
from .tools import ToolRegistry

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

tool_registry = ToolRegistry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MCP test server...")
    yield
    logger.info("Shutting down MCP test server...")


app = FastAPI(
    title="MCP Test Server",
    description="Test MCP server with sample tools",
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
    return {"status": "healthy", "service": "mcp-test-server"}


@app.get("/tools", response_model=List[Tool])
async def get_tools():
    tools = tool_registry.get_tools()
    logger.info(f"Returning {len(tools)} available tools")
    return tools


@app.post("/tools/execute", response_model=ExecuteToolResponse)
async def execute_tool(request: ExecuteToolRequest):
    try:
        logger.info(f"Executing tool: {request.name}")
        result = await tool_registry.execute_tool(request.name, request.arguments)
        return ExecuteToolResponse(result=result)
    except ValueError as e:
        logger.error(f"Tool not found: {request.name}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing tool {request.name}: {str(e)}")
        return ExecuteToolResponse(error=str(e))


@app.get("/tools/{tool_name}")
async def get_tool_details(tool_name: str):
    tools = tool_registry.tools
    if tool_name not in tools:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    tool = tools[tool_name]
    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.parameters
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.mcp_server.server:app",
        host="localhost",
        port=8001,
        reload=True
    )