import uvicorn
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
        log_level="info"
    )