#!/usr/bin/env python3
"""
Run the FastMCP server
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mcp_server.fastmcp_server import mcp

if __name__ == "__main__":
    print("Starting FastMCP server...")
    print("Press Ctrl+C to stop")
    
    # Run with stdio transport for Claude compatibility
    mcp.run(transport="stdio")