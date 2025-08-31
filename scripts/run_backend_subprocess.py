#!/usr/bin/env python3
"""
Run the backend with MCP server as subprocess
No separate MCP server needed - it runs as subprocess via stdio
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
    
    print("=" * 60)
    print("Starting Backend with MCP Subprocess Integration")
    print("=" * 60)
    print(f"Backend URL: http://{settings.backend_host}:{settings.backend_port}")
    print("MCP Server: Runs as subprocess (no separate server needed)")
    print("Benefits:")
    print("  - Single process to manage")
    print("  - MCP server starts/stops with backend")
    print("  - Same server works with Claude Desktop")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print()
    
    uvicorn.run(
        "src.backend.main_subprocess:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )