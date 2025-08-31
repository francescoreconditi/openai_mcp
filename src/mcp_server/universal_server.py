"""
Universal MCP Server - Supports all MCP standard transports
Compatibile con Claude Desktop, backend web, e altri client MCP
"""
import sys
import asyncio
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.mcp_server.fastmcp_server import mcp

def main():
    """
    Avvia il server MCP con il transport appropriato basato sui parametri.
    
    Supporta:
    - stdio: Per Claude Desktop e CLI tools
    - sse: Server-Sent Events per HTTP streaming (standard MCP)
    - hybrid: Modalità doppia per compatibilità massima
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "hybrid"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port for HTTP/SSE transport (default: 8001)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for HTTP/SSE transport (default: localhost)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        print("Starting MCP server with stdio transport (Claude Desktop compatible)...")
        mcp.run(transport="stdio")
        
    elif args.transport == "sse":
        print(f"Starting MCP server with SSE transport on {args.host}:{args.port}...")
        print("This is MCP standard HTTP streaming transport")
        print("WARNING: SSE mode does NOT include REST endpoints (/tools, /tools/execute)")
        print("Use --transport hybrid for both SSE and REST support")
        mcp.run(
            transport="sse",
            host=args.host,
            port=args.port
        )
        
    elif args.transport == "hybrid":
        print("Hybrid mode: Starting both SSE and REST endpoints...")
        print(f"SSE endpoint: http://{args.host}:{args.port}/sse")
        print(f"REST endpoints: http://{args.host}:{args.port}/tools")
        
        # In hybrid mode, we run the hybrid server that has both
        # FastMCP SSE support and REST API endpoints
        import uvicorn
        from src.mcp_server.hybrid_server import app
        
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=False
        )

if __name__ == "__main__":
    main()