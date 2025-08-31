import json
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
                        arguments=json.loads(tc.function.arguments) if tc.function.arguments else {}
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
            
            if msg.role == MessageRole.TOOL and msg.metadata and "tool_name" in msg.metadata:
                openai_msg["tool_call_id"] = f"call_{msg.metadata['tool_name']}"
                openai_msg["name"] = msg.metadata["tool_name"]
            elif msg.role == MessageRole.ASSISTANT and msg.metadata and "tool_calls" in msg.metadata:
                openai_msg["tool_calls"] = [
                    {
                        "id": f"call_{tc['name']}",
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"])
                        }
                    }
                    for tc in msg.metadata["tool_calls"]
                ]
            
            openai_messages.append(openai_msg)
        return openai_messages
    
