import logging
from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
from pydantic import BaseModel

from .models import Message, MessageRole, ToolCall, ToolResponse
from .config import Settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        
    async def generate_response(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        use_tools: bool = True
    ) -> tuple[str, Optional[List[ToolCall]]]:
        try:
            openai_messages = self._convert_to_openai_format(messages)
            
            kwargs = {
                "model": self.settings.model_name,
                "messages": openai_messages,
                "max_tokens": self.settings.max_tokens,
                "temperature": self.settings.temperature,
            }
            
            if tools and use_tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            response = await self.client.chat.completions.create(**kwargs)
            
            message = response.choices[0].message
            content = message.content or ""
            
            tool_calls = None
            if message.tool_calls:
                tool_calls = [
                    ToolCall(
                        name=tc.function.name,
                        arguments=eval(tc.function.arguments) if tc.function.arguments else {}
                    )
                    for tc in message.tool_calls
                ]
            
            return content, tool_calls
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _convert_to_openai_format(self, messages: List[Message]) -> List[Dict[str, Any]]:
        openai_messages = []
        for msg in messages:
            openai_msg = {
                "role": msg.role.value,
                "content": msg.content
            }
            if msg.metadata and "name" in msg.metadata:
                openai_msg["name"] = msg.metadata["name"]
            openai_messages.append(openai_msg)
        return openai_messages
    
    async def handle_tool_response(
        self,
        messages: List[Message],
        tool_response: ToolResponse,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        messages.append(
            Message(
                role=MessageRole.TOOL,
                content=str(tool_response.result),
                metadata={"tool_name": tool_response.tool_name}
            )
        )
        
        response, _ = await self.generate_response(messages, tools, use_tools=False)
        return response