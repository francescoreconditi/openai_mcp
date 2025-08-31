import httpx
import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from .models import ToolCall, ToolResponse
from .config import Settings

logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = f"http://{settings.mcp_server_host}:{settings.mcp_server_port}"
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        try:
            response = await self.client.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching available tools: {str(e)}")
            return []
    
    async def execute_tool(self, tool_call: ToolCall) -> ToolResponse:
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/execute",
                json={
                    "name": tool_call.name,
                    "arguments": tool_call.arguments
                }
            )
            response.raise_for_status()
            result = response.json()
            
            return ToolResponse(
                tool_name=tool_call.name,
                result=result.get("result"),
                error=result.get("error")
            )
        except Exception as e:
            logger.error(f"Error executing tool {tool_call.name}: {str(e)}")
            return ToolResponse(
                tool_name=tool_call.name,
                result=None,
                error=str(e)
            )
    
    async def close(self):
        await self.client.aclose()
    
    def convert_tools_to_openai_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        openai_tools = []
        for tool in tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                }
            }
            openai_tools.append(openai_tool)
        return openai_tools