#!/usr/bin/env python3
"""
Run the backend with agents library integration
This version uses MCP server as subprocess via stdio
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.backend.config import get_settings

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    print("Starting Backend with agents library...")
    print(f"Backend URL: http://{settings.backend_host}:{settings.backend_port}")
    print("MCP integration: stdio subprocess (no separate server needed)")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "src.backend.main_agents:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )