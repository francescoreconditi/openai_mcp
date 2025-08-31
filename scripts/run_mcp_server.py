import uvicorn
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    uvicorn.run(
        "src.mcp_server.server:app",
        host="localhost",
        port=8001,
        reload=True,
        log_level="info"
    )