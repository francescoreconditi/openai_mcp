import datetime
import json
import random
from typing import Dict, Any, List
import logging

from .models import Tool

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.handlers: Dict[str, callable] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        self.register_tool(
            Tool(
                name="get_current_time",
                description="Get the current date and time",
                parameters={
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
            ),
            self._get_current_time
        )
        
        self.register_tool(
            Tool(
                name="calculate",
                description="Perform basic mathematical calculations",
                parameters={
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            ),
            self._calculate
        )
        
        self.register_tool(
            Tool(
                name="get_random_number",
                description="Generate a random number within a range",
                parameters={
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
            ),
            self._get_random_number
        )
        
        self.register_tool(
            Tool(
                name="convert_temperature",
                description="Convert temperature between Celsius, Fahrenheit, and Kelvin",
                parameters={
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
            ),
            self._convert_temperature
        )
        
        self.register_tool(
            Tool(
                name="get_weather",
                description="Get mock weather information for a city",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City name"
                        }
                    },
                    "required": ["city"]
                }
            ),
            self._get_weather
        )
    
    def register_tool(self, tool: Tool, handler: callable):
        self.tools[tool.name] = tool
        self.handlers[tool.name] = handler
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tools(self) -> List[Tool]:
        return list(self.tools.values())
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name not in self.handlers:
            raise ValueError(f"Tool '{name}' not found")
        
        handler = self.handlers[name]
        try:
            result = await handler(arguments) if hasattr(handler, '__await__') else handler(arguments)
            logger.info(f"Executed tool '{name}' successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool '{name}': {str(e)}")
            raise
    
    def _get_current_time(self, arguments: Dict[str, Any]) -> str:
        timezone = arguments.get("timezone", "UTC")
        now = datetime.datetime.now(datetime.timezone.utc)
        return f"Current time in {timezone}: {now.isoformat()}"
    
    def _calculate(self, arguments: Dict[str, Any]) -> float:
        expression = arguments.get("expression", "")
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return float(result)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    def _get_random_number(self, arguments: Dict[str, Any]) -> int:
        min_val = arguments.get("min", 0)
        max_val = arguments.get("max", 100)
        return random.randint(int(min_val), int(max_val))
    
    def _convert_temperature(self, arguments: Dict[str, Any]) -> Dict[str, float]:
        value = float(arguments["value"])
        from_unit = arguments["from_unit"].lower()
        to_unit = arguments["to_unit"].lower()
        
        if from_unit == "celsius":
            celsius = value
        elif from_unit == "fahrenheit":
            celsius = (value - 32) * 5/9
        elif from_unit == "kelvin":
            celsius = value - 273.15
        else:
            raise ValueError(f"Invalid from_unit: {from_unit}")
        
        if to_unit == "celsius":
            result = celsius
        elif to_unit == "fahrenheit":
            result = celsius * 9/5 + 32
        elif to_unit == "kelvin":
            result = celsius + 273.15
        else:
            raise ValueError(f"Invalid to_unit: {to_unit}")
        
        return {
            "original_value": value,
            "original_unit": from_unit,
            "converted_value": round(result, 2),
            "converted_unit": to_unit
        }
    
    def _get_weather(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
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