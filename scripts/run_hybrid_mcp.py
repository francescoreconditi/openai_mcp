#!/usr/bin/env python3
"""
Run the hybrid MCP server (FastMCP + REST API)
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    
    print("Starting Hybrid MCP Server on port 8001...")
    print("Provides both FastMCP tools and REST API compatibility")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "src.mcp_server.hybrid_server:app",
        host="localhost",
        port=8001,
        reload=True
    )