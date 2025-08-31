#!/usr/bin/env python3
"""
Run the Universal MCP Server with configurable transport
Supports stdio (Claude), SSE (MCP HTTP standard), and hybrid mode
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    from src.mcp_server.universal_server import main
    main()