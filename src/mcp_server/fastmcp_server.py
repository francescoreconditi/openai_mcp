import datetime
import json
import random
from typing import Dict, Any
import logging

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Chatbot Tools")

@mcp.tool()
def get_current_time(timezone: str = "UTC") -> str:
    """Get the current date and time.
    
    Args:
        timezone: Timezone (e.g., 'UTC', 'America/New_York')
    
    Returns:
        Current time in the specified timezone
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"Current time in {timezone}: {now.isoformat()}"

@mcp.tool()
def calculate(expression: str) -> float:
    """Perform basic mathematical calculations.
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        Result of the calculation
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")

@mcp.tool()
def get_random_number(min: float = 0, max: float = 100) -> int:
    """Generate a random number within a range.
    
    Args:
        min: Minimum value (default: 0)
        max: Maximum value (default: 100)
        
    Returns:
        Random integer between min and max
    """
    return random.randint(int(min), int(max))

@mcp.tool()
def convert_temperature(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """Convert temperature between Celsius, Fahrenheit, and Kelvin.
    
    Args:
        value: Temperature value to convert
        from_unit: Source temperature unit (celsius, fahrenheit, kelvin)
        to_unit: Target temperature unit (celsius, fahrenheit, kelvin)
        
    Returns:
        Dictionary with conversion details
    """
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # Convert to celsius first
    if from_unit == "celsius":
        celsius = value
    elif from_unit == "fahrenheit":
        celsius = (value - 32) * 5/9
    elif from_unit == "kelvin":
        celsius = value - 273.15
    else:
        raise ValueError(f"Invalid from_unit: {from_unit}")
    
    # Convert from celsius to target
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

@mcp.tool()
def get_weather(city: str) -> Dict[str, Any]:
    """Get mock weather information for a city.
    
    Args:
        city: City name
        
    Returns:
        Dictionary with weather information
    """
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

if __name__ == "__main__":
    import sys
    
    # Check if running with --http flag for backend compatibility
    if "--http" in sys.argv:
        print("Starting FastMCP server with HTTP transport for backend compatibility...")
        mcp.run(
            transport="sse",
            host="localhost", 
            port=8001
        )
    else:
        print("Starting FastMCP server with stdio transport...")
        print("Compatible with: Claude Desktop, agents library, or any MCP client")
        mcp.run(transport="stdio")